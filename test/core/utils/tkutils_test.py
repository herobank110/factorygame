from factorygame.core.utils.tkutils import MotionInput
from test.template.template_gui import GuiTest
from factorygame.core.utils.loc import Loc
from tkinter import Label, Canvas
from tkinter.ttk import Labelframe, Button

class MotionInputTest(GuiTest):
    # Colors to use for vertical, horizontal and any direction visualisation.
    hcol = "dark green"
    vcol = "dark cyan"
    acol = "dark red"

    _test_name = "Motion Input Visualisation"

    def on_horiz_mov(self, event):
        # Cancel old canvas clear timer.
        if self.htimer is not None:
            self.after_cancel(self.htimer)

        # Delete old visualisation preview.
        self.hcanvas.delete("delta")

        # Create a new line of delta preview.
        center = Loc(int(self.hcanvas.cget("width")),
            int(self.hcanvas.cget("height"))) // 2

        # WARNING: The delta will contain x and y components, even if
        # this function is only called on changes to one axis!
        offset = Loc(event.delta.x * 50, 0)
        coords2 = center + offset

        self.hcanvas.create_line(center, coords2, 
            fill=self.hcol, width=5, tags=("delta", "line"))

        self.hcanvas.create_text(center + (0, 80),
            text=str(round(event.delta, 1)), tags=("delta"))

        self.hcanvas.create_oval(coords2 + 5, coords2 - 5,
            fill=self.hcol, outline=self.hcol, tags=("delta"))

        # Set timer to remove after 50ms.
        self.htimer = self.after(50, lambda: self.hcanvas.delete("line"))

    def on_vert_mov(self, event):
        # Cancel old canvas clear timer.
        if self.vtimer is not None:
            self.after_cancel(self.vtimer)

        # Delete old visualisation preview.
        self.vcanvas.delete("delta")

        # Create a new line of delta preview.
        center = Loc(int(self.vcanvas.cget("width")),
            int(self.vcanvas.cget("height"))) // 2

        # WARNING: The delta will contain x and y components, even if
        # this function is only called on changes to one axis!
        offset = Loc(0, event.delta.y * 50)
        coords2 = center + offset

        self.vcanvas.create_line(center, coords2, 
            fill=self.vcol, width=5, tags=("delta", "line"))

        self.vcanvas.create_text(center + (0, 80),
            text=str(round(event.delta, 1)), tags=("delta"))

        self.vcanvas.create_oval(coords2 + 5, coords2 - 5,
            fill=self.vcol, outline=self.vcol, tags=("delta"))

        # Set timer to remove after 50ms.
        self.vtimer = self.after(50, lambda: self.vcanvas.delete("line"))

    def on_any_mov(self, event):
        # Cancel old canvas clear timer.
        if self.atimer is not None:
            self.after_cancel(self.atimer)
        
        # Delete old visualisation preview.
        self.acanvas.delete("delta")

        # Create a new line of delta preview.
        center = Loc(int(self.acanvas.cget("width")),
            int(self.acanvas.cget("height"))) // 2

        offset = event.delta * 50
        coords2 = center + offset

        self.acanvas.create_line(center, coords2, 
            fill=self.acol, width=5, tags=("delta", "line"))

        self.acanvas.create_text(center + (0, 80),
            text=str(round(event.delta, 1)), tags=("delta"))

        self.acanvas.create_oval(coords2 + 5, coords2 - 5,
            fill=self.acol, outline=self.acol, tags=("delta"))

        # Set timer to remove after 50ms.
        self.atimer = self.after(50, lambda: self.acanvas.delete("line"))


    # Setup widgets and movement components.

    def start(self):
        """Called when initialised to create test widgets."""

        # Initialise timer variables to None. (no need to clear canvas yet!)
        self.vtimer = self.htimer = self.atimer = None

        Label(self, text="WARNING: The delta will contain x and y components, " \
        "even if that function is only called on changes to one axis!"
            ).pack()

        # Horizontal movement

        horiz_frame = Labelframe(self, text="Horizontal")
        horiz_frame.pack(side="left", padx=10, pady=10)

        # Canvas for previewing delta movement.
        self.hcanvas = Canvas(horiz_frame, width=200, height=200)
        self.hcanvas.create_oval(110, 110, 90, 90, fill=self.hcol,
            outline=self.hcol)
        self.hcanvas.pack()

        # Label for dragging from.
        l = Label(horiz_frame, text="DRAG ME", relief="ridge")
        l.pack(ipadx=10, ipady=10, padx=20, pady=20)

        # Create button to reset canvas.
        Button(horiz_frame, text="Reset",
            command=lambda: self.hcanvas.delete("delta")
            ).pack(padx=3, pady=3)

        # Motion input (the actual thing being tested!)
        m = MotionInput(l)
        m.bind("<Motion-X>", self.on_horiz_mov)


        # Vertical movement        

        vert_frame = Labelframe(self, text="Vertical")
        vert_frame.pack(side="left", padx=10, pady=10)

        # Canvas for previewing delta movement.
        self.vcanvas = Canvas(vert_frame, width=200, height=200)
        self.vcanvas.create_oval(110, 110, 90, 90, fill=self.vcol,
            outline=self.vcol)
        self.vcanvas.pack()

        # Label for dragging from.
        l = Label(vert_frame, text="DRAG ME", relief="ridge")
        l.pack(ipadx=10, ipady=10, padx=20, pady=20)

        # Create button to reset canvas.
        Button(vert_frame, text="Reset",
            command=lambda: self.vcanvas.delete("delta")
            ).pack(padx=3, pady=3)

        # Motion input (the actual thing being tested!)
        m = MotionInput(l)
        m.bind("<Motion-Y>", self.on_vert_mov)


        # Any movement

        any_frame = Labelframe(self, text="Any Direction")
        any_frame.pack(side="left", padx=10, pady=10)

        # Canvas for previewing delta movement.
        self.acanvas = Canvas(any_frame, width=200, height=200)
        self.acanvas.create_oval(110, 110, 90, 90, fill=self.acol,
            outline=self.acol)
        self.acanvas.pack()

        # Label for dragging from.
        l = Label(any_frame, text="DRAG ME", relief="ridge")
        l.pack(ipadx=10, ipady=10, padx=20, pady=20)

        # Create button to reset canvas.
        Button(any_frame, text="Reset",
            command=lambda: self.acanvas.delete("delta")
            ).pack(padx=3, pady=3)

        # Motion input (the actual thing being tested!)
        m = MotionInput(l)
        m.bind("<Motion-XY>", self.on_any_mov)
