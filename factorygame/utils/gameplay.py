"""Utilities for working with gameplay mechanics."""

class __GameplayStatics(object):
    """Holds central information about the running game."""

    def clear_all(self):
        """Clear all references to gameplay objects."""
        cls = type(self)

        cls._game_engine = None
        cls._world = None

    @classmethod
    def is_game_valid(cls):
        """Check whether the game engine is still valid."""
        return cls._game_engine is not None \
            and cls._world is not None

    # GameEngine

    _game_engine = None
    game_engine  = property(lambda self: self._game_engine)

    @classmethod
    def set_game_engine(cls, value):
        cls._game_engine = value


    # World

    _world = None
    world  = property(lambda self: self._world)

    @classmethod
    def set_world(cls, value):
        cls._world = value

class GameplayUtilities(object):
    def close_game(self):
        """Close the game."""

# Initialise an object to work with properties.
GameplayStatics = __GameplayStatics()


