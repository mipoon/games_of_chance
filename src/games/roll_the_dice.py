"""
Roll the Dice Game

A pure luck-based game where players roll two dice and earn tokens
based on the sum of the dice rolls.
"""

from random import randint
from time import sleep
from .abstract_game import AbstractGame


class RollTheDice(AbstractGame):
    """
    Dice rolling game based purely on luck.
    
    Players automatically roll two six-sided dice and earn tokens
    based on the sum of the rolls. Higher sums result in more tokens.
    """
    
    def _play_game(self) -> int:
        """
        Execute the dice rolling game logic.
        
        Automatically rolls two dice and calculates tokens based on
        the sum. No player input required - pure luck game.
        
        Returns:
            int: Number of tokens earned based on dice sum
        """
        print("You don't have to do anything here, just hope you have good luck!")
        print("Rolling two dice...\n")
        
        # Simulate dice rolling with suspense
        sleep(2)
        
        # Roll two six-sided dice
        base_tokens = 15
        die1 = randint(1, 6)
        die2 = randint(1, 6)
        total_roll = die1 + die2
        
        # Calculate tokens (sum acts as multiplier)
        earned_tokens = base_tokens * total_roll
        
        # Display results
        print(f"Die 1: {die1}")
        print(f"Die 2: {die2}")
        print(f"Total: {total_roll}")
        print(f"Multiplier: {total_roll}x")
        
        return earned_tokens
