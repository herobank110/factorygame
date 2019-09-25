"""
Input module for keyboard and mouse interations.

All keyboard and mouse input events will be routed through the
engine first. Then custom events can be set up when these events
happen.
"""


class GameViewportClient(object):
    pass


class EKeys:

    # Mouse keys

	LeftMouseButton = "LeftMouseButton"
	RightMouseButton = "RightMouseButton"
	MiddleMouseButton = "MiddleMouseButton"
	ThumbMouseButton = "ThumbMouseButton"
	ThumbMouseButton2 = "ThumbMouseButton2"

    # Keyboard keys

	A = "A"
	B = "B"
	C = "C"
	D = "D"
	E = "E"
	F = "F"
	G = "G"
	H = "H"
	I = "I"
	J = "J"
	K = "K"
	L = "L"
	M = "M"
	N = "N"
	O = "O"
	P = "P"
	Q = "Q"
	R = "R"
	S = "S"
	T = "T"
	U = "U"
	V = "V"
	W = "W"
	X = "X"
	Y = "Y"
	Z = "Z"


class EInputEvent:
    """Type of event that can occur on a given key."""
    IE_PRESSED = 0
    IE_RELEASED = 1


class EngineInputMappings:
    """
    Contains mappings between input events and functions to fire.
    """

    ## Mappings of actions to keys. Each action has a set of keys.
    _action_mappings = {}

    # dictionary: keys -> action mapping CONCAT key_event : value -> set of callables
    ## Functions to fire when relevant input is received.
    _bound_events = {}

    @classmethod
    def add_action_mapping(cls, in_name, *keys):
        """
        Add an action mapping to be called when input comes from keys.

        :param in_name: (str) Name of (existing) action mapping.

        :param keys: (EKeys) Keys to map to action name.
        """
        key_set = cls._action_mappings.get(in_name)
        if key_set is not None:
            # Needs to reassign returned set
            key_set.update(keys)

        else:
            # Create a new set of keys.
            cls._action_mappings[in_name] = set(keys)

    @classmethod
    def remove_action_mapping(cls, in_name):
        """
        Remove an action mapping, including all keys that were previously
        added to it.
        """
        cls._action_mappings.pop(in_name)

    @classmethod
    def bind_action(cls, action_name, key_event, func):
        """
        Bind a function to an action defined in add_action_mapping.

        :param action_name: (str) Name of existing action mapping.

        :param key_event: (EInputEvent, int) Key event to bind to.

        :param func: (callable) Function to call when input comes in.
        """

        # Concatenate action name and key event.
        binding = "%s:%d" % (action_name, key_event)

        func_set = cls._bound_events.get(binding)
        if func_set is not None:
            # Add to existing set.
            func_set.add(func)

        else:
            # Create a new set.
            cls._bound_events[binding] = {func}

class GUIInputHandler:
    """
    Handle raw input from a GUI system to map it to an FKey
    """

    def receive_tkinter_key_input(self, tk_event, input_event):
        """
        Called when tkinter sends an input event.

        :param tk_event: Tkinter event from widget.

        :param input_event: (EInputEvent) Information about the event.
        """

        # TODO: fire any bounds input functions
        pass
