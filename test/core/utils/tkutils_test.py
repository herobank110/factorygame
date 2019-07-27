from factorygame.core.utils.tkutils import MotionInput
from test.template.template_gui import GuiTest
from factorygame.core.utils.loc import Loc
from tkinter import Label, Canvas

class TkutilsTest(GuiTest):
    def on_horiz_mov(self, event):
        print("Moved horizontally by", event.delta)

    def on_vert_mov(self, event):
        print("Moved vertically by", event.delta)

    def on_any_mov(self, event):
        # Delete old visualisation preview.
        self.canvas.delete("all")

        # Create a new line of delta preview.
        center = Loc(int(self.canvas.cget("width")),
            int(self.canvas.cget("height"))) // 2

        offset = event.delta * 50

        self.canvas.create_line(center, center + offset, 
            fill="red", tags=("delta-line"))

        self.canvas.create_text(center + (0, 80),
            text=round(offset, 3), tags=("delta-text"))


    def start(self):
        """Called when initialised to create test widgets."""

        # Canvas for previewing delta movement.
        self.canvas = Canvas(self, width=200, height=200)
        self.canvas.pack()

        # Label for dragging from.
        l = Label(self, text="DRAG ME", relief="ridge")
        l.pack(ipadx=10, ipady=10, padx=20, pady=20)

        # Motion input (the actual thing being tested!)
        m = MotionInput(l)
        ##m.bind("<Motion-X>", self.on_horiz_mov)
        ##m.bind("<Motion-Y>", self.on_vert_mov)

        m.bind("<Motion-XY>", self.on_any_mov)