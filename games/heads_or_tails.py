from random import choice
from .abstract_game import AbstractGame


class HeadsOrTails(AbstractGame):
    def _play_game(self):
        '''
        Flip a coin game.

        Args: (str) User's guess "heads" or "tails"
        Returns: (int) Tokens earned
        '''
        while True:
            user_guess = input(
                ("Guess 'heads' or 'tails'\nIf you're correct, you'll gain a lot of tokens!: ")).lower()
            if user_guess in ['heads', 'tails']:
                break
            print("Please enter 'heads' or 'tails'\n")

        base_tokens = 10
        coin = ["heads", "tails"]
        flip = choice(coin)

        if user_guess == flip:
            earned_tokens = base_tokens * 10
        else:
            earned_tokens = base_tokens * 2

        return earned_tokens
