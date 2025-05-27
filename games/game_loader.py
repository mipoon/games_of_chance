from random import choice

from .guess_the_number import GuessTheNumber
from .heads_or_tails import HeadsOrTails
from .roll_the_dice import RollTheDice


class GameLoader:

    game_library = [GuessTheNumber, HeadsOrTails, RollTheDice]
    # # could import AbstractGame and use the line below instead but pylint hates that the concrete class imports don't get used
    # game_library = [v for k, v in globals().items() if isinstance(v, type) and issubclass(v, AbstractGame) and v is not AbstractGame]

    @staticmethod
    def pick_random_game():
        game_choice = choice(GameLoader.game_library)
        return game_choice()
