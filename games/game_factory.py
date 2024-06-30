from random import randint
from .guess_the_number import GuessTheNumber
from .heads_or_tails import HeadsOrTails
from .roll_the_dice import RollTheDice


class GameFactory:

    @staticmethod
    def create_game(game_choice):
        if game_choice == 1:
            return GuessTheNumber()
        elif game_choice == 2:
            return HeadsOrTails()
        elif game_choice == 3:
            return RollTheDice()
        else:
            raise ValueError("Invalid game type specified.")

    @staticmethod
    def pick_random_game():
        game_choice = randint(1, 3)
        return GameFactory.create_game(game_choice)
