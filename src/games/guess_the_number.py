"""
Guess the Number Game

A number guessing game where players earn more tokens for being farther
from the correct answer, creating an interesting risk/reward dynamic.
"""

from random import randint
from .abstract_game import AbstractGame


class GuessTheNumber(AbstractGame):
    """
    Number guessing game with inverse scoring.

    Players guess a number between 1-10, and earn more tokens the farther
    their guess is from the actual number. This creates a unique strategic
    element where being wrong is actually better.
    """

    def _play_game(self) -> int:
        """
        Execute the guess the number game logic.

        Prompts the player to guess a number between 1-10, generates a random
        target number, and calculates tokens based on the distance between
        the guess and the target.

        Returns:
            int: Number of tokens earned based on guess accuracy (inverse)
        """
        # Get valid user input
        while True:
            try:
                user_guess = int(
                    input(
                        "Guess the number 1 - 10\n"
                        "The FARTHER you are, the more tokens you'll earn!: "
                    )
                )
                if 1 <= user_guess <= 10:
                    break
                print("Please enter a number between 1 and 10")
            except ValueError:
                print("Please enter a numerical value\n")

        # Generate target number and calculate tokens
        base_tokens = 15
        target_number = randint(1, 10)
        distance = abs(target_number - user_guess)
        multiplier = distance + 1  # +1 ensures minimum 1x multiplier
        earned_tokens = base_tokens * multiplier

        # Display results
        print(f"The number was: {target_number}")
        print(f"Your guess: {user_guess}")
        print(f"Distance: {distance}")
        print(f"Multiplier: {multiplier}x")

        return earned_tokens
