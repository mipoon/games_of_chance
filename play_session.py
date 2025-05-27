from time import sleep
from prize_booth import PrizeBooth
from player import Player
from db import Database
from games.game_loader import GameLoader
from helpers.clear_output import clear_output

class PlaySession():
    def __init__(self) -> None:
        self.db = Database()
        self.player = Player()
        self.prize_booth = PrizeBooth(self.player)

    def run_session(self):
        self.setup_player()
        self.display_instructions()
        self.play_games()
        self.prize_booth.spend_tokens()
        self.final_results()
        self.conclude()

    def display_instructions(self):
        '''
        Display game instructions.

        Args: None
        Returns: None
        '''
        print("\nWelcome to Games of Chance with Prizes!")
        print("In this game, you'll play a series of mini-games to earn tokens, which you can then use to win prizes.")
        print("\nHere's how it works:")
        print("1. There will be three mini-games to earn tokens.")
        print("2. The mini-games include guessing a number, flipping a coin, and rolling dice, which will be randomly selected.")
        print("3. After earning tokens, you can spend them to try and win prizes of various rarities.")
        print("4. You'll also be given a choice to spend tokens to increase your chances of getting a rarer prize.")
        print("5. Prizes are categorized into common, odd, rare, epic, and legendary.")
        print("6. If you roll a prize that you already own, you might get some tokens back as a refund.")
        print("\nGood luck and have fun!\n")

    def setup_player(self):
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
            self.player.prizes = [[], [], [], []]
            print(f"Welcome, {self.player.name}! Let's play some games!")
        print(f"Set up complete. You, {self.player.name}, currently have {self.player.tokens} tokens, and your prize list is: {self.player.prizes}.")

    def play_games(self):
        '''
        Main function to run the game

        Args: none
        Returns: none
        '''
        # Money Games
        for _ in range(3):
            game = GameLoader.pick_random_game()
            earned_tokens = game.play()
            self.player.tokens += earned_tokens

        sleep(3)
        clear_output()
        print("You have", self.player.tokens, "tokens\n")


    # Print 'final results':
    def final_results(self):
        '''
        Display final results.

        Args: none
        Returns: None
        '''
        clear_output()
        print(50 * "-")
        print("\nPrizes earned:\n")

        # ChatGPT helped fix the function, using an index counter in a loop
        index = 0
        categories = ['Common', 'Odd', 'Rare', 'Epic', 'Legendary']
        for row in self.player.prizes:
            print(f"{categories[index]} -", end="  ")
            for col in row:
                print(f"{col}", end=", ")

            print("\n")
            index += 1
        print(50 * "-")

    def conclude(self):
        '''
        Conclude the play session. Display a concluding message and perform any cleanup

        Args: None
        Returns: None
        '''
        self.db.update_user_data(self.player)
        print("\nThanks for playing!\n")
