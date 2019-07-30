from tkinter import Canvas
from uuid import uuid4
from factorygame.utils.loc import Loc
from factorygame.utils.tkutils import MotionInput
from factorygame.utils.gameplay import GameplayStatics
from factorygame.utils.mymath import MathStat
from factorygame.core.engine_base import World, Actor

class Drawable(object):
    """Abstract base class for objects receiving draw calls."""

    def start_cycle(self):
        """Start a full draw cycle."""
        self._clear()
        self._draw()

    def _clear(self):
        """
        Called every draw cycle before drawing to clear previous drawing.
        
        Override for clearing behaviour.
        """
        pass

    def _draw(self):
        """
        Called every draw cycle to create new drawing.

        Override for drawing behaviour.
        """
        pass

class DrawnActor(Drawable, Actor):
    """Base class for drawable actors who receive a draw cycle each frame."""
    def tick(self, dt):
        """Called every frame to perform draw cycle."""
        self.start_cycle()

# class NodeBase(Drawable):
#     """Base class for nodes in a graph with visual representation."""

#     def __init__(self, owner, location=None):
#         """Initialiase drawable object with graph OWNER at LOCATION."""

#         ## Blueprint graph this object is in.
#         self.owner = owner

#         ## 2D blueprint location with depth as Z.
#         if location is None:
#             self.location = Loc(0.0, 0.0, 0)
#         else:
#             # Use provided location.
#             self.location = Loc(location)
#             if len(location) < 3:
#                 # Use 0 depth if depth not provided.
#                 self.location.append(0)

#         ## Random, unique ID for this drawable object.
#         self.unique_id = uuid4()

class GraphBase(Canvas, Drawable):
    """Base blueprint graph for displaying drawable objects."""

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
        self._view_offset += event.delta
        print("view offset:", round(self._view_offset, 2))

        # Redraw the graph.
        self.start_cycle()

    def on_graph_wheel_input(self, event):
        """Called when a mouse wheel event occurs on the graph."""
        # On windows wheel delta is in 120x
        # Zoom out on scroll down
        self.zoom_ratio += (-event.delta / 120)
        print("zoom ratio: 1:%s" % self.zoom_ratio)

        # Redraw the graph.
        self.start_cycle()

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def _clear(self):
        """Clear old drawn canvas elements."""
        # Delete old grid lines.
        self.delete("grid")

    def _draw(self):
        """Create new canvas elements."""

        GRID_SIZE = 30 * self.zoom_ratio

        dim = self.get_canvas_dim()
        num_elem = (self.get_view_dim() // GRID_SIZE) + 1
        tr, bl = self.get_view_coords()

        print("tr %s, bl %s" % (tr, bl))
        print("view bounds:", self.get_view_dim())

        # Create vertical grid lines.        
        draw_pos = Loc(0, 0)
        for i in range(num_elem.x):
            draw_pos.x = bl.x + GRID_SIZE * i
            self.create_line(draw_pos, draw_pos + (0, dim.y),
                tags=("grid"))

        # Create horizontal grid lines.
        draw_pos = Loc(0, 0)
        for i in range(num_elem.y):
            draw_pos.y = bl.y + GRID_SIZE * i
            print("draw_pos:", draw_pos)
            self.create_line(draw_pos, draw_pos + (dim.x, 0),
                tags=("grid"))


    # End of drawable interface.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_canvas_dim(self):
        """Return dimensions of canvas in pixels as a Loc."""
        return Loc(int(self.cget("width")), int(self.cget("height")))

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
        self.pack()
