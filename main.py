"""
Games of Chance with Prizes:
1. Password
2. Tokens
3. Rarities
4. Prizes
5. Re-rolls
6. 1 hour timer
"""

import sys
from play_session import PlaySession
from gui import run_gui

def main():
    """Main entry point - supports both console and GUI modes"""
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        run_gui()
    else:
        # Default console mode
        choice = input("Choose mode: (1) Console (2) GUI [default: 1]: ").strip()
        if choice == "2":
            run_gui()
        else:
            PlaySession().run_session()

if __name__ == "__main__": # pragma: no cover
    main()
