from factorygame.core.engine_base import GameEngine
from spookygame.core.world import HighwayWorld

class SpookyEngine(GameEngine):
    """Game engine class for a zombie apocalypse."""
    def __init__(self):
        super().__init__()

        # Set default properties.
        self._window_title      = "SpookyGame"
        self._frame_rate        = 90
        self._starting_world    = HighwayWorld
