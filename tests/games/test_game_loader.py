from src.games.game_loader import GameLoader
from src.games.guess_the_number import GuessTheNumber
from src.games.heads_or_tails import HeadsOrTails
from src.games.roll_the_dice import RollTheDice


def test_pick_random_game():
    game = GameLoader.pick_random_game()
    assert isinstance(game, (GuessTheNumber, HeadsOrTails, RollTheDice))
