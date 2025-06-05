"""
Prize Booth Module

Manages the prize system where players can spend tokens to win prizes
of various rarities with customizable probability modifiers.
"""

from random import choice
from time import sleep
from .player import Player


class PrizeBooth:
    """
    Manages the prize booth where players spend tokens to win prizes.

    Handles rarity probability calculations, prize selection, and duplicate
    prize refunds based on rarity-specific refund rates.
    """

    def __init__(self, player: Player) -> None:
        """
        Initialize the prize booth with a player.

        Args:
            player: The player who will be spending tokens
        """
        self.user = player

    def spend_tokens(self) -> None:
        """
        Main prize booth interaction loop.

        Allows players to spend tokens on prizes while they have sufficient
        funds (minimum 20 tokens required). Handles rarity selection,
        prize rolling, and duplicate refunds.
        """
        while self.user.tokens >= 20:
            # Spend for rarity enhancement
            while True:
                try:
                    spend_tokens = int(
                        input(
                            "\nEnter an amount of tokens\n"
                            "Every 3 tokens grants +1% chance of rolling your desired rarity: "
                        )
                    )
                    if spend_tokens < 0:
                        print("You cannot spend a negative amount of tokens.")
                        continue

                    user_rarity = input(
                        "'Common'\n'Odd'\n'Rare'\n'Epic'\n'Legendary'\n\n"
                        "Enter your desired rarity, or 'None': "
                    ).lower()

                    if user_rarity not in [
                        "common", "odd", "rare", "epic", "legendary", "none"
                    ]:
                        print("\nYou must enter a valid rarity\n")
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

            # Prize rolling phase
            print("Rolling for prize...")
            sleep(2)
            prize = self.select_prize(rarity)
            self.user.tokens -= 20
            print(f"You won a {rarity} {prize}")

            # Handle duplicate prizes
            refunded_tokens = self.refund_rerolls(prize, rarity)
            self.user.tokens += refunded_tokens
            if refunded_tokens == 0:
                self.user.add_prize(prize, rarity)

            print(f"\nYou have {self.user.tokens} tokens left.\n")

            # Continue playing prompt
            while True:
                user_play = input(
                    "Enter 'continue' to keep going, or 'exit' to finish playing: "
                ).lower()
                if user_play not in ("continue", "exit"):
                    print("Invalid response\n")
                else:
                    break
            if user_play == "exit":
                break

    def spend_for_rarity(self, user_rarity: str, tokens: int) -> tuple[str, int]:
        """
        Calculate rarity based on tokens spent and desired rarity.

        Args:
            user_rarity: Desired rarity category or 'none'
            tokens: Number of tokens to spend on rarity enhancement

        Returns:
            tuple: (actual_rarity_rolled, extra_tokens_refunded)
        """
        add_percent = tokens // 3
        extra = tokens % 3

        # Base rarity thresholds
        common, odd, rare, epic, legendary = 35, 60, 80, 95, 100
        roll_rarity = list(range(1, 101 + add_percent))

        # Adjust thresholds based on desired rarity
        if user_rarity == "common":
            common += add_percent
            odd += add_percent
            rare += add_percent
            epic += add_percent
            legendary += add_percent
        elif user_rarity == "odd":
            odd += add_percent
            rare += add_percent
            epic += add_percent
            legendary += add_percent
        elif user_rarity == "rare":
            rare += add_percent
            epic += add_percent
            legendary += add_percent
        elif user_rarity == "epic":
            epic += add_percent
            legendary += add_percent
        elif user_rarity == "legendary":
            legendary += add_percent

        roll = choice(roll_rarity)

        # Determine final rarity
        if roll <= common:
            rarity = "common"
        elif roll <= odd:
            rarity = "odd"
        elif roll <= rare:
            rarity = "rare"
        elif roll <= epic:
            rarity = "epic"
        else:
            rarity = "legendary"

        print(f"Roll: {roll}")
        print(f"Rarity: {rarity}")
        return rarity, extra

    def select_prize(self, rarity: str) -> str:
        """
        Randomly select a prize from the specified rarity category.

        Args:
            rarity: The rarity category to select from

        Returns:
            str: The selected prize name

        Raises:
            ValueError: If rarity is not a valid category
        """
        # Prize collections by rarity
        prize_pools = {
            "common": [
                "Cat", "Dog", "Gerbil", "Guinea Pig",
                "Hamster", "Mouse", "Pig", "Starfish"
            ],
            "odd": [
                "Bird", "Chicken", "Fish", "Lizard",
                "Snake", "Spider", "Turkey"
            ],
            "rare": [
                "Ferret", "Hedgehog", "Owl", "Shrimp", "Turtle"
            ],
            "epic": [
                "Butterfly", "Crab", "Duck", "Frog"
            ],
            "legendary": [
                "Crocodile", "Elephant", "Toad"
            ]
        }

        if rarity not in prize_pools:
            raise ValueError(f"Invalid prize rarity: {rarity}")

        return choice(prize_pools[rarity])

    def refund_rerolls(self, prize: str, rarity: str) -> int:
        """
        Calculate refund for duplicate prizes based on rarity.

        Args:
            prize: The prize that was won
            rarity: The rarity category of the prize

        Returns:
            int: Number of tokens to refund (0 if not a duplicate)
        """
        refund_rates = {
            "common": 3,
            "odd": 5,
            "rare": 7,
            "epic": 10,
            "legendary": 20
        }

        rarity_categories = ["common", "odd", "rare", "epic", "legendary"]
        rarity_index = rarity_categories.index(rarity)

        if prize in self.user.prizes[rarity_index]:
            refund_amount = refund_rates[rarity]
            print(f"You already own this prize, refunding {refund_amount} tokens")
            return refund_amount

        return 0
