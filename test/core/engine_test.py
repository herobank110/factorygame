from test.template.template_gui import GuiTest
from factorygame.core.engine_base import GameEngine, Actor
from factorygame.utils.gameplay import GameplayStatics, GameplayUtilities
from tkinter.ttk import Label


class MyActor(Actor):
    def __init__(self):
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
