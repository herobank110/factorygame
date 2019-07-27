"""GUI helpers for tkinter application."""
from factorygame.core.utils.loc import Loc
from factorygame.core.utils.mymath import MathStat

class MotionInput(object):
    def __init__(self, *args, **kw):
        """initialise attributes. optionally call bind_to_widget with
        specified args if args are not empty

        AVAILABLE KEYWORDS
            normalise (bool) Whether to use acceleration smoothing on motion.
            True by default
        """
        self._isheld = False

        self._delta = (0, 0)
        self._normalised_delta_max = 5
        self._use_normalisation = kw.get("normalise", True)

        self._bound_events = {}
        ##self._held_buttons = {}

        # bind to widget if extra args given
        if args:
            self.bind_to_widget(*args)


    @property
    def delta(self):
        return Loc(self._delta)

    def bind_to_widget(self, in_widget, button="1"):
        """binds relevant inputs to in_widget, optionally using the
        specified button (1=LMB, 2=MMB, 3=RMB)"""
        in_widget.bind("<ButtonPress-%s>"%button, self.inp_press)
        in_widget.bind("<ButtonRelease-%s>"%button, self.inp_release)
        in_widget.bind("<Button%s-Motion>"%button, self.inp_motion)
        # add to held buttons dict (defualt False not held)
        ##self._held_buttons[button] = False

    def bind(self, event_code=None, func=None, add=None):
        """Binds func to be called on event_code.
        Event codes is written in the format <MODIFIER-MODIFIER-IDENTIFIER>.
        Available MODIFIERS:
            Motion
        Available IDENTIFIERS:
            X
            Y
            XY"""
        event_code = event_code.replace("<", "").replace(">", "")
        keys = event_code.split("-")
        identifier = keys.pop()
        modifiers = keys
        # check if the event_code is valid
        if identifier not in ["X", "Y", "XY"]:
            return False # fail
        for m in modifiers:
            if m not in ["Motion", "Button1", "Button2", "Button3"]:
                return False # epic fail!

        # bind the function
        # create new list for event if not already bound
        if event_code not in self._bound_events:
            self._bound_events[event_code] = [func]
        else:
            # append to list if necessary
            if add:
                self._bound_events[event_code].append(func)
            # otherwise initialise new list
            else:
                self._bound_events[event_code] = [func]
        return True # success

    def _get_bound_events(self, identifier=None, *modifiers):
        """Returns list of bound functions to call for the specified event"""
        ret_funcs = []
        modifiers = set(modifiers) # ensure modifiers are unique

        # check every bound event code
        for event_code, func_list in self._bound_events.items():
            event_keys = event_code.split("-")
            event_id = event_keys.pop()
            event_mods = event_keys
            all_mods_work = True

            # check identifier
            id_works = (identifier is None
                        or identifier is not None and identifier == event_id)
            # only check modifiers if identifier is correct
            if id_works:
                for m in modifiers:
                    if m not in event_mods:
                        all_mods_work = False
                        break
            # add bound functions if id and modifiers are correct
            if id_works and all_mods_work:
                    ret_funcs = ret_funcs + func_list

        # finally return found functions
        return ret_funcs if ret_funcs else None

    def _normalise_delta(self, in_delta, set_in_place=True):
        """Normalises in_delta to range (-1, 1).
        Optionally don't set in place"""

        # set attributes of passed in list object if necessary
        if set_in_place:
            in_delta.x = MathStat.map_range(in_delta.x,
                                          -self._normalised_delta_max,
                                          self._normalised_delta_max, -1, 1)
            in_delta.y = MathStat.map_range(in_delta.y,
                                          -self._normalised_delta_max,
                                          self._normalised_delta_max, -1, 1)
            return in_delta

        # otherwise initialise a new Loc object
        else:
            return Loc(MathStat.map_range(in_delta.x,
                                          -self._normalised_delta_max,
                                          self._normalised_delta_max, -1, 1),
                       MathStat.map_range(in_delta.y,
                                          -self._normalised_delta_max,
                                          self._normalised_delta_max, -1, 1))

    def _is_held(self, button):
        """returns whether the button is held"""
        return button in self._held_buttons and self._held_buttons[button]

    def inp_press(self, event, func=None):
        """Bind this to a widget on a ButtonPress-X event"""
        self._isheld = True
        ##self._held_buttons[event.num] = True
        self._last_loc = Loc(event.x, event.y)
        self._orig_press_loc = self._last_loc.copy()
        # call function if specified with event
        if func:
            func(event)

    def inp_release(self, event=None, func=None):
        """Bind this to a widget on a ButtonRelease-X event"""
        self._isheld = False
        ##self._held_buttons[event.num] = False
        # call function if specified with event
        if func:
            func(event)

    def inp_motion(self, event, func=None):
        """Bind this to a widget on a ButtonX-Motion event"""
        def near_to_zero(val, offset=0.05):
            return val < offset and val > -offset

        if self._isheld:
            # get and set delta
            new_loc = Loc(event.x, event.y)
            self._delta = d = new_loc - self._last_loc
            if self._use_normalisation:
                self._normalise_delta(d)
            else:
                d *= 0.2
            # set delta in event object to return in callbacks
            event.delta = d
            # ensure the last location is updated for next motion
            self._last_loc = new_loc

            # call function if specified with event and delta (in event)
            if func:
                func(event)

        # fire bound events for button invariant bindings

        if not near_to_zero(d.x):
            be = self._get_bound_events("X", "Motion")
            if be:
                for func in be:
                    func(event)

        if not near_to_zero(d.y):
            be = self._get_bound_events("Y", "Motion")
            if be:
                for func in be:
                    func(event)

        if not near_to_zero(d.x) or not near_to_zero(d.y):
            be = self._get_bound_events("XY", "Motion")
            if be:
                for func in be:
                    func(event)

class LocalPlayer(object):
    def __init__(self, canvas):
        self.input_tracker = {}
        self._setup_input(canvas)

    def _setup_input(self, input_component):
        """Setup input bindings to input_component using widget bindings"""
        pass