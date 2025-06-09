"""
Additional comprehensive tests for GUI components to achieve higher coverage.
"""
import queue
import tkinter as tk
from unittest.mock import Mock, patch

import pytest

from src.gui import (
    PlayerInfoDisplay, ConversationArea, InputControls, 
    GameIOHandler, GameSession, GameWrapper, PrizeBooth, GameGUI
)
from src.player import Player


class TestPlayerInfoDisplay:
    """Test the PlayerInfoDisplay component"""

    @pytest.fixture
    def root(self):
        """Create a tkinter root for testing"""
        root = tk.Tk()
        root.withdraw()
        yield root
        if root:
            root.destroy()

    @pytest.fixture
    def display(self, root):
        """Create a PlayerInfoDisplay for testing"""
        return PlayerInfoDisplay(root)

    def test_player_info_display_init(self, display):
        """Test PlayerInfoDisplay initialization"""
        assert display.frame is not None
        assert display.name_label is not None
        assert display.tokens_label is not None
        assert display.prizes_label is not None

    def test_player_info_display_update(self, display):
        """Test updating player information"""
        display.update("TestPlayer", 100, 5)
        
        assert display.name_label.cget("text") == "Player: TestPlayer"
        assert display.tokens_label.cget("text") == "Tokens: 100"
        assert display.prizes_label.cget("text") == "Prizes: 5"


class TestConversationArea:
    """Test the ConversationArea component"""

    @pytest.fixture
    def root(self):
        """Create a tkinter root for testing"""
        root = tk.Tk()
        root.withdraw()
        yield root
        if root:
            root.destroy()

    @pytest.fixture
    def conversation(self, root):
        """Create a ConversationArea for testing"""
        return ConversationArea(root)

    def test_conversation_area_init(self, conversation):
        """Test ConversationArea initialization"""
        assert conversation.frame is not None
        assert conversation.text_widget is not None

    def test_conversation_area_add_text(self, conversation):
        """Test adding text to conversation area"""
        conversation.add_text("Hello World!")
        
        # Get the text content
        content = conversation.text_widget.get("1.0", tk.END)
        assert "Hello World!" in content


class TestInputControls:
    """Test the InputControls component"""

    @pytest.fixture
    def root(self):
        """Create a tkinter root for testing"""
        root = tk.Tk()
        root.withdraw()
        yield root
        if root:
            root.destroy()

    @pytest.fixture
    def controls(self, root):
        """Create InputControls for testing"""
        send_callback = Mock()
        end_game_callback = Mock()
        return InputControls(root, send_callback, end_game_callback)

    def test_input_controls_init(self, controls):
        """Test InputControls initialization"""
        assert controls.frame is not None
        assert controls.entry is not None
        assert controls.send_button is not None
        assert controls.end_game_button is not None

    def test_input_controls_set_enabled_true(self, controls):
        """Test enabling input controls"""
        controls.set_enabled(True)
        
        assert str(controls.entry.cget("state")) == "normal"
        assert str(controls.send_button.cget("state")) == "normal"

    def test_input_controls_set_enabled_false(self, controls):
        """Test disabling input controls"""
        controls.set_enabled(False)
        
        assert str(controls.entry.cget("state")) == "disabled"
        assert str(controls.send_button.cget("state")) == "disabled"

    def test_input_controls_get_input(self, controls):
        """Test getting input and clearing entry"""
        # Enable the entry first (it starts disabled)
        controls.set_enabled(True)
        controls.entry.insert(0, "test input")
        
        result = controls.get_input()
        
        assert result == "test input"
        assert controls.entry.get() == ""


class TestGameIOHandler:
    """Test the GameIOHandler component"""

    @pytest.fixture
    def io_handler(self):
        """Create a GameIOHandler for testing"""
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        return GameIOHandler(input_queue, output_queue)

    def test_game_io_handler_init(self, io_handler):
        """Test GameIOHandler initialization"""
        assert io_handler.input_queue is not None
        assert io_handler.output_queue is not None

    def test_send_output(self, io_handler):
        """Test sending output"""
        io_handler.send_output("Test message")
        
        assert not io_handler.output_queue.empty()
        message = io_handler.output_queue.get()
        assert message == "Test message\n"

    def test_send_output_with_number(self, io_handler):
        """Test sending output with number"""
        io_handler.send_output(42)
        
        assert not io_handler.output_queue.empty()
        message = io_handler.output_queue.get()
        assert message == "42\n"

    def test_request_input(self, io_handler):
        """Test requesting input"""
        # Put input in queue first
        io_handler.input_queue.put("user response")
        
        # Request input in a separate thread to avoid blocking
        import threading
        result = []
        
        def request_input_thread():
            result.append(io_handler.request_input("Enter something: "))
        
        thread = threading.Thread(target=request_input_thread)
        thread.start()
        thread.join(timeout=1)
        
        assert len(result) == 1
        assert result[0] == "user response"

    def test_update_player_info(self, io_handler):
        """Test updating player info"""
        player = Player()
        player.name = "TestPlayer"
        player.tokens = 50
        player.prizes = [["Cat"], [], [], [], []]
        
        io_handler.update_player_info(player)
        
        assert not io_handler.output_queue.empty()
        message = io_handler.output_queue.get()
        assert message == "UPDATE_PLAYER_INFO:TestPlayer|50|1"


class TestGameSessionEdgeCases:
    """Test edge cases and error handling in GameSession"""

    @pytest.fixture
    def session(self):
        """Create a GameSession for testing"""
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)
        return GameSession(io_handler)

    def test_run_with_exception(self, session):
        """Test run method with exception handling"""
        with patch.object(session, 'setup_player', side_effect=Exception("Test error")):
            session.run()
            
            # Check that error was sent to output
            messages = []
            while not session.io.output_queue.empty():
                messages.append(session.io.output_queue.get())
            
            assert any("Error: Test error" in msg for msg in messages)
            assert "GAME_ENDED" in messages


class TestPrizeBoothEdgeCases:
    """Test edge cases in PrizeBooth"""

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
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)
        return PrizeBooth(player, io_handler)

    def test_spend_tokens_negative_input(self, booth, player):
        """Test spend_tokens with negative input"""
        player.tokens = 50
        
        # Create a mock that will return negative first, then valid inputs
        def mock_input_side_effect(prompt):
            if "amount of tokens" in prompt:
                if not hasattr(mock_input_side_effect, 'called'):
                    mock_input_side_effect.called = True
                    return "-5"  # First call returns negative
                else:
                    return "10"  # Second call returns valid
            elif "desired rarity" in prompt:
                return "common"
            elif "continue" in prompt:
                return "exit"
            return "exit"
        
        with patch.object(booth.io, 'request_input', side_effect=mock_input_side_effect), \
             patch.object(booth, '_calculate_rarity', return_value=("common", 1)), \
             patch.object(booth, '_select_prize', return_value="Cat"), \
             patch.object(booth, '_handle_duplicate', return_value=0), \
             patch('time.sleep'):
            
            booth.spend_tokens()
            
            messages = []
            while not booth.io.output_queue.empty():
                messages.append(booth.io.output_queue.get())
            
            assert any("You cannot spend a negative amount of tokens" in msg for msg in messages)

    def test_spend_tokens_invalid_rarity_input(self, booth, player):
        """Test spend_tokens with invalid rarity input"""
        player.tokens = 50
        
        def mock_input_side_effect(prompt):
            if "amount of tokens" in prompt:
                return "10"
            elif "desired rarity" in prompt:
                if not hasattr(mock_input_side_effect, 'rarity_called'):
                    mock_input_side_effect.rarity_called = True
                    return "invalid_rarity"  # First call returns invalid
                else:
                    return "common"  # Second call returns valid
            elif "continue" in prompt:
                return "exit"
            return "exit"
        
        with patch.object(booth.io, 'request_input', side_effect=mock_input_side_effect), \
             patch.object(booth, '_calculate_rarity', return_value=("common", 1)), \
             patch.object(booth, '_select_prize', return_value="Cat"), \
             patch.object(booth, '_handle_duplicate', return_value=0), \
             patch('time.sleep'):
            
            booth.spend_tokens()
            
            messages = []
            while not booth.io.output_queue.empty():
                messages.append(booth.io.output_queue.get())
            
            assert any("You must enter a valid rarity" in msg for msg in messages)

    def test_spend_tokens_value_error_input(self, booth, player):
        """Test spend_tokens with non-numeric input"""
        player.tokens = 50
        
        def mock_input_side_effect(prompt):
            if "amount of tokens" in prompt:
                if not hasattr(mock_input_side_effect, 'tokens_called'):
                    mock_input_side_effect.tokens_called = True
                    return "not_a_number"  # First call returns invalid
                else:
                    return "10"  # Second call returns valid
            elif "desired rarity" in prompt:
                return "common"
            elif "continue" in prompt:
                return "exit"
            return "exit"
        
        with patch.object(booth.io, 'request_input', side_effect=mock_input_side_effect), \
             patch.object(booth, '_calculate_rarity', return_value=("common", 1)), \
             patch.object(booth, '_select_prize', return_value="Cat"), \
             patch.object(booth, '_handle_duplicate', return_value=0), \
             patch('time.sleep'):
            
            booth.spend_tokens()
            
            messages = []
            while not booth.io.output_queue.empty():
                messages.append(booth.io.output_queue.get())
            
            assert any("ERROR: Enter a valid numerical value" in msg for msg in messages)

    def test_calculate_rarity_none(self, booth):
        """Test calculate rarity with 'none' preference"""
        with patch('src.gui.choice', return_value=50):
            rarity, extra = booth._calculate_rarity("none", 10)
            
            assert rarity == "odd"  # 50 falls in odd range
            assert extra == 1

    def test_calculate_rarity_all_categories(self, booth):
        """Test calculate rarity for all categories"""
        test_cases = [
            ("common", 30, "common"),
            ("odd", 50, "odd"),
            ("rare", 70, "rare"),
            ("epic", 90, "epic"),
            ("legendary", 110, "legendary")
        ]
        
        for user_rarity, roll_value, expected_rarity in test_cases:
            with patch('src.gui.choice', return_value=roll_value):
                rarity, extra = booth._calculate_rarity(user_rarity, 9)
                assert rarity == expected_rarity
                assert extra == 0

    def test_handle_duplicate_all_rarities(self, booth, player):
        """Test duplicate handling for all rarities"""
        # Set up existing prizes
        player.prizes = [["Cat"], ["Bird"], ["Ferret"], ["Butterfly"], ["Elephant"]]
        
        test_cases = [
            ("Cat", "common", 3),
            ("Bird", "odd", 5),
            ("Ferret", "rare", 7),
            ("Butterfly", "epic", 10),
            ("Elephant", "legendary", 20)
        ]
        
        for prize, rarity, expected_refund in test_cases:
            refund = booth._handle_duplicate(prize, rarity)
            assert refund == expected_refund


class TestGameGUIEdgeCases:
    """Test edge cases in GameGUI"""

    @pytest.fixture
    def root(self):
        """Create a tkinter root for testing"""
        root = tk.Tk()
        root.withdraw()
        yield root
        if root:
            root.destroy()

    def test_update_player_info_insufficient_parts(self, root):
        """Test _update_player_info with insufficient parts"""
        gui = GameGUI(root, auto_start=False)
        
        # Mock the update method to avoid actual GUI updates
        gui.player_info.update = Mock()
        
        # Test with insufficient parts
        gui._update_player_info("TestPlayer|100")  # Missing third part
        
        # Should not call update
        gui.player_info.update.assert_not_called()

    def test_send_input_with_event(self, root):
        """Test send_input with event parameter"""
        gui = GameGUI(root, auto_start=False)
        gui.waiting_for_input = True
        
        # Mock get_input to return test data
        gui.input_controls.get_input = Mock(return_value="test input")
        gui.conversation.add_text = Mock()
        
        # Call with event (simulating Enter key press)
        mock_event = Mock()
        gui.send_input(mock_event)
        
        assert not gui.input_queue.empty()
        assert gui.input_queue.get() == "test input"

    def test_end_game_not_running(self, root):
        """Test end_game when game is not running"""
        gui = GameGUI(root, auto_start=False)
        gui.game_running = False
        gui.on_closing = Mock()
        
        gui.end_game()
        
        # Should still call on_closing
        gui.on_closing.assert_called_once()
        # Queue should be empty since game wasn't running
        assert gui.input_queue.empty()

    def test_check_output_queue_empty(self, root):
        """Test check_output_queue when queue is empty"""
        gui = GameGUI(root, auto_start=False)
        gui.game_running = True
        
        # Mock root.after to prevent actual scheduling
        gui.root.after = Mock()
        
        gui.check_output_queue()
        
        # Should schedule next check
        gui.root.after.assert_called_once_with(100, gui.check_output_queue)


class TestGameWrapperEdgeCases:
    """Test edge cases in GameWrapper"""

    def test_play_with_exception(self):
        """Test play method when game raises exception"""
        mock_game = Mock()
        mock_game.play.side_effect = Exception("Game error")
        
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)
        
        wrapper = GameWrapper(mock_game, io_handler)
        
        # Should restore original functions even if exception occurs
        import builtins
        original_input = builtins.input
        original_print = builtins.print
        
        with pytest.raises(Exception, match="Game error"):
            wrapper.play()
        
        # Verify functions were restored
        assert builtins.input == original_input
        assert builtins.print == original_print


class TestRunGUIFunction:
    """Test the run_gui function"""

    @patch('src.gui.GameGUI')
    @patch('src.gui.tk.Tk')
    def test_run_gui_main_execution(self, mock_tk, mock_game_gui):
        """Test run_gui when called as main"""
        mock_root = Mock()
        mock_tk.return_value = mock_root
        mock_app = Mock()
        mock_game_gui.return_value = mock_app
        
        # Import and test the main execution
        import src.gui
        
        # Mock the __name__ check
        with patch.object(src.gui, '__name__', '__main__'):
            # This would normally call run_gui(), but we'll call it directly
            src.gui.run_gui()
        
        mock_tk.assert_called_once()
        mock_game_gui.assert_called_once_with(mock_root)
        mock_root.mainloop.assert_called_once()


class TestHelpersCoverage:
    """Test to cover the helpers __init__.py file"""

    def test_helpers_init_import(self):
        """Test importing helpers module"""
        import src.helpers
        
        # The __all__ list should be empty
        assert hasattr(src.helpers, '__all__')
        assert src.helpers.__all__ == []
