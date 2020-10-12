"""
Input module for keyboard and mouse interations.

All keyboard and mouse input events will be routed through the
engine first. Then custom events can be set up when these events
happen.
"""

# from factorygame.core.engine_base import EngineObject
from factorygame.utils.gameplay import GameplayStatics


class GameViewportClient(object):
    pass


class FKey:
    """
    Holder for an input key. Should not be used directly, use EKeys instead.
    """

    def __init__(self, in_name):
        self._key_name = in_name

    @property
    def key_name(self):
        return self._key_name

    def __eq__(self, other):
        return self.key_name == other.key_name

    def __hash__(self):
        return hash(self.key_name)


class EKeys:
    """Enum of all input keys."""

    # Mouse keys

    LeftMouseButton = FKey("LeftMouseButton")
    RightMouseButton = FKey("RightMouseButton")
    MiddleMouseButton = FKey("MiddleMouseButton")

    # Currently thumb buttons aren't recognised by tkinter.
    ThumbMouseButton = FKey("ThumbMouseButton")
    ThumbMouseButton2 = FKey("ThumbMouseButton2")

    # Keyboard keys

    A = FKey("A")
    B = FKey("B")
    C = FKey("C")
    D = FKey("D")
    E = FKey("E")
    F = FKey("F")
    G = FKey("G")
    H = FKey("H")
    I = FKey("I")
    J = FKey("J")
    K = FKey("K")
    L = FKey("L")
    M = FKey("M")
    N = FKey("N")
    O = FKey("O")
    P = FKey("P")
    Q = FKey("Q")
    R = FKey("R")
    S = FKey("S")
    T = FKey("T")
    U = FKey("U")
    V = FKey("V")
    W = FKey("W")
    X = FKey("X")
    Y = FKey("Y")
    Z = FKey("Z")


class EInputEvent:
    """Type of event that can occur on a given key."""
    PRESSED = 0
    RELEASED = 1

    MAX = 2


class AxisKey:
    ## (FKey) Key in the axis mapping.
    key = None

    ## (float) The extent to which to exert itself upon axis.
    strength = 0.0


class EngineInputMappings:
    """
    Contains mappings between input events and functions to fire.
    """

    def __init__(self):

        ## Mappings of actions to keys. Each action has a set of keys.
        self._action_mappings = {}

        # dictionary: keys -> action mapping CONCAT key_event : value -> set of callables
        ## Functions to fire when relevant input is received.
        self._bound_events = {}

        ## Mappings of axis to axis keys. Each axis has a set of keys.
        self._axis_mappings = {}

        # dictionary: keys -> axis mapping : value -> list of callables
        ## Functions that fire continuously on axis input.
        self._bound_axis_events = {}

    def add_action_mapping(self, in_name, *keys):
        """
        Add an action mapping to be called when input comes from keys.

        :param in_name: (str) Name of (existing) action mapping.

        :param keys: (EKeys) Keys to map to action name.
        """
        key_set = self._action_mappings.get(in_name)
        if key_set is not None:
            # Needs to reassign returned set
            key_set.update(keys)

        else:
            # Create a new set of keys.
            self._action_mappings[in_name] = set(keys)

    def add_axis_mapping(self, in_name, *axis_keys):
        """Add an axis mapping to be called continuously.

        :param in_name: (str) Name of (existing) axis mapping.

        :param axis_keys: (list<AxisKey>) Keys and their
        strength to map to axis name.
        """
        key_set = self._axis_mappings.get(in_name)
        if key_set is not None:
            # Needs to reassign returned set.
            key_set.update(axis_keys)

        else:
            # Create a new set of keys.
            self._axis_mappings[in_name] = set(axis_keys)

    def remove_action_mapping(self, in_name):
        """
        Remove an action mapping, including all keys that were previously
        added to it.
        """
        self._action_mappings.pop(in_name)

    def remove_axis_mapping(self, in_name):
        """
        Remove an axis mapping, including all axis keys that were
        previously added to it.
        """
        self._axis_mappings.pop(in_name)

    def bind_action(self, action_name, key_event, func):
        """
        Bind a function to an action defined in add_action_mapping.

        :param action_name: (str) Name of existing action mapping.

        :param key_event: (EInputEvent) Key event to bind to.

        :param func: (callable) Function to call when input comes in.
        """

        # Concatenate action name and key event.
        binding = "%s:%d" % (action_name, key_event)

        func_set = self._bound_events.get(binding)
        if func_set is not None:
            # Add to existing set.
            func_set.add(func)

        else:
            # Create a new set.
            self._bound_events[binding] = {func}

    def bind_axis(self, axis_name, func):
        """
        Bind a function to an axis defined in add_axis_mapping.

        :param axis_name: (str) Name of existing axis mapping.

        :param func: (callable) Function to call continuously. The axis
        extent is supplied as a float argument.
        """

        func_set = self._bound_axis_events.get(axis_name)
        if func_set is not None:
            # Add to existing set.
            func_set.add(func)

        else:
            # Create a new set.
            self._bound_axis_events[axis_name] = {func}

    def get_mappings_for_key(self, key):
        """
        Return a list of mappings that contain a given key.

        :param key: (EKeys) Key to search for.

        :return: (list) List of corresponding mappings.
        """
        return [mapping
            for mapping, key_set in self._action_mappings.items()
            if key in key_set]

    def get_axis_mapping_for_key(self, key):
        """
        Return a list of axis mapping that contain a given key.

        :param key: (EKeys) Key to search for.

        :return: (list) List of corresponding mappings.
        """
        return [mapping
            for mapping, key_set in self._axis_mappings.items()
            if key in key_set]

    def fire_action_bindings(self, action_name, key_event):
        """
        Invoke all callables registered to a mapping.

        :param action_name: (str) Name of existing mapping.

        :param key_event: (EInputEvent) Type of key event.
        """

        event_code = "%s:%d" % (action_name, key_event)
        bound_funcs = self._bound_events.get(event_code)
        if bound_funcs is not None:
            for func in bound_funcs:
                func.__call__()

    def visit_action_mappings(self, visitor):
        """Iterate through axis mappings.

        :param visitor: (callable) Function to call at each action
        mapping, taking the mapping name and axis key as arguments.

        :return: (generator) Generator to visit action mappings.
        """
        return map(lambda kvp: visitor(*kvp), self._action_mappings.items())

    def visit_axis_mappings(self, visitor):
        """Iterate through axis mappings.

        :param visitor: (callable) Function to call at each axis
        mapping, taking the mapping name and axis key as arguments.

        :return: (generator) Generator to visit axis mappings.
        """
        return map(lambda kvp: visitor(*kvp), self._axis_mappings.items())

class GUIInputHandler:
    """
    Handle raw input from a GUI system to map it to an FKey
    """

    def __init__(self):
        """Set default values."""

        ## Hold currently held buttons in a set.
        self._held_keys = set()

        self.begin_play()

    def begin_play(self):
        # This is being called manually in the constructor,
        # but once the engine module is refactored this will
        # be derived from EngineObject and it will be called
        # automatically when it is appropriate.
        self._input_mappings = GameplayStatics.game_engine.input_mappings

    def fire_action_events(self, key, key_event):
        """
        Fire functions bound to action mappings that are bound
        to the key.
        """
        # A single key could trigger several actions.
        mappings = self._input_mappings.get_mappings_for_key(key)
        for action_name in mappings:
            # Fire events for each action.
            self._input_mappings.fire_action_bindings(action_name, key_event)

    def register_key_event(self, in_key, key_event):
        """
        Called when a key press is received to fire bound events.

        Only for action events (not axis events).

        :param in_key: (EKeys) Key that was pressed.

        :param key_event: (EInputEvent, int) Type of event to occur.
        """

        if key_event == EInputEvent.PRESSED:
            if in_key in self.held_keys:
                # Don't fire events repeatedly if already held.
                return

            self.fire_action_events(in_key, EInputEvent.PRESSED)
            self.held_keys.add(in_key)

        elif key_event == EInputEvent.RELEASED:
            # Remove reference from held keys.
            self.fire_action_events(in_key, EInputEvent.RELEASED)
            try:
                self.held_keys.remove(in_key)
            except KeyError:
                pass

    def register_analogue_event(self, in_axis_key, raw_value):
        """
        Called when an analogue key is changed.

        Only for axis events.

        :param in_axis_key: (EKeys) Key that was pressed. For
        multidimensional axis keys this is also the axis that was
        pressed. Each axis should be registered separately.

        :param raw_value: (float) How much the key is pressed. 1 means
        fully pressed and 0 means fully released. Negative numbers
        should only be used for bidirectional axis keys.
        """

    @property
    def held_keys(self):
        return self._held_keys
