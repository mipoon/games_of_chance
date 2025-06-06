"""
Tests for database configuration module.
"""

from unittest.mock import patch, Mock
from src.database.database import init_db, get_db_session, close_db, SessionLocal, engine


def test_init_db():
    """Test database initialization."""
    with patch('src.database.database.Base') as mock_base:
        init_db()
        mock_base.metadata.create_all.assert_called_once_with(bind=engine)


def test_get_db_session():
    """Test getting database session."""
    with patch('src.database.database.SessionLocal') as mock_session_local:
        mock_session = Mock()
        mock_session_local.return_value = mock_session

        session = get_db_session()

        assert session == mock_session
        mock_session_local.assert_called_once()


def test_close_db():
    """Test closing database connections."""
    with patch('src.database.database.engine') as mock_engine:
        close_db()
        mock_engine.dispose.assert_called_once()


def test_session_local_exists():
    """Test that SessionLocal is properly configured."""
    assert SessionLocal is not None


def test_engine_exists():
    """Test that engine is properly configured."""
    assert engine is not None
