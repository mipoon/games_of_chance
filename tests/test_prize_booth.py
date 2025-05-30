from unittest.mock import patch
import pytest

# pylint: disable=redefined-outer-name

from prize_booth import PrizeBooth
from player import Player


@pytest.fixture()
def fixture_prize_booth():
    test_player = Player()
    test_player.add_tokens(300)
    test_player.add_prize("duck", "epic")
    test_prize_booth = PrizeBooth(test_player)
    return test_prize_booth


@pytest.fixture()
def fixture_prize_booth_low_tokens():
    test_player = Player()
    test_player.add_tokens(10)  # Less than 20 tokens
    test_prize_booth = PrizeBooth(test_player)
    return test_prize_booth


def test_spend_tokens(fixture_prize_booth):
    with patch("builtins.input", side_effect=["100", "odd", "exit"]):
        prize_booth = fixture_prize_booth
        prize_booth.spend_tokens()


def test_spend_tokens_insufficient_tokens(fixture_prize_booth_low_tokens):
    """Test spend_tokens when user has insufficient tokens."""
    prize_booth = fixture_prize_booth_low_tokens
    # Should not enter the while loop since tokens < 20
    prize_booth.spend_tokens()
    assert prize_booth.user.tokens == 10


def test_spend_tokens_negative_input(fixture_prize_booth, capsys):
    """Test spend_tokens with negative token input."""
    with patch("builtins.input", side_effect=["-10", "50", "common", "exit"]):
        prize_booth = fixture_prize_booth
        prize_booth.spend_tokens()
    
    capture = capsys.readouterr()
    assert "You cannot spend a negative amount of tokens." in capture.out


def test_spend_tokens_invalid_rarity(fixture_prize_booth, capsys):
    """Test spend_tokens with invalid rarity input."""
    with patch("builtins.input", side_effect=["50", "invalid", "50", "common", "exit"]):
        with patch.object(fixture_prize_booth, 'select_prize', return_value="Cat"):
            with patch.object(fixture_prize_booth, 'refund_rerolls', return_value=0):
                prize_booth = fixture_prize_booth
                prize_booth.spend_tokens()
    
    capture = capsys.readouterr()
    assert "You must enter a valid rarity" in capture.out


def test_spend_tokens_value_error(fixture_prize_booth, capsys):
    """Test spend_tokens with non-numeric input."""
    with patch("builtins.input", side_effect=["abc", "50", "common", "exit"]):
        prize_booth = fixture_prize_booth
        prize_booth.spend_tokens()
    
    capture = capsys.readouterr()
    assert "ERROR: Enter a valid numerical value:" in capture.out


def test_spend_tokens_sufficient_after_spending(fixture_prize_booth):
    """Test spend_tokens when user has enough tokens after spending (covers line 50)."""
    with patch("builtins.input", side_effect=["50", "common", "exit"]):
        with patch.object(fixture_prize_booth, 'select_prize', return_value="Cat"):
            with patch.object(fixture_prize_booth, 'refund_rerolls', return_value=0):
                initial_tokens = fixture_prize_booth.user.tokens
                prize_booth = fixture_prize_booth
                prize_booth.spend_tokens()
                
                # Verify tokens were spent correctly 
                # 50 tokens spent for rarity, but 50 % 3 = 2 extra tokens returned
                # Then 20 tokens spent for prize
                expected_tokens = initial_tokens - 50 + 2 - 20  # spend 50, get 2 back, spend 20
                assert prize_booth.user.tokens == expected_tokens


# def test_spend_tokens_insufficient_after_spending():
#     """Test spend_tokens when user doesn't have enough tokens after spending."""
#     # Create a player with exactly 25 tokens
#     player = Player()
#     player.add_tokens(25)
#     prize_booth = PrizeBooth(player)
    
#     # Test the logic directly by checking the condition
#     # If user has 25 tokens, spends 10, gets 1 back, they have 16 tokens left
#     # 16 - 20 (cost of prize) = -4, which is < 20, so should trigger the message
#     tokens_after_spending = 25 - 10 + 1 - 20  # spend 10, get 1 back, spend 20 for prize
#     assert tokens_after_spending < 20


# def test_spend_tokens_insufficient_after_spending(capsys):
#     """Test spend_tokens when user doesn't have enough tokens after spending."""
#     # Create a player with exactly 25 tokens
#     player = Player()
#     player.add_tokens(25)
#     prize_booth = PrizeBooth(player)
    
#     # Mock input to simulate:
#     # 1. Spending 10 tokens on 'common' rarity, which makes (25 - 10 + 1) = 16 < 20 tokens, triggering line 50.
#     #    The inner loop continues without deducting tokens.
#     # 2. Spending 5 tokens on 'common' rarity, which makes (25 - 5 + 2) = 22 >= 20 tokens.
#     #    This allows the inner loop to break, tokens are deducted (25 - 5 + 2 = 22),
#     #    and then 20 tokens are spent for the prize (22 - 20 = 2).
#     # 3. 'exit' to gracefully exit the outer loop.
#     with patch("builtins.input", side_effect=["10", "common", "5", "common", "exit"]):
#         with patch.object(prize_booth, 'select_prize', return_value="Cat"):
#             with patch.object(prize_booth, 'refund_rerolls', return_value=0):
#                 prize_booth.spend_tokens()

#     # Capture the printed output
#     captured = capsys.readouterr()
    
#     # Assert that the specific message from line 50 was printed
#     assert "You do not have enough tokens to continue playing" in captured.out
    
#     # Assert the final token count
#     # After initial 10 tokens spend leading to the message, and then 5 tokens spend + prize:
#     # 25 (initial) - 5 (spent) + 2 (refunded from modulo) - 20 (prize cost) = 2 tokens
#     assert prize_booth.user.tokens == 2


def test_spend_tokens_insufficient_after_spending(fixture_prize_booth, capsys):
    """Test spend_tokens when user doesn't have enough tokens after spending."""
    # Set up player with exactly 25 tokens
    fixture_prize_booth.user.tokens = 25
    
    # Mock input and spend_for_rarity to return values that would leave insufficient tokens initially,
    # then provide a second set of inputs that allows the loop to successfully complete.
    with patch("builtins.input", side_effect=["10", "common", "5", "common", "exit"]):
        with patch.object(fixture_prize_booth, 'spend_for_rarity', return_value=("common", 1)):
            # Mock select_prize and refund_rerolls as they will be called after successful spend
            with patch.object(fixture_prize_booth, 'select_prize', return_value="Cat"):
                with patch.object(fixture_prize_booth, 'refund_rerolls', return_value=0):
                    prize_booth = fixture_prize_booth
                    prize_booth.spend_tokens()
    
    capture = capsys.readouterr()
    
    # Assert that the specific message from line 50 was printed during the first attempt
    assert "You do not have enough tokens to continue playing" in capture.out
    
    # Assert the final token count after the successful second attempt and prize spending
    # Initial tokens: 25
    # First attempt: "10" tokens, "common" rarity. Mocked spend_for_rarity returns (common, 1).
    # (25 - 10 + 1) = 16 < 20, so line 50 is hit, message printed, loop continues. Tokens remain 25.
    # Second attempt: "5" tokens, "common" rarity. Mocked spend_for_rarity returns (common, 1).
    # (25 - 5 + 1) = 21 >= 20, so loop breaks.
    # Tokens become: 25 (initial) - 5 (spent) + 1 (extras) = 21
    # Prize cost: 20 tokens.
    # Final tokens: 21 - 20 = 1
    assert prize_booth.user.tokens == 1


def test_spend_tokens_continue_playing(fixture_prize_booth):
    """Test spend_tokens with continue option."""
    with patch("builtins.input", side_effect=["50", "common", "continue", "50", "rare", "exit"]):
        with patch.object(fixture_prize_booth, 'select_prize', return_value="Cat"):
            with patch.object(fixture_prize_booth, 'refund_rerolls', return_value=0):
                prize_booth = fixture_prize_booth
                prize_booth.spend_tokens()


def test_spend_tokens_invalid_continue_response(fixture_prize_booth, capsys):
    """Test spend_tokens with invalid continue/exit response."""
    with patch("builtins.input", side_effect=["50", "common", "invalid", "exit"]):
        with patch.object(fixture_prize_booth, 'select_prize', return_value="Cat"):
            with patch.object(fixture_prize_booth, 'refund_rerolls', return_value=0):
                prize_booth = fixture_prize_booth
                prize_booth.spend_tokens()
    
    capture = capsys.readouterr()
    assert "Invalid response" in capture.out


def test_spend_for_rarity_common():
    """Test spend_for_rarity with common rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with patch('prize_booth.choice', return_value=30):  # Should be common
        rarity, extra = prize_booth.spend_for_rarity("common", 10)
    
    assert rarity == "common"
    assert extra == 1  # 10 % 3 = 1


def test_spend_for_rarity_odd():
    """Test spend_for_rarity with odd rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with patch('prize_booth.choice', return_value=50):  # Should be odd
        rarity, extra = prize_booth.spend_for_rarity("odd", 9)
    
    assert rarity == "odd"
    assert extra == 0  # 9 % 3 = 0


def test_spend_for_rarity_rare():
    """Test spend_for_rarity with rare rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with patch('prize_booth.choice', return_value=70):  # Should be rare
        rarity, extra = prize_booth.spend_for_rarity("rare", 12)
    
    assert rarity == "rare"
    assert extra == 0  # 12 % 3 = 0


def test_spend_for_rarity_epic():
    """Test spend_for_rarity with epic rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with patch('prize_booth.choice', return_value=90):  # Should be epic
        rarity, extra = prize_booth.spend_for_rarity("epic", 15)
    
    assert rarity == "epic"
    assert extra == 0  # 15 % 3 = 0


def test_spend_for_rarity_legendary():
    """Test spend_for_rarity with legendary rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with patch('prize_booth.choice', return_value=99):  # Should be legendary
        rarity, extra = prize_booth.spend_for_rarity("legendary", 18)
    
    assert rarity == "legendary"
    assert extra == 0  # 18 % 3 = 0


def test_spend_for_rarity_none():
    """Test spend_for_rarity with none rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with patch('prize_booth.choice', return_value=50):  # Should be odd with base percentages
        rarity, extra = prize_booth.spend_for_rarity("none", 6)
    
    assert rarity == "odd"
    assert extra == 0  # 6 % 3 = 0


def test_select_prize_common():
    """Test select_prize for common rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with patch('prize_booth.choice', return_value="Cat"):
        prize = prize_booth.select_prize("common")
    
    assert prize == "Cat"


def test_select_prize_odd():
    """Test select_prize for odd rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with patch('prize_booth.choice', return_value="Bird"):
        prize = prize_booth.select_prize("odd")
    
    assert prize == "Bird"


def test_select_prize_rare():
    """Test select_prize for rare rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with patch('prize_booth.choice', return_value="Owl"):
        prize = prize_booth.select_prize("rare")
    
    assert prize == "Owl"


def test_select_prize_epic():
    """Test select_prize for epic rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with patch('prize_booth.choice', return_value="Duck"):
        prize = prize_booth.select_prize("epic")
    
    assert prize == "Duck"


def test_select_prize_legendary():
    """Test select_prize for legendary rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with patch('prize_booth.choice', return_value="Elephant"):
        prize = prize_booth.select_prize("legendary")
    
    assert prize == "Elephant"


def test_select_prize_invalid_rarity():
    """Test select_prize with invalid rarity."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    with pytest.raises(ValueError, match="Invalid prize rarity"):
        prize_booth.select_prize("invalid")


def test_refund_rerolls_existing_prize(capsys):
    """Test refund_rerolls when prize already exists."""
    player = Player()
    player.add_prize("duck", "epic")
    prize_booth = PrizeBooth(player)
    
    refund = prize_booth.refund_rerolls("duck", "epic")
    
    assert refund == 10
    capture = capsys.readouterr()
    assert "You already own this prize, refunding 10 tokens" in capture.out


def test_refund_rerolls_new_prize():
    """Test refund_rerolls when prize is new."""
    player = Player()
    prize_booth = PrizeBooth(player)
    
    refund = prize_booth.refund_rerolls("cat", "common")
    
    assert refund == 0


def test_refund_rerolls_all_rarities(capsys):
    """Test refund_rerolls for all rarity levels."""
    player = Player()
    player.add_prize("cat", "common")
    player.add_prize("bird", "odd")
    player.add_prize("owl", "rare")
    player.add_prize("duck", "epic")
    player.add_prize("elephant", "legendary")
    prize_booth = PrizeBooth(player)
    
    # Test each rarity refund amount
    assert prize_booth.refund_rerolls("cat", "common") == 3
    assert prize_booth.refund_rerolls("bird", "odd") == 5
    assert prize_booth.refund_rerolls("owl", "rare") == 7
    assert prize_booth.refund_rerolls("duck", "epic") == 10
    assert prize_booth.refund_rerolls("elephant", "legendary") == 20


def test_refund_rolls(fixture_prize_booth):
    """Test the existing refund_rolls test."""
    prize_booth = fixture_prize_booth
    assert prize_booth.refund_rerolls("duck", "epic") == 10
