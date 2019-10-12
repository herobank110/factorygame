from factorygame.core.blueprint import WorldGraph, GridGismo
from factorygame import Loc, MathStat

class HighwayWorld(WorldGraph):
    def __init__(self):
        super().__init__()

    def begin_play(self):
        super().begin_play()

        # Spawn the grid lines actor to show grid lines.
        self.spawn_actor(GridGismo, (0, 0))

    def view_to_canvas(self, in_coords, clamp_to_viewport=False):
        """
        Return viewport coordinates in canvas coordinates as a Loc.
        
        :param in_coords: Viewport coordinates as a Loc.

        :param clamp_to_viewport: Whether to clamp coordinates to valid
        canvas coordinates.

        :return: Canvas coordinates converted from in_coords.
        """
        canvas_dim = self.get_canvas_dim()
        tr, bl = self.get_view_coords()

        if clamp_to_viewport:
            coords = Loc(
            MathStat.map_range_clamped(in_coords.x, bl.x, tr.x, 0, canvas_dim.x),
            MathStat.map_range_clamped(in_coords.y, bl.y, tr.y, canvas_dim.y, 0))

        else:
            coords = Loc(
            MathStat.map_range(in_coords.x, bl.x, tr.x, 0, canvas_dim.x),
            MathStat.map_range(in_coords.y, bl.y, tr.y, canvas_dim.y, 0))

        return coords
