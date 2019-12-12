from factorygame import Loc, FColor
from factorygame.core.blueprint import DrawnActor

class BrainWorldHud(DrawnActor):
    """HUD manager for placing nodes in a brain.
    """

    def _draw(self):
        self.__draw_existing_connections()
        self.__draw_active_connection()

    def __draw_existing_connections(self):
        """Draw lines for nodes that are already connected.
        """
        network = self.world.default_node_network
        if network is None or network.held_node is None:
            return

        canvas = self.world
        for start_node in network.nodes:
            start = canvas.view_to_canvas(start_node.location)
            for end_node in start_node.to_trigger:
                end = canvas.view_to_canvas(end_node.location)

                # Draw a line connecting two center points.
                canvas.create_line(start, end,
                    fill=FColor.white(), tags=(self.unique_id))

    def __draw_active_connection(self):
        """Draw a line for the current attempt to connect two nodes.
        """

        network = self.world.default_node_network
        if network is None or network.held_node is None:
            return

        # Start line from center of active connection start node.
        canvas = self.world
        start = canvas.view_to_canvas(network.held_node.location)

        if network.hovered_node is not None:
            # Magnetize to hovered node's center.
            end = canvas.view_to_canvas(network.hovered_node.location)

        else:
            # Draw to the cursor point (already in terms of canvas).
            end = Loc(canvas.winfo_pointerx() - canvas.winfo_rootx(),
                canvas.winfo_pointery() - canvas.winfo_rooty())

        canvas.create_line(start, end,
            fill=FColor.cyan().to_hex(), tags=(self.unique_id))
