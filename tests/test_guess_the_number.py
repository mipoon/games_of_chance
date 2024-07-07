import pytest
from unittest.mock import MagicMock, patch
from games.guess_the_number import GuessTheNumber

@pytest.fixture
def game():
    return GuessTheNumber()

def test_guess_the_number_valid_input(game):
    # Mock the input function to simulate user input
    with patch('builtins.input', return_value='5'):
        # Mock the randint function to return a consistent number
        with patch('games.guess_the_number.randint', return_value=10):
            earned_tokens = game.play()

            # The multiplier is abs(num - user_guess) + 1 = abs(10 - 5) + 1 = 6
            # The earned tokens are base_tokens * multiplier = 15 * 6 = 90
            assert earned_tokens == 90

def test_play_game_value_error_handled_gracefully(capsys, game):
    # Mock the input function to simulate user input
    with patch('builtins.input', side_effect=['a', '11', '10']):
        # Mock the randint function to return a consistent number
        with patch('games.guess_the_number.randint', return_value=10):
            game = GuessTheNumber()
            earned_tokens = game.play()

            # Capture the printed output
            captured = capsys.readouterr()
            assert "Please enter a numerical value" in captured.out
            assert "Please enter a number 1 - 10" in captured.out

            # The multiplier is abs(num - user_guess) + 1 = abs(10 - 10) + 1 = 0
            # The earned tokens are base_tokens * multiplier = 15 * 1 = 15
            assert earned_tokens == 15
