from factorygame.core.engine_base import GameEngine

class FactoryEngine(GameEngine):
    """Game engine class for factories."""
    def __init__(self):

        # Set default properties.
        self._window_title = "FactoryGame"
        self._frame_rate   = 30
