from random import randint
from time import sleep
from .abstract_game import AbstractGame

class RollTheDice(AbstractGame):
    def _play_game(self):
        '''
        Roll the dice game.

        Args: None
        Returns: (int) Tokens earned
        '''
        print("You don't have to do anything here, just hope you have good luck!")

        base_tokens = 15
        roll1 = randint(1, 6)
        roll2 = randint(1, 6)

        print("Rolling...\n")
        sleep(3)

        multip = roll1 + roll2
        earned_tokens = base_tokens * multip
        print("You rolled a", multip)

        return earned_tokens
