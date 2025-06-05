"""
Game Loader Module

Provides a centralized game selection system for randomly choosing
and instantiating games from the available game library.
"""

from random import choice
from .guess_the_number import GuessTheNumber
from .heads_or_tails import HeadsOrTails
from .roll_the_dice import RollTheDice


class GameLoader:
    """
    Manages the game library and provides random game selection.

    Maintains a collection of available games and provides methods
    to randomly select and instantiate games for play sessions.
    """

    # Available games in the library
    game_library = [GuessTheNumber, HeadsOrTails, RollTheDice]

    @staticmethod
    def pick_random_game():
        """
        Randomly select and instantiate a game from the library.

        Returns:
            AbstractGame: A new instance of a randomly selected game
        """
        game_choice = choice(GameLoader.game_library)
        return game_choice()

    @staticmethod
    def get_available_games():
        """
        Get a list of all available game classes.

        Returns:
            list: List of game classes available in the library
        """
        return GameLoader.game_library.copy()

    @staticmethod
    def get_game_count():
        """
        Get the total number of available games.

        Returns:
            int: Number of games in the library
        """
        return len(GameLoader.game_library)
