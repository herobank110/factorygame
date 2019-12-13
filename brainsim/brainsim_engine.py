from factorygame import GameEngine
from factorygame.core.input_base import EKeys
from brainsim.core.world import BrainWorld


class BrainsimEngine(GameEngine):
    def __init__(self):
        super().__init__()

        self._frame_rate = 90
        self._window_title = "Brain Simulator"
        self._starting_world = BrainWorld

    def setup_input_mappings(self):
        self.input_mappings.add_action_mapping("AddNode", EKeys.E)
        self.input_mappings.add_action_mapping("ConnectNode", EKeys.LeftMouseButton)
