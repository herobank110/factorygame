from tkinter.ttk import Label
from math import atan2
from random import randrange
from test.template.template_gui import GuiTest
from factorygame import (
    GameEngine, Loc, GameplayStatics, FColor, GameplayUtilities
)
from factorygame.core.engine_base import ETickGroup
from factorygame.core.blueprint import (
    WorldGraph, GridGismo, DrawnActor, PolygonNode, GeomHelper
)
from factorygame.core.input_base import EKeys, EInputEvent
from factorygame.components.projectile_movement import (
    ProjectileAimOffsetStruct, ProjectileMovementComponent, HitResult
)


class Bullet(PolygonNode):
    """Projectile that will be launched.
    """

    def __init__(self):
        super().__init__()

        # Disable collision handling.
        self.generate_cursor_over_events = False
        self.generate_click_events = False

        # Create projectile movement component to move like a projectile.
        proj = self.projectile_movement = GameplayUtilities.create_engine_object(
            ProjectileMovementComponent
        )
        proj.owning_actor = self
        proj.max_speed = 1000
        proj.max_num_bounces = 10
        proj.bounce_speed_multiplier = 1.0 # don't lose speed on bounce

    def begin_play(self):
        super().begin_play()
        if self.projectile_movement:
            # Launch projectile movement with aim settings.
            self.projectile_movement.launch()

        # Set shape to a triangle.
        self.vertices = tuple(GeomHelper.generate_reg_poly(3, radius=30))

    def tick(self, dt):
        proj = self.projectile_movement
        # Tell projectile movement component to move bullet actor.
        proj.tick_physics(dt)

        # Set triangle vertices at rotation of current velocity.
        rotation = atan2(*proj.velocity)
        self.vertices = tuple(GeomHelper.generate_reg_poly(
            3, radius=30, radial_offset=rotation
        ))

        if self.location.y <= 0:
            # Create the hit result data structure with current state.
            hit_result = HitResult()
            hit_result.surface_normal = Loc(0.0, 1.0) # flat upward
            hit_result.impact_velocity = proj.velocity
            hit_result.location = self.location
            hit_result.other_actor = None

            proj.bounce(hit_result)
            self.fill_color = FColor(
                randrange(0, 256), randrange(0, 256), randrange(0, 256)
            )

        # Continue drawing actor.
        super().tick(dt)
        if (proj.max_num_bounces > 0
            and proj._current_num_bounces >= proj.max_num_bounces
            ):
            # Delete if max bounces reached.
            self.world.destroy_actor(self)


class AimingPlayer(DrawnActor):
    """Handle input to aim and fire projectiles.
    """
    def __init__(self):
        super().__init__()
        self._aim_struct = None
        self.primary_actor_tick.tick_group = ETickGroup.GAME

    def begin_play(self):
        super().begin_play()

        # Bind firing inputs.
        input_component = GameplayStatics.game_engine.input_mappings
        input_component.bind_action(
            "Fire", EInputEvent.PRESSED, self.on_fire_pressed
        )
        input_component.bind_action(
            "Fire", EInputEvent.RELEASED, self.on_fire_released
        )

    def on_fire_pressed(self):
        """Start aiming protocol before launching projectile.
        """
        if self._aim_struct is not None:
            return

        # Get the mouse position currently.
        mouse_pos = self.world.get_mouse_viewport_position()

        # Convert to world coordinates.
        world_over_pos = self.world.canvas_to_view(mouse_pos)

        # Initialise aiming structure with initial position.
        self._aim_struct = ProjectileAimOffsetStruct(world_over_pos)

    def on_fire_released(self):
        """Finish aiming and fire projectile from current aim.
        """
        if (self._aim_struct is not None
            and abs(self._aim_struct.fire_velocity) > 0.0
        ):
            # Create bullet and configure initial pre-firing state.
            spawn_pos = self._aim_struct.start_position
            proj = self.world.deferred_spawn_actor(Bullet, spawn_pos)
            proj.projectile_movement.config_from_aim(self._aim_struct)
            # Finalise setup to let projectile move in the world.
            self.world.finish_deferred_spawn_actor(proj)

            print(
                "Launched bullet from: %s, with initial velocity: %s"
                % (round(spawn_pos), round(self._aim_struct.fire_velocity))
            )

        # Delete aiming data to stop aiming.
        self._aim_struct = None

    def tick(self, dt):
        """Process aiming each frame.
        """
        if self._aim_struct is not None:
            # Aim structure is initialised and ready to calculate offset.

            # Get the mouse position currently.
            mouse_pos = self.world.get_mouse_viewport_position()

            # Convert to world coordinates and set fire velocity.
            world_over_pos = self.world.canvas_to_view(mouse_pos)
            self._aim_struct.set_velocity_from_position(world_over_pos)

        # Call parent behaviour to start draw cycle.
        super().tick(dt)

    def _should_draw(self):
        """Only draw if currently aiming.
        """
        return (
            super()._should_draw()
            and self._aim_struct is not None
            and self._aim_struct.start_position is not None
        )

    def _draw(self):
        """Draw debug line to show current firing velocity.
        """

        canvas = self.world
        # Get screen space coordinates of aim vector start and end.
        start_pos = canvas.view_to_canvas(self._aim_struct.start_position)
        mouse_pos = canvas.get_mouse_viewport_position()

        # Hide arrow for small velocities.
        arrow = "last" if abs(self._aim_struct.fire_velocity) > 20 else ""

        # Draw line with current parameters.
        canvas.create_line(
            start_pos, mouse_pos,
            fill=FColor.red().to_hex(), width=5, arrow=arrow,
            tags=(self.unique_id),
        )


class ProjectileTestWorld(WorldGraph):
    """World for launching projectiles on a grid.
    """

    def begin_play(self):
        super().begin_play()
        self.spawn_actor(GridGismo, Loc(0, 0))
        self.spawn_actor(AimingPlayer, Loc(0, 0))


class ProjectileTestEngine(GameEngine):
    """Game engine for testing projectile motion.
    """
    def __init__(self):
        super().__init__()
        self._frame_rate = 90
        self._starting_world = ProjectileTestWorld
        self._window_title = "Projectile Motion Testing"

    def setup_input_mappings(self):
        super().setup_input_mappings()
        self.input_mappings.add_action_mapping("Fire", EKeys.LeftMouseButton)


class ProjectileMovementTest(GuiTest):
    _test_name = "Projectile Movement"

    def start(self):
        # Create a label to show frame count.
        Label(
            self, text=(
                "Drag Right Mouse Button to move\n"
                "Drag Left Mouse Button to launch bullets")
            ).pack(pady=10)

        # Create the projectile test engine in this Toplevel window.
        GameplayUtilities.create_game_engine(ProjectileTestEngine, master=self)

        # Ensure we stop the game engine when closing the test,
        # so that subsequent runs are fully restarted.
        self.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        """Called when test window is destroyed."""
        GameplayUtilities.close_game()
