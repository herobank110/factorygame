from tkinter import Variable

class Loc(list):
    """Structure for representing coordinates, with basic arithmetic.

    Usage example: 
    ```
    a = Loc([0]*3) # Make 3D Loc like (X=0, Y=0, Z=0).
    b = Loc(-20, 0, 20)
    c = a + b   # Add components of a and b.
    c += 20     # Add 20 to components of c.
    print(c)
    # Output: (X=0, Y=20, Z=40)
    ```
    """
    _repr_items = "XYZ"

    def get_named(self, i):
        return self[i]
    def set_named(self, i, value):
        self[i] = value

    # allow index 0 - 2 to be accessed through letters:
    # x,y,z or r,g,b. IndexError if list too small!
    x = r = property(lambda self: self.get_named(0),
                     lambda self, v: self.set_named(0,v))
    y = g = property(lambda self: self.get_named(1),
                     lambda self, v: self.set_named(1,v))
    z = b = property(lambda self: self.get_named(2),
                     lambda self, v: self.set_named(2,v))

    def set(self, *args):
        self.__init__(*list(args))

    def __init__(self, *args):
        """Create a new Loc object of any size, although the size will
        be set from how many values are given. These can be given
        separately or as an iterable.

        Eg,
        `Loc(10, 10)` or
        `Loc([10, 10])`
        """
        try:
            super().__init__(list(*args))
        except TypeError:
            super().__init__(list(args))

    @classmethod
    def from_str(self, other):
        """Return Loc with types (int or float) from repr string OTHER.
        Example input is `(10.0, 5.0)`, not `(X=2, Y=30)`"""
        ret = Loc()
        items = other.strip().replace(" ", "").strip("()").split(",")
        for it in items:
            try:
                ret.append(eval(it))
            except:
                pass
        return ret

    def __repr__(self):
        return "(%s)"%", ".join((str(it) for it in self))
    def __str__(self):
        return "(%s)"%", ".join(("%s=%s"%(self._repr_items[i], str(it))
                                 if i < len(self._repr_items) else str(it)
                                 for i, it in enumerate(self)))
    def __add__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] + other[i])
            except TypeError:
                ret.append(self[i] + other)
        return ret
    def __mul__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] * other[i])
            except TypeError:
                ret.append(self[i] * other)
        return ret
    def __mod__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] % other[i])
            except TypeError:
                ret.append(self[i] % other)
        return ret
    def __sub__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] - other[i])
            except TypeError:
                ret.append(self[i] - other)
        return ret
    def __truediv__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] / other[i])
            except TypeError:
                ret.append(self[i] / other)
        return ret
    def __floordiv__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(self[i] // other[i])
            except TypeError:
                ret.append(self[i] // other)
        return ret
    def __pow__(self, other):
        ret = Loc()
        for i in range(len(self)):
            try:
                ret.append(pow(self[i], other[i]))
            except TypeError:
                ret.append(pow(self[i], other))
        return ret
    def __round__(self, *args):
        ret = Loc()
        for i in range(len(self)):
            ret.append(round(self[i], *args))
        return ret
    def __iadd__(self, other):
        self = self + other
        return self
    def __isub__(self, other):
        self = self - other
        return self
    def __imul__(self, other):
        self = self * other
        return self
    def __imod__(self, other):
        self = self % other
        return self
    def __itruediv__(self, other):
        self = self / other
        return self
    def __ifloordiv__(self, other):
        self = self / other
        return self
    def copy(self):
        return Loc(*self)

class LocVar(Variable):
    """Value holder for Loc variables."""
    _default = Loc(0.0, 0.0)
    def __init__(self, master=None, value=None, name=None):
        """Construct an Loc variable.

        MASTER can be given as master widget.
        VALUE is an optional value (defaults to 0)
        NAME is an optional Tcl name (defaults to PY_VARnum).

        If NAME matches an existing variable and VALUE is omitted
        then the existing value is retained.
        """
        Variable.__init__(self, master, value, name)

    def set(self, value):
        """Set the variable to value, converting iterable to Loc."""
        if not isinstance(value, Loc):
            try:
                value = Loc(*value)
            except TypeError:
                pass
        return Variable.set(self, repr(value))

    def get(self):
        """Return the value of the variable as an Loc."""
        return Loc.from_str(self._tk.globalgetvar(self._name))
