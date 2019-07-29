"""
Default program start for FactoryGame.
"""

from factorygame.factory_engine import FactoryEngine
from factorygame.utils.gameplay import GameplayUtilities

def main():
    # Create the game.
    GameplayUtilities.create_game_engine(FactoryEngine)

if __name__ == '__main__':
    main()
