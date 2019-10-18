from factorygame import GameEngine
from brainsim.core.world import BrainWorld


class BrainsimEngine(GameEngine):
    def __init__(self):
        super().__init__()

        self._frame_rate = 90
        self._window_title = "Brain Simulator"
        self._starting_world = BrainWorld
