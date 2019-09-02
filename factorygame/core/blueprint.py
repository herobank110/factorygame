from tkinter import Canvas
from uuid import uuid4
import base64
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
    def tick(self, dt):
        """Called every frame to perform draw cycle."""
        self.start_cycle()

class NodeBase(DrawnActor):
    """Base class for nodes in a graph with visual representation."""

    def __init__(self):
        """Set default values."""

        ## Random, serialisable unique ID for this drawable object.
        self.unique_id = uuid4()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def _clear(self):
        self.world.delete(self.unique_id)

    def _should_draw(self):
        """Only draw if visible in the blueprint graph."""
        graph = self.world
        my_coords = graph.view_to_canvas(self.location)
        del my_coords

        return True

    def _draw(self):
        c1 = self.world.view_to_canvas(self.location)
        c2 = self.world.view_to_canvas(self.location + 100)
        self.world.create_oval(c1, c2, tags=(self.unique_id))

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

        ## Average size of each square grid, in pixels.
        self.grid_size      = 150


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
        motion = event.delta * self.zoom_ratio * 3
        motion.x *= -1 # Invert x axis
        self._view_offset += motion

    def on_graph_wheel_input(self, event):
        """Called when a mouse wheel event occurs on the graph."""
        # On windows wheel delta is in 120x
        # Zoom out on scroll down
        self.zoom_ratio += (-event.delta / 120)

        # TODO: also change _view_offset to use mouse cursor as center of zoom.

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def _clear(self):
        """Clear old drawn canvas elements."""
        # Delete old grid lines.
        self.delete("grid")

    def _draw(self):
        """Create new canvas elements."""

        # Draw the grid lines.
        self.__draw_grid()

        # TODO: Add additional draw functions here.

    def __draw_grid(self):
        """Create grid lines."""

        _, bl = self.get_view_coords()        
        dim = self.get_canvas_dim()
        edge_offset = +self._view_offset % self.grid_size
        for i, it in enumerate(self._view_offset):
            # Reapply signs afterward if necessary.
            if it < 0:
                edge_offset[i] *= -1


        # Gap between lines, in world units.
        grid_mult = self.zoom_ratio // 10 # Density of grid lines.
        gap_size = self.grid_size

        # Adjust density for zoom.
        # When further zoomed out, increase
        # density (decrease gap size).
        gap_size += self.grid_size * grid_mult
        num_elem = (self.get_view_dim() // gap_size) + 2

        # Create vertical grid lines.   
        # Start at the bottom left corner.     
        draw_pos = bl.copy()
        for i in range(num_elem.x):
            draw_pos.x = bl.x - edge_offset.x + gap_size * i
            c1 = self.view_to_canvas(draw_pos)
            # Stretch to the other edge of the canvas.
            c2 = c1 - (0, dim.y)
            if c1.x < dim.x:
                # Only draw for lines visible in the canvas.
                self.create_line(c1, c2, tags=("grid"))

            # TODO: Fix additional line being drawn to the left when 
            # the graph is offset slightly to the right (drag mouse left)

            c1.y = dim.y - 5
            self.create_text(c1, text="%d (%d)" % (draw_pos.x, c1.x),
                anchor="sw", tags=("grid"))

        # Create horizontal grid lines.
        # Start at the bottom left corner.
        draw_pos = bl.copy()
        for i in range(num_elem.y):
            draw_pos.y = bl.y - edge_offset.y + gap_size * i
            c1 = self.view_to_canvas(draw_pos)
            c2 = c1 + (dim.x, 0)
            if c1.y < dim.y:
                self.create_line(c1, c2, tags=("grid"))

            c1.x = 5
            self.create_text(c1, text="%d (%d)" % (draw_pos.y, c1.y),
                anchor="nw", tags=("grid"))


        # Create lines for origin
        # Horizontal
        c1 = self.view_to_canvas(Loc(0, 0))
        c1.x = 0
        c2 = c1 + (dim.x, 0)
        self.create_line(c1, c2, fill="red", width=3, tags=("grid"))
        # Vertical
        c1 = self.view_to_canvas(Loc(0, 0))
        c1.y = 0
        c2 = c1 + (0, dim.y)
        self.create_line(c1, c2, fill="red", width=3, tags=("grid"))

    # End of drawable interface.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_canvas_dim(self):
        """Return dimensions of canvas in pixels as a Loc."""
        return Loc(self.winfo_width(), self.winfo_height())

    def get_view_dim(self):
        """Return dimensions of viewport in coordinates as a Loc."""
        return self.get_canvas_dim() * self.zoom_ratio

    def get_view_coords(self):
        """Return top right and bottom left coordinates of viewport
        as a 2 tuple of Loc."""
        center = self._view_offset
        half_bounds = self.get_view_dim() / 2
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

class RenderManager(Actor):
    """
    Abstract actor class to process rendering blueprint
    world graph in the world every frame.
    """
    def __init__(self):
        """Set default values."""

        world = GameplayStatics.world

        if world and isinstance(world, Drawable):
            self.blueprint_world = world

        else:
            raise ValueError("World type not valid for blueprint rendering. " \
                "Expected 'Drawable' but got '%s'" % type(world).__name__)

    def tick(self, dt):
        # Start cycle for the blueprint canvas.
        self.blueprint_world.start_cycle()

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
        # Spawn the render manager to redraw the blueprint
        # graph according to game framerate.
        self.spawn_actor(RenderManager, (0, 0))

        self.spawn_actor(NodeBase, (50, 50))
