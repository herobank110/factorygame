from tkinter import Tk, Label
from factorygame.core.utils.tkutils import MotionInput
from test.template.template_gui import GuiTest

class TkutilsTest(GuiTest):
    def on_horiz_mov(self, event):
        print(event.delta)

    def start(self):
        l = Label(self, text="Drag Here")
        l.pack()

        m = MotionInput(l)
        m.bind("<Motion-X>", self.on_horiz_mov)
