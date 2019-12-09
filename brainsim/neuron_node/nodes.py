from factorygame import FColor, Actor
from factorygame.core.blueprint import PolygonNode, GeomHelper


class NeuronNodeNetwork(Actor):
    """Represent a group of connected neurons in the synapse.
    """

    def __init__(self):
        super().__init__()

        self.primary_actor_tick.can_ever_tick = False

        ## Default node class when adding nodes to the network.
        self.default_node_class = NeuronNodeBase

        ## Node currently being connected from.
        self.held_node = None

        ## Node currently being connected to.
        self.hovered_node = None

        ## All nodes in this group.
        self.nodes = []

    def add_node(self, location, node_class=None):
        """Add a new node to the network.

        :param location: (int) Location of the new node, in world
        coordinates.

        :param node_class: (NeuronNodeBase) Class of node to spawn. If
        omitted, the default node class will be used.

        :return: (node_class) Newly spawned node.
        """

        if node_class is None:
            node_class = self.default_node_class

        new_node = self.world.deferred_spawn_actor(node_class, location)

        # Set references.
        new_node.network = self
        self.nodes.append(new_node)

        self.world.finish_deferred_spawn_actor(new_node)
        return new_node

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

    def on_mouse_over(self, event):
        print("mouse over")
