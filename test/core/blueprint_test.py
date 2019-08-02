from test.template.template_gui import GuiTest
from factorygame.core.blueprint import GraphBase

class TestGraph(GraphBase):
    """Basic graph, with debugging features."""

    def on_graph_motion_input(self, event):
        """Called when a motion event occurs on the graph."""
        super().on_graph_motion_input(event)

        print("view offset:", round(self._view_offset, 2))
        # Redraw the graph.
        self.start_cycle()

    def on_graph_wheel_input(self, event):
        """Called when a mouse wheel event occurs on the graph."""
        super().on_graph_wheel_input(event)
        print("zoom ratio: 1:%s" % self.zoom_ratio)

        # Redraw the graph.
        self.start_cycle()


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