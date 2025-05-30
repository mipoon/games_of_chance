import pytest
from play_session import PlaySession

# pylint: disable=redefined-outer-name


@pytest.fixture()
def fixture_play_session():
    play_session = PlaySession()
    return play_session


def test_run_session(mocker, fixture_play_session):
    play_session = fixture_play_session
    mock_setup_player = mocker.patch.object(play_session, "setup_player")
    mock_display_instructions = mocker.patch.object(
        play_session, "display_instructions"
    )
    mock_play_games = mocker.patch.object(play_session, "play_games")
    mock_spend_token = mocker.patch.object(play_session.prize_booth, "spend_tokens")
    mock_final_results = mocker.patch.object(play_session, "final_results")
    mock_conclude = mocker.patch.object(play_session, "conclude")

    play_session.run_session()
    mock_setup_player.assert_called_once()
    mock_display_instructions.assert_called_once()
    mock_play_games.assert_called_once()
    mock_spend_token.assert_called_once()
    mock_final_results.assert_called_once()
    mock_conclude.assert_called_once()


def test_display_instructions(capsys):
    play_session = PlaySession()
    expected_output = (
        "\nWelcome to Games of Chance with Prizes!\n"
        "In this game, you'll play a series of mini-games to earn tokens, which you can then use to win prizes.\n"
        "\nHere's how it works:\n"
        "1. There will be three mini-games to earn tokens.\n"
        "2. The mini-games include guessing a number, flipping a coin, and rolling dice, which will be randomly selected.\n"
        "3. After earning tokens, you can spend them to try and win prizes of various rarities.\n"
        "4. You'll also be given a choice to spend tokens to increase your chances of getting a rarer prize.\n"
        "5. Prizes are categorized into common, odd, rare, epic, and legendary.\n"
        "6. If you roll a prize that you already own, you might get some tokens back as a refund.\n"
        "\nGood luck and have fun!\n\n"
    )
    play_session.display_instructions()
    capture = capsys.readouterr()
    assert capture.out == expected_output


def test_setup_existing_player(mocker, fixture_play_session, capsys):
    play_session = fixture_play_session
    mocker.patch("builtins.input", return_value="mocked input")
    mock_does_user_exist = mocker.patch.object(
        play_session.db, "does_user_exist", return_value=True
    )
    mock_get_user_data = mocker.patch.object(
        play_session.db,
        "get_user_data",
        return_value={"tokens": 50, "prizes": [["Cat"], [], [], []]},
    )

    play_session.setup_player()
    captured = capsys.readouterr()
    assert "Welcome back, mocked input! Let's play some more games!" in captured.out
    assert "Set up complete. You, mocked input, currently have 50 tokens, and your prize list is: [['Cat'], [], [], []]." in captured.out
    assert play_session.player.name == "mocked input"
    assert play_session.player.tokens == 50
    assert play_session.player.prizes == [["Cat"], [], [], []]
    mock_does_user_exist.assert_called_once()
    mock_get_user_data.assert_called_once()


def test_setup_new_player(mocker, fixture_play_session, capsys):
    play_session = fixture_play_session
    mocker.patch("builtins.input", return_value="mocked input")
    mock_does_user_exist = mocker.patch.object(
        play_session.db, "does_user_exist", return_value=False
    )
    mock_add_user_data = mocker.patch.object(play_session.db, "add_user_data")

    play_session.setup_player()
    captured = capsys.readouterr()
    assert "Welcome, mocked input! Let's play some games!" in captured.out
    assert "Set up complete. You, mocked input, currently have 30 tokens, and your prize list is: [[], [], [], []]." in captured.out
    assert play_session.player.name == "mocked input"
    assert play_session.player.tokens == 30
    assert play_session.player.prizes == [[], [], [], []]
    mock_does_user_exist.assert_called_once()
    mock_add_user_data.assert_called_once()


def test_play_games(capsys, mocker, fixture_play_session):
    play_session = fixture_play_session
    # Mock the pick_random_game method to return a mock game object
    mock_game = mocker.Mock()
    mocker.patch("play_session.GameLoader.pick_random_game", return_value=mock_game)

    # Mock the play method on the mock game object to return 10 tokens each time it is called
    mock_game.play = mocker.Mock(return_value=10)
    play_session.player.tokens = 0
    play_session.play_games()
    capture = capsys.readouterr()
    assert "You have 30 tokens\n" in capture.out



def test_final_results(capsys, fixture_play_session):
    play_session = fixture_play_session
    play_session.player.prizes = [["common_prize"], ["odd_prize"], [], [], ["legendary_prize"]]
    play_session.final_results()
    captured = capsys.readouterr()
    assert "Common -  common_prize," in captured.out
    assert "Odd -  odd_prize," in captured.out
    assert "Legendary -  legendary_prize," in captured.out


def test_conclude(mocker, fixture_play_session, capsys):
    play_session = fixture_play_session
    mock_update = mocker.patch.object(play_session.db, "update_user_data")
    play_session.conclude()
    captured = capsys.readouterr()
    assert "\nThanks for playing!\n" in captured.out
    mock_update.assert_called_once_with(play_session.player)
