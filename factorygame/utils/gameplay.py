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

    @staticmethod
    def create_game_engine(engine_class, master=None):
        """
        Create new game engine instance. Only one game engine can 
        exist at a time. Will fail if one already exists.

        :return: a new game engine
        """
        if GameplayStatics.is_game_valid():
            raise RuntimeWarning("Attempted to create game engine when valid game engine already exists.")
        
        # Initialise to set default values.
        engine = engine_class()
        
        # Call create game on base class.
        engine.create_game(master=master)

        return engine

    @staticmethod
    def close_game():
        """
        Completely close down the active engine and all currently
        running processes, including all worlds and spawned actors.
        
        Will not exit Python execution process.
        """
        if GameplayStatics.is_game_valid():
            GameplayStatics.game_engine.close_game()

# Initialise an object to work with properties.
GameplayStatics = __GameplayStatics()


