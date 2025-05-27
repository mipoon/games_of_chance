from games.game_loader import GameLoader, GuessTheNumber, HeadsOrTails, RollTheDice


def test_pick_random_game():
    game = GameLoader.pick_random_game()
    assert isinstance(game, (GuessTheNumber, HeadsOrTails, RollTheDice))
