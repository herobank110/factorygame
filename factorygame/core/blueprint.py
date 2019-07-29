from tkinter import Canvas
from uuid import uuid4
from factorygame.utils.loc import Loc

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
