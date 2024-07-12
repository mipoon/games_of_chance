import pytest
from user import User

@pytest.fixture
def user():
    return User()

def test_user_initialized(user):
    assert user.username == "Test User"
    assert user.tokens == 0
    assert user.prizes == [[], [], [], [], []]

def test_add_tokens(user):
    user.add_tokens(10)
    assert user.tokens == 10

def test_subtract_tokens(user):
    user.tokens = 30
    user.subtract_tokens(5)
    assert user.tokens == 25

def test_subtract_tokens_invalid(user):
    user.tokens = 30
    assert(user.subtract_tokens(31) == False)
    assert user.tokens == 30

def test_add_prize(user):
    user.add_prize('alligator', 'odd')
    user.add_prize('owl', 'common')
    user.add_prize('turtle', 'odd')
    print(user.prizes[1])
    assert user.prizes[1] == ['alligator', 'turtle']
    assert user.prizes[0] == ['owl']
    # TODO: better unit tests. E.g., mock append and sort, assert on call frequency
