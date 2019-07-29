from tkinter import Canvas
from uuid import uuid4
from factorygame.utils.loc import Loc
from factorygame.utils.tkutils import MotionInput

class DrawableObject(object):
    """Base class for all blueprint drawable objects."""

    def __init__(self, owner, location=None):
        """Initialiase drawable object with canvas OWNER at LOCATION."""

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
        
    def clear(self):
        """Called every frame before drawing to clear current drawn representation."""

    def draw(self):
        """Called every frame to create the drawn representation."""
        pass

class GraphBase(Canvas):
    """Base blueprint graph for displaying drawable objects."""

    ## Constant for button to hold and drag to move graph.
    ## Default is 3 (right mouse button).
    GRAPH_MOTION_BUTTON = property(lambda self: 3)

    def __init__(self, master=None, cnf={}, **kw):
        """Initialiase blueprint graph in widget MASTER."""

        # Initialise canvas parent.
        Canvas.__init__(self, master, cnf, **kw)

        # Create and bind motion input object so we can receive motion events.
        self.motioninput = MotionInput()
        self.motioninput.bind_to_widget(self, button=self.GRAPH_MOTION_BUTTON)
        self.motioninput.bind("Motion-XY", self.on_graph_motion_input)

    def on_graph_motion_input(self, event):
        """Called when a motion event occurs on the graph."""
        print("motion delta: %s" % round(event.delta, 2))
