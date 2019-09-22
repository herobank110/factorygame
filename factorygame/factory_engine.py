from factorygame.core.engine_base import GameEngine
from factorygame.core.blueprint import WorldGraph

class FactoryEngine(GameEngine):
    """Game engine class for factories."""
    def __init__(self):

        # Set default properties.
        self._window_title      = "FactoryGame"
        self._frame_rate        = 90
        self._starting_world    = WorldGraph
