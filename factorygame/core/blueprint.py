from tkinter import Canvas
from uuid import uuid4
import itertools, math
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

        ## Set of transient canvas IDs this node represents for this draw cycle.
        ## Used to determine if this canvas shape was clicked.
        self.canvas_ids = set()

    def tick(self, dt):
        """Called every frame to perform draw cycle."""
        self.start_cycle()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def _clear(self):
        self.world.delete(self.unique_id)
        try:
            self.canvas_ids.clear()
        except AttributeError:
            # Py3.2 compatibility
            self.canvas_ids = set()

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

    def register_canvas_id(self, canvas_id):
        """
        Register a canvas id with the graph to enable input.
        Must be called each draw cycle with each canvas shape to
        receive input.
        """
        self.world.render_manager.node_canvas_ids[canvas_id] = self

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
    A single polygon with a set of vertices.
    Contains methods to create regular polygon vertex sets.
    """

    def __init__(self):
        """Set default values."""
        super().__init__()

        ## Set of vertex coordinates (Loc) that make up the polygon,
        ## relative to the polygon's location.
        self._vertices = tuple()

        ## Set of vertex coordinates (Loc) that make up the polygon,
        ## in world coordinates. Should not be set directly.
        self._world_vertices = tuple()

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

        # Store relative coordinates for convenience.
        self._vertices = tuple(value)
        # Add node's world location, to avoid calculating per draw call.
        self._world_vertices = tuple(map(lambda v: self.location + v, value))

    @property
    def world_vertices(self):
        return self._world_vertices

    def __getitem__(self, index):
        """Return the vertex at the given index."""
        return self._vertices[index]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def _should_draw(self):
        """Only draw if visible in graph and has vertices."""
        return super()._should_draw() and self.vertices

    def _draw(self):
        # Create a generator to convert vertices into canvas coordinates.
        transpose_func = self.world.view_to_canvas
        transposed_verts = map(transpose_func, self.world_vertices)

        new_id = self.world.create_polygon(*transposed_verts,
            tags=(self.unique_id))

        self.register_canvas_id(new_id)

    # End of drawable interface.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # TODO: create more robust input handling system
    def on_click(self, event):
        print("hello")

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

        self.__setup_input_bindings()

    def __setup_input_bindings(self):
        """Construction helper to set widget input bindings."""

        # Create and bind motion input object to receive motion events.
        self.motioninput = MotionInput(self, self.GRAPH_MOTION_BUTTON,
            normalise=False)
        self.motioninput.bind("Motion-XY", self.on_graph_motion_input)

        # Bind mouse wheel events for zoom.
        self.bind("<MouseWheel>", self.on_graph_wheel_input)

        # Since we aren't specifying the specific button to be pressed, tkinter
        # will not callback if a more specific event is given. In this case
        # motioninput uses right mouse button explicitly, se we won't receive
        # RMB press events.
        self.bind("<ButtonPress>", self.on_graph_button_press_input, True)

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

    def on_graph_button_press_input(self, event):
        """Called when a mouse button press event occurs on the graph."""
        pass

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

        ## Actor to control draw cycles. Receives tick event before other actors.
        self._render_manager = None

    def begin_play(self):
        # Spawn the world render manager first for tick priority.
        self._render_manager = self.spawn_actor(RenderManager, Loc(0, 0))

        # Spawn the grid lines actor to show grid lines.
        self.spawn_actor(GridGismo, Loc(0, 0))

        my_poly = self.deferred_spawn_actor(PolygonNode, (-100, 0))
        my_poly.vertices = list(GeomHelper.generate_reg_poly(5, radius=150.0))
        self.finish_deferred_spawn_actor(my_poly)

        self.spawn_actor(NodeBase, Loc(200, 200))

    def on_graph_button_press_input(self, event):
        """Call input events on nodes that are clicked."""
        # Find the node we pressed.
        center = Loc(event.x, event.y)

        # Found ids are returned in order of creation, not necessarily what
        # is displayed at the top.
        found_ids = self.find_overlapping(*center - 3, *center + 3)
        for it in found_ids:
            node = self.render_manager.node_canvas_ids.get(it)
            if node is not None:
                node.on_click(event)

    @property
    def render_manager(self):
        return self._render_manager

class GeomHelper:
    """Helper class to create geometric objects for the graph."""

    @staticmethod
    def generate_reg_poly(num_sides, **kw):
        """
        Generate a set of vertices for a regular polygon.

        :param num_sides: (int) Number of sides of the polygon.
        
        :keyword center: (Loc) Center point of the polygon, in relative
        coordinates.
        Defaults to origin.
        
        :keyword radius: (float) Radius of the circle bounds by the polygon's
        vertices, in world units.
        Defaults to 1.0.

        :keyword radial_offset: (float) Angle to rotate the polygon, in radians.
        Defaults to 0.0.

        :return: A generator that yields vertices as Loc objects.
        """
        radius = kw.get("radius", 1.0)

        center = kw.get("center", Loc(0, 0))

        # Rotate the polygon so that the top has a flat side.
        radial_offset = math.pi / num_sides
        radial_offset += kw.get("radial_offset", 0.0)

        for i in range(num_sides):
            yield GeomHelper.get_nth_vertex_offset(i, num_sides, radius, radial_offset) \
                + center

    @staticmethod
    def get_nth_vertex_offset(n, num_sides, radius, radial_offset=0.0):
        """
        Find the offset of the nth vertex of a round shape.
        
        :param n: (int) Vertex index to get offset of.

        :param num_sides: (int) Total number of sides of the polygon.

        :param radius: (float) Radius of the polygon.

        :param radial_offset: (float) Angle to rotate the polygon, in radians.
        Defaults to 0.0.

        :return: (Loc) The offset of the nth vertex.        
        """
        # Angle of vertex in relation to first vertex.
        theta = (2 * math.pi) / num_sides \
            * n \
            + radial_offset

        # Extend direction by the shape's radius.
        return GeomHelper.get_unit_vector(theta) * radius

    @staticmethod
    def get_unit_vector(angle):
        """
        Find the unit vector in the direction of the angle.
        
        :param angle: (float) Angle of vector, in radians.

        :return: (Loc) The unit vector.
        """
        return Loc(math.sin(angle), math.cos(angle))

class RenderManager(Actor, Drawable):
    def __init__(self):
        """Set default values."""
        
        ## Dictionary of canvas ids belongs to a Node object. Used to 
        ## map a given transient canvas id to a particular node.
        self.node_canvas_ids = {}

    def _draw(self):
        """This should be called before any other nodes receive draw calls."""

        # Reset the transient canvas ids from the previous draw cycle.
        try:
            self.node_canvas_ids.clear()
        except AttributeError:
            # Py3.2 compatibility
            self.node_canvas_ids = {}

    def tick(self, dt):
        self.start_cycle()
