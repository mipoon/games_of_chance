"""
Abstract Game Module

Defines the base interface and common functionality for all games
in the Games of Chance application.
"""

from abc import ABC, abstractmethod


class AbstractGame(ABC):
    """
    Abstract base class for all games in the application.

    Provides common token management functionality and defines the
    interface that all concrete games must implement.
    """

    def __init__(self) -> None:
        """Initialize a new game instance with zero tokens."""
        super().__init__()
        self._tokens = 0

    def add_tokens(self, number_of_tokens: int) -> None:
        """
        Add tokens to the game's token count.

        Args:
            number_of_tokens: Number of tokens to add
        """
        self._tokens += number_of_tokens

    @abstractmethod
    def _play_game(self) -> int:
        """
        Implement the core game logic in concrete classes.

        This method should contain the main game interaction and
        return the number of tokens earned from playing.

        Returns:
            int: Number of tokens earned from the game
        """

    def play(self) -> int:
        """
        Execute the game and handle token rewards.

        Calls the concrete game implementation, displays results,
        and manages token accumulation.

        Returns:
            int: Total tokens accumulated by this game instance
        """
        earned_tokens = self._play_game()
        print(f"Tokens earned: {earned_tokens}\n")
        self.add_tokens(earned_tokens)
        return self._tokens

    def get_tokens(self) -> int:
        """
        Get the current token count for this game instance.

        Returns:
            int: Current number of tokens
        """
        return self._tokens

    def reset_tokens(self) -> None:
        """Reset the token count to zero."""
        self._tokens = 0
