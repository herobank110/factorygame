from factorygame.core.blueprint import WorldGraph, GridGismo


class HighwayWorld(WorldGraph):
    def __init__(self):
        super().__init__()

    def begin_play(self):
        super().begin_play()

        # Spawn the grid lines actor to show grid lines.
        self.spawn_actor(GridGismo, (0, 0))
