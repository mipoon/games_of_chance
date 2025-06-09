"""
Comprehensive tests for gui.py module using pytest framework.
Converted from unittest and expanded for better coverage.
"""
import queue
import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from src.gui import GameGUI, GameSession, GameWrapper, PrizeBooth, run_gui
from src.player import Player


class TestGameGUI:  # pylint: disable=too-many-public-methods
    """Test the main GameGUI class"""

    @pytest.fixture
    def root(self):
        """Create a tkinter root for testing"""
        root = tk.Tk()
        root.withdraw()  # Hide the window during testing
        yield root
        if root:
            root.destroy()

    @pytest.fixture
    def gui(self, root):
        """Create a GameGUI instance for testing"""
        return GameGUI(root, auto_start=False)

    def test_game_gui_init(self, gui):
        """Test GameGUI initialization"""
        # Check that UI components are created
        assert gui.player_info is not None
        assert gui.conversation is not None
        assert gui.input_controls is not None

        # Check initial state
        assert gui.waiting_for_input is False
        assert gui.game_running is False  # Should be False when auto_start=False

    def test_game_gui_init_with_auto_start(self, root):
        """Test GameGUI initialization with auto_start=True"""
        with patch.object(GameGUI, 'start_game') as mock_start:
            GameGUI(root, auto_start=True)
            mock_start.assert_called_once()

    def test_send_input_when_waiting(self, gui):
        """Test sending input when waiting for input"""
        gui.waiting_for_input = True
        gui.input_controls.entry.insert(0, "test input")

        # Mock the get_input method to return our test input
        original_get_input = gui.input_controls.get_input
        gui.input_controls.get_input = lambda: "test input"

        gui.send_input()

        # Check that input was queued
        assert not gui.input_queue.empty()
        input_value = gui.input_queue.get()
        assert input_value == "test input"

        # Restore original method
        gui.input_controls.get_input = original_get_input

    def test_send_input_when_not_waiting(self, gui):
        """Test sending input when not waiting for input"""
        gui.waiting_for_input = False
        gui.input_controls.entry.insert(0, "test input")

        gui.send_input()

        # Check that input was not queued
        assert gui.input_queue.empty()

    def test_start_game(self, gui):
        """Test starting the game"""
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance

            gui.start_game()

            assert gui.game_running is True
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()

    def test_start_game_already_running(self, gui):
        """Test starting game when already running"""
        gui.game_running = True

        with patch('threading.Thread') as mock_thread:
            gui.start_game()
            mock_thread.assert_not_called()

    def test_end_game(self, gui):
        """Test ending the game"""
        gui.game_running = True
        gui.on_closing = Mock()

        gui.end_game()

        assert not gui.input_queue.empty()
        assert gui.input_queue.get() == "exit"
        assert gui.game_running is False
        gui.on_closing.assert_called_once()

    def test_on_closing(self, gui):
        """Test window closing behavior"""
        gui.game_running = True

        # Mock the root methods to prevent actual closing during test
        gui.root.quit = Mock()
        gui.root.destroy = Mock()

        gui.on_closing()

        assert gui.game_running is False
        gui.root.quit.assert_called_once()
        gui.root.destroy.assert_called_once()

    def test_check_output_queue_game_ended(self, gui):
        """Test check_output_queue when game ends"""
        gui.output_queue.put("GAME_ENDED")
        gui.game_running = True
        gui.conversation.add_text = Mock()

        gui.check_output_queue()

        assert gui.game_running is False
        gui.conversation.add_text.assert_called_with("Game ended. You can close the window.\n")

    def test_check_output_queue_waiting_for_input(self, gui):
        """Test check_output_queue when waiting for input"""
        gui.output_queue.put("WAITING_FOR_INPUT")
        gui.input_controls.set_enabled(False)

        gui.check_output_queue()

        assert gui.waiting_for_input is True

    def test_check_output_queue_input_received(self, gui):
        """Test check_output_queue when input is received"""
        gui.output_queue.put("INPUT_RECEIVED")
        gui.waiting_for_input = True

        gui.check_output_queue()

        assert gui.waiting_for_input is False

    def test_check_output_queue_update_player_info(self, gui):
        """Test check_output_queue with player info update"""
        gui.output_queue.put("UPDATE_PLAYER_INFO:TestPlayer|100|5")
        gui._update_player_info = Mock()

        gui.check_output_queue()

        gui._update_player_info.assert_called_with("TestPlayer|100|5")

    def test_check_output_queue_regular_message(self, gui):
        """Test check_output_queue with regular message"""
        gui.output_queue.put("Regular message")
        gui.conversation.add_text = Mock()

        gui.check_output_queue()

        gui.conversation.add_text.assert_called_with("Regular message")


class TestGameSession:
    """Test the GameSession class"""

    @pytest.fixture
    def session(self):
        """Create a GameSession for testing"""
        from src.gui import GameIOHandler
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)
        return GameSession(io_handler)

    def test_game_session_init(self, session):
        """Test GameSession initialization"""
        assert session.io is not None
        assert session.db is not None
        assert session.player is not None

    def test_display_instructions(self, session):
        """Test display instructions"""
        session.display_instructions()

        messages = []
        while not session.io.output_queue.empty():
            messages.append(session.io.output_queue.get())

        # Check that welcome message is included
        assert any("Welcome to Games of Chance with Prizes!" in msg for msg in messages)
        assert any("mini-games" in msg for msg in messages)

    def test_setup_player_new(self, session):
        """Test setting up a new player"""
        with patch.object(session.io, 'request_input', return_value="NewPlayer"), \
             patch.object(session.io, 'update_player_info') as mock_update, \
             patch.object(session.db, 'does_user_exist', return_value=False), \
             patch.object(session.db, 'add_user_data') as mock_add:

            session.setup_player()

            assert session.player.name == "NewPlayer"
            assert session.player.tokens == 30
            assert session.player.prizes == [[], [], [], [], []]
            mock_add.assert_called_once_with("NewPlayer")
            mock_update.assert_called_once()

    def test_setup_player_existing(self, session):
        """Test setting up an existing player"""
        with patch.object(session.io, 'request_input', return_value="ExistingPlayer"), \
             patch.object(session.io, 'update_player_info') as mock_update, \
             patch.object(session.db, 'does_user_exist', return_value=True), \
             patch.object(session.db, 'get_user_data', return_value={
                 "tokens": 50,
                 "prizes": [["Cat"], [], [], [], []]
             }):

            session.setup_player()

            assert session.player.name == "ExistingPlayer"
            assert session.player.tokens == 50
            assert session.player.prizes == [["Cat"], [], [], [], []]
            mock_update.assert_called_once()

    def test_play_games(self, session):
        """Test playing games"""
        with patch.object(session.io, 'update_player_info') as mock_update, \
             patch('src.games.game_loader.GameLoader.pick_random_game') as mock_pick_game, \
             patch('src.gui.GameWrapper') as mock_wrapper_class:

            # Mock game and wrapper
            mock_game = Mock()
            mock_pick_game.return_value = mock_game
            mock_wrapper = Mock()
            mock_wrapper.play.return_value = 20
            mock_wrapper_class.return_value = mock_wrapper

            session.player.tokens = 30

            session.play_games()

            # Should have played 3 games
            assert mock_wrapper_class.call_count == 3
            assert mock_wrapper.play.call_count == 3
            assert mock_update.call_count == 3

            # Should have earned 60 tokens (20 * 3)
            assert session.player.tokens == 90

    def test_show_final_results(self, session):
        """Test final results display"""
        session.player.prizes = [["Cat", "Dog"], ["Bird"], [], ["Butterfly"], []]

        session.show_final_results()

        messages = []
        while not session.io.output_queue.empty():
            messages.append(session.io.output_queue.get())

        # Check for category displays
        assert any("Common - Cat, Dog" in msg for msg in messages)
        assert any("Odd - Bird" in msg for msg in messages)
        assert any("Rare - None" in msg for msg in messages)
        assert any("Epic - Butterfly" in msg for msg in messages)
        assert any("Legendary - None" in msg for msg in messages)

    def test_conclude(self, session):
        """Test conclude method"""
        with patch.object(session.db, 'update_user_data') as mock_update:
            session.conclude()

            mock_update.assert_called_once_with(session.player)

    def test_run_prize_booth(self, session):
        """Test prize booth interaction"""
        with patch('src.gui.PrizeBooth') as mock_booth_class:
            mock_booth = Mock()
            mock_booth_class.return_value = mock_booth

            session.run_prize_booth()

            mock_booth_class.assert_called_once()
            mock_booth.spend_tokens.assert_called_once()


class TestGameWrapper:
    """Test the GameWrapper class"""

    def test_game_wrapper_init(self):
        """Test GameWrapper initialization"""
        mock_game = Mock()
        from src.gui import GameIOHandler
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)

        wrapper = GameWrapper(mock_game, io_handler)

        assert wrapper.game == mock_game
        assert wrapper.io == io_handler

    def test_play_with_monkey_patching(self):
        """Test that play method correctly monkey patches input/output"""
        mock_game = Mock()
        mock_game.play.return_value = 50
        from src.gui import GameIOHandler
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)

        wrapper = GameWrapper(mock_game, io_handler)
        result = wrapper.play()

        assert result == 50
        mock_game.play.assert_called_once()

    @patch('builtins.input')
    @patch('builtins.print')
    def test_play_restores_original_functions(self, mock_print, mock_input):
        """Test that original functions are restored after play"""
        original_input = mock_input
        original_print = mock_print

        mock_game = Mock()
        mock_game.play.return_value = 25
        from src.gui import GameIOHandler
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)

        wrapper = GameWrapper(mock_game, io_handler)
        wrapper.play()

        # Check that builtins were restored
        import builtins  # pylint: disable=import-outside-toplevel
        assert builtins.input == original_input  # pylint: disable=comparison-with-callable
        assert builtins.print == original_print  # pylint: disable=comparison-with-callable


class TestPrizeBooth:
    """Test the PrizeBooth class"""

    @pytest.fixture
    def player(self):
        """Create a test player"""
        player = Player()
        player.name = "TestPlayer"
        player.tokens = 100
        player.prizes = [[], [], [], [], []]
        return player

    @pytest.fixture
    def booth(self, player):
        """Create a PrizeBooth for testing"""
        from src.gui import GameIOHandler
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)
        return PrizeBooth(player, io_handler)

    def test_prize_booth_init(self, booth, player):
        """Test PrizeBooth initialization"""
        assert booth.player == player
        assert booth.io is not None

    @patch('src.gui.choice')
    def test_calculate_rarity_common(self, mock_choice, booth):
        """Test calculating rarity for common"""
        mock_choice.return_value = 30

        rarity, extra = booth._calculate_rarity("common", 10)

        assert rarity == "common"
        assert extra == 1  # 10 % 3 = 1

    @patch('src.gui.choice')
    def test_calculate_rarity_legendary(self, mock_choice, booth):
        """Test calculating rarity for legendary"""
        # With 9 tokens spent on legendary, we get 3% bonus (9//3)
        # So the range becomes 1-103, and we need a roll > 100 for legendary
        mock_choice.return_value = 103

        rarity, extra = booth._calculate_rarity("legendary", 9)

        assert rarity == "legendary"
        assert extra == 0  # 9 % 3 = 0

    @patch('src.gui.choice')
    def test_select_prize_all_rarities(self, mock_choice, booth):
        """Test selecting prizes for all rarities"""
        test_cases = [
            ("common", "Cat"),
            ("odd", "Bird"),
            ("rare", "Ferret"),
            ("epic", "Butterfly"),
            ("legendary", "Elephant")
        ]

        for rarity, expected_prize in test_cases:
            mock_choice.return_value = expected_prize
            prize = booth._select_prize(rarity)
            assert prize == expected_prize

    def test_select_prize_invalid_rarity(self, booth):
        """Test selecting prize with invalid rarity"""
        with pytest.raises(ValueError, match="Invalid prize rarity"):
            booth._select_prize("invalid")

    def test_handle_duplicate_existing_prize(self, booth, player):
        """Test handling duplicate prize"""
        player.prizes[0] = ["Cat"]  # Common prize

        refund = booth._handle_duplicate("Cat", "common")

        assert refund == 3

    def test_handle_duplicate_new_prize(self, booth):
        """Test no refund for new prize"""
        refund = booth._handle_duplicate("Dog", "common")

        assert refund == 0

    def test_spend_tokens_insufficient_tokens(self, booth, player):
        """Test spending tokens when insufficient tokens"""
        player.tokens = 15  # Less than 20 required

        booth.spend_tokens()

        # Should not have requested any input
        assert booth.io.input_queue.empty()


class TestRunGUI:
    """Test the run_gui function"""

    @patch('src.gui.tk.Tk')
    @patch('src.gui.GameGUI')
    def test_run_gui(self, mock_game_gui, mock_tk):
        """Test run_gui function"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_app = Mock()
        mock_game_gui.return_value = mock_app

        run_gui()

        mock_tk.assert_called_once()
        mock_game_gui.assert_called_once_with(mock_root)
        mock_root.mainloop.assert_called_once()
