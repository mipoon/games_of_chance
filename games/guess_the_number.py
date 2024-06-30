from random import randint
from .abstract_game import AbstractGame


class GuessTheNumber(AbstractGame):

    def _play_game(self):
        '''
        Guess the number game.

        Args: (int) User's guessed number between 1 and 10
        Returns: (int) Tokens earned
        '''
        while True:
            try:
                user_guess = int(input(
                    "Guess the number 1 - 10\nThe FARTHER you are, the more tokens you'll earn!: "))
                if 1 <= user_guess <= 10:
                    break
                print("Please enter a number 1 - 10")
            except ValueError:
                print("Please enter a numerical value\n")

        base_tokens = 15
        num = randint(1, 10)
        multiplier = abs(num - user_guess) + 1
        earned_tokens = base_tokens * multiplier

        print("Tokens earned:", earned_tokens, "\n")
        self.add_tokens(earned_tokens)
