from tkinter import Canvas, Frame
from tkinter.ttk import Button

from factorygame import FColor, GameplayStatics, Loc
from factorygame.core.blueprint import WorldGraph, GridGismo
from factorygame.core.input_base import EInputEvent
from brainsim.neuron_node.nodes import NeuronNodeBase, NeuronNodeNetwork
from brainsim.menus.hud import BrainWorldHud


class BrainWorld(WorldGraph):
    """This is where neurons live.
    """

    def begin_play(self):
        super().begin_play()
        self.config(bg=FColor(210).to_hex())

        # Spawn initial world actors.

        grid = self.deferred_spawn_actor(GridGismo, (0, 0))
        grid.grid_line_color = FColor(160)
        grid.grid_text_color = FColor(160)
        grid.origin_line_color = FColor(160)
        self.finish_deferred_spawn_actor(grid)

        self.default_node_network = self.spawn_actor(
            NeuronNodeNetwork, Loc(0, 0))

        self.hud = self.spawn_actor(BrainWorldHud, Loc(0, 0))

        button_frame = Frame(self)
        Button(
            button_frame, text="Save",
            command=self.on_save_polygon
            ).pack()
        Button(
            button_frame, text="Reset",
            command=self.on_reset_polygon
            ).pack()
        self.create_window(Loc(20, 20), window=button_frame, anchor="nw")

        # Setup input bindings.

        input_comp = GameplayStatics.game_engine.input_mappings
        input_comp.bind_action(
            "AddNode", EInputEvent.PRESSED, self.on_add_node)

    def on_add_node(self):
        if self.default_node_network is None:
            return

        canvas = super(Canvas, self)
        mouse_position = Loc(
            canvas.winfo_pointerx() - canvas.winfo_rootx(),
            canvas.winfo_pointery() - canvas.winfo_rooty())

        spawn_position = self.canvas_to_view(mouse_position)
        self.default_node_network.add_node(spawn_position)

    def on_save_polygon(self):
        polygon_coords = [
            "Loc(%s, %s)" % (node.location.x, node.location.y)
            for node in self.default_node_network.nodes]
        coords_as_str = str(polygon_coords).replace("'", "")
        self.clipboard_clear()
        self.clipboard_append(coords_as_str)

        msg = ("Generating Polygon Coordinates".center(60, "-") + "\n"
               + "\n"
               + "Coords: %s" % coords_as_str[:40].replace("\n", " ") + "..." + "\n"
               + "Copied to clipboard")

        print(msg)

    def on_reset_polygon(self):
        for node in self.default_node_network.nodes:
            self.destroy_actor(node)
        self.default_node_network.nodes = []
        self.default_node_network.held_node = None
        self.default_node_network.hovered_node = None
