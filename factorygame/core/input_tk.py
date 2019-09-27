"""
Take input from the tkinter widget system and send engine input events.
"""

from factorygame.core.input_base import GUIInputHandler, EKeys, EInputEvent


class TkInputHandler(GUIInputHandler):
    """Handle input from tkinter."""

    tk_key_mapping = {
        "mouse": {
            "press_format":     "<ButtonPress-%s>",
            "release_format":   "<ButtonRelease-%s>",
            "keys": {
                "1": EKeys.LeftMouseButton,
                "2": EKeys.MiddleMouseButton,
                "3": EKeys.RightMouseButton,
            },
        },

        "keyboard": {
            "press_format":     "<KeyPress-%s>",
            "release_format":   "<KeyRelease-%s>",
            "keys": {
                "a": EKeys.A,
                "b": EKeys.B,
                "c": EKeys.C,
                "d": EKeys.D,
                "e": EKeys.E,
                "f": EKeys.F,
                "g": EKeys.G,
                "h": EKeys.H,
                "i": EKeys.I,
                "j": EKeys.J,
                "k": EKeys.K,
                "l": EKeys.L,
                "m": EKeys.M,
                "n": EKeys.N,
                "o": EKeys.O,
                "p": EKeys.P,
                "q": EKeys.Q,
                "r": EKeys.R,
                "s": EKeys.S,
                "t": EKeys.T,
                "u": EKeys.U,
                "v": EKeys.V,
                "w": EKeys.W,
                "x": EKeys.X,
                "y": EKeys.Y,
                "z": EKeys.Z,
            },
        },
    }

    def bind_to_widget(self, in_widget):
        """
        Setup input events for a widget.
        """

        # Bind mouse events.
        mouse_bindings = self.tk_key_mapping.get("mouse")
        if mouse_bindings is not None:
            press_format    = mouse_bindings["press_format"]
            released_format = mouse_bindings["release_format"]

            for format_arg, key in mouse_bindings["keys"].items():
                # Bind when the button is pressed.
                in_widget.bind_all(press_format % format_arg, lambda e, k=key:
                    self.register_key_event(k, EInputEvent.IE_PRESSED))

                # Bind when the button is released.
                in_widget.bind_all(released_format % format_arg, lambda e, k=key:
                    self.register_key_event(k, EInputEvent.IE_RELEASED))

        # Bind keyboard events.
        keyboard_bindings = self.tk_key_mapping.get("keyboard")
        if keyboard_bindings is not None:
            press_format    = keyboard_bindings["press_format"]
            released_format = keyboard_bindings["release_format"]

            for format_arg, key in keyboard_bindings["keys"].items():
                # Bind when the button is pressed.
                in_widget.bind_all(press_format % format_arg, lambda e, k=key:
                    self.register_key_event(k, EInputEvent.IE_PRESSED))

                # Bind when the button is released.
                in_widget.bind_all(released_format % format_arg, lambda e, k=key:
                    self.register_key_event(k, EInputEvent.IE_RELEASED))
