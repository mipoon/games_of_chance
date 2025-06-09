"""
Games of Chance with Prizes

A collection of mini-games where players can earn tokens and win prizes.
Features include:
- Multiple chance-based games (number guessing, coin flip, dice roll)
- Token-based economy
- Prize system with different rarities (common, odd, rare, epic, legendary)
- GUI interface
- Player data persistence
"""

from src.gui import run_gui


def main():
    """
    Main entry point for the Games of Chance application.
    
    Launches the GUI version of the game.
    """
    run_gui()


if __name__ == "__main__":  # pragma: no cover
    main()
