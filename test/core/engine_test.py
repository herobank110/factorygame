from test.template.template_gui import GuiTest
from factorygame.core.engine_base import GameEngine, Actor, ETickGroup
from factorygame.utils.gameplay import GameplayStatics, GameplayUtilities
from tkinter.ttk import Label, Button, Frame
from tkinter import Text, DISABLED

import random

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


class CounterRefreshActor(Actor):
    """Refresh how many actors are in the world each frame."""

    def __init__(self):
        super().__init__()

        ## GuiTest object to refresh each frame.
        self.test_object = None

        self.primary_actor_tick.tick_group = ETickGroup.ENGINE

    def tick(self, delta_time):
        self.test_object.refresh_actor_count()

class DestroyingActor(Actor):

    def __init__(self):
        super().__init__()

        ## GuiTest object to refresh each frame.
        self.test_object = None

        self.primary_actor_tick.tick_group = ETickGroup.GAME

    def tick(self, delta_time):
        self.test_object.refresh_active_actor_tick(
            random.randint(0, 9))

class SlowTickEngine(GameEngine):
    """Engine with really slow tick for easy demonstration."""

    def __init__(self):
        super().__init__()
        self._frame_rate = 5  # Frames per second.

class ActorDestroyTest(GuiTest):
    _test_name = "Actor Destroy"

    def spawn_new_actor(self):
        new_actor = GameplayStatics.world.spawn_actor(DestroyingActor, (0, 0))
        new_actor.test_object = self

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

        # Also clear previous active actor ticks.
        self.active_actor_digits = []
        # self.active_actor_tick_label.config(
        #     text=self.active_actor_tick_format.format(0))

    def refresh_active_actor_tick(self, new_digit):
        self.active_actor_digits.append(new_digit)

        concat_digits = "".join(map(lambda x: str(x), self.active_actor_digits))

        self.active_actor_tick_label.config(
            text=self.active_actor_tick_format.format(concat_digits))

    def start(self):
        t = Text(
            self, height=4, relief="flat",
            wrap="word",
            font="Chicken 10")
        t.insert("end",
            "Actors in a world can be destroyed by the world. The actor's "
            "begin_destroy will be called and it will no longer receive "
            "ticks.The actor is removed from the world's master list, but "
            "to be GC'd all references must be removed!")
        t.pack(fill="both", expand="true", padx=10, pady=3)
        t.config(state=DISABLED)

        # List of spawned actors, to track creation by this test.
        # Although, the world has the true master list of actors
        # in the world. This is just to destroy the actors we made.
        self.spawned_actors = []

        # Create label to show number of active actors.
        self.actor_count_format = "There are currently {:d} actors in the world."

        self.actor_count_label = Label(
            self, text=self.actor_count_format.format(0))
        self.actor_count_label.pack()

        command_frame = Frame(self)

        # Create a button to create a new actor.
        Button(
            command_frame, text="Spawn",
            command=self.spawn_new_actor
            ).pack(side="left")

        # Create a button to destroy last spawned actor.
        Button(
            command_frame, text="Destroy",
            command=self.destroy_newest_actor
            ).pack(side="right")

        command_frame.pack(pady=10)

        # Create a label to show when actors are spawned.

        self.active_actor_tick_format = "This number is changed by actors to {:s}."
        self.active_actor_digits = []  # Random chosen digits this frame.

        self.active_actor_tick_label = Label(
            self, text="This text is changed by spawned actors")
        self.active_actor_tick_label.pack()

        # Create the base class engine in this Toplevel window.
        GameplayUtilities.create_game_engine(SlowTickEngine, master=self)

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
