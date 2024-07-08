from random import choice
from time import sleep

class PrizeBooth():

    def __init__(self, user) -> None:
        self.user = user


    def spend_tokens(self):
        '''
        Spend tokens on prizes

        Args: none
        Returns: None
        '''
        while self.user.tokens >= 20:
            # Spend for rarity
            while True:
                try:
                    # Enter tokens
                    spend_tokens = int(input(
                        "\nEnter an amount of tokens\nEvery 3 tokens grants +1% chance of rolling your desired rarity: "))
                    if spend_tokens < 0:
                        print("You cannot spend a negative amount of tokens.")
                        continue
                    # Enter desired rarity
                    user_rarity = input(
                        "'Common'\n'Odd'\n'Rare'\n'Epic'\n'Legendary'\n\nEnter your desired rarity, or 'None': ").lower()
                    if user_rarity not in ['common', 'odd', 'rare', 'epic', 'legendary', 'none']:
                        print("\nYou must enter a valid rarity\n")
                    # If the user enters too many tokens
                    else:
                        rarity, extras = self.spend_for_rarity(
                            user_rarity, spend_tokens)
                        if (self.user.tokens - spend_tokens + extras) < 20:
                            print(
                                "You do not have enough tokens to continue playing")
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
                self.user.append_prizes(prize, rarity)

            print("\nYou have", self.user.tokens, "tokens left.\n")

            # Want to keep playing?
            while True:
                user_play = input(
                    "Enter 'continue' to keep going, or 'exit' to finish playing: ").lower()
                if user_play not in ('continue', 'exit'):
                    print("Invalid response\n")
                else:
                    break
            if user_play == 'exit':
                break

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
        Randomly select prize from rarity prize list selected

        Args: rarity from spend_for_rarity

        Returns: selected prize
        '''
        # Prize Lists:
        common = ["Cat", "Dog", "Gerbil", "Guinea Pig",
                  "Hamster", "Mouse", "Pig", "Starfish"]

        odd = ["Bird", "Chicken", "Fish",
               "Lizard", "Snake", "Spider", "Turkey"]

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

    # Find rerolls
    def refund_rerolls(self, prize, rarity):
        '''
        Refund tokens if prize is already owned.

        Args:
            prize: (str) Prize just earned
            rarity: (str) Rarity of prize
        Returns: (int) Refunded tokens
        '''
        # 'Inspired' by ChatGPT's work on append_prizes()
        refund_amounts = [['common', 3], ['odd', 5], [
            'rare', 7], ['epic', 10], ['legendary', 20]]
        rarity_index = ['common', 'odd', 'rare',
                        'epic', 'legendary'].index(rarity)
        if prize in self.user.prizes[rarity_index]:
            print(f"You already own this prize, refunding {
                  refund_amounts[rarity_index][1]} tokens")
            return refund_amounts[rarity_index][1]
        return 0
