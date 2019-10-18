from factorygame import MathStat, FColor


class Gradient:
    """One dimensional gradient to interpolate between color keys.
    """

    def __init__(self):
        ## Stores sorted list of dicts.
        self.color_keys = []

    def add_key(self, value, location):
        """Insert a new key to the gradient at the given location.
        
        :param value: (FColor) Color at this key. Can also be a
        string containing hex values, or any lerp-able value.

        :param location: (float) Should be normalised between 0 and 1.
        
        :return: (int) Index new key was added at if successful.
        """

        # Ensure location between [0, 1].
        location = MathStat.clamp(location)

        if isinstance(value, str):
            # Convert to FColor if necessary.
            value = FColor.from_hex(value)

        # adjust location if value already exists at that location
        while self._key_exists_at_loc(location):
            location += 0.001
            if location > 1:
                return

        # determine the correct location to add the key
        new_idx = self._get_index_for_loc(location)

        # create dictionary to store key in
        new_key = {"location": location, "color": value}

        # insert the new key at the specified location
        self.color_keys.insert(new_idx, new_key)
        return new_idx  # return index successfully added at

    def remove_key(self, index=None, location=None):
        """Remove the key at the given index or location.

        :return: (bool) Whether it was successful."""
        # get index from location if specified
        if location is not None:
            location = MathStat.clamp(location)
            index = self.get_key(location)

        # validate index using range check
        if index not in range(len(self.color_keys)):
            return False
        # perform removal of the key
        self.color_keys.remove(index)
        return True  # success

    def sample(self, location, default=None):
        """Return value at any location on the gradient.
        
        :param location: (float) Location on the gradient, between
        [0, 1].

        :param default: (float) Optional return value if key not found.

        :return: (FColor) The interpolated color value.
        """
        location = MathStat.clamp(location)  # clamp to 0-1
        # check there are any keys
        if not self.color_keys:
            return default  # return default color
        # get keys surrouding the location
        key_min, key_max = self._get_keys_around_loc(location)
        if key_min == key_max is not None:  # out of key bounds
            bias = 0
        else:
            bias = MathStat.map_range(location, key_min["location"],
                                      key_max["location"])

        return MathStat.lerp(key_min["color"], key_max["color"], bias)

    def set_value(self, in_value, index=None, location=None):
        """Set value of the key at the given index or location.
        
        :return: (bool) Whether it was successful.
        """
        # get index from location if specified
        if location is not None:
            location = MathStat.clamp(location)
            index = self.get_key(location)
        # validate index using range check
        if index not in range(len(self.color_keys)):
            return False
        # set color
        self.color_keys[index]["color"] = in_value
        return True  # success

    def get_key(self, location, radius=0.01):
        """Return index of key in a given range.
        
        :param location: (float) Point to search from, between [0, 1].

        :param radius: (float) Search radius, between [0, 1].
        
        :return: (int) Index of key, or -1 if one isn't found.
        """
        for i, key in enumerate(self.color_keys):
            loc = key["location"]
            if loc > location-radius and loc < location+radius:
                return i
        return -1

    def _key_exists_at_loc(self, location):
        """Return whether a key exists at an exact location."""
        for key in self.color_keys:
            if key["location"] == location:
                return True
        return False

    def _get_index_for_loc(self, location):
        """Return index to insert new key at in the sorted `color_keys`
        list"""
        for key in reversed(self.color_keys):
            if key["location"] < location:
                return self.color_keys.index(key) + 1
        return 0

    def _get_closest_key(self, location):
        """Return closest color key to the given location.

        Returns None if no keys exist.
        """
        # check if any keys exist
        if not self.color_keys:
            return
        # search through the keys to find the closest
        best_gap = None
        best_col = None
        for loc, col in self.color_keys.items():
            gap = abs(location - loc)
            if gap < best_gap or best_gap is None:
                best_gap = gap
                best_col = col
        return best_col

    def _get_keys_around_loc(self, location):
        """Return closest colors above and below the location.
        """

        # return None if no keys
        if not self.color_keys:
            return None, None
        # return single key if only 1 key
        if len(self.color_keys) == 1:
            return self.color_keys[0], self.color_keys[0]
        # otherwise return surrounding keys
        location = MathStat.clamp(location, 0.001, 0.999)
        i = self._get_index_for_loc(location)
        # return surrounding keys
        if i <= len(self.color_keys)-1:
            return self.color_keys[i-1], self.color_keys[i]
        # return last key twice - we went beyond the last key
        else:
            return self.color_keys[i-1], self.color_keys[i-1]
