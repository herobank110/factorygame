from test.template.template_gui import GuiTest
from factorygame.core.engine_base import GameEngine
from factorygame.utils.gameplay import GameplayStatics, GameplayUtilities

from tkinter.ttk import Label
import random

# Input testing
from factorygame.core.input_base import EKeys, EInputEvent


class ActionMappingTest(GuiTest):
    _test_name = "Action Mapping"

    def show_jump_text(self):
        if self.clear_timer is not None:
            self.after_cancel(self.clear_timer)
            self.clear_timer = None

        # Show random number to make it easy to tell when a new
        # input event has come in and the text hasn't been cleared yet.
        self.label.config(text="%d Received a jump press" % random.randint(1000, 9999))

        # Clear the text after a short delay.
        self.clear_timer = self.after(300, lambda: self.label.config(text=""))        

    def start(self):

        Label(self, text="Press any key in \"j-u-m-p\" to jump.").pack()

        self.label = Label(self)
        self.label.pack()
        self.clear_timer = None

        # Create the base class engine in this Toplevel window.
        game_engine = GameplayUtilities.create_game_engine(GameEngine, master=self)


        # Add an input mapping.

        # Map the keys in 'j u m p' to a new action mapping called "Jump".
        game_engine.input_mappings.add_action_mapping("Jump", 
            EKeys.J, EKeys.U, EKeys.M, EKeys.P)

        # Bind the test function to be triggered when "Jump" is pressed.
        game_engine.input_mappings.bind_action("Jump", EInputEvent.PRESSED,
            self.show_jump_text)

        
        # Ensure we stop the game engine when closing the test, 
        # so that subsequent runs are fully restarted.
        self.bind("<Destroy>", self.on_destroy)

    def on_destroy(self, event):
        """Called when test window is destroyed."""
        GameplayUtilities.close_game()
