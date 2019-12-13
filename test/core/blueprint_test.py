from tkinter.ttk import Label
from test.template.template_gui import GuiTest
from factorygame.core.blueprint import (GraphBase, PolygonNode,
    GeomHelper, FColor, WorldGraph)
from factorygame import GameEngine, GameplayUtilities, GameplayStatics

class TestGraph(GraphBase):
    """Basic graph, with debugging features."""

    def __init__(self, master=None):
        super().__init__(master)

        self.start_cycle()

        self.bind("<Configure>", self.on_graph_resize)

    def on_graph_motion_input(self, event):
        """Called when a motion event occurs on the graph."""
        super().on_graph_motion_input(event)

        # Redraw the graph.
        self.start_cycle()

    def on_graph_wheel_input(self, event):
        """Called when a mouse wheel event occurs on the graph."""
        super().on_graph_wheel_input(event)

        # Redraw the graph.
        self.start_cycle()

    def on_graph_resize(self, event):
        """Called when the graph widget is resized."""
        self.start_cycle()


    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Start of drawable interface.

    def start_cycle(self):
        try:
            super().start_cycle()
        except:
            # This widget was destroyed already.
            return

    def _draw(self):

        self.draw_view_offset()
        self.draw_zoom_ratio()
        self.draw_graph_size()

    def _clear(self):
        self.delete("view_offset")
        self.delete("zoom_ratio")
        self.delete("graph_size")

    # End of drawable interface.
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def draw_view_offset(self):
        msg = "View offset: %s" % round(self._view_offset, 2)
        self.create_text(10, 10, anchor="nw", text=msg, tag="view_offset")

    def draw_zoom_ratio(self):
        msg = "Zoom ratio: 1:%d" % self.zoom_ratio
        self.create_text(10, 50, anchor="nw", text=msg, tag="zoom_ratio")

    def draw_graph_size(self):
        msg = "Graph size (pixels): %s" % self.get_canvas_dim()
        self.create_text(10, 90, anchor="nw", text=msg, tag="graph_size")
        msg = "Viewport size (units): %s" % round(self.get_view_dim(), 2)
        self.create_text(10, 110, anchor="nw", text=msg, tag="graph_size")


        tr, bl = self.get_view_coords()
        msg = "Viewport bottom left at: %s" % round(bl, 2)
        self.create_text(10, 150, anchor="nw", text=msg, tag="graph_size")
        msg = "Viewport top right at: %s" % round(tr, 2)
        self.create_text(10, 170, anchor="nw", text=msg, tag="graph_size")


class GraphMotionTest(GuiTest):
    _test_name = "Blueprint Graph Motion"

    def start(self):
        # Simply display an empty basic graph that
        # redraws on every motion received, NOT a good
        # idea for real use!
        TestGraph(self).pack()

class GraphResizeTest(GuiTest):
    _test_name = "Blueprint Graph Resize"

    def start(self):
        # Make the graph fill the bounds of the
        # popup window and expand/shrink its bounds
        # according to the window size.
        TestGraph(self).pack(fill="both", expand=True)


# Nodes test


class _NodesInputTestNode(PolygonNode):
    def __init__(self):
        super().__init__()
        self.label = None

    def begin_play(self):
        super().begin_play()
        self.vertices = list(GeomHelper.generate_reg_poly(6, radius=200))
        self.fill_color = FColor.cyan()

    def _get_text_as_dict(self):
        """Return dict of name to value currently in label text.

        eg: "a: 1\nb: 2" => {'a': '1', 'b': '2'}
        """
        if self.label is None:
            return

        text = self.label.cget("text")
        info_lines = {}
        for line in text.split("\n"):
            name, value = line.strip().split(": ")
            info_lines[name] = value

        return info_lines

    def _set_text_from_dict(self, info_lines):
        """Set text from dict of values.

        Order of items (if present)
          Last Event, Is Hovered
        """
        if self.label is None:
            return

        name_priority = ("Last Event", "Is Hovered")
        self.label.config(text=
            "\n".join(
                filter(
                    None,
                    (
                        (
                            lambda k, v: v and "%s: %s" %(k, v)
                            )(k, info_lines.get(k))
                        for k in name_priority))))

    def on_click(self, event):
        info_lines = self._get_text_as_dict()
        info_lines.update(
            {"Last Event": "on_click"})
        self._set_text_from_dict(info_lines)

    def on_release(self, event):
        info_lines = self._get_text_as_dict()
        info_lines.update(
            {"Last Event": "on_release"})
        self._set_text_from_dict(info_lines)

    def on_begin_cursor_over(self, event):
        info_lines = self._get_text_as_dict()
        info_lines.update({
            "Last Event": "on_begin_cursor_over",
            "Is Hovered": "True"})
        self._set_text_from_dict(info_lines)

    def on_end_cursor_over(self, event):
        info_lines = self._get_text_as_dict()
        info_lines.update({
            "Last Event": "on_end_cursor_over",
            "Is Hovered": "False"})
        self._set_text_from_dict(info_lines)


class NodesInputTest(GuiTest):
    _test_name = "Nodes Viewport Input"

    def start(self):
        # Create a label to show frame count.
        Label(
            self, text=(
                "Interact with the shape using your mouse\n"
                "to see the NodeBase Viewport Input events.")
            ).pack(pady=10)

        node_info_label = Label(self, text="Last Event: --\nIs Hovered: --")
        node_info_label.pack(anchor="w", padx=40)

        # Create the base class engine in this Toplevel window.
        GameplayUtilities.create_game_engine(GameEngine, master=self)
        GameplayUtilities.travel(WorldGraph)

        # Spawn the ticking actor.
        actor = GameplayStatics.world.deferred_spawn_actor(
            _NodesInputTestNode, (0, 0))
        # Set properties before calling tick.
        actor.label = node_info_label
        GameplayStatics.world.finish_deferred_spawn_actor(actor)

        # Ensure we stop the game engine when closing the test,
        # so that subsequent runs are fully restarted.
        self.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        """Called when test window is destroyed."""
        GameplayUtilities.close_game()
