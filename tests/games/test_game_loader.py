from src.games.game_loader import GameLoader
from src.games.guess_the_number import GuessTheNumber
from src.games.heads_or_tails import HeadsOrTails
from src.games.roll_the_dice import RollTheDice


def test_pick_random_game():
    game = GameLoader.pick_random_game()
    assert isinstance(game, (GuessTheNumber, HeadsOrTails, RollTheDice))


def test_get_available_games():
    """Test getting list of available games."""
    games = GameLoader.get_available_games()

    assert len(games) == 3
    assert GuessTheNumber in games
    assert HeadsOrTails in games
    assert RollTheDice in games

    # Ensure it returns a copy, not the original list
    games.append("fake_game")
    original_games = GameLoader.get_available_games()
    assert len(original_games) == 3


def test_get_game_count():
    """Test getting the count of available games."""
    count = GameLoader.get_game_count()
    assert count == 3
