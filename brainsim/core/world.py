from factorygame import FColor
from factorygame.core.blueprint import WorldGraph, GridGismo


class BrainWorld(WorldGraph):
    """This is where neurons live.
    """

    def begin_play(self):
        super().begin_play()
        self.config(bg=FColor(45, 23, 12).to_hex())

        grid = self.deferred_spawn_actor(GridGismo, (0, 0))
        grid.grid_line_color = FColor(45, 45, 17)
        grid.grid_text_color = FColor(145, 145, 117)
        grid.origin_line_color = FColor(45, 45, 17)
        self.finish_deferred_spawn_actor(grid)
