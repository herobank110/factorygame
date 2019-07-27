from tkinter import Tk, Label
from factorygame.core.utils.tkutils import MotionInput

def on_horiz_mov(event):
    print(event.delta)

window = Tk()

l = Label(window, text="Drag Here")
l.pack()

m = MotionInput(l)
m.bind("<Motion-X>", on_horiz_mov)

window.mainloop()
