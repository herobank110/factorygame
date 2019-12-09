from tkinter import Canvas

from factorygame import FColor, GameplayStatics, Loc
from factorygame.core.blueprint import WorldGraph, GridGismo
from factorygame.core.input_base import EInputEvent
from brainsim.neuron_node.nodes import NeuronNodeBase


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

        input_comp = GameplayStatics.game_engine.input_mappings
        input_comp.bind_action("AddNode", EInputEvent.PRESSED, self.on_add_node)

    def on_add_node(self):
        canvas = super(Canvas, self)
        mouse_position = Loc(
            canvas.winfo_pointerx() - canvas.winfo_rootx(),
            canvas.winfo_pointery() - canvas.winfo_rooty())

        print("Adding node at %s" % mouse_position)

        spawn_position = self.canvas_to_view(mouse_position)
        self.spawn_actor(NeuronNodeBase, spawn_position)
