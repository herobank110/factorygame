"""Utilities for working with gameplay mechanics."""

class GameplayStatics(object):
    """Holds central information about the running game."""

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
