"""
Default program start for FactoryGame.
"""
import sys

try:
    # Py 3.6
    py_36_path, _ = sys.argv[0].split("/")
except ValueError:
    # Py 3.2
    sys.path.insert(0, "\\".join(sys.argv[0].split("\\")[:-1]))
else:
    sys.path.insert(0, py_36_path)

from factorygame import GameplayUtilities, GameplayStatics
from brainsim import BrainsimEngine

def main():
    # Create the game.
    GameplayUtilities.create_game_engine(BrainsimEngine)

if __name__ == '__main__':
    main()
