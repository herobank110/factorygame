from factorygame import FColor, Actor, GameplayStatics
from factorygame.core.blueprint import PolygonNode, GeomHelper
from factorygame.core.input_base import EInputEvent


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

    def begin_play(self):
        # Bind inputs
        input_component = GameplayStatics.game_engine.input_mappings
        input_component.bind_action(
            "ConnectNode", EInputEvent.RELEASED, self.on_end_connect_node)

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

    def on_end_connect_node(self):
        pass

    def on_node_clicked(self, node):
        """Handle a click on a node in this network.
        """

    def on_node_released(self, node):
        """Handle a release of a node in this network.
        """

    def on_node_start_cursor_over(self, node):
        """Handle the start of a cursor over a node in this network.
        """

    def on_node_end_cursor_over(self, node):
        """Handle the end of a cursor over a node in this network.
        """


class NeuronNodeBase(PolygonNode):
    """Base class for neuron nodes.
    """

    def __init__(self):
        super().__init__()

        ## Neural network this neuron belongs to.
        self.network = None  # type: NeuronNodeNetwork

    def begin_play(self):
        super().begin_play()
        self.vertices = list(GeomHelper.generate_reg_poly(4, radius=50))
        self.fill_color = FColor.white()

    def on_click(self, event):
        if self.network is not None:
            self.network.on_node_clicked(self)

    def on_release(self, event):
        if self.network is not None:
            self.network.on_node_released(self)

    def on_begin_cursor_over(self, event):
        if self.network is not None:
            self.network.on_node_start_cursor_over(self)

    def on_end_cursor_over(self, event):
        if self.network is not None:
            self.network.on_node_end_cursor_over(self)
