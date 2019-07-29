from test.template.template_gui import GuiTest
from factorygame.core.blueprint import GraphBase

class GraphMotionTest(GuiTest):
    _test_name = "Blueprint Graph Motion"

    def start(self):
        # Simply display an empty basic graph.
        GraphBase(self).pack()