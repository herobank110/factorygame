"""
Defines all visual elements of the engine.
"""

from tkinter import Canvas
from uuid import uuid4
import itertools, math
from factorygame.utils.loc import Loc
from factorygame.utils.tkutils import MotionInput, ScalingImage
from factorygame.utils.gameplay import GameplayStatics
from factorygame.utils.mymath import MathStat
from factorygame.core.engine_base import World, Actor, ETickGroup

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

        super().__init__()

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

    # TODO: create more robust input handling system
    def on_click(self, event):
        print("hello")

    def on_release(self, event):
        print("hello")

    def on_mouse_over(self, event):
        print("hello")

    def on_mouse_leave(self, event):
        print("hello")

class PolygonNode(NodeBase):
    """
    A single polygon with a set of vertices.

    :see: GeomHelper for generating vertices.
    """

    def __init__(self):
        """Set default values."""
        super().__init__()

        self._fill_color = None
        self._fill_color_hex = ""
        self._outline_color = None
        self._outline_color_hex = ""

        ## Set of vertex coordinates (Loc) that make up the polygon,
        ## relative to the polygon's location.
        self._vertices = tuple()

        ## Set of vertex coordinates (Loc) that make up the polygon,
        ## in world coordinates. Should not be set directly.
        self._world_vertices = tuple()

        ## Fill color of the polygon (FColor)
        self.fill_color = FColor.default()

        ## Outline color of the polygon (FColor). If None, matches fill color
        self.outline_color = None

        ## Width of outline of the polygon (float)
        self.outline_width = 1.0

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
        # Calculate each time it is called.
        # return tuple(map(lambda v: self.location + v, self.vertices))

        return self._world_vertices

    @property
    def fill_color(self):
        return self._fill_color

    @fill_color.setter
    def fill_color(self, value):
        try:
            hex_val = value.to_hex()
        except AttributeError:
            raise ValueError("Expecting FColor, but got '%s' instead" % type(value).__name__)
        self._fill_color = value
        self._fill_color_hex = hex_val

        if self.outline_color is None:
            # Update outline color to match
            self._outline_color_hex = hex_val
            pass

    @property
    def outline_color(self):
        return self._outline_color

    @outline_color.setter
    def outline_color(self, value):
        if value is None:
            # Match fill color
            self._outline_color = None  # Keep track when fill color changes.
            self._outline_color_hex = self._fill_color_hex
            return

        try:
            hex_val = value.to_hex()
        except AttributeError:
            raise ValueError("Expecting FColor, but got '%s' instead" % type(value).__name__)
        self._outline_color = value
        self._outline_color_hex = hex_val

    @property
    def outline_width(self):
        return self._outline_width

    @outline_width.setter
    def outline_width(self, value):
        # Only allow positive numbers
        if value < 0:
            raise ValueError("Outline width must be positive")

        self._outline_width = value

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
            tags=(self.unique_id), fill=self._fill_color_hex,
            outline=self._outline_color_hex, width=self.outline_width)

        self.register_canvas_id(new_id)

    # End of drawable interface.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def begin_destroy(self):
        super().begin_destroy()
        self._clear()

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
        self.config(bg=FColor(240).to_hex())

        self.__setup_input_bindings()

    def __setup_input_bindings(self):
        """Construction helper to set widget input bindings."""

        # Create and bind motion input object to receive motion events.
        self.motioninput = MotionInput(self, self.GRAPH_MOTION_BUTTON,
            normalise=False)
        self.motioninput.bind("Motion-XY", self.on_graph_motion_input)

        # Bind mouse wheel events for zoom.
        self.bind_all("<MouseWheel>", self.on_graph_wheel_input)

        # Since we aren't specifying the specific button to be pressed, tkinter
        # will not callback if a more specific event is given. In this case
        # motioninput uses right mouse button explicitly, se we won't receive
        # RMB press events.
        self.bind("<ButtonPress>", self.on_graph_button_press_input, True)
        self.bind("<ButtonRelease>", self.on_graph_button_release_input, True)
        # self.bind("<Motion>", self.on_graph_pointer_movement_input, True)

    def on_graph_motion_input(self, event):
        """Called when a motion event occurs on the graph."""

        # Calculate world displacement between 2 canvas pixels,
        # but not necessarily touching pixels.

        canvas_a = Loc(0, 0)  # Start from top left corner
        canvas_b = canvas_a + event.delta

        # MotionInput's delta in capped to 5 pixels of movement per event.
        canvas_b *= 5

        world_displacement = \
            self.canvas_to_view(canvas_a) - self.canvas_to_view(canvas_b)

        self._view_offset += world_displacement

    def on_graph_wheel_input(self, event):
        """Called when a mouse wheel event occurs on the graph."""
        # On windows wheel delta is in 120x
        # Zoom out on scroll down
        self.zoom_ratio += (-event.delta / 120)

        # TODO: also change _view_offset to use mouse cursor as center of zoom.

    def on_graph_button_press_input(self, event):
        """Called when a mouse button press event occurs on the graph."""
        pass

    def on_graph_button_release_input(self, event):
        """Called when a mouse button release event occurs on the graph."""
        pass

    def on_graph_pointer_movement_input(self, event):
        """Called when a mouse pointer movement event occurs on the graph."""
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

        ## Color of grid lines.
        self.grid_line_color = FColor(215)

        ## Color of grid text.
        self.grid_text_color = FColor(150)

        ## Color of origin lines.
        self.origin_line_color = FColor(145)

        super().__init__()

        self.primary_actor_tick.tick_group = ETickGroup.WORLD

        self._canvas_cache = {}

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def _clear(self):
        """Clear old drawn canvas elements."""
        # Delete old grid lines.
        self.world.delete("axis_number_vertical")
        self.world.delete("grid_line_horizontal")
        self.world.delete("axis_number_horizontal")
        self.world.delete("origin_line_vertical")
        self.world.delete("origin_line_horizontal")

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

        line_color = self.grid_line_color.to_hex()
        text_color = self.grid_text_color.to_hex()

        # Gap between lines, in world units.
        grid_mult = graph.zoom_ratio // 10 # Density of grid lines.
        gap_size = self.grid_size

        # Adjust density for zoom.
        # When further zoomed out, increase
        # density (decrease gap size).
        gap_size += self.grid_size * ((2 ** grid_mult) - 1)

        # Offset of the first leftmost line from the
        # bottom left viewport corner.
        bl_line_offset = -bl % gap_size

        # Find number of vertical lines to draw
        first = bl.x + bl_line_offset.x
        last = tr.x - (first % gap_size)
        num_lines = ((last - first) // gap_size ) + 1

        should_recache = not self._canvas_cache \
            or len(self._canvas_cache["grid_line_vertical"]) != num_lines
        if should_recache:
            graph.delete("grid_line_vertical")
            self._canvas_cache["grid_line_vertical"] = []

        # Create vertical grid lines.
        # Find left most line, then draw lines towards the right.
        draw_pos = bl + bl_line_offset
        while bl.x < draw_pos.x < tr.x:
            c1 = graph.view_to_canvas(draw_pos)
            c1.y = 0
            c2 = c1 + (0, dim.y)
            if should_recache:
                new_id = graph.create_line(c1, c2, fill=line_color,
                tags=(self.unique_id, "grid_line_vertical"))

                self._canvas_cache["grid_line_vertical"].append(new_id)
            else:
                old_id = self._canvas_cache["grid_line_vertical"].pop(0)
                graph.coords(old_id, c1.x,c1.y, c2.x,c2.y)
                self._canvas_cache["grid_line_vertical"].append(old_id)

            if draw_axis_numbers:
                c1.x += 3
                c1.y = dim.y - 5
                graph.create_text(c1, text="%d" % draw_pos.x,
                anchor="sw", fill=text_color,
                tags=(self.unique_id, "axis_number_vertical"))

            draw_pos.x += gap_size

        # Create horizontal grid lines.
        # Start at the bottom left corner.
        draw_pos = bl + bl_line_offset
        while bl.y < draw_pos.y < tr.y:
            c1 = graph.view_to_canvas(draw_pos)
            c1.x = 0
            c2 = c1 + (dim.x, 0)
            graph.create_line(c1, c2, fill=line_color,
                tags=(self.unique_id, "grid_line_horizontal"))

            if draw_axis_numbers:
                c1.x = 5
                graph.create_text(c1, text="%d" % draw_pos.y,
                    anchor="nw", fill=text_color,
                    tags=(self.unique_id, "axis_number_horizontal"))

            draw_pos.y += gap_size

    def __draw_grid_origin_lines(self):
        """Create grid lines for origin lines of x and y."""

        graph = self.world
        dim = graph.get_canvas_dim()

        line_color = self.origin_line_color.to_hex()

        # Vertical
        c1 = graph.view_to_canvas(Loc(0, 0))
        if c1.x > 0 and c1.x < dim.x:
            c1.y = 0
            c2 = c1 + (0, dim.y)
            graph.create_line(c1, c2, fill=line_color, width=3,
                tags=(self.unique_id, "origin_line_vertical"))

        # Horizontal
        c1 = graph.view_to_canvas(Loc(0, 0))
        if c1.y > 0 and c1.y < dim.y:
            c1.x = 0
            c2 = c1 + (dim.x, 0)
            graph.create_line(c1, c2, fill=line_color, width=3,
            tags=(self.unique_id, "origin_line_horizontal"))

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

    def begin_destroy(self):
        super().begin_destroy()

        # Destroy the tkinter graph canvas.
        self.destroy()

    def on_graph_button_press_input(self, event):
        """Call input events on nodes that are clicked."""
        # Find the node we pressed.
        center = Loc(event.x, event.y)
        found_nodes = []
        self.multi_box_trace_for_objects(center, 2, found_nodes)
        for node in found_nodes:
            node.on_click(event)

    def on_graph_button_release_input(self, event):
        """Call input events on nodes that are released."""
        # Find the node we released.
        center = Loc(event.x, event.y)
        found_nodes = []
        self.multi_box_trace_for_objects(center, 2, found_nodes)
        for node in found_nodes:
            node.on_release(event)

    def on_graph_pointer_movement_input(self, event):
        """Call input events on nodes that that are hovered."""
        center = Loc(event.x, event.y)
        found_nodes = []
        self.multi_box_trace_for_objects(center, 2, found_nodes)

        # Use sets for easy intersection and overlaps.
        found_nodes = set(found_nodes)
        hovered_nodes = self.render_manager.hovered_nodes

        # Call mouse leave events on nodes that are no longer hovered.
        for node in hovered_nodes.difference(found_nodes):
            node.on_mouse_leave(event)
        
        # Call mouse over events on nodes that are newly hovered.
        for node in found_nodes.difference(hovered_nodes):
            node.on_mouse_over(event)
        
        # Save state for next call.
        self.render_manager.hovered_nodes = found_nodes

        # all(map(lambda node: node.on_mouse_over(event), found_nodes))

    def multi_box_trace_for_objects(self, start, half_size, found=None):
        """Get nodes at the position in a radius.

        :param start: (Loc) Location to start from.

        :param half_size: (float) Radius of box, in pixels.

        :param found: (list) Optionally add items to passed in list.

        :return: (list) Objects that collided.
        """

        if found is None: found = []

        coords = []
        coords.extend(start - half_size)
        coords.extend(start + half_size)

        # Found ids are returned in order of creation, not necessarily what
        # is displayed at the top.
        found_ids = self.find_overlapping(*coords)
        for it in found_ids:
            node = self.render_manager.node_canvas_ids.get(it)
            if node is not None:
                found.append(node)

        return found

    def multi_box_trace_for_objects2(self, start, half_size, found=None):
        if found is None: found = []

        coords = []
        coords.extend(start - half_size)
        coords.extend(start + half_size)

        found.extend(
            node
            for node in map(
                self.render_manager.node_canvas_ids.get,
                self.find_overlapping(*coords))
            if node is not None)

        return found

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

        # Rotate the polygon so that the bottom has a flat side.
        radial_offset = GeomHelper.get_poly_start_angle(num_sides)
        to_add = kw.get("radial_offset")
        if to_add is not None:
            radial_offset += to_add

        for i in range(num_sides):
            yield GeomHelper.get_nth_vertex_offset(i, num_sides, radius, radial_offset) \
                + center

    @staticmethod
    def get_poly_start_angle(num_sides):
        """
        Find the start angle of a regular polygon so that its
        bottom is a flat side.

        :param num_sides: (int) Number of sides of the polygon

        :return: (float) Angle of polygon, in radians.
        """

        if num_sides % 2 == 1:
            # Number is odd
            # return math.pi / 2
            return 0.0

        # Number is even
        center_angle = (2 * math.pi) / num_sides
        return math.pi / 2 - (center_angle / 2)

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
        center_angle = (2 * math.pi) / num_sides
        theta = (center_angle * n) + radial_offset

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

class FColor(Loc):
    """Store color data in RGB with format conversions."""

    # The properties for r, g, b components are built in to Loc,
    # so can be reused. In addition, accessing them from x, y, z
    # is also allowed.

    _repr_items = "RGB"

    @staticmethod
    def default():
        """Return the default color."""
        return FColor(20)

    @staticmethod
    def black():
        """Return the black color."""
        return FColor(0)

    @staticmethod
    def white():
        """Return the white color."""
        return FColor(255)

    @staticmethod
    def red():
        """Return the red color."""
        return FColor(255, 0, 0)

    @staticmethod
    def green():
        """Return the green color."""
        return FColor(0, 255, 0)

    @staticmethod
    def blue():
        """Return the blue color."""
        return FColor(0, 0, 255)

    @staticmethod
    def yellow():
        """Return the yellow color."""
        return FColor(255, 255, 0)

    @staticmethod
    def cyan():
        """Return the cyan color."""
        return FColor(0, 255, 255)

    @staticmethod
    def magenta():
        """Return the magenta color."""
        return FColor(255, 0, 255)

    @staticmethod
    def turqoise():
        """Return the turquoise color."""
        return FColor(64, 224, 208)

    @staticmethod
    def pink():
        """Return the pink color."""
        return FColor(255, 192, 203)

    def __init__(self, *args):
        """
        Construct FColor from RGB components.

        0 arguments sets 0 for RGB values.
        1 argument sets given value for RGB.
        3 arguments set RGB values respectively.
        """

        num_args = len(args)
        if num_args == 0:
            # Setup rgb components
            for i in range(3): self.append(0)

        elif num_args == 1:
            # Setup components linearly
            for i in range(3): self.append(round(args[0]))

        elif num_args == 3:
            # Setup components individually.
            for i in range(3): self.append(round(args[i]))

        else:
            raise ValueError("Invalid number of arguments to make RGB color")

    @staticmethod
    def hex_to_rgb(hex_string, digits=2):
        """
        Yield RGB values from a hexadecimal string.
        """
        for i in range(1, len(hex_string), digits):
            yield int("0x%s" % hex_string[i:i + digits], 0)

    @staticmethod
    def from_hex(hex_string, digits=2):
        """
        Construct a FColor from a hex string containing RGB components.

        :param hex_string: (str) Hex color in format "#rrggbb"

        :param bits: (int) Number of digits per component.

        :return: (FColor) RGB components as a FColor.
        """
        return FColor(*FColor.hex_to_rgb(hex_string, digits))

    def to_hex(self):
        """
        Get hexadecimal representation of this color.

        :return: (str) Hex color code
        """
        return "#%02x%02x%02x" % tuple(self)

class RenderManager(Actor, Drawable):
    def __init__(self):
        """Set default values."""

        super().__init__()

        ## Dictionary of canvas ids belongs to a Node object. Used to
        ## map a given transient canvas id to a particular node.
        self.node_canvas_ids = {}

        ## Set of nodes the mouse is currently hovering over.
        self.hovered_nodes = set()

        # ENSURE we tick before any other actors!
        self.primary_actor_tick.tick_group = ETickGroup.ENGINE

    def _draw(self):
        """This should be called before any other nodes receive draw calls."""

        # Reset the transient canvas ids from the previous draw cycle.
        try:
            self.node_canvas_ids.clear()
        except AttributeError:
            # Py3.2 compatibility
            self.node_canvas_ids = {}

    def tick(self, dt):
        # Call motion input every frame rather than on mouse movement.
        canvas = self.world
        event = type(
            "MyTkEvent", (), {
                "x": canvas.winfo_pointerx() - canvas.winfo_rootx(),
                "y": canvas.winfo_pointery() - canvas.winfo_rooty()})

        self.world.on_graph_pointer_movement_input(event)


        self.start_cycle()
