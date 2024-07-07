from random import choice
from time import sleep
from user import User
from games.game_factory import GameFactory

class PlaySession():
    def __init__(self) -> None:
        self.user = User()


    def run_session(self):
        self.display_instructions()
        self.play_games()
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

    def clear_output(self):
        '''
        Hacky way to simulate clearing the output screen

        Args: None
        Returns: None
        '''
        print("\n" * 100)


    def play_games(self):
        '''
        Main function to run the game

        Args: none
        Returns: none
        '''
        # Money Games
        for _ in range(3):
            game = GameFactory.pick_random_game()
            earned_tokens = game.play()
            self.user.tokens += earned_tokens

        sleep(3)
        self.clear_output()
        print("You have", self.user.tokens, "tokens\n")

        while self.user.tokens >= 20:
            # Spend for rarity
            while True:
                try:
                    # Enter tokens
                    spend_tokens = int(input("\nEnter an amount of tokens\nEvery 3 tokens grants +1% chance of rolling your desired rarity: "))
                    if spend_tokens < 0:
                        print("You cannot spend a negative amount of tokens.")
                        continue
                    # Enter desired rarity
                    user_rarity = input("'Common'\n'Odd'\n'Rare'\n'Epic'\n'Legendary'\n\nEnter your desired rarity, or 'None': ").lower()
                    if user_rarity not in ['common', 'odd', 'rare', 'epic', 'legendary', 'none']:
                        print("\nYou must enter a valid rarity\n")
                    # If the user enters too many tokens
                    else:
                        rarity, extras = self.spend_for_rarity(user_rarity, spend_tokens)
                        if (self.user.tokens - spend_tokens + extras) < 20:
                            print("You do not have enough tokens to continue playing")
                        else:
                            self.user.tokens -= spend_tokens
                            self.user.tokens += extras
                            break
                except ValueError:
                    print("\nERROR: Enter a valid numerical value:\n")

            # Spending for prizes
            print("Rolling for prize...")
            sleep(2)
            prize = self.select_prize(rarity)
            self.user.tokens -= 20
            print("You won a", rarity, prize)

            refunded_tokens = self.refund_rerolls(prize, rarity)
            self.user.tokens += refunded_tokens
            if refunded_tokens == 0:
                self.append_prizes(prize, rarity)

            print("\nYou have", self.user.tokens, "tokens left.\n")

            # Want to keep playing?
            while True:
                user_play = input("Enter 'continue' to keep going, or 'exit' to finish playing: ").lower()
                if user_play not in ('continue', 'exit'):
                    print("Invalid response\n")
                else:
                    break
            if user_play == 'exit':
                self.clear_output()
                break


    # Print 'final results':
    def final_results(self):
        '''
        Display final results.

        Args:
            self.user.prizes: (list) User's list of prizes
        Returns: None
        '''
        print(50 * "-")
        print("\nPrizes earned:\n")

        # ChatGPT helped fix the function, using an index counter in a loop
        index = 0
        categories = ['Common', 'Odd', 'Rare', 'Epic', 'Legendary']
        for row in self.user.prizes:
            print(f"{categories[index]} -", end = "  ")
            for col in row:
                print(f"{col}", end = ", ")

            print("\n")
            index += 1
        print(50 * "-")


    # Spend for rarity

    def spend_for_rarity(self, user_rarity, tokens):
        '''
        Spend tokens for a chance to increase rarity.

        Args:
            user_rarity: (str) Desired rarity
            tokens: (int) Amount of tokens to spend
        Returns:
            tuple (str, int): Selected rarity and extra tokens back to the user
        '''
        add_percent = tokens // 3
        extra = tokens % 3

        # Base percentages: Refactored by ChatGPT
        common, odd, rare, epic, legendary = 35, 60, 80, 95, 100
        roll_rarity = list(range(1, 101 + add_percent))

        # Alter percentages
        if user_rarity == 'common':
            common += add_percent
            odd += add_percent
            rare += add_percent
            epic += add_percent
            legendary += add_percent
        elif user_rarity == 'odd':
            odd += add_percent
            rare += add_percent
            epic += add_percent
            legendary += add_percent
        elif user_rarity == 'rare':
            rare += add_percent
            epic += add_percent
            legendary += add_percent
        elif user_rarity == 'epic':
            epic += add_percent
            legendary += add_percent
        elif user_rarity == 'legendary':
            legendary += add_percent

        roll = choice(roll_rarity)

        if roll <= common:
            rarity = 'common'
        elif roll <= odd:
            rarity = 'odd'
        elif roll <= rare:
            rarity = 'rare'
        elif roll <= epic:
            rarity = 'epic'
        else:
            rarity = 'legendary'

        print(roll)
        print(rarity)
        print(roll_rarity)
        return rarity, extra

    # Select prize

    def select_prize(self, rarity):
        '''
        Args: rarity from spend_for_rarity

        Randomly select prize from rarity prize list selected

        Returns: selected prize
        '''
        # Prize Lists:
        common = ["Cat", "Dog", "Gerbil", "Guinea Pig", "Hamster", "Mouse", "Pig", "Starfish"]

        odd = ["Bird", "Chicken", "Fish", "Lizard", "Snake", "Spider", "Turkey"]

        rare = ["Ferret", "Hedgehog", "Owl", "Shrimp", "Turtle"]

        epic = ["Butterfly", "Crab", "Duck", "Frog"]

        legendary = ["Crocodile", "Elephant", "Toad"]

        # Roll random prize
        if rarity == "common":
            prize = choice(common)
        elif rarity == "odd":
            prize = choice(odd)
        elif rarity == "rare":
            prize = choice(rare)
        elif rarity == "epic":
            prize = choice(epic)
        elif rarity == "legendary":
            prize = choice(legendary)
        else:
            raise ValueError("Invalid prize rarity")

        return prize

    # Add prizes to user's prize list
    def append_prizes(self, prize, rarity):
        """
        Add prize to user's list.

        Args:
            self.user.prizes: (list) User's list of prizes
            prize: (str) Prize to add
            rarity: (str) Rarity of the prize
        Returns: None
        """
        # Refactored by ChatGPT
        rarity_index = ['common', 'odd', 'rare', 'epic', 'legendary'].index(rarity)
        self.user.prizes[rarity_index].append(prize)
        self.user.prizes[rarity_index].sort()

    # Find rerolls
    def refund_rerolls(self, prize, rarity):
        '''
        Refund tokens if prize is already owned.

        Args:
            self.user.prizes: (list) User's list of prizes
            prize: (str) Prize just earned
            rarity: (str) Rarity of prize
        Returns: (int) Refunded tokens
        '''
        # 'Inspired' by ChatGPT's work on append_prizes()
        refund_amounts = [['common', 3], ['odd', 5], ['rare', 7], ['epic', 10], ['legendary', 20]]
        rarity_index = ['common', 'odd', 'rare', 'epic', 'legendary'].index(rarity)
        if prize in self.user.prizes[rarity_index]:
            print(f"You already own this prize, refunding {refund_amounts[rarity_index][1]} tokens")
            return refund_amounts[rarity_index][1]
        return 0


    def conclude(self):
        '''
        Conclude the play session. Display a concluding message and perform any cleanup

        Args: None
        Returns: None
        '''
        print("\nThanks for playing!\n")
