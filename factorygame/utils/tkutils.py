"""GUI helpers for tkinter application."""
from tkinter import PhotoImage
from fractions import Fraction
import itertools, base64

from factorygame.utils.loc import Loc
from factorygame.utils.mymath import MathStat


class MotionInput(object):
    """Add motion input event to widgets."""

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
        in_widget.bind("<ButtonPress-%s>" % button, self.inp_press)
        in_widget.bind("<ButtonRelease-%s>" % button, self.inp_release)
        in_widget.bind("<Button%s-Motion>" % button, self.inp_motion)
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
            return False  # fail
        for m in modifiers:
            if m not in ["Motion", "Button1", "Button2", "Button3"]:
                return False  # epic fail!

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
        return True  # success

    def _get_bound_events(self, identifier=None, *modifiers):
        """Returns list of bound functions to call for the specified event"""
        ret_funcs = []
        modifiers = set(modifiers)  # ensure modifiers are unique

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

    # def _is_held(self, button):
    #     """returns whether the button is held"""
    #     return button in self._held_buttons and self._held_buttons[button]

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

from tkinter import _cnfmerge
class ScalingImage(PhotoImage):
    """Widget which can display images in PGM, PPM, GIF, PNG format with
    enhanced support for scaling to arbitrary proportions."""

    def configure(self, **kw):
        """Configure the image."""
        # Check if we can store the image data as base64 instead of filename.
        self._load_image_data(kw)
        super().configure(**kw)
    config = configure

    def _load_image_data(self, kw):
        """Load the image data from FILENAME to base64 encoded data."""

        # Check keywords for valid image data arguments.        
        filename = kw.pop("file", None)
        imgdata = kw.get("data")

        if filename:
            with open(filename, "rb") as fp:
                imgdata = base64.b64encode(fp.read())
                # For some reason it is faster to decode it straight away!
                imgdata = base64.b64decode(imgdata)
                kw["data"] = imgdata

        elif imgdata is not None: pass
        else: return
        self._imgdata = imgdata

    def __init__(self, name=None, cnf={}, master=None, **kw):
        """Create an image with NAME.

        Valid resource names: data, format, file, gamma, height, palette,
        width.
        """

        # Currently displayed image proportion as an integer fraction.
        # Store in a list to avoid instant simplification where possible.
        self.current_frac = Loc(Loc(1, 1), Loc(1, 1))

        # Current input values received from using fast mode (continuous). When
        # scale_continuous_end is called the accurate value will be computed from
        # these values.
        self.current_fast_input = (1, 1)

        # Sensitivity to unprecise easy to compute figures
        # Greater remainder tolerance means less precision is retained.
        self.remainder_tolerance = 1

        # Cached image data.        
        # Use preloaded base64 data so we don't have to read
        # from HDD every time (slower)
        self._imgdata = None

        # Attempt to load image data.
        kw.update(cnf)
        cnf = {}
        self._load_image_data(kw)

        super().__init__(name=name, cnf=cnf, master=master, **kw)

    def scale(self, x, y=None):
        """Return a new ScalingImage with the same image as this widget
        but scale it with a factor of x in the X direction and y in the Y
        direction.  If y is not given, the default value is the same as x.

        Zoom factors can be given in 2-tuple integer fractions, `(3, 4)`
        or a floating point value, `0.75`."""
        return self._scale(x, y, False)

    def scale_continuous(self, x, y=None):
        """Return a new ScalingImage with the same image as this widget
        but in low quality for fast computation.  Should be used when the
        scaling operation will happen multiple times in quick succession,
        and the given scale is not final."""

        # This should store the input proportions and the current continuous
        # proportion separately so that scale_continuous_end can use the most
        # accurate scaling and this can be as fast as possible.
        self.current_fast_input = (x, y)
        return self._scale(x, y, True)

    def scale_continuous_end(self):
        """Return a new ScalingImage with the same image and scale
        as this widget in the highest quality after continuous scaling has
        been finalised.  This is optional, but will reduce the time lag to
        delivering the highest quality image."""
        img = self.get_original_image()
        img = img.scale(*self.current_fast_input)
        img.current_frac = self.current_frac
        img._imgdata = self._imgdata
        return img

    def _scale(self, x, y, use_fast_mode):

        if y is None:
            y = x

        try:
            numer_x, denom_x = x
        except TypeError:
            # X is not iterable, it is a single decimal value.
            numer_x, denom_x = self._decimal_to_frac(x)
        finally:
            numer_x, denom_x = self._simplify_frac(numer_x, denom_x, use_fast_mode)

        try:
            numer_y, denom_y = y
        except TypeError:
            # Y is not iterable, it is a single decimal value.
            numer_y, denom_y = self._decimal_to_frac(y)
        finally:
            numer_y, denom_y = self._simplify_frac(numer_y, denom_y, use_fast_mode)

        self.current_frac.x *= (numer_x, denom_x)
        self.current_frac.y *= (numer_y, denom_y)

        return self._on_scale(numer_x, numer_y, denom_x, denom_y, use_fast_mode)

    def _decimal_to_frac(self, decimal):
        """Convert a decimal to non simpified fraction."""
        decimal = round(abs(decimal), 5)

        # Find accurate fraction
        # frac = fractions.Fraction(decimal).limit_denominator(40)
        # numer = abs(frac.numerator)
        # denom = abs(frac.denominator)

        # Find fast and easy to compute fraction
        # Greater denominator means more precision is kept. Reduce precision
        # at larger values.
        denom = abs(int(40 // decimal))
        numer = abs(int(denom * decimal))

        return numer, denom
        #return self._simplify_frac(numer, denom)

    def _simplify_frac(self, numer, denom, use_fast_mode=None):
        """Internal function to scale the image."""
        numer = 1 if not numer else abs(int(numer))
        denom = 1 if not denom else abs(int(denom))

        if denom > 3 or numer/denom > 0.25:
            # Attempt to simplify the proportions.

            if use_fast_mode:
                # Less accurate than using Fraction class.
                # Find common factors up to 7.
                for i in range(7, 1, -1):
                    if numer % i + denom % i <= self.remainder_tolerance:
                        # Simplify if both are exactly divisble
                        numer //= i
                        denom //= i
                        break

            else:
                # Convert to a fraction for quick simplification
                frac = Fraction(numer, denom)
                numer = frac.numerator
                denom = frac.denominator

        # Avoid really tiny scale.
        i = itertools.count()
        while numer/denom < 0.01:
            numer += 1
            if next(i) > 10:
                return  # don't scale anything

        return numer, denom

    def get_original_image(self):
        """Return the original full size image. Valid only if an image
        is already loaded (from file or data arguments.)"""
        out_image = ScalingImage(data=self._imgdata, format=self["format"])
        return out_image

    def _on_scale(self, zoom_x, zoom_y, subsample_x, subsample_y, use_fast_mode=None):
        """Internal function to scale the image to the specified proportion. If USE_FAST_MODE
        is true the efficient but low quality mode will be used. Should be called after
        self.current_frac is set to the same as the given parameters."""

        # Scale using the current image. If the original image is wanted
        # then caller should use get_original_image.
        #out_image = self.get_original_image()
        out_image = self.copy()

        if use_fast_mode:
            out_image = out_image.subsample(
                subsample_x, subsample_y).zoom(zoom_x, zoom_y)
        else:
            out_image = out_image.zoom(zoom_x, zoom_y).subsample(
                subsample_x, subsample_y)

        out_image.current_frac = self.current_frac
        out_image.current_fast_input = self.current_fast_input
        out_image._imgdata = self._imgdata
        return out_image

    # Overrides from tkinter PhotoImage to return correct class.

    def copy(self):
        """Return a new ScalingImage with the same image as this widget."""
        destImage = ScalingImage(master=self.tk)
        self.tk.call(destImage, 'copy', self.name)
        return destImage

    def zoom(self, x, y=''):
        """Return a new ScalingImage with the same image as this widget
        but zoom it with a factor of x in the X direction and y in the Y
        direction.  If y is not given, the default value is the same as x.
        """
        destImage = ScalingImage(master=self.tk)
        if y == '':
            y = x
        self.tk.call(destImage, 'copy', self.name, '-zoom', x, y)
        return destImage

    def subsample(self, x, y=''):
        """Return a new ScalingImage based on the same image as this widget
        but use only every Xth or Yth pixel.  If y is not given, the
        default value is the same as x.
        """
        destImage = ScalingImage(master=self.tk)
        if y == '':
            y = x
        self.tk.call(destImage, 'copy', self.name, '-subsample', x, y)
        return destImage
