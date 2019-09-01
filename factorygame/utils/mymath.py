from math import sqrt
from random import random

class MathStat(object):
    """Static math library."""

    @staticmethod
    def clamp(val, min=0, max=1):
        return min if val < min else max if val > max else val

    @staticmethod
    def getpercent(val, min, max):
        """returns what percent (0 to 1) val is between min and max.
        eg: val of 15 from 10 to 20 will return 0.5"""
        return (val-min) / (max-min)

    @staticmethod
    def map_range(val, in_a, in_b, out_a=0, out_b=1):
        """returns val mapped from range(in_a to in_b) to range(out_a to out_b)
        eg: 15 mapped from 10,20 to 1,100 returns 50"""
        return MathStat.lerp(out_a, out_b,
            MathStat.getpercent(val, in_a, in_b), False)

    @staticmethod
    def map_range_clamped(val, in_a, in_b, out_a=0, out_b=1):
        """returns val mapped from range(in_a to in_b) to range(out_a to out_b)
        eg: 15 mapped from 10,20 to 1,100 returns 50"""
        return MathStat.lerp(out_a, out_b,
            MathStat.clamp(MathStat.getpercent(val, in_a, in_b)), True)

    @staticmethod
    def lerp(a, b, bias, clamp=True):
        """returns interpolation between a and b. bias 0 = a, bias 1 = b.
        also works with iterables by lerping each element of a and b
        can also extrapolate if clamp is set to False"""
        def lerp1(a, b, bias):
            return a + (b-a) * bias
        def cross_iter(a, b):
            for i in range(len(a)):
                yield a[i], b[i]
        def cross_iter_str(a, b):
            # format: '#rrggbb...' hex codes
            # yields integers rr, gg, bb, etc for a and b
            for i in range(1, len(a)):
                if i % 2 == 1:
                    yield int("0x%s"%a[i:i+2], 0), int("0x%s"%b[i:i+2], 0)
        if clamp:
            #bias = bias if bias > 0 else 1 if bias > 1 else 0
            bias = MathStat.clamp(bias)
        try:
##                cross_lerp = [lerp1(ax, bx, bias)
##                              for ax, bx in cross_iter_str(a, b)]
##                return cross_lerp

            # lerp each element in iterable container
            cross_lerp = [lerp1(ax, bx, bias) for ax, bx in cross_iter(a, b)]
            try:
                return type(a)(*cross_lerp)
            except:
                return type(a)(cross_lerp)
        except:
            # string hex code color lerp
            if isinstance(a, str):
                ret_str = "#"
                for ax, bx in cross_iter_str(a, b):
                    ret_str += "%02x"%int(lerp1(ax, bx, bias))
                return ret_str
            # simple lerp
            return lerp1(a, b, bias)

    @staticmethod
    def getdistsquared(loc1, loc2):
        """returns squared distance between coords"""
        return sum((loc2-loc1)**2)

    @staticmethod
    def getdist(loc1, loc2):
        """returns distance between coords"""
        return sqrt(sum((loc2-loc1)**2))

    @staticmethod
    def get_random_location_in_bounding_box(origin, bounds):
        return origin + [MathStat.lerp(0, i, random()) for i in bounds]