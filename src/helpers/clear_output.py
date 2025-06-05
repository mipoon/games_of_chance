"""
Output Clearing Utilities

Provides cross-platform screen clearing functionality for console applications.
"""

import os
import sys


def clear_output() -> None:
    """
    Clear the console output in a cross-platform way.
    
    Attempts to use the appropriate system command for clearing the screen.
    Falls back to printing newlines if system commands are not available.
    """
    try:
        # Try to use system-specific clear commands
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Unix/Linux/MacOS
            os.system('clear')
    except Exception:
        # Fallback method: print newlines to simulate clearing
        print("\n" * 100)


def clear_output_simple() -> None:
    """
    Simple screen clearing using newlines.
    
    A basic fallback method that simulates clearing by printing
    many newlines. Works on all platforms but less elegant.
    """
    print("\n" * 100)


def clear_output_ansi() -> None:
    """
    Clear screen using ANSI escape sequences.
    
    Uses ANSI escape codes to clear the screen and move cursor to top.
    Works on most modern terminals but may not work in all environments.
    """
    try:
        # ANSI escape sequence to clear screen and move cursor to home
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()
    except Exception:
        # Fallback to simple method
        clear_output_simple()
