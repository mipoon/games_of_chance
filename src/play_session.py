"""
Play Session Module

Manages the main game session flow including player setup, game execution,
and prize distribution for the Games of Chance application.
"""

from time import sleep
from .prize_booth import PrizeBooth
from .player import Player
from .db import Database
from .games.game_loader import GameLoader
from .helpers.clear_output import clear_output


class PlaySession:
    """
    Manages a complete game session from player setup to conclusion.
    
    Handles player authentication, game execution, prize distribution,
    and data persistence.
    """
    
    def __init__(self) -> None:
        """Initialize a new play session with database, player, and prize booth."""
        self.db = Database()
        self.player = Player()
        self.prize_booth = PrizeBooth(self.player)

    def run_session(self):
        """
        Execute a complete game session.
        
        Runs through the full game flow: setup, instructions, games,
        prize booth, results display, and cleanup.
        """
        self.setup_player()
        self.display_instructions()
        self.play_games()
        self.prize_booth.spend_tokens()
        self.final_results()
        self.conclude()

    def display_instructions(self):
        """Display comprehensive game instructions to the player."""
        print("\nWelcome to Games of Chance with Prizes!")
        print(
            "In this game, you'll play a series of mini-games to earn tokens, "
            "which you can then use to win prizes."
        )
        print("\nHere's how it works:")
        print("1. There will be three mini-games to earn tokens.")
        print(
            "2. The mini-games include guessing a number, flipping a coin, "
            "and rolling dice, which will be randomly selected."
        )
        print(
            "3. After earning tokens, you can spend them to try and win prizes "
            "of various rarities."
        )
        print(
            "4. You'll also be given a choice to spend tokens to increase your "
            "chances of getting a rarer prize."
        )
        print("5. Prizes are categorized into common, odd, rare, epic, and legendary.")
        print(
            "6. If you roll a prize that you already own, you might get some "
            "tokens back as a refund."
        )
        print("\nGood luck and have fun!\n")

    def setup_player(self):
        """
        Set up player data by loading existing player or creating new one.
        
        Prompts for player name and either loads existing data from database
        or creates a new player with default starting values.
        """
        input_name = input("Please enter your name: ")
        player_exists = self.db.does_user_exist(input_name)
        
        if player_exists:
            player_data = self.db.get_user_data(input_name)
            self.player.name = input_name
            self.player.tokens = player_data.get("tokens")
            self.player.prizes = player_data.get("prizes")
            print(f"Welcome back, {self.player.name}! Let's play some more games!")
        else:
            self.db.add_user_data(input_name)
            self.player.name = input_name
            self.player.tokens = 30
            self.player.prizes = [[], [], [], [], []]  # Fixed: should be 5 categories
            print(f"Welcome, {self.player.name}! Let's play some games!")
            
        print(
            f"Set up complete. You, {self.player.name}, currently have "
            f"{self.player.tokens} tokens, and your prize list is: {self.player.prizes}."
        )

    def play_games(self):
        """
        Execute the main gaming phase.
        
        Runs three randomly selected mini-games and accumulates tokens
        earned by the player.
        """
        for _ in range(3):
            game = GameLoader.pick_random_game()
            earned_tokens = game.play()
            self.player.tokens += earned_tokens

        sleep(3)
        clear_output()
        print(f"You have {self.player.tokens} tokens\n")

    def final_results(self):
        """Display the final results showing all prizes earned by category."""
        clear_output()
        print("-" * 50)
        print("\nPrizes earned:\n")

        categories = ["Common", "Odd", "Rare", "Epic", "Legendary"]
        for index, prize_category in enumerate(self.player.prizes):
            print(f"{categories[index]} - ", end="")
            if prize_category:
                print(", ".join(str(prize) for prize in prize_category))
            else:
                print("None")
        print("-" * 50)

    def conclude(self):
        """
        Conclude the play session.
        
        Saves player data to database and displays farewell message.
        """
        self.db.update_user_data(self.player)
        print("\nThanks for playing!\n")
