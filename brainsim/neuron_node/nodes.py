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
        self.held_node = None  # type: NeuronNodeBase

        ## Node currently being connected to.
        self.hovered_node = None  # type: NeuronNodeBase

        ## All nodes in this group.
        self.nodes = []

    def begin_play(self):
        # Bind inputs
        input_component = GameplayStatics.game_engine.input_mappings
        input_component.bind_action("ConnectNode", EInputEvent.RELEASED, self.on_release_connect)

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

    def on_release_connect(self):
        """Handle connection release anywhere in the synapse.
        
        Called every time the node connect button is released when
        the cursor may or may be over a particular node. If the cursor
        is not directly over a node, the connection attempt should be
        ended.
        
        If a release event did occur over a node, both this method and
        `on_node_released` are called but `on_node_released` should
        have higher priority to make the actual connection.
        """

    def on_node_clicked(self, node):
        """Handle a click on a node in this network.

        :see: `on_release_connect`
        """
        if self.held_node is None:
            self.held_node = node

    def on_node_released(self, node):
        """Handle a release of a node in this network.
        """
        if self.held_node is not None:
            # Make connection between nodes
            if self.held_node.can_connect_to(node):
                self.held_node.to_trigger.append(node)
                self.held_node = None
                self.hovered_node = None

    def on_node_start_cursor_over(self, node):
        """Handle the start of a cursor over a node in this network.
        """
        if self.hovered_node is None:
            self.hovered_node = node

    def on_node_end_cursor_over(self, node):
        """Handle the end of a cursor over a node in this network.
        """
        if self.hovered_node is not None and self.hovered_node is node:
            self.hovered_node = None


class NeuronNodeBase(PolygonNode):
    """Base class for neuron nodes.
    """

    def __init__(self):
        super().__init__()

        ## Neural network this neuron belongs to.
        self.network = None  # type: NeuronNodeNetwork

        ## List of nodes to trigger when signal passes to this node.
        self.to_trigger = [] # type: List[NeuronNodeBase]

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

    def can_connect_to(self, other_node):
        return (
            # Only connect valid nodes.
            other_node is not None

            # Can't connect to itself.
            and self is not other_node

            # Don't allow duplicate connections.
            and other_node not in self.to_trigger
            
            # Don't allow circular connections.
            and self not in other_node.to_trigger)
