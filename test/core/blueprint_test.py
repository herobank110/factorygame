from test.template.template_gui import GuiTest
from factorygame.core.blueprint import GraphBase

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