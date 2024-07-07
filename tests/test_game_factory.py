import pytest
from games.game_factory import GameFactory, GuessTheNumber, HeadsOrTails, RollTheDice

def test_pick_random_game():
    game = GameFactory.pick_random_game()
    assert isinstance(game, (GuessTheNumber, HeadsOrTails, RollTheDice))
