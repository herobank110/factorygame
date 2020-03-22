from math import atan2
from factorygame import Loc
from factorygame.core.engine_base import EngineObject
from factorygame.core.blueprint import GeomHelper


class HitResult:
    """Structure for result of a colliding hit.
    """
    def __init__(self):
        self.impact_velocity = Loc(0.0, 0.0)
        self.surface_normal = Loc(0.0, 0.0)
        self.location = Loc(0.0, 0.0)
        self.other_actor = None


class ProjectileAimStruct:
    """Structure for aiming data of projectile to be launched.
    """

    def __init__(self):
        """Set default values.
        """
        ## Velocity to fire projectile at.
        self.fire_velocity = Loc(0, 0)


class ProjectileAimOffsetStruct(ProjectileAimStruct):
    """Structure for aiming by specifying positional offset.
    """

    def __init__(self, start_position=None):
        super().__init__()

        ## Initial position before supplying offset.
        self.start_position = start_position

        ## Multiplier for speed in case offset is a unit vector.
        self.fire_speed_multiplier = 1.0

        ## Whether to keep fire velocity constant (fire speed).
        self.should_normalise_speed = False

    def set_velocity_from_position(self, new_position):
        """Calculate offset and set fire velocity.
        """

        if self.start_position is None:
            # Can only calculate fire position if two points given.
            return

        # Calculate positional offset by difference in new position.
        new_velocity = new_position - self.start_position

        if self.should_normalise_speed:
            # Turn to unit vector if using constant velocity.
            new_velocity /= abs(self.fire_velocity)

        # Multiple strength of firing by constant value.
        new_velocity *= self.fire_speed_multiplier

        # Set final fire velocity.
        self.fire_velocity = new_velocity


class ProjectileMovementComponent(EngineObject):
    """Drives projectile like motion for an actor.
    """

    def __init__(self):
        super().__init__()

        ## Actor this component belongs to.
        self.owning_actor = None

        ## Initial speed to launch projectile with.
        self.initial_speed = 0.0
        ## Maximum projectile speed. Zero means no limit.
        self.max_speed = 0.0
        ## Affect of downward gravity on this projectile.
        self.gravity_strength = 1.0
        ## Multiplier for speed when a bounce occurs.
        self.bounce_speed_multiplier = 0.8
        ## Whether projectile should bounce off surfaces
        self.should_bounce = False
        ## Maximum number of times to bounce. Further bounce events are
        # ignored. Zero means no limit.
        self.max_num_bounces = 0
        ## Number of times actor has bounced since launched..
        self._current_num_bounces = 0
        ## Rotation of actor - rotation is not natively handled!!!
        self.rotation_direction = Loc(0.0, 0.0)
        ## Current movement velocity, set each frame.
        self.velocity = Loc(0.0, 0.0)
        ## Whether to simulate projectile movement currently.
        self.enable_simulation = False

    def config_from_aim(self, aim_data):
        """Configure values using a ProjectileAimStruct.

        Doesn't launch immediately.
        """
        self.initial_speed = abs(aim_data.fire_velocity)
        self.rotation_direction = aim_data.fire_velocity

    def tick_physics(self, dt):
        """Process changes to actor position.
        """
        if not self.enable_simulation:
            return

        # Convert delta time ms to seconds.
        dt *= 0.001

        # Find positional offset this frame and add to location.
        # instantaneous velocity = delta distance / delta time
        # delta distance = instantaneous velocity * delta time
        loc_offset = self.velocity * dt

        # Calculate velocity this frame.
        # instantaneous velocity = delta distance / delta time
        new_vel = loc_offset / dt

        # Add downward effects of gravity.
        # acceleration = delta velocity / delta time
        # delta velocity = acceleration * delta time
        new_vel += Loc(0.0, -9.8) * self.gravity_strength * dt * 100

        # Clamp to max speed if over limit.
        new_speed = abs(new_vel)
        if self.max_speed > 0.0 and new_speed > self.max_speed:
            # Find scale factor of current value and max limit.
            new_vel *= self.max_speed / new_speed

        # Set final state of projectile this frame.
        self.owning_actor.location += loc_offset
        self.velocity = new_vel

    def bounce(self, hit_data):
        """Trigger direction change with when a collision occurs.

        Must be called manually as robust collision detection system not
        made yet.
        """
        if (not self.enable_simulation
            or not self.bounce
            or (self.max_num_bounces > 0 
                and self._current_num_bounces >= self.max_num_bounces
            )):
            return

        # Increment bounce counter.
        self._current_num_bounces += 1

        # Recalculate velocity direction considering surface normal.
		# Assume values from hit data are correct rather than using
        # the current projectile values.
        incoming_angle = atan2(*hit_data.impact_velocity)
        surface_angle = atan2(*hit_data.surface_normal)
        launch_angle = surface_angle + incoming_angle + (4* 3.14 /3 )
        new_direction, *_ = tuple(
            GeomHelper.generate_reg_poly(3, radial_offset=launch_angle)
		)
        
        # Calculate new speed (magnitude of velocity) to relaunch with.
        current_speed = abs(self.velocity)
        new_speed = current_speed * self.bounce_speed_multiplier
        
        # Set velocity for an similar effect to launching.
        self.velocity = new_direction * new_speed


    def launch(self):
        """Begin simulating physics and launch with initial speed.

        Call this to initialise launch, then call `tick_physics` each
        frame to process movement thereafter.
        """
        # Calculate firing velocity.
        rot = self.rotation_direction / abs(self.rotation_direction)
        self.velocity = rot * self.initial_speed

        # Reset firing data.
        self._current_num_bounces = 0

        # Set flag to process movement each frame.
        self.enable_simulation = True
