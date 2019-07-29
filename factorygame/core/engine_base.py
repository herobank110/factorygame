"""Game engine for FactoryGame."""

from tkinter import Tk
from factorygame.utils.loc import Loc
from factorygame.utils.gameplay import GameplayStatics

class EngineObjectBase(object):
    """
    Low level implementation of EngineObjectBase, should not be used directly
    in game code.
    """
    pass

class EngineObject(EngineObjectBase):
    """
    Base object for all Engine objects. Provides basic gameplay functions
    that can be overridden in children.
    """

    def begin_play(self):
        """
        Called when this object has been successfully initialised
        and it is safe to call gameplay functions from this point on
        """
        pass

    def begin_destroy(self):
        """
        Called before this object will be destroyed.
        """
        pass

class GameEngine(EngineObject):
    """
    High level engine object that initialises other components when the
    game is created.
    """

    WINDOW_TITLE = property(lambda self: self._window_title)
    FRAME_RATE   = property(lambda self: self._frame_rate) # in frames per second
    FRAME_TIME   = property(lambda self: 1000 // self.FRAME_RATE) # in miliseconds

    def __init__(self, master=None):
        """Initialise game engine in widget MASTER. If omitted a new window is made."""

        ## Name to use in window title.
        self._window_title = "engine_base"

        ## Number of times to update game per second.
        self._frame_rate   = 30

        # Set central reference to game engine.
        GameplayStatics.set_game_engine(self)

        if master is None:
            # Create window for game.
            self._window = Tk()
            self._window.title(self.WINDOW_TITLE)
        else:
            # Use existing window.
            self._window = master

        # Initialise a default world.
        world = World(self._window)
        GameplayStatics.set_world(world)

    def close_game(self):
        """
        Close the game engine. Shouldn't be called directly, call
        from GameplayUtilities instead.
        """
        if not GameplayStatics.is_game_valid():
            return

        # Attempt to close game window.
        if self._window is not None and self._window.winfo_exists():
            # It does exist. Close it.
            self._window.destroy()
        
        # Delete world and all actors.
        world = GameplayStatics.world
        if world is not None:
            world.begin_destroy()

        # Delete gameplay statics, which holds many references.
        GameplayStatics.clear_all()

class World(EngineObject):
    """
    Manages all content that makes up a level as well as keeping
    track of all dynamically spawned actors and triggering core
    gameplay events such as tick.
    """

    _ticking_actors = set()    # all spawned actors to receive tick events
    _actors = []    # all spawned actors in the world

    def __init__(self, tk_obj):
        """Initialise world with any active tkinter object TK_OBJ."""

        ## Tkinter object reference for tick loop timer.
        self._tk_obj = tk_obj

        # Call begin play on self.
        self.begin_play() 

        # Attempt to start tick loop.
        self.__try_start_tick_loop()

    def spawn_actor(self, actor_class, loc):
        """
        Attempt to initialise a new actor in this world, from start
        to finish.

        To have further control on the actor before it is gameplay ready,
        use deferred_spawn_actor.

        * actor_class: Class of actor to spawn
        * loc: Location to spawn actor at.

        * return: Spawned actor if successful, otherwise None
        """

        actor_object = self.deferred_spawn_actor(actor_class, loc)
        return (self.finish_deferred_spawn_actor(actor_object)
                if actor_object else None)

    def deferred_spawn_actor(self, actor_class, loc):
        """
        Begin to initialise a new actor in this world, then allow
        attributes to be set before finishing the spawning process.

        Warning: It is not safe to call any gameplay functions (eg tick)
        or anything involving the world because the actor is not officially
        in the world yet.

        * actor_class: class of actor to spawn
        * loc: location to spawn actor at

        * return: initialised actor object if successful, otherwise None
        """

        # validate actor_class to check it is valid
        if actor_class is None:
            return None

        # initialise new actor object
        actor_object = actor_class()
        actor_object.__spawn__(self, loc)

        # return the newly created actor_object for further modification and
        # to pass in to finish_deferred_spawn_actor
        return actor_object

    def finish_deferred_spawn_actor(self, actor_object):
        """
        Finish spawning an actor in this world, allowing gameplay
        functions to safely begin for the actor.

        * actor_object: initialised actor object to finish spawning

        * return: gameplay ready actor object if successful, otherwise None
        """

        # validate actor_object to check that it is valid
        if actor_object is None:
            return None

        # update world references
        actor_object._world = self
        self._actors.append(actor_object)

        # call begin play
        actor_object.begin_play()

        # schedule ticks if necessary
        if actor_object.start_with_tick_enabled:
            self.set_actor_tick_enabled(actor_object, True)

        # return the fully spawned actor for further use
        return actor_object

    def __try_start_tick_loop(self):
        """
        Attempt to start a tick loop.

        :return bool: Whether the tick loop was started successfully.
        """
        if not self._tk_obj:
            return False

        self._tick_loop()
        return True        

    def _tick_loop(self):
        # get delta time
        dt = GameplayStatics.game_engine.FRAME_TIME # in miliseconds, as integer

        # call tick event on other actors
        for actor in self._ticking_actors:
            actor.tick(dt)

        # schedule next tick
        self._tk_obj.after(dt, self._tick_loop)

    def set_actor_tick_enabled(self, actor, new_tick_enabled):
        """
        Set whether an actor should tick and schedule/cancel tick events
        for the future. Shouldn't be called directly, call from the actor itself.
        """
        if new_tick_enabled:
            self._ticking_actors.add(actor)
        else:
            try:
                self._ticking_actors.remove(actor)
            except KeyError:
                pass

    def begin_destroy(self):
        """Destroy all actors."""
        for actor in self._actors:
            actor.begin_destroy()
            self._actors.pop(0)
            self._ticking_actors.remove(actor)

class Actor(EngineObject):
    """
    An object that has a visual representation in the world. Actors
    are directly managed by a world object and should only be created
    by using spawn_actor functions from the current world.
    """
    start_with_tick_enabled = property(lambda self: True)
    world = property(lambda self: self._world)
    location = property(lambda self: self.__get_location(),
        lambda self, value: self.__set_location(value))
    ##tick_enabled = property(__get_tick_enabled, __set_tick_enabled)
    tick_enabled = property()

    def __get_location(self):
        return self._location
    def __set_location(self, value):
        self._location = Loc(value)

    @tick_enabled.getter
    def __get_tick_enabled(self):
        return self._location
    @tick_enabled.setter
    def __set_tick_enabled(self, value):
        self.world.set_actor_tick_enabled(self, value)

    def __spawn__(self, world, location):
        """Called when actor is spawned by world. Shouldn't be called directly."""

        ## World actor is in.
        self._world = world

        ## Location of actor in world.
        self._location = location

        ## Whether to receive tick events.
        self._tick_enabled = self.start_with_tick_enabled

    def __init__(self):
        pass

    def tick(self, delta_time):
        """
        Called every frame if the actor is set to tick.
        delta_time: time since last frame, in seconds
        """
        raise NotImplementedError("Actor %s has tick enabled but default tick "
              "function is being called" % self)
