from factorygame import FColor
from factorygame.core.blueprint import PolygonNode, GeomHelper


class NeuronNodeBase(PolygonNode):
    """Base class for neuron nodes.
    """

    def begin_play(self):
        super().begin_play()
        self.vertices = list(GeomHelper.generate_reg_poly(4, radius=50))
        self.fill_color = FColor.white()

    def on_click(self, event):
        print("clicked!")

    def on_release(self, event):
        print("released")
