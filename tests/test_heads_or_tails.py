import pytest
from unittest.mock import patch
from games.heads_or_tails import HeadsOrTails

@pytest.fixture
def game():
    return HeadsOrTails()

def test_play_with_correct_guess(game):
     with patch('builtins.input', return_value='heads'):
          with patch('games.heads_or_tails.choice', return_value='heads'):
               earned_tokens = game.play()
               assert earned_tokens == 100

def test_play_with_incorrect_guess(game):
     with patch('builtins.input', return_value='tails'):
          with patch('games.heads_or_tails.choice', return_value='heads'):
               earned_tokens = game.play()
               assert earned_tokens == 20

def test_invalid_guess(capsys, game):
     with patch('builtins.input', side_effect=['foo', 'tails']):
          with patch('games.heads_or_tails.choice', return_value='heads'):
            earned_tokens = game.play()
            captured = capsys.readouterr()
            assert "Please enter 'heads' or 'tails'\n" in captured.out
            assert earned_tokens == 20