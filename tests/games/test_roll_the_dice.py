from unittest.mock import patch
import pytest
from games.roll_the_dice import RollTheDice


@pytest.fixture(name="game")
def fixture_game():
    return RollTheDice()


def test_play_game(capsys, game):
    with patch('games.roll_the_dice.randint', side_effect=[1, 3]):
        with patch('games.roll_the_dice.sleep', return_value=None):
            earned_tokens = game.play()

            # Capture the printed output
            captured = capsys.readouterr()
            assert "You don't have to do anything here, just hope you have good luck!" in captured.out
            assert "You rolled a 4" in captured.out
            assert earned_tokens == 60


def test_play(game):
    with patch.object(game, '_play_game', return_value=30) as mock_play_game:
        game.play()
        mock_play_game.assert_called_once()
