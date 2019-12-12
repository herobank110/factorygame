from factorygame import Loc, FColor
from factorygame.core.engine_base import ETickGroup
from factorygame.core.blueprint import DrawnActor

class BrainWorldHud(DrawnActor):
    """HUD manager for placing nodes in a brain.
    """
    def __init__(self):
        super().__init__()
        self.primary_actor_tick.tick_group = ETickGroup.UI

    def _should_draw(self):
        # Only draw on close up zoom.
        return super()._should_draw() and self.world.zoom_ratio < 10

    def tick(self, dt):
        super().tick(dt)
        # Always draw the active connection line
        self.__draw_active_connection()

    def _draw(self):
        self.__draw_existing_connections()

    def __draw_existing_connections(self):
        """Draw lines for nodes that are already connected.
        """
        network = self.world.default_node_network
        if network is None:
            return

        canvas = self.world
        for start_node in network.nodes:
            if not start_node._should_draw():
                # Don't draw lines for nodes we can't see.
                continue

            start = canvas.view_to_canvas(start_node.location)

            for end_node in start_node.to_trigger:
                if not end_node._should_draw:
                    continue

                end = canvas.view_to_canvas(end_node.location)

                # Draw a line connecting two center points.
                canvas.create_line(start, end,
                    fill=FColor.white().to_hex(), tags=(self.unique_id))

    def __draw_active_connection(self):
        """Draw a line for the current attempt to connect two nodes.
        """

        network = self.world.default_node_network
        if network is None or network.held_node is None:
            return

        # Start line from center of active connection start node.
        canvas = self.world
        start = canvas.view_to_canvas(network.held_node.location)
        is_valid_connection = True

        get_mouse_coords = lambda: Loc(
            canvas.winfo_pointerx() - canvas.winfo_rootx(),
            canvas.winfo_pointery() - canvas.winfo_rooty())

        if network.hovered_node is None:
            # Draw to the cursor point (already in terms of canvas).
            end = get_mouse_coords()
            fill_color = FColor.cyan()

        else:
            if network.held_node.can_connect_to(network.hovered_node):
                # Hovered over a node and connection is allowed.
                # Magnetize to hovered node's center.
                end = canvas.view_to_canvas(network.hovered_node.location)
                fill_color = FColor.green()

            else:
                # Hovered over a node, but connection is not allowed.
                end = get_mouse_coords()
                fill_color = FColor.red()

        canvas.create_line(start, end,
            fill=fill_color.to_hex(), tags=(self.unique_id))
