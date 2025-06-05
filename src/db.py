"""
Database Module

Handles all database operations for the Games of Chance application
including user management, data persistence, and SQLAlchemy integration.
"""

from sqlite3 import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .database.database import SessionLocal, init_db
from .database.models import User
from .player import Player


class Database:
    """
    Database interface for managing user data and game state persistence.

    Provides methods for user authentication, data retrieval, and updates
    using SQLAlchemy ORM with SQLite backend.
    """

    def __init__(self) -> None:
        """Initialize database connection and ensure tables exist."""
        init_db()

    def does_user_exist(self, username: str) -> bool:
        """
        Check if a user exists in the database.

        Args:
            username: The username to check

        Returns:
            bool: True if user exists, False otherwise
        """
        session = SessionLocal()
        try:
            session.query(User).filter(User.username == username).one()
            print(f"User {username} exists.")
            return True
        except NoResultFound:
            print(f"User {username} does not exist.")
            return False
        finally:
            session.close()

    def get_user_data(self, username: str) -> dict:
        """
        Retrieve user data from the database.

        Args:
            username: The username to retrieve data for

        Returns:
            dict: User data containing tokens and prizes, or None if not found
        """
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.username == username).one()
            user_data = {
                "tokens": user.tokens,
                "prizes": user.prizes
            }
            return user_data
        except NoResultFound:
            print(f"No user found: {username}")
            return None
        finally:
            session.close()

    def add_user_data(self, username: str) -> User:
        """
        Add a new user to the database with default starting values.

        Args:
            username: The username for the new user

        Returns:
            User: The created user object, or None if creation failed
        """
        session = SessionLocal()
        try:
            user = User(
                username=username,
                tokens=30,
                prizes=[[], [], [], [], []]  # 5 prize categories
            )
            session.add(user)
            print(f"Adding new entry for user {username}")
            session.commit()
            print(f"User {username} saved!")
            return user
        except IntegrityError as e:
            session.rollback()
            print(f"Session rolled back. Error: {e}")
            return None
        finally:
            session.close()

    def update_user_data(self, player: Player) -> None:
        """
        Update existing user data in the database.

        Args:
            player: Player object containing updated data to save
        """
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.username == player.name).one()
            user.tokens = player.tokens
            user.prizes = player.prizes
            session.commit()
            print("User data updated successfully.")
        except NoResultFound:
            print(f"User {player.name} not found for update.")
        except Exception as e:
            session.rollback()
            print(f"Error updating user data: {e}")
        finally:
            session.close()
