from time import sleep
from prize_booth import PrizeBooth
from user import User
from games.game_loader import GameLoader


class PlaySession():
    def __init__(self) -> None:
        self.user = User()
        self.prize_booth = PrizeBooth(self.user)

    def clear_output(self):
        '''
        Hacky way to simulate clearing the output screen

        Args: None
        Returns: None
        '''
        print("\n" * 100)

    def run_session(self):
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
        print("\nGood luck and have fun!")

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
            self.user.tokens += earned_tokens

        sleep(3)
        self.clear_output()
        print("You have", self.user.tokens, "tokens\n")


    # Print 'final results':
    def final_results(self):
        '''
        Display final results.

        Args: none
        Returns: None
        '''
        self.clear_output()
        print(50 * "-")
        print("\nPrizes earned:\n")

        # ChatGPT helped fix the function, using an index counter in a loop
        index = 0
        categories = ['Common', 'Odd', 'Rare', 'Epic', 'Legendary']
        for row in self.user.prizes:
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
        print("\nThanks for playing!\n")
