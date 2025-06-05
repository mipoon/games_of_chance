"""
Database Models Module

Defines SQLAlchemy ORM models for the Games of Chance application.
Contains user data structure and prize collection schema.
"""

from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import declarative_base

# Create the base class for all models
Base = declarative_base()


class User(Base):
    """
    User model for storing player data and game progress.

    Stores player information including username, token balance,
    and prize collections organized by rarity categories.
    """

    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # User identification
    username = Column(String(50), unique=True, nullable=False, index=True)

    # Game progress
    tokens = Column(Integer, nullable=False, default=30)

    # Prize collections stored as JSON array of arrays
    # Format: [[common], [odd], [rare], [epic], [legendary]]
    prizes = Column(JSON, nullable=False, default=lambda: [[], [], [], [], []])

    def __repr__(self) -> str:
        """
        String representation of the User model.

        Returns:
            str: User information for debugging
        """
        total_prizes = sum(len(category) for category in (self.prizes or []))
        return f"<User(username='{self.username}', tokens={self.tokens}, total_prizes={total_prizes})>"

    def get_total_prizes(self) -> int:
        """
        Calculate the total number of prizes owned by the user.

        Returns:
            int: Total count of all prizes across all rarity categories
        """
        if not self.prizes:
            return 0
        return sum(len(category) for category in self.prizes)

    def get_prizes_by_rarity(self, rarity: str) -> list:
        """
        Get prizes for a specific rarity category.

        Args:
            rarity: The rarity category ('common', 'odd', 'rare', 'epic', 'legendary')

        Returns:
            list: List of prizes in the specified rarity category
        """
        rarity_map = {
            'common': 0,
            'odd': 1,
            'rare': 2,
            'epic': 3,
            'legendary': 4
        }

        if rarity.lower() not in rarity_map or not self.prizes:
            return []

        index = rarity_map[rarity.lower()]
        return self.prizes[index] if index < len(self.prizes) else []
