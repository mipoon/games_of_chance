"""
Database Configuration Module

Configures SQLAlchemy engine, session management, and database initialization
for the Games of Chance application.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# Database configuration
DATABASE_URL = "sqlite:///./game.db"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    Creates all tables defined in the models module if they don't exist.
    This function is safe to call multiple times.
    """
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """
    Get a database session with automatic cleanup.

    Returns a database session that should be used in a context manager
    or manually closed after use.

    Returns:
        Session: SQLAlchemy database session
    """
    return SessionLocal()


def close_db():
    """
    Close all database connections.

    Useful for cleanup during application shutdown.
    """
    engine.dispose()
