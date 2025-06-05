"""
Heads or Tails Game

A classic coin flip guessing game with high rewards for correct guesses
and consolation prizes for incorrect ones.
"""

from random import choice
from .abstract_game import AbstractGame


class HeadsOrTails(AbstractGame):
    """
    Coin flip guessing game.
    
    Players guess the outcome of a coin flip and receive significant
    token rewards for correct guesses, with smaller consolation prizes
    for incorrect guesses.
    """
    
    def _play_game(self) -> int:
        """
        Execute the heads or tails game logic.
        
        Prompts the player to guess heads or tails, simulates a coin flip,
        and awards tokens based on whether the guess was correct.
        
        Returns:
            int: Number of tokens earned (high for correct, low for incorrect)
        """
        # Get valid user input
        while True:
            user_guess = input(
                "Guess 'heads' or 'tails'\n"
                "If you're correct, you'll gain a lot of tokens!: "
            ).lower().strip()
            
            if user_guess in ["heads", "tails"]:
                break
            print("Please enter 'heads' or 'tails'\n")

        # Simulate coin flip
        base_tokens = 10
        coin_options = ["heads", "tails"]
        flip_result = choice(coin_options)

        # Calculate tokens based on result
        if user_guess == flip_result:
            earned_tokens = base_tokens * 10  # Big reward for correct guess
            result_message = "Correct! You win big!"
        else:
            earned_tokens = base_tokens * 2   # Consolation prize
            result_message = "Wrong, but you still get some tokens!"

        # Display results
        print(f"The coin landed on: {flip_result}")
        print(f"Your guess: {user_guess}")
        print(result_message)

        return earned_tokens
