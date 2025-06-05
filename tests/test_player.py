import pytest
from src.player import Player


@pytest.fixture(name="player")
def this_player():
    return Player()


def test_player_initialized(player):
    assert player.name == "Test Player"
    assert player.tokens == 0
    assert player.prizes == [[], [], [], [], []]


def test_add_tokens(player):
    player.add_tokens(10)
    assert player.tokens == 10


def test_subtract_tokens(player):
    player.tokens = 30
    player.subtract_tokens(5)
    assert player.tokens == 25


def test_subtract_tokens_invalid(player):
    player.tokens = 30
    assert player.subtract_tokens(31) is False
    assert player.tokens == 30


def test_add_prize(player):
    player.add_prize("alligator", "odd")
    player.add_prize("owl", "common")
    player.add_prize("turtle", "odd")
    print(player.prizes[1])
    assert player.prizes[1] == ["alligator", "turtle"]
    assert player.prizes[0] == ["owl"]
    # write better unit tests. E.g., mock append and sort, assert on call frequency
