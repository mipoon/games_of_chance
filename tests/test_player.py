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


def test_add_prize_all_rarities(player):
    """Test adding prizes to all rarity categories."""
    player.add_prize("common_item", "common")
    player.add_prize("odd_item", "odd")
    player.add_prize("rare_item", "rare")
    player.add_prize("epic_item", "epic")
    player.add_prize("legendary_item", "legendary")

    assert "common_item" in player.prizes[0]
    assert "odd_item" in player.prizes[1]
    assert "rare_item" in player.prizes[2]
    assert "epic_item" in player.prizes[3]
    assert "legendary_item" in player.prizes[4]


def test_add_prize_invalid_rarity(player):
    """Test adding prize with invalid rarity raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        player.add_prize("invalid_item", "invalid_rarity")

    assert "Invalid rarity 'invalid_rarity'" in str(exc_info.value)


def test_add_prize_case_insensitive(player):
    """Test adding prize with different case rarities."""
    player.add_prize("item1", "COMMON")
    player.add_prize("item2", "Odd")
    player.add_prize("item3", "RARE")

    assert "item1" in player.prizes[0]
    assert "item2" in player.prizes[1]
    assert "item3" in player.prizes[2]


def test_has_prize_true(player):
    """Test has_prize returns True when player owns the prize."""
    player.add_prize("test_item", "common")

    assert player.has_prize("test_item", "common") is True


def test_has_prize_false(player):
    """Test has_prize returns False when player doesn't own the prize."""
    assert player.has_prize("nonexistent_item", "common") is False


def test_has_prize_invalid_rarity(player):
    """Test has_prize returns False for invalid rarity."""
    assert player.has_prize("any_item", "invalid_rarity") is False


def test_has_prize_case_insensitive(player):
    """Test has_prize works with different case rarities."""
    player.add_prize("test_item", "common")

    assert player.has_prize("test_item", "COMMON") is True
    assert player.has_prize("test_item", "Common") is True


def test_get_total_prizes(player):
    """Test get_total_prizes returns correct count."""
    player.add_prize("item1", "common")
    player.add_prize("item2", "odd")
    player.add_prize("item3", "rare")

    assert player.get_total_prizes() == 3


def test_get_total_prizes_empty(player):
    """Test get_total_prizes returns 0 when no prizes."""
    assert player.get_total_prizes() == 0


def test_add_tokens_zero(player):
    """Test adding zero tokens doesn't change balance."""
    initial_tokens = player.tokens
    player.add_tokens(0)
    assert player.tokens == initial_tokens


def test_add_tokens_negative(player):
    """Test adding negative tokens doesn't change balance."""
    initial_tokens = player.tokens
    player.add_tokens(-10)
    assert player.tokens == initial_tokens


def test_subtract_tokens_exact_amount(player):
    """Test subtracting exact token amount."""
    player.tokens = 50
    result = player.subtract_tokens(50)
    assert result is True
    assert player.tokens == 0


def test_str_representation(player):
    """Test string representation of player."""
    player.name = "TestUser"
    player.tokens = 100
    player.add_prize("item1", "common")
    player.add_prize("item2", "rare")

    str_repr = str(player)

    assert "TestUser" in str_repr
    assert "100" in str_repr
    assert "2" in str_repr  # Total prizes
