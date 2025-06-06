"""
Tests for abstract game module.
"""

import pytest
from src.games.abstract_game import AbstractGame


class ConcreteGame(AbstractGame):
    """Concrete implementation of AbstractGame for testing."""

    def __init__(self, tokens_to_earn=5):
        super().__init__()
        self.tokens_to_earn = tokens_to_earn

    def _play_game(self) -> int:
        """Simple implementation that returns a fixed number of tokens."""
        return self.tokens_to_earn


class TestAbstractGame:
    """Test cases for the AbstractGame class."""

    def test_initialization(self):
        """Test that abstract game initializes with zero tokens."""
        game = ConcreteGame()
        assert game.get_tokens() == 0

    def test_add_tokens(self):
        """Test adding tokens to the game."""
        game = ConcreteGame()
        game.add_tokens(10)
        assert game.get_tokens() == 10

        game.add_tokens(5)
        assert game.get_tokens() == 15

    def test_add_negative_tokens(self):
        """Test adding negative tokens."""
        game = ConcreteGame()
        game.add_tokens(10)
        game.add_tokens(-3)
        assert game.get_tokens() == 7

    def test_play_game(self, capsys):
        """Test playing the game and earning tokens."""
        game = ConcreteGame(tokens_to_earn=8)

        total_tokens = game.play()

        assert total_tokens == 8
        assert game.get_tokens() == 8

        # Check that the earned tokens message was printed
        capture = capsys.readouterr()
        assert "Tokens earned: 8" in capture.out

    def test_play_multiple_times(self):
        """Test playing the game multiple times accumulates tokens."""
        game = ConcreteGame(tokens_to_earn=3)

        # Play first time
        total_tokens = game.play()
        assert total_tokens == 3

        # Play second time
        total_tokens = game.play()
        assert total_tokens == 6

        # Play third time
        total_tokens = game.play()
        assert total_tokens == 9

        assert game.get_tokens() == 9

    def test_reset_tokens(self):
        """Test resetting tokens to zero."""
        game = ConcreteGame()
        game.add_tokens(20)
        assert game.get_tokens() == 20

        game.reset_tokens()
        assert game.get_tokens() == 0

    def test_get_tokens(self):
        """Test getting current token count."""
        game = ConcreteGame()
        assert game.get_tokens() == 0

        game.add_tokens(15)
        assert game.get_tokens() == 15

    def test_abstract_game_cannot_be_instantiated(self):
        """Test that AbstractGame cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AbstractGame()  # pylint: disable=abstract-class-instantiated

    def test_play_with_zero_tokens_earned(self, capsys):
        """Test playing game when no tokens are earned."""
        game = ConcreteGame(tokens_to_earn=0)

        total_tokens = game.play()

        assert total_tokens == 0
        assert game.get_tokens() == 0

        capture = capsys.readouterr()
        assert "Tokens earned: 0" in capture.out
