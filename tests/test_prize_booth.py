from unittest.mock import patch
import pytest

from prize_booth import PrizeBooth
from player import Player

@pytest.fixture()
def fixture_prize_booth():
    test_player = Player()
    test_player.add_tokens(300)
    test_player.add_prize("duck", "epic")
    test_prize_booth = PrizeBooth(test_player)
    return test_prize_booth

def test_spend_tokens(capsys, fixture_prize_booth):
    with patch('builtins.input', side_effect=["100", "odd", "exit"]):
            prize_booth = fixture_prize_booth
            prize_booth.spend_tokens()

def test_refund_rolls(fixture_prize_booth):
     prize_booth = fixture_prize_booth
     assert prize_booth.refund_rerolls("duck", "epic") == 10
     