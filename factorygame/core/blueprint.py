from tkinter import Canvas
from uuid import uuid4
from factorygame.utils.loc import Loc
from factorygame.utils.tkutils import MotionInput
from factorygame.utils.gameplay import GameplayStatics
from factorygame.utils.mymath import MathStat
from factorygame.core.engine_base import World

class Drawable(object):
    """Abstract base class for objects receiving draw calls."""

    def clear(self):
        """Called every frame before drawing to clear current drawing."""
        pass

    def draw(self):
        """Called every frame to create new drawing."""
        pass

class NodeBase(Drawable):
    """Base class for nodes in a graph with visual representation."""

    def __init__(self, owner, location=None):
        """Initialiase drawable object with graph OWNER at LOCATION."""

        ## Blueprint graph this object is in.
        self.owner = owner

        ## 2D blueprint location with depth as Z.
        if location is None:
            self.location = Loc(0.0, 0.0, 0)
        else:
            # Use provided location.
            self.location = Loc(location)
            if len(location) < 3:
                # Use 0 depth if depth not provided.
                self.location.append(0)

        ## Random, unique ID for this drawable object.
        self.unique_id = uuid4()

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

    def on_graph_wheel_input(self, event):
        """Called when a mouse wheel event occurs on the graph."""
        # On windows wheel delta is in 120x
        # Zoom out on scroll down
        self.zoom_ratio += (-event.delta / 120)
        print("zoom ratio: 1:%s" % self.zoom_ratio)

    def draw(self):
        pass

class EngineGraph(World, GraphBase):
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
