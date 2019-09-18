from tkinter import Canvas
from uuid import uuid4
import base64, itertools, math
from factorygame.utils.loc import Loc
from factorygame.utils.tkutils import MotionInput, ScalingImage
from factorygame.utils.gameplay import GameplayStatics
from factorygame.utils.mymath import MathStat
from factorygame.core.engine_base import World, Actor

class Drawable(object):
    """
    Abstract base class for objects receiving draw calls.
    
    Each draw cycle must be invoked with `start_cycle`, and
    consists of these stages:
    _clear, _should_draw, _draw
    """

    def start_cycle(self):
        """Start a full draw cycle."""
        self._clear()
        if self._should_draw():
            self._draw()

    def _clear(self):
        """
        Called every draw cycle before drawing to clear previous drawing.
        
        Override for clearing behaviour.
        """
        pass

    def _should_draw(self):
        """
        Called every draw cycle before drawing to decide whether
        anything should be drawn.

        Override for special branching behaviour (default always true).

        :return: (bool) Whether anything should be drawn.
        """
        return True

    def _draw(self):
        """
        Called every draw cycle to create new drawing.

        Override for drawing behaviour.
        """
        pass

class DrawnActor(Actor, Drawable):
    """Base class for drawable actors who receive a draw cycle each frame."""

    def __init__(self):
        """Set default values."""

        ## Random, serialisable unique ID for this drawable object.
        self.unique_id = uuid4()

    def tick(self, dt):
        """Called every frame to perform draw cycle."""
        self.start_cycle()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def _clear(self):
        self.world.delete(self.unique_id)

    # End of drawable interface.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class NodeBase(DrawnActor):
    """
    Base class for nodes in a graph with visual representation.
    By default it is only drawn when its location is in the viewport.
    """

    def __init__(self):
        """Set default values."""
        super().__init__()

        ## Amount of viewport padding to give when deciding whether to draw
        self.drawable_padding = Loc(300, 300)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def _should_draw(self):
        """Only draw if visible in the blueprint graph."""
        graph = self.world
        tr, bl = graph.get_view_coords()
        tr += self.drawable_padding
        bl -= self.drawable_padding

        my_coords = self.location

        return (bl.x < my_coords.x < tr.x) \
            and (bl.y < my_coords.y < tr.y)

    def _draw(self):
        c1 = self.world.view_to_canvas(self.location)
        c2 = self.world.view_to_canvas(self.location + 100)
        self.world.create_oval(c1, c2, tags=(self.unique_id))

    # End of drawable interface.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class PolygonNode(NodeBase):
    """
    A polygon with a set of vertices. Optionally can
    create regular polygon presets.
    """

    def __init__(self):
        """Set default values."""
        super().__init__()

        ## Set of vertex coordinates (Loc) that make up the polygon.
        self._vertices = tuple()

    @property
    def vertices(self):
        return self._vertices

    @vertices.setter
    def vertices(self, value):
        # Only allow setting all vertices at once. Since Loc
        # objects are mutable, the referenced objects can still
        # be manipulated.

        if len(value) < 3:
            raise ValueError("Polygon must have at least 3 vertices")

        self._vertices = tuple(value)

    def __getitem__(self, index):
        """Return the vertex at the given index."""
        return self._vertices[index]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def _draw(self):
        # Create a generator to convert vertices into canvas coordinates.
        transpose_func = self.world.view_to_canvas
        transposed_verts = map(transpose_func, self.vertices)

        self.world.create_polygon(*transposed_verts,
            tags=(self.unique_id))

    # End of drawable interface.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class ImageNode(NodeBase):
    """Node that shows an image. EXPERIMENTAL!!!"""
    def __init__(self):
        super().__init__()

        ## Path to look in for the image.
        self.image_path = ""

        ## Reference to image that is shown by this node.
        self.image_ref = None

        ## Scaling to always apply to image (before graph scaling).
        self.image_base_scale = 1

        ## Last scale used on the image.
        self.image_scale = 1.0

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of actor interface.

    def begin_play(self):
        self._init_image()

    # End of actor interface.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def _init_image(self):
        """Initialise the scaling image from image_path."""
        self.image_ref = ScalingImage(file=self.image_path)
        # Setup callback for after scaling the image.
        self.image_ref.on_assign_image = self.on_assign_image
        self._scale_image()

    def _scale_image(self):
        """Scale the image to match the current zoom ratio."""
        graph = self.world
        img = self.image_ref.get_original_image()

        # Use a real number for the scale.
        new_scale = self.image_base_scale \
            * (1/graph.zoom_ratio) \
            * graph.get_screen_size_factor()

        # Only scale if scale changed.
        if new_scale == self.image_scale: return
        self.image_scale = new_scale


        # Get the original image, otherwise the
        # scale would get multiplied each time.
        img = img.scale(new_scale)
        # img = img.scale_continuous(new_scale)
        # TODO: Use a timer to call scale_continuous_end

        self.on_assign_image(img)

    def on_assign_image(self, image_to_use):
        """Set the actively shown image to IMAGE_TO_USE."""
        self.image_ref = image_to_use

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def _draw(self):
        self._scale_image()
        c1 = self.world.view_to_canvas(self.location)
        self.world.create_image(c1, image=self.image_ref,
            tags=(self.unique_id))

        self.world.create_text(self.world.view_to_canvas(self.location),
            text=round(self.image_scale, 2), tags=(self.unique_id))

    # End of drawable interface.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GraphBase(Canvas, Drawable):
    """
    Base blueprint graph for displaying drawable objects.
    
    :warning: Does not redraw graph automatically, to avoid
    redraw lags with constant motion. Call `start_cycle()` to 
    redraw.
    """

    ## Constant for button to hold and drag to move graph.
    ## Default is 3 (right mouse button).
    GRAPH_MOTION_BUTTON = property(lambda self: 3)

    def __get_zoom_ratio(self):
        return self._zoom_ratio
    def __set_zoom_ratio(self, value):
        # Only allow values between 1 and 20.
        self._zoom_ratio = int(MathStat.clamp(value, 1, 20))
        # Calculate zoom amount for later calculations.
        self._zoom_amt = 1 / self._zoom_ratio

    ## Integer property for zoom level [1-20].
    ## Higher values zoom out further.
    zoom_ratio = property(__get_zoom_ratio, __set_zoom_ratio)

    def __init__(self, master=None, cnf={}, **kw):
        """Initialiase blueprint graph in widget MASTER."""

        # Set default values.

        ## Offset of viewport from center of the graph in pixels.
        self._view_offset   = Loc(0, 0)

        ## Relative zoom factor of the viewport.
        self._zoom_amt      = 0.0

        ## Set zoom ratio. Default is 3.
        self._zoom_ratio    = 3

        ## Inversion scale for graph motion, for x and y independently.
        ## Should only be 1 or -1 per axis.
        self.axis_inversion = Loc(1, 1)


        # Initialise canvas parent.
        Canvas.__init__(self, master, cnf, **kw)

        # Create and bind motion input object to receive motion events.
        self.motioninput = MotionInput(self, self.GRAPH_MOTION_BUTTON,
            normalise=False)
        self.motioninput.bind("Motion-XY", self.on_graph_motion_input)

        # Bind mouse wheel events for zoom.
        self.bind("<MouseWheel>", self.on_graph_wheel_input)

    def on_graph_motion_input(self, event):
        """Called when a motion event occurs on the graph."""
        screen_size_factor = self.get_screen_size_factor()

        motion = event.delta \
            * self.axis_inversion \
            * self.zoom_ratio \
            * math.e \
            * screen_size_factor

        motion.x *= -1 # Invert x axis because delta motion is inverted
        self._view_offset += motion

    def on_graph_wheel_input(self, event):
        """Called when a mouse wheel event occurs on the graph."""
        # On windows wheel delta is in 120x
        # Zoom out on scroll down
        self.zoom_ratio += (-event.delta / 120)

        # TODO: also change _view_offset to use mouse cursor as center of zoom.

    def get_canvas_dim(self):
        """Return dimensions of canvas in pixels as a Loc."""
        return Loc(self.winfo_width(), self.winfo_height())

    def get_screen_size_factor(self):
        """Return the viewport scale factor to ensure the same
        sized viewport is shown at all scales."""
        return MathStat.clamp(max(MathStat.getpercent(self.get_canvas_dim(), Loc(3840, 2160), Loc(640, 480))), 0.5, 8)

    def get_view_dim(self):
        """Return dimensions of viewport in coordinates as a Loc."""
        screen_size_factor = self.get_screen_size_factor()
        return self.get_canvas_dim() * self.zoom_ratio * screen_size_factor

    def get_view_coords(self):
        """Return top right and bottom left coordinates of viewport
        as a 2 tuple of Loc."""
        center = self._view_offset
        screen_size_factor = self.get_screen_size_factor()
        half_bounds = (self.get_view_dim() / 2) * (screen_size_factor / 2)
        tr = center + half_bounds
        bl = center - half_bounds
        return tr, bl

    def view_to_canvas(self, in_coords, clamp_to_viewport=False):
        """
        Return viewport coordinates in canvas coordinates as a Loc.
        
        :param in_coords: Viewport coordinates as a Loc.

        :param clamp_to_viewport: Whether to clamp coordinates to valid
        canvas coordinates.

        :return: Canvas coordinates converted from in_coords.
        """
        canvas_dim = self.get_canvas_dim()
        tr, bl = self.get_view_coords()

        if clamp_to_viewport:
            coords = Loc(
            MathStat.map_range_clamped(in_coords.x, bl.x, tr.x, 0, canvas_dim.x),
            MathStat.map_range_clamped(in_coords.y, bl.y, tr.y, canvas_dim.y, 0))

        else:
            coords = Loc(
            MathStat.map_range(in_coords.x, bl.x, tr.x, 0, canvas_dim.x),
            MathStat.map_range(in_coords.y, bl.y, tr.y, canvas_dim.y, 0))

        return coords

    def canvas_to_view(self, in_coords, clamp_to_canvas=False):
        """
        Return canvas coordinates in viewport coordinates as a Loc.
        
        :param in_coords: Canvas coordinates as a Loc.

        :param clamp_to_canvas: Whether to clamp coordinates to valid
        viewport coordinates.

        :return: Viewport coordinates converted from in_coords.
        """
        canvas_dim = self.get_canvas_dim()
        tr, bl = self.get_view_coords()

        if clamp_to_canvas:
            coords = Loc(
            MathStat.map_range_clamped(in_coords.x, 0, canvas_dim.x, bl.x, tr.x),
            MathStat.map_range_clamped(in_coords.y, canvas_dim.y, 0, bl.y, tr.y))

        else:
            coords = Loc(
            MathStat.map_range(in_coords.x, 0, canvas_dim.x, bl.x, tr.x),
            MathStat.map_range(in_coords.y, canvas_dim.y, 0, bl.y, tr.y))

        return coords

class GridGismo(DrawnActor):
    """
    Actor class to show grid lines on the viewport area
    which is currently visible.
    """
    
    def __init__(self):
        """Set default values."""
        
        ## Average size of each square grid, in pixels.
        self.grid_size = 300

        super().__init__()
        

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def _clear(self):
        """Clear old drawn canvas elements."""
        # Delete old grid lines.
        self.world.delete(self.unique_id)

    def _draw(self):
        """Create new grid lines."""

        # Draw the grid lines.
        self.__draw_grid()
        self.__draw_grid_origin_lines()

        # TODO: Add additional draw functions here.

    # End of drawable interface.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __draw_grid(self, draw_axis_numbers=True):
        """Create grid lines."""

        graph = self.world

        tr, bl = graph.get_view_coords()
        dim = graph.get_canvas_dim()

        # Gap between lines, in world units.
        grid_mult = graph.zoom_ratio // 10 # Density of grid lines.
        gap_size = self.grid_size

        # Adjust density for zoom.
        # When further zoomed out, increase
        # density (decrease gap size).
        gap_size += self.grid_size * grid_mult

        # Offset of the first leftmost line from the
        # bottom left viewport corner.
        bl_line_offset = -bl % gap_size

        # Create vertical grid lines.   
        # Find left most line, then draw lines towards the right.
        draw_pos = bl + bl_line_offset
        for _ in itertools.count():
            if draw_pos.x > tr.x or draw_pos.x < bl.x: break
            c1 = graph.view_to_canvas(draw_pos)
            c1.y = 0
            c2 = c1 + (0, dim.y)
            graph.create_line(c1, c2, tags=(self.unique_id, "grid_line_vertical"))

            if draw_axis_numbers:
                c1.x += 3
                c1.y = dim.y - 5
                graph.create_text(c1, text="%d" % draw_pos.x,
                anchor="sw", tags=(self.unique_id, "axis_number_vertical"))

            draw_pos.x += gap_size

        # Create horizontal grid lines.
        # Start at the bottom left corner.
        draw_pos = bl + bl_line_offset
        for _ in itertools.count():
            if draw_pos.y > tr.y or draw_pos.y < bl.y: break
            c1 = graph.view_to_canvas(draw_pos)
            c1.x = 0
            c2 = c1 + (dim.x, 0)
            graph.create_line(c1, c2, tags=(self.unique_id, "grid_line_horizontal"))

            if draw_axis_numbers:
                c1.x = 5
                graph.create_text(c1, text="%d" % draw_pos.y,
                anchor="nw", tags=(self.unique_id, "axis_number_horizontal"))

            draw_pos.y += gap_size

    def __draw_grid_origin_lines(self):
        """Create grid lines for origin lines of x and y."""

        graph = self.world
        dim = graph.get_canvas_dim()

        # Vertical
        c1 = graph.view_to_canvas(Loc(0, 0))
        if c1.x > 0 and c1.x < dim.x:
            c1.y = 0
            c2 = c1 + (0, dim.y)
            graph.create_line(c1, c2, fill="red", width=3, tags=(self.unique_id, "origin_line_vertical"))

        # Horizontal
        c1 = graph.view_to_canvas(Loc(0, 0))
        if c1.y > 0 and c1.y < dim.y:
            c1.x = 0
            c2 = c1 + (dim.x, 0)
            graph.create_line(c1, c2, fill="red", width=3, tags=(self.unique_id, "origin_line_horizontal"))

class WorldGraph(World, GraphBase):
    """
    Engine blueprint graph integrated with engine World,
    containing actor tracking capabilities for nodes.
    """
    def __init__(self):
        # Initialise world.
        World.__init__(self)

        # Initialise canvas parent.
        GraphBase.__init__(self, master=GameplayStatics.root_window)
        # Pack the graph in the given window.
        self.pack(fill="both", expand=True)

    def begin_play(self):
        # Spawn the grid lines actor to show grid lines.
        self.spawn_actor(GridGismo, Loc(0, 0))

        my_poly = self.deferred_spawn_actor(PolygonNode, (0, 0))
        my_poly.vertices = [Loc(100, 20), Loc(50, 100), Loc(-100, 0)]
        self.finish_deferred_spawn_actor(my_poly)

        self.spawn_actor(NodeBase, Loc(200, 200))
