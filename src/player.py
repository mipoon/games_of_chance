"""
Player Module

Manages player data including name, tokens, and prize collections
for the Games of Chance application.
"""


class Player:
    """
    Represents a player in the Games of Chance application.

    Manages player state including name, token balance, and prize collections
    organized by rarity categories.
    """

    def __init__(self) -> None:
        """
        Initialize a new player with default values.

        Creates a player with default name, zero tokens, and empty prize lists
        for each rarity category (common, odd, rare, epic, legendary).
        """
        self.name = "Test Player"
        self.tokens = 0
        self.prizes = [[], [], [], [], []]  # [common, odd, rare, epic, legendary]

    def add_tokens(self, tokens: int) -> None:
        """
        Add tokens to the player's balance.

        Args:
            tokens: Number of tokens to add (must be positive)
        """
        if tokens > 0:
            self.tokens += tokens

    def subtract_tokens(self, tokens: int) -> bool:
        """
        Subtract tokens from the player's balance if sufficient funds exist.

        Args:
            tokens: Number of tokens to subtract

        Returns:
            bool: True if tokens were successfully subtracted, False if insufficient funds
        """
        if tokens <= self.tokens:
            self.tokens -= tokens
            return True
        return False

    def add_prize(self, prize: str, rarity: str) -> None:
        """
        Add a prize to the player's collection in the appropriate rarity category.

        Args:
            prize: Name of the prize to add
            rarity: Rarity category ('common', 'odd', 'rare', 'epic', 'legendary')

        Raises:
            ValueError: If rarity is not a valid category
        """
        rarity_categories = ["common", "odd", "rare", "epic", "legendary"]

        if rarity.lower() not in rarity_categories:
            raise ValueError(f"Invalid rarity '{rarity}'. Must be one of: {rarity_categories}")

        rarity_index = rarity_categories.index(rarity.lower())
        self.prizes[rarity_index].append(prize)
        self.prizes[rarity_index].sort()

    def has_prize(self, prize: str, rarity: str) -> bool:
        """
        Check if the player already owns a specific prize.

        Args:
            prize: Name of the prize to check
            rarity: Rarity category of the prize

        Returns:
            bool: True if player owns the prize, False otherwise
        """
        rarity_categories = ["common", "odd", "rare", "epic", "legendary"]

        if rarity.lower() not in rarity_categories:
            return False

        rarity_index = rarity_categories.index(rarity.lower())
        return prize in self.prizes[rarity_index]

    def get_total_prizes(self) -> int:
        """
        Get the total number of prizes owned by the player.

        Returns:
            int: Total count of all prizes across all rarity categories
        """
        return sum(len(category) for category in self.prizes)

    def __str__(self) -> str:
        """
        Return a string representation of the player.

        Returns:
            str: Player information including name, tokens, and prize count
        """
        total_prizes = self.get_total_prizes()
        return f"Player: {self.name}, Tokens: {self.tokens}, Total Prizes: {total_prizes}"
