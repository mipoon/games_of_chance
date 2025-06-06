from unittest.mock import Mock, patch
from sqlite3 import IntegrityError
import pytest
from sqlalchemy.orm.exc import NoResultFound
from src.db import Database
from src.player import Player

# pylint: disable=redefined-outer-name


@pytest.fixture
def mock_session():
    """Create a mock session for database operations."""
    session = Mock()
    return session


@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = Mock()
    user.username = "test_user"
    user.tokens = 50
    user.prizes = [["Cat"], [], [], []]
    return user


@pytest.fixture
def database():
    """Create a Database instance."""
    with patch('src.db.init_db'):
        return Database()


def test_database_init(database):
    """Test Database initialization."""
    assert isinstance(database, Database)


def test_does_user_exist_true(database, mock_session, mock_user, capsys):
    """Test does_user_exist when user exists."""
    mock_session.query.return_value.filter.return_value.one.return_value = mock_user

    with patch('src.db.SessionLocal', return_value=mock_session):
        result = database.does_user_exist("test_user")

    assert result is True
    capture = capsys.readouterr()
    assert "User test_user exists." in capture.out


def test_does_user_exist_false(database, mock_session, capsys):
    """Test does_user_exist when user does not exist."""
    mock_session.query.return_value.filter.return_value.one.side_effect = NoResultFound()

    with patch('src.db.SessionLocal', return_value=mock_session):
        result = database.does_user_exist("nonexistent_user")

    assert result is False
    capture = capsys.readouterr()
    assert "User nonexistent_user does not exist." in capture.out


def test_get_user_data_success(database, mock_session, mock_user):
    """Test get_user_data when user exists."""
    mock_session.query.return_value.filter.return_value.one.return_value = mock_user

    with patch('src.db.SessionLocal', return_value=mock_session):
        result = database.get_user_data("test_user")

    expected = {"tokens": 50, "prizes": [["Cat"], [], [], []]}
    assert result == expected


def test_get_user_data_not_found(database, mock_session, capsys):
    """Test get_user_data when user does not exist."""
    mock_session.query.return_value.filter.return_value.one.side_effect = NoResultFound()

    with patch('src.db.SessionLocal', return_value=mock_session):
        result = database.get_user_data("nonexistent_user")

    assert result is None
    capture = capsys.readouterr()
    assert "No user found: nonexistent_user" in capture.out


def test_add_user_data_success(database, mock_session, capsys):
    """Test add_user_data successful creation."""
    mock_user = Mock()

    with patch('src.db.SessionLocal', return_value=mock_session), \
         patch('src.db.User', return_value=mock_user):
        result = database.add_user_data("new_user")

    mock_session.add.assert_called_once_with(mock_user)
    mock_session.commit.assert_called_once()
    assert result == mock_user
    capture = capsys.readouterr()
    assert "Adding new entry for user new_user" in capture.out
    assert "User new_user saved!" in capture.out


def test_add_user_data_integrity_error(database, mock_session, capsys):
    """Test add_user_data with IntegrityError."""
    mock_user = Mock()
    mock_session.commit.side_effect = IntegrityError("Duplicate entry", None, None)

    with patch('src.db.SessionLocal', return_value=mock_session), \
         patch('src.db.User', return_value=mock_user):
        result = database.add_user_data("duplicate_user")

    mock_session.rollback.assert_called_once()
    assert result is None
    capture = capsys.readouterr()
    assert "Session rolled back. Error:" in capture.out


def test_update_user_data(database, mock_session, mock_user, capsys):
    """Test update_user_data."""
    player = Player()
    player.name = "test_user"
    player.tokens = 100
    player.prizes = [["Dog"], ["Bird"], [], []]

    mock_session.query.return_value.filter.return_value.one.return_value = mock_user

    with patch('src.db.SessionLocal', return_value=mock_session):
        database.update_user_data(player)

    assert mock_user.tokens == 100
    assert mock_user.prizes == [["Dog"], ["Bird"], [], []]
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()
    capture = capsys.readouterr()
    assert "User data updated successfully." in capture.out


def test_update_user_data_user_not_found(database, mock_session, capsys):
    """Test update_user_data when user is not found."""
    player = Player()
    player.name = "nonexistent_user"
    player.tokens = 100
    player.prizes = [["Dog"], ["Bird"], [], []]

    mock_session.query.return_value.filter.return_value.one.side_effect = NoResultFound()

    with patch('src.db.SessionLocal', return_value=mock_session):
        database.update_user_data(player)

    mock_session.close.assert_called_once()
    capture = capsys.readouterr()
    assert "User nonexistent_user not found for update." in capture.out


def test_update_user_data_general_exception(database, mock_session, mock_user, capsys):
    """Test update_user_data when a general exception occurs."""
    player = Player()
    player.name = "test_user"
    player.tokens = 100
    player.prizes = [["Dog"], ["Bird"], [], []]

    mock_session.query.return_value.filter.return_value.one.return_value = mock_user
    mock_session.commit.side_effect = Exception("Database error")

    with patch('src.db.SessionLocal', return_value=mock_session):
        database.update_user_data(player)

    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
    capture = capsys.readouterr()
    assert "Error updating user data: Database error" in capture.out
