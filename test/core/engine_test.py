from test.template.template_gui import GuiTest
from factorygame.core.engine_base import GameEngine, Actor
from factorygame.utils.gameplay import GameplayStatics, GameplayUtilities
from tkinter.ttk import Label, Button


class MyActor(Actor):
    def __init__(self):
        super().__init__()

        self.frame_count = 0
        self.label       = None
    def tick(self, dt):
        # Actors are set to tick by default.
        self.frame_count += 1
        self.label.config(text=str(self.frame_count))

class EngineTickTest(GuiTest):
    _test_name = "Engine Tick"

    def start(self):
        # Create a label to show frame count.
        frame_count_label = Label(self, text="you should not see this")
        frame_count_label.pack()

        # Create the base class engine in this Toplevel window.
        GameplayUtilities.create_game_engine(GameEngine, master=self)

        # Spawn the ticking actor.        
        actor = GameplayStatics.world.deferred_spawn_actor(MyActor, (0, 0))
        # Set properties before calling tick.
        actor.label = frame_count_label
        actor.frame_count = 0
        GameplayStatics.world.finish_deferred_spawn_actor(actor)
        
        # Ensure we stop the game engine when closing the test, 
        # so that subsequent runs are fully restarted.
        self.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        """Called when test window is destroyed."""
        GameplayUtilities.close_game()


class DestroyingActor(Actor):
    def tick(self, delta_time):
        # Make sure we receive ticks for testing, but don't actually
        # do anything.
        pass

class CounterRefreshActor(Actor):
    """Refresh how many actors are in the world each frame."""

    def __init__(self):
        super().__init__()

        ## GuiTest object to refresh each frame.
        self.test_object = None

    def tick(self, delta_time):
        self.test_object.refresh_actor_count()

class ActorDestroyTest(GuiTest):
    _test_name = "Actor Destroy"

    def spawn_new_actor(self):
        new_actor = GameplayStatics.world.spawn_actor(DestroyingActor, (0, 0))

        self.spawned_actors.append(new_actor)

        self.refresh_actor_count()

    def destroy_newest_actor(self):
        try:
            last_actor = self.spawned_actors.pop()
        except IndexError:
            # No more actors to destroy.
            return
        
        GameplayStatics.world.destroy_actor(last_actor)

        self.refresh_actor_count()

    def refresh_actor_count(self):
        # This shouldn't be used for production code as _actors
        # is the master list and should be hidden.
        num_actors = len(GameplayStatics.world._actors)
        new_text = self.actor_count_format.format(num_actors)

        self.actor_count_label.config(text=new_text)

    def start(self):
        # List of spawned actors, to track creation by this test.
        # Although, the world has the true master list of actors
        # in the world. This is just to destroy the actors we made.
        self.spawned_actors = []


        # Create a button to create a new actor.
        Button(self, text="Spawn", command=self.spawn_new_actor).pack()

        # Create a button to destroy last spawned actor.
        Button(self, text="Destroy", command=self.destroy_newest_actor).pack()

        # Create label to show number of active actors.
        self.actor_count_format = "There are currently {:d} actors in the world"

        self.actor_count_label = Label(
            self, text=self.actor_count_format.format(0))
        self.actor_count_label.pack()


        # Create the base class engine in this Toplevel window.
        GameplayUtilities.create_game_engine(GameEngine, master=self)

        # Create actor to refresh actor count.
        counter_refresh_actor = GameplayStatics.world.spawn_actor(
            CounterRefreshActor, (0, 0))
        counter_refresh_actor.test_object = self

        # Ensure we stop the game engine when closing the test,
        # so that subsequent runs are fully restarted.
        self.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        """Called when test window is destroyed."""
        GameplayUtilities.close_game()
