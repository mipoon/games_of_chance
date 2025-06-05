"""
Games of Chance with Prizes

A collection of mini-games where players can earn tokens and win prizes.
Features include:
- Multiple chance-based games (number guessing, coin flip, dice roll)
- Token-based economy
- Prize system with different rarities (common, odd, rare, epic, legendary)
- Both console and GUI interfaces
- Player data persistence
"""

import sys
from src.play_session import PlaySession
from src.gui import run_gui


def main():
    """
    Main entry point for the Games of Chance application.
    
    Supports both console and GUI modes. Can be launched with --gui flag
    for direct GUI mode, otherwise prompts user for mode selection.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        run_gui()
    else:
        # Default console mode
        choice = input("Choose mode: (1) Console (2) GUI [default: 1]: ").strip()
        if choice == "2":
            run_gui()
        else:
            PlaySession().run_session()


if __name__ == "__main__":  # pragma: no cover
    main()
