"""
Tests for database models module.
"""

from src.database.models import User, Base


class TestUser:
    """Test cases for the User model."""

    def test_user_creation(self):
        """Test basic user creation with default values."""
        user = User(username="testuser")

        assert user.username == "testuser"
        # Note: SQLAlchemy defaults are only applied when inserting to database
        # For in-memory objects, we need to explicitly set values or they'll be None
        assert user.tokens is None  # Will be 30 when saved to database
        assert user.prizes is None  # Will be [[], [], [], [], []] when saved to database

    def test_user_creation_with_custom_values(self):
        """Test user creation with custom values."""
        custom_prizes = [["item1"], ["item2"], [], [], ["item3"]]
        user = User(
            username="customuser",
            tokens=100,
            prizes=custom_prizes
        )

        assert user.username == "customuser"
        assert user.tokens == 100
        assert user.prizes == custom_prizes

    def test_user_repr(self):
        """Test string representation of User."""
        user = User(username="testuser", tokens=50)
        user.prizes = [["item1", "item2"], ["item3"], [], [], []]

        repr_str = repr(user)

        assert "testuser" in repr_str
        assert "tokens=50" in repr_str
        assert "total_prizes=3" in repr_str

    def test_user_repr_with_none_prizes(self):
        """Test string representation when prizes is None."""
        user = User(username="testuser", tokens=50)
        user.prizes = None

        repr_str = repr(user)

        assert "testuser" in repr_str
        assert "tokens=50" in repr_str
        assert "total_prizes=0" in repr_str

    def test_get_total_prizes(self):
        """Test getting total prize count."""
        user = User(username="testuser")
        user.prizes = [["item1", "item2"], ["item3"], [], ["item4"], []]

        total = user.get_total_prizes()

        assert total == 4

    def test_get_total_prizes_empty(self):
        """Test getting total prize count when no prizes."""
        user = User(username="testuser")
        user.prizes = [[], [], [], [], []]

        total = user.get_total_prizes()

        assert total == 0

    def test_get_total_prizes_none(self):
        """Test getting total prize count when prizes is None."""
        user = User(username="testuser")
        user.prizes = None

        total = user.get_total_prizes()

        assert total == 0

    def test_get_prizes_by_rarity_common(self):
        """Test getting prizes by common rarity."""
        user = User(username="testuser")
        user.prizes = [["common1", "common2"], ["odd1"], [], [], []]

        common_prizes = user.get_prizes_by_rarity("common")

        assert common_prizes == ["common1", "common2"]

    def test_get_prizes_by_rarity_odd(self):
        """Test getting prizes by odd rarity."""
        user = User(username="testuser")
        user.prizes = [["common1"], ["odd1", "odd2"], [], [], []]

        odd_prizes = user.get_prizes_by_rarity("odd")

        assert odd_prizes == ["odd1", "odd2"]

    def test_get_prizes_by_rarity_rare(self):
        """Test getting prizes by rare rarity."""
        user = User(username="testuser")
        user.prizes = [[], [], ["rare1"], [], []]

        rare_prizes = user.get_prizes_by_rarity("rare")

        assert rare_prizes == ["rare1"]

    def test_get_prizes_by_rarity_epic(self):
        """Test getting prizes by epic rarity."""
        user = User(username="testuser")
        user.prizes = [[], [], [], ["epic1", "epic2"], []]

        epic_prizes = user.get_prizes_by_rarity("epic")

        assert epic_prizes == ["epic1", "epic2"]

    def test_get_prizes_by_rarity_legendary(self):
        """Test getting prizes by legendary rarity."""
        user = User(username="testuser")
        user.prizes = [[], [], [], [], ["legendary1"]]

        legendary_prizes = user.get_prizes_by_rarity("legendary")

        assert legendary_prizes == ["legendary1"]

    def test_get_prizes_by_rarity_case_insensitive(self):
        """Test getting prizes by rarity is case insensitive."""
        user = User(username="testuser")
        user.prizes = [["common1"], [], [], [], []]

        common_prizes = user.get_prizes_by_rarity("COMMON")

        assert common_prizes == ["common1"]

    def test_get_prizes_by_rarity_invalid(self):
        """Test getting prizes by invalid rarity."""
        user = User(username="testuser")
        user.prizes = [["common1"], [], [], [], []]

        invalid_prizes = user.get_prizes_by_rarity("invalid")

        assert invalid_prizes == []

    def test_get_prizes_by_rarity_none_prizes(self):
        """Test getting prizes by rarity when prizes is None."""
        user = User(username="testuser")
        user.prizes = None

        common_prizes = user.get_prizes_by_rarity("common")

        assert common_prizes == []

    def test_get_prizes_by_rarity_short_prizes_list(self):
        """Test getting prizes by rarity when prizes list is shorter than expected."""
        user = User(username="testuser")
        user.prizes = [["common1"], ["odd1"]]  # Only 2 categories instead of 5

        # Should return empty list for categories beyond the list length
        rare_prizes = user.get_prizes_by_rarity("rare")
        epic_prizes = user.get_prizes_by_rarity("epic")
        legendary_prizes = user.get_prizes_by_rarity("legendary")

        assert rare_prizes == []
        assert epic_prizes == []
        assert legendary_prizes == []

    def test_base_class_exists(self):
        """Test that Base class is properly defined."""
        assert Base is not None
        assert hasattr(Base, 'metadata')
