from factorygame.utils.tkutils import MotionInput, ScalingImage
from test.template.template_gui import GuiTest
from factorygame.utils.loc import Loc
from tkinter import Label, Canvas, Toplevel, IntVar, DoubleVar
from tkinter.ttk import Labelframe, Button, Scale, LabelFrame
import base64

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

class ScalingImageTest(GuiTest):
    _test_name = "Scaling Image Test"

    def on_zoom(self, x, y=None):
        #img = self.img.get_original_image()
        img = ScalingImage(data=self.imgdata)
        img = img.scale_continuous(x, y)
        self._assign_image(img)

    def on_end_zoom(self):
        # TODO: fix get_original_image
        pass
        # img = self.img.scale_continuous_end()
        # self.img = img
        # self.my_label.config(image=self.img)

    def on_reset(self):
        # img = self.img.get_original_image()
        # (data=self["data"], format=self["format"], file=self["file"],
        #                          gamma=self["gamma"], height=self["height"], palette=self["palette"],
        #                          width=self["width"]
        #print("data is", self.img._imgdata)


        #img = self.img.get_original_image()
        
        with open("test/utils/ACU_Young_Élise_Arno.png", "rb") as fp:
            imgdata = base64.b64encode(fp.read())
            # For some reason it is faster to decode it straight away!
            imgdata = base64.b64decode(imgdata)

        #img = ScalingImage(data=imgdata)
        img = ScalingImage(file="test/utils/ACU_Young_Élise_Arno.png")
        img = ScalingImage(data=img._imgdata)

        img2 = self.img.get_original_image()

        print("is the same?", imgdata == img2._imgdata, type(img2._imgdata))

        self._assign_image(img2)

    def _assign_image(self, img):
        self.img = img
        self.my_label.config(image=img)


    def on_frac_changed(self):
        frac_x = (self.numer_var.get(), self.denom_var.get())
        self.on_zoom(frac_x)
        self.numer_display_var.set(self.numer_var.get())
        self.denom_display_var.set(self.denom_var.get())
    def on_numer_scale_changed(self):
        frac_x = (self.numer_scale_var.get(), 20)
        self.on_zoom(frac_x)
        self.numer_scale_display_var.set(self.numer_scale_var.get())
    def on_decimal_changed(self):
        decimal_x = self.decimal_scale_var.get()
        self.on_zoom(decimal_x)
        self.decimal_display_var.set(round(self.decimal_scale_var.get(), 8))

    # Setup widgets and movement components.

    def start(self):
        """Called when initialised to create test widgets."""

        with open("test/utils/ACU_Young_Élise_Arno.png", "rb") as fp:
            self.imgdata = base64.b64encode(fp.read())
            # For some reason it is faster to decode it straight away!
            self.imgdata = base64.b64decode(self.imgdata)

        # self.img = ScalingImage(data=self.imgdata)

        self.img = ScalingImage(file="test/utils/ACU_Young_Élise_Arno.png")

        self.my_label = Label(Toplevel(self), image=self.img)
        self.my_label.__image = self.img
        # The window snaps to the right size faster with these pack options
        self.my_label.pack(fill="both", expand="true", side="left", anchor="nw")



        self.numer_var = IntVar()
        self.denom_var = IntVar()
        self.numer_display_var = IntVar()
        self.denom_display_var = IntVar()

        self.numer_var.set(10)
        self.denom_var.set(20)
        self.numer_display_var.set(10)
        self.denom_display_var.set(20)

        frac_frame = LabelFrame(self, text="Full Fraction")
        frac_frame.pack(side="left", fill="both", expand="true", padx=5, pady=5)

        frac_numer_scale = Scale(frac_frame, variable=self.numer_var, from_=1, to=100,
            orient="vertical", command=lambda i: self.on_frac_changed())
        frac_numer_scale.bind("<ButtonRelease>", lambda e: self.on_end_zoom())
        frac_numer_scale.pack(side="left")

        frac_denom_scale = Scale(frac_frame, variable=self.denom_var, from_=1, to=100,
            orient="vertical",command=lambda i: self.on_frac_changed())
        frac_denom_scale.bind("<ButtonRelease>", lambda e: self.on_end_zoom())
        frac_denom_scale.pack(side="left")

        Label(frac_frame, textvariable=self.numer_display_var).pack()
        Label(frac_frame, text="__\n").pack()
        Label(frac_frame, textvariable=self.denom_display_var).pack()




        numer_scale_frame = LabelFrame(self, text="Numeric Scale")
        numer_scale_frame.pack(side="left", fill="both", expand="true", padx=5, pady=5)

        self.numer_scale_var = IntVar()
        self.numer_scale_display_var = IntVar()
        self.numer_scale_var.set(20)
        self.numer_scale_display_var.set(20)

        zoom_scale = Scale(numer_scale_frame, from_=1, to=60, variable=self.numer_scale_var,
            orient="horizontal", command=lambda i: self.on_numer_scale_changed())
        zoom_scale.bind("<ButtonRelease>", lambda e: self.on_end_zoom())
        zoom_scale.pack(fill="x")

        Label(numer_scale_frame, textvariable=self.numer_scale_display_var).pack()
        Label(numer_scale_frame, text="__\n\n20").pack()



        decimal_frame = LabelFrame(self, text="Decimal")
        decimal_frame.pack(side="left", fill="both", expand="true", padx=5, pady=5)

        self.decimal_scale_var = DoubleVar()
        self.decimal_display_var = DoubleVar()
        self.decimal_scale_var.set(1)
        self.decimal_display_var.set(1)

        decimal_scale = Scale(decimal_frame, variable=self.decimal_scale_var, from_=0.01, to=3,
            command=lambda i: self.on_decimal_changed())
        decimal_scale.bind("<ButtonRelease>", lambda e: self.on_end_zoom())
        decimal_scale.pack()

        Label(decimal_frame, textvariable=self.decimal_display_var).pack()


        Button(self, text="Reset", command=self.on_reset).pack(side="left")