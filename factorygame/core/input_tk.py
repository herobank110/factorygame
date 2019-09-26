"""
Take input from the tkinter widget system and send engine input events.
"""

from factorygame.core.input_base import GUIInputHandler, EKeys, EInputEvent


class TkInputHandler(GUIInputHandler):
    """Handle input from tkinter."""

    def bind_to_widget(self, in_widget):
        """
        Setup input events for a widget.
        """

        # Bind mouse events.
        in_widget.bind_all("<ButtonPress-1>", lambda e: self.register_key_press(
            EKeys.LeftMouseButton, EInputEvent.IE_PRESSED))
        in_widget.bind_all("<ButtonRelease-1>", lambda e: self.register_key_press(
            EKeys.LeftMouseButton, EInputEvent.IE_RELEASED))

        in_widget.bind_all("<ButtonPress-2>", lambda e: self.register_key_press(
            EKeys.MiddleMouseButton, EInputEvent.IE_PRESSED))
        in_widget.bind_all("<ButtonRelease-2>", lambda e: self.register_key_press(
            EKeys.MiddleMouseButton, EInputEvent.IE_RELEASED))

        in_widget.bind_all("<ButtonPress-3>", lambda e: self.register_key_press(
            EKeys.RightMouseButton, EInputEvent.IE_PRESSED))
        in_widget.bind_all("<ButtonRelease-3>", lambda e: self.register_key_press(
            EKeys.RightMouseButton, EInputEvent.IE_RELEASED))
