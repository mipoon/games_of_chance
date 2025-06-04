"""
Comprehensive tests for gui.py module using pytest framework.
Converted from unittest and expanded for better coverage.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import queue
import threading
import time
from gui import GameGUI, GUIPlaySession, GUIGameWrapper, GUIPrizeBooth, run_gui
from player import Player


class TestGameGUI:
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
        assert gui.info_frame is not None
        assert gui.conversation_frame is not None
        assert gui.input_frame is not None
        assert gui.name_label is not None
        assert gui.tokens_label is not None
        assert gui.prizes_label is not None
        assert gui.conversation_text is not None
        assert gui.input_entry is not None
        assert gui.send_button is not None
        assert gui.end_game_button is not None
        
        # Check initial state
        assert gui.waiting_for_input is False
        assert gui.game_running is False  # Should be False when auto_start=False
        
    def test_game_gui_init_with_auto_start(self, root):
        """Test GameGUI initialization with auto_start=True"""
        with patch.object(GameGUI, 'start_game') as mock_start:
            gui = GameGUI(root, auto_start=True)
            mock_start.assert_called_once()
            
    def test_add_to_conversation(self, gui):
        """Test adding text to conversation area"""
        test_text = "Test message"
        
        gui.add_to_conversation(test_text)
        
        # Get the text from the conversation widget
        content = gui.conversation_text.get("1.0", tk.END)
        assert test_text in content
        
    def test_update_player_info(self, gui):
        """Test updating player information display"""
        gui.update_player_info("TestPlayer|100|5")
        
        assert gui.name_label.cget("text") == "Player: TestPlayer"
        assert gui.tokens_label.cget("text") == "Tokens: 100"
        assert gui.prizes_label.cget("text") == "Prizes: 5"
        
    def test_update_player_info_insufficient_parts(self, gui):
        """Test updating player info with insufficient data"""
        # Should not crash with insufficient parts
        gui.update_player_info("TestPlayer|100")
        # Labels should remain unchanged from default
        assert "Player: Not logged in" in gui.name_label.cget("text")
        
    def test_send_input_when_waiting(self, gui):
        """Test sending input when waiting for input"""
        gui.waiting_for_input = True
        gui.input_entry.insert(0, "test input")
        
        gui.send_input()
        
        # Check that input was queued
        assert not gui.input_queue.empty()
        input_value = gui.input_queue.get()
        assert input_value == "test input"
        
        # Check that entry was cleared
        assert gui.input_entry.get() == ""
        
    def test_send_input_when_not_waiting(self, gui):
        """Test sending input when not waiting for input"""
        gui.waiting_for_input = False
        gui.input_entry.insert(0, "test input")
        
        gui.send_input()
        
        # Check that input was not queued
        assert gui.input_queue.empty()
        
    def test_send_input_with_event(self, gui):
        """Test send_input with event parameter (Enter key)"""
        gui.waiting_for_input = True
        gui.input_entry.insert(0, "test input")
        
        # Simulate Enter key event
        event = Mock()
        gui.send_input(event)
        
        assert not gui.input_queue.empty()
        
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
        
    def test_end_game_not_running(self, gui):
        """Test ending game when not running"""
        gui.game_running = False
        gui.on_closing = Mock()
        
        gui.end_game()
        
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
        gui.add_to_conversation = Mock()
        
        gui.check_output_queue()
        
        assert gui.game_running is False
        gui.add_to_conversation.assert_called_with("Game ended. You can close the window.\n")
        
    def test_check_output_queue_waiting_for_input(self, gui):
        """Test check_output_queue when waiting for input"""
        gui.output_queue.put("WAITING_FOR_INPUT")
        gui.input_entry.config(state=tk.DISABLED)
        gui.send_button.config(state=tk.DISABLED)
        
        gui.check_output_queue()
        
        assert gui.waiting_for_input is True
        assert str(gui.input_entry.cget("state")) == "normal"
        assert str(gui.send_button.cget("state")) == "normal"
        
    def test_check_output_queue_input_received(self, gui):
        """Test check_output_queue when input is received"""
        gui.output_queue.put("INPUT_RECEIVED")
        gui.waiting_for_input = True
        
        gui.check_output_queue()
        
        assert gui.waiting_for_input is False
        assert str(gui.input_entry.cget("state")) == "disabled"
        assert str(gui.send_button.cget("state")) == "disabled"
        
    def test_check_output_queue_update_player_info(self, gui):
        """Test check_output_queue with player info update"""
        gui.output_queue.put("UPDATE_PLAYER_INFO:TestPlayer|100|5")
        gui.update_player_info = Mock()
        
        gui.check_output_queue()
        
        gui.update_player_info.assert_called_with("TestPlayer|100|5")
        
    def test_check_output_queue_regular_message(self, gui):
        """Test check_output_queue with regular message"""
        gui.output_queue.put("Regular message")
        gui.add_to_conversation = Mock()
        
        gui.check_output_queue()
        
        gui.add_to_conversation.assert_called_with("Regular message")
        
    def test_check_output_queue_empty(self, gui):
        """Test check_output_queue when queue is empty"""
        gui.game_running = True
        gui.root.after = Mock()
        
        gui.check_output_queue()
        
        gui.root.after.assert_called_with(100, gui.check_output_queue)
        
    def test_run_game_session_success(self, gui):
        """Test successful game session run"""
        with patch('gui.GUIPlaySession') as mock_session_class:
            mock_session = Mock()
            mock_session_class.return_value = mock_session
            
            gui.run_game_session()
            
            mock_session_class.assert_called_once_with(gui.input_queue, gui.output_queue)
            mock_session.run_session.assert_called_once()
            assert not gui.output_queue.empty()
            assert gui.output_queue.get() == "GAME_ENDED"
            
    def test_run_game_session_exception(self, gui):
        """Test game session run with exception"""
        with patch('gui.GUIPlaySession') as mock_session_class:
            mock_session = Mock()
            mock_session.run_session.side_effect = Exception("Test error")
            mock_session_class.return_value = mock_session
            
            gui.run_game_session()
            
            # Should have error message and GAME_ENDED
            messages = []
            while not gui.output_queue.empty():
                messages.append(gui.output_queue.get())
            
            assert any("Error: Test error" in msg for msg in messages)
            assert "GAME_ENDED" in messages


class TestGUIPlaySession:
    """Test the GUIPlaySession class"""
    
    @pytest.fixture
    def session(self):
        """Create a GUIPlaySession for testing"""
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        return GUIPlaySession(input_queue, output_queue)
        
    def test_gui_play_session_init(self, session):
        """Test GUIPlaySession initialization"""
        assert session.input_queue is not None
        assert session.output_queue is not None
        assert session.db is not None
        assert session.player is not None
        assert session.prize_booth is not None
        
    def test_gui_print(self, session):
        """Test GUI print functionality"""
        session.gui_print("Test message")
        
        assert not session.output_queue.empty()
        message = session.output_queue.get()
        assert message == "Test message\n"
        
    def test_gui_print_with_number(self, session):
        """Test GUI print with number"""
        session.gui_print(42)
        
        assert not session.output_queue.empty()
        message = session.output_queue.get()
        assert message == "42\n"
        
    def test_gui_input(self, session):
        """Test GUI input functionality"""
        # Put input in queue
        session.input_queue.put("test input")
        
        # Start input in a thread to avoid blocking
        result = []
        def get_input():
            result.append(session.gui_input("Enter something: "))
            
        thread = threading.Thread(target=get_input)
        thread.start()
        thread.join(timeout=1)
        
        assert len(result) == 1
        assert result[0] == "test input"
        
        # Check that prompt and signals were sent
        messages = []
        while not session.output_queue.empty():
            messages.append(session.output_queue.get())
            
        assert "Enter something: \n" in messages
        assert "WAITING_FOR_INPUT" in messages
        assert "INPUT_RECEIVED" in messages
        
    def test_update_player_display(self, session):
        """Test player display update"""
        session.player.name = "TestPlayer"
        session.player.tokens = 100
        session.player.prizes = [["Cat"], ["Bird"], [], [], []]
        
        session.update_player_display()
        
        assert not session.output_queue.empty()
        message = session.output_queue.get()
        assert message == "UPDATE_PLAYER_INFO:TestPlayer|100|2"
        
    def test_update_player_display_empty_prizes(self, session):
        """Test player display update with empty prizes"""
        session.player.name = "TestPlayer"
        session.player.tokens = 50
        session.player.prizes = [[], [], [], [], []]
        
        session.update_player_display()
        
        message = session.output_queue.get()
        assert message == "UPDATE_PLAYER_INFO:TestPlayer|50|0"
        
    def test_display_instructions(self, session):
        """Test display instructions"""
        session.display_instructions()
        
        messages = []
        while not session.output_queue.empty():
            messages.append(session.output_queue.get())
            
        # Check that welcome message is included
        assert any("Welcome to Games of Chance with Prizes!" in msg for msg in messages)
        assert any("mini-games" in msg for msg in messages)
        
    @patch('gui.GUIPlaySession.gui_input')
    @patch('gui.GUIPlaySession.gui_print')
    @patch('gui.GUIPlaySession.update_player_display')
    def test_setup_player_new(self, mock_update, mock_print, mock_input):
        """Test setting up a new player"""
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        session = GUIPlaySession(input_queue, output_queue)
        
        with patch.object(session.db, 'does_user_exist', return_value=False), \
             patch.object(session.db, 'add_user_data') as mock_add:
            
            mock_input.return_value = "NewPlayer"
            
            session.setup_player()
            
            assert session.player.name == "NewPlayer"
            assert session.player.tokens == 30
            assert session.player.prizes == [[], [], [], [], []]
            mock_add.assert_called_once_with("NewPlayer")
            mock_update.assert_called_once()
            
    @patch('gui.GUIPlaySession.gui_input')
    @patch('gui.GUIPlaySession.gui_print')
    @patch('gui.GUIPlaySession.update_player_display')
    def test_setup_player_existing(self, mock_update, mock_print, mock_input):
        """Test setting up an existing player"""
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        session = GUIPlaySession(input_queue, output_queue)
        
        with patch.object(session.db, 'does_user_exist', return_value=True), \
             patch.object(session.db, 'get_user_data', return_value={
                 "tokens": 50,
                 "prizes": [["Cat"], [], [], [], []]
             }):
            
            mock_input.return_value = "ExistingPlayer"
            
            session.setup_player()
            
            assert session.player.name == "ExistingPlayer"
            assert session.player.tokens == 50
            assert session.player.prizes == [["Cat"], [], [], [], []]
            mock_update.assert_called_once()
            
    @patch('gui.GUIGameWrapper')
    @patch('games.game_loader.GameLoader.pick_random_game')
    @patch('gui.GUIPlaySession.update_player_display')
    @patch('time.sleep')
    def test_play_games(self, mock_sleep, mock_update, mock_pick_game, mock_wrapper_class):
        """Test playing games"""
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        session = GUIPlaySession(input_queue, output_queue)
        
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
        
    def test_final_results(self, session):
        """Test final results display"""
        session.player.prizes = [["Cat", "Dog"], ["Bird"], [], ["Butterfly"], []]
        
        session.final_results()
        
        messages = []
        while not session.output_queue.empty():
            messages.append(session.output_queue.get())
            
        # Check for category displays
        assert any("Common - Cat, Dog" in msg for msg in messages)
        assert any("Odd - Bird" in msg for msg in messages)
        assert any("Rare - None" in msg for msg in messages)
        assert any("Epic - Butterfly" in msg for msg in messages)
        assert any("Legendary - None" in msg for msg in messages)
        
    @patch('gui.GUIPlaySession.gui_print')
    def test_conclude(self, mock_print, session):
        """Test conclude method"""
        with patch.object(session.db, 'update_user_data') as mock_update:
            session.conclude()
            
            mock_update.assert_called_once_with(session.player)
            mock_print.assert_called_with("\nThanks for playing!\n")
            
    @patch('gui.GUIPlaySession.setup_player')
    @patch('gui.GUIPlaySession.display_instructions')
    @patch('gui.GUIPlaySession.play_games')
    @patch('gui.GUIPlaySession.prize_booth_interaction')
    @patch('gui.GUIPlaySession.final_results')
    @patch('gui.GUIPlaySession.conclude')
    def test_run_session(self, mock_conclude, mock_final, mock_prize, 
                        mock_play, mock_instructions, mock_setup, session):
        """Test complete run session"""
        session.run_session()
        
        mock_setup.assert_called_once()
        mock_instructions.assert_called_once()
        mock_play.assert_called_once()
        mock_prize.assert_called_once()
        mock_final.assert_called_once()
        mock_conclude.assert_called_once()
        
    @patch('gui.GUIPrizeBooth')
    def test_prize_booth_interaction(self, mock_booth_class, session):
        """Test prize booth interaction"""
        mock_booth = Mock()
        mock_booth_class.return_value = mock_booth
        
        session.prize_booth_interaction()
        
        mock_booth_class.assert_called_once()
        mock_booth.spend_tokens.assert_called_once()


class TestGUIGameWrapper:
    """Test the GUIGameWrapper class"""
    
    def test_gui_game_wrapper_init(self):
        """Test GUIGameWrapper initialization"""
        mock_game = Mock()
        mock_input = Mock()
        mock_output = Mock()
        
        wrapper = GUIGameWrapper(mock_game, mock_input, mock_output)
        
        assert wrapper.game == mock_game
        assert wrapper.gui_input == mock_input
        assert wrapper.gui_print == mock_output
        
    @patch('builtins.input')
    @patch('builtins.print')
    def test_play_with_monkey_patching(self, mock_print, mock_input):
        """Test that play method correctly monkey patches input/output"""
        mock_game = Mock()
        mock_game.play.return_value = 50
        mock_gui_input = Mock()
        mock_gui_output = Mock()
        
        wrapper = GUIGameWrapper(mock_game, mock_gui_input, mock_gui_output)
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
        mock_gui_input = Mock()
        mock_gui_output = Mock()
        
        wrapper = GUIGameWrapper(mock_game, mock_gui_input, mock_gui_output)
        wrapper.play()
        
        # Check that builtins were restored
        import builtins
        assert builtins.input == original_input
        assert builtins.print == original_print
        
    @patch('builtins.input')
    @patch('builtins.print')
    def test_play_with_exception(self, mock_print, mock_input):
        """Test that original functions are restored even when exception occurs"""
        original_input = mock_input
        original_print = mock_print
        
        mock_game = Mock()
        mock_game.play.side_effect = Exception("Game error")
        mock_gui_input = Mock()
        mock_gui_output = Mock()
        
        wrapper = GUIGameWrapper(mock_game, mock_gui_input, mock_gui_output)
        
        with pytest.raises(Exception, match="Game error"):
            wrapper.play()
            
        # Check that builtins were restored despite exception
        import builtins
        assert builtins.input == original_input
        assert builtins.print == original_print


class TestGUIPrizeBooth:
    """Test the GUIPrizeBooth class"""
    
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
        """Create a GUIPrizeBooth for testing"""
        mock_input = Mock()
        mock_output = Mock()
        mock_update = Mock()
        return GUIPrizeBooth(player, mock_input, mock_output, mock_update)
        
    def test_gui_prize_booth_init(self, booth, player):
        """Test GUIPrizeBooth initialization"""
        assert booth.user == player
        assert booth.gui_input is not None
        assert booth.gui_print is not None
        assert booth.update_display is not None
        
    @patch('random.choice')
    def test_spend_for_rarity_common(self, mock_choice, booth):
        """Test spending for common rarity"""
        mock_choice.return_value = 30
        
        rarity, extra = booth.spend_for_rarity("common", 10)
        
        assert rarity == "common"
        assert extra == 1  # 10 % 3 = 1
        
    @patch('random.choice')
    def test_spend_for_rarity_legendary(self, mock_choice, booth):
        """Test spending for legendary rarity"""
        mock_choice.return_value = 110
        
        rarity, extra = booth.spend_for_rarity("legendary", 9)
        
        assert rarity == "legendary"
        assert extra == 0  # 9 % 3 = 0
        
    @patch('random.choice')
    def test_spend_for_rarity_none(self, mock_choice, booth):
        """Test spending for no specific rarity"""
        mock_choice.return_value = 50
        
        rarity, extra = booth.spend_for_rarity("none", 6)
        
        assert rarity == "odd"  # 50 falls in odd range
        assert extra == 0  # 6 % 3 = 0
        
    @patch('random.choice')
    def test_spend_for_rarity_all_categories(self, mock_choice, booth):
        """Test all rarity categories"""
        test_cases = [
            (20, "common"),
            (50, "odd"),
            (70, "rare"),
            (90, "epic"),
            (110, "legendary")
        ]
        
        for roll, expected_rarity in test_cases:
            mock_choice.return_value = roll
            rarity, _ = booth.spend_for_rarity("none", 0)
            assert rarity == expected_rarity
            
    @patch('random.choice')
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
            prize = booth.select_prize(rarity)
            assert prize == expected_prize
            
    def test_select_prize_invalid_rarity(self, booth):
        """Test selecting prize with invalid rarity"""
        with pytest.raises(ValueError, match="Invalid prize rarity"):
            booth.select_prize("invalid")
            
    def test_refund_rerolls_existing_prize(self, booth, player):
        """Test refund for existing prize"""
        player.prizes[0] = ["Cat"]  # Common prize
        
        refund = booth.refund_rerolls("Cat", "common")
        
        assert refund == 3
        
    def test_refund_rerolls_new_prize(self, booth):
        """Test no refund for new prize"""
        refund = booth.refund_rerolls("Dog", "common")
        
        assert refund == 0
        
    def test_refund_rerolls_all_rarities(self, booth, player):
        """Test refund amounts for all rarities"""
        # Set up existing prizes
        player.prizes[0] = ["Cat"]      # Common
        player.prizes[1] = ["Bird"]     # Odd
        player.prizes[2] = ["Ferret"]   # Rare
        player.prizes[3] = ["Butterfly"] # Epic
        player.prizes[4] = ["Elephant"] # Legendary
        
        # Test refunds
        assert booth.refund_rerolls("Cat", "common") == 3
        assert booth.refund_rerolls("Bird", "odd") == 5
        assert booth.refund_rerolls("Ferret", "rare") == 7
        assert booth.refund_rerolls("Butterfly", "epic") == 10
        assert booth.refund_rerolls("Elephant", "legendary") == 20
        
    @patch('time.sleep')
    @patch('random.choice')
    def test_spend_tokens_single_round(self, mock_choice, mock_sleep, booth, player):
        """Test spending tokens for one round"""
        player.tokens = 50
        
        # Mock user inputs
        booth.gui_input.side_effect = ["10", "common", "exit"]
        
        # Mock random choices
        mock_choice.side_effect = [30, "Cat"]  # rarity roll, prize selection
        
        booth.spend_tokens()
        
        # Should have spent 10 + 20 = 30 tokens, gained 1 back (10 % 3)
        assert player.tokens == 21  # 50 - 10 - 20 + 1
        
    @patch('time.sleep')
    @patch('random.choice')
    def test_spend_tokens_insufficient_tokens(self, mock_choice, mock_sleep, booth, player):
        """Test spending tokens when insufficient tokens"""
        player.tokens = 15  # Less than 20 required
        
        booth.spend_tokens()
        
        # Should not enter the spending loop
        booth.gui_input.assert_not_called()
        
    @patch('time.sleep')
    @patch('random.choice')
    def test_spend_tokens_negative_amount(self, mock_choice, mock_sleep, booth, player):
        """Test spending negative amount of tokens"""
        player.tokens = 50
        
        # Mock user inputs: negative amount, then valid amount, then exit
        booth.gui_input.side_effect = ["-5", "5", "common", "exit"]
        
        # Mock random choices
        mock_choice.side_effect = [30, "Cat"]
        
        booth.spend_tokens()
        
        # Should have called gui_print with error message
        booth.gui_print.assert_any_call("You cannot spend a negative amount of tokens.")
        
    @patch('time.sleep')
    @patch('random.choice')
    def test_spend_tokens_invalid_rarity(self, mock_choice, mock_sleep, booth, player):
        """Test spending tokens with invalid rarity"""
        player.tokens = 50
        
        # Mock user inputs: valid amount, invalid rarity, valid rarity, exit
        booth.gui_input.side_effect = ["10", "invalid", "10", "common", "exit"]
        
        # Mock random choices
        mock_choice.side_effect = [30, "Cat"]
        
        booth.spend_tokens()
        
        # Should have called gui_print with error message
        booth.gui_print.assert_any_call("\nYou must enter a valid rarity\n")
        
    @patch('time.sleep')
    @patch('random.choice')
    def test_spend_tokens_invalid_number(self, mock_choice, mock_sleep, booth, player):
        """Test spending tokens with invalid number input"""
        player.tokens = 50
        
        # Mock user inputs: invalid number, valid number, rarity, exit
        booth.gui_input.side_effect = ["abc", "10", "common", "exit"]
        
        # Mock random choices
        mock_choice.side_effect = [30, "Cat"]
        
        booth.spend_tokens()
        
        # Should have called gui_print with error message
        booth.gui_print.assert_any_call("\nERROR: Enter a valid numerical value:\n")
        
    @patch('time.sleep')
    @patch('random.choice')
    def test_spend_tokens_continue_playing(self, mock_choice, mock_sleep, booth, player):
        """Test continuing to play multiple rounds"""
        player.tokens = 100
        
        # Mock user inputs for two rounds
        booth.gui_input.side_effect = [
            "10", "common",  # First round
            "continue",      # Continue playing
            "5", "rare",     # Second round
            "exit"           # Exit
        ]
        
        # Mock random choices for two rounds
        mock_choice.side_effect = [30, "Cat", 70, "Ferret"]
        
        booth.spend_tokens()
        
        # Should have played two rounds
        assert booth.gui_input.call_count == 6  # 2 amounts + 2 rarities + 2 continue/exit prompts
        
    @patch('time.sleep')
    @patch('random.choice')
    def test_spend_tokens_invalid_continue_response(self, mock_choice, mock_sleep, booth, player):
        """Test invalid response to continue/exit prompt"""
        player.tokens = 50
        
        # Mock user inputs: valid amount, rarity, invalid response, valid response
        booth.gui_input.side_effect = ["10", "common", "invalid", "exit"]
        
        # Mock random choices
        mock_choice.side_effect = [30, "Cat"]
        
        booth.spend_tokens()
        
        # Should have called gui_print with error message
        booth.gui_print.assert_any_call("Invalid response\n")
        

        
    @patch('time.sleep')
    @patch('random.choice')
    def test_spend_tokens_with_refund(self, mock_choice, mock_sleep, booth, player):
        """Test spending tokens with refund for duplicate prize"""
        player.tokens = 50
        player.prizes[0] = ["Cat"]  # Already own this prize
        
        # Mock user inputs
        booth.gui_input.side_effect = ["10", "common", "exit"]
        
        # Mock random choices - will get Cat which is already owned
        mock_choice.side_effect = [30, "Cat"]
        
        booth.spend_tokens()
        
        # Should have refunded 3 tokens for duplicate common prize
        # 50 - 10 (rarity) - 20 (prize) + 1 (extra from rarity) + 3 (refund) = 24
        assert player.tokens == 24
        
        # Should have called gui_print with refund message
        booth.gui_print.assert_any_call("You already own this prize, refunding 3 tokens")


class TestRunGUI:
    """Test the run_gui function"""
    
    @patch('gui.tk.Tk')
    @patch('gui.GameGUI')
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
