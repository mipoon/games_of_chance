import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import queue
import threading
import time
from gui import GameGUI, GUIPlaySession, GUIGameWrapper, GUIPrizeBooth, run_gui
from player import Player


class TestGameGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during testing
        
    def tearDown(self):
        if self.root:
            self.root.destroy()
            
    def test_game_gui_init(self):
        """Test GameGUI initialization"""
        gui = GameGUI(self.root, auto_start=False)
        
        # Check that UI components are created
        self.assertIsNotNone(gui.info_frame)
        self.assertIsNotNone(gui.conversation_frame)
        self.assertIsNotNone(gui.input_frame)
        self.assertIsNotNone(gui.name_label)
        self.assertIsNotNone(gui.tokens_label)
        self.assertIsNotNone(gui.prizes_label)
        self.assertIsNotNone(gui.conversation_text)
        self.assertIsNotNone(gui.input_entry)
        self.assertIsNotNone(gui.send_button)
        self.assertIsNotNone(gui.end_game_button)
        
        # Check initial state
        self.assertFalse(gui.waiting_for_input)
        self.assertFalse(gui.game_running)  # Should be False when auto_start=False
        
    def test_add_to_conversation(self):
        """Test adding text to conversation area"""
        gui = GameGUI(self.root, auto_start=False)
        test_text = "Test message"
        
        gui.add_to_conversation(test_text)
        
        # Get the text from the conversation widget
        content = gui.conversation_text.get("1.0", tk.END)
        self.assertIn(test_text, content)
        
    def test_update_player_info(self):
        """Test updating player information display"""
        gui = GameGUI(self.root, auto_start=False)
        
        gui.update_player_info("TestPlayer|100|5")
        
        self.assertEqual(gui.name_label.cget("text"), "Player: TestPlayer")
        self.assertEqual(gui.tokens_label.cget("text"), "Tokens: 100")
        self.assertEqual(gui.prizes_label.cget("text"), "Prizes: 5")
        
    def test_send_input_when_waiting(self):
        """Test sending input when waiting for input"""
        gui = GameGUI(self.root, auto_start=False)
        gui.waiting_for_input = True
        gui.input_entry.insert(0, "test input")
        
        gui.send_input()
        
        # Check that input was queued
        self.assertFalse(gui.input_queue.empty())
        input_value = gui.input_queue.get()
        self.assertEqual(input_value, "test input")
        
        # Check that entry was cleared
        self.assertEqual(gui.input_entry.get(), "")
        
    def test_send_input_when_not_waiting(self):
        """Test sending input when not waiting for input"""
        gui = GameGUI(self.root, auto_start=False)
        gui.waiting_for_input = False
        gui.input_entry.insert(0, "test input")
        
        gui.send_input()
        
        # Check that input was not queued
        self.assertTrue(gui.input_queue.empty())
        
    def test_on_closing(self):
        """Test window closing behavior"""
        gui = GameGUI(self.root, auto_start=False)
        gui.game_running = True
        
        # Mock the root methods to prevent actual closing during test
        gui.root.quit = Mock()
        gui.root.destroy = Mock()
        
        gui.on_closing()
        
        self.assertFalse(gui.game_running)
        gui.root.quit.assert_called_once()
        gui.root.destroy.assert_called_once()


class TestGUIPlaySession(unittest.TestCase):
    def setUp(self):
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        
    def test_gui_play_session_init(self):
        """Test GUIPlaySession initialization"""
        session = GUIPlaySession(self.input_queue, self.output_queue)
        
        self.assertEqual(session.input_queue, self.input_queue)
        self.assertEqual(session.output_queue, self.output_queue)
        self.assertIsNotNone(session.db)
        self.assertIsNotNone(session.player)
        self.assertIsNotNone(session.prize_booth)
        
    def test_gui_print(self):
        """Test GUI print functionality"""
        session = GUIPlaySession(self.input_queue, self.output_queue)
        
        session.gui_print("Test message")
        
        self.assertFalse(self.output_queue.empty())
        message = self.output_queue.get()
        self.assertEqual(message, "Test message\n")
        
    def test_gui_input(self):
        """Test GUI input functionality"""
        session = GUIPlaySession(self.input_queue, self.output_queue)
        
        # Put input in queue
        self.input_queue.put("test input")
        
        # Start input in a thread to avoid blocking
        result = []
        def get_input():
            result.append(session.gui_input("Enter something: "))
            
        thread = threading.Thread(target=get_input)
        thread.start()
        thread.join(timeout=1)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "test input")
        
        # Check that prompt and signals were sent
        messages = []
        while not self.output_queue.empty():
            messages.append(self.output_queue.get())
            
        self.assertIn("Enter something: \n", messages)
        self.assertIn("WAITING_FOR_INPUT", messages)
        self.assertIn("INPUT_RECEIVED", messages)
        
    def test_update_player_display(self):
        """Test player display update"""
        session = GUIPlaySession(self.input_queue, self.output_queue)
        session.player.name = "TestPlayer"
        session.player.tokens = 100
        session.player.prizes = [["Cat"], ["Bird"], [], [], []]
        
        session.update_player_display()
        
        self.assertFalse(self.output_queue.empty())
        message = self.output_queue.get()
        self.assertEqual(message, "UPDATE_PLAYER_INFO:TestPlayer|100|2")
        
    @patch('gui.GUIPlaySession.gui_input')
    @patch('gui.GUIPlaySession.gui_print')
    @patch('db.Database')
    def test_setup_player_new(self, mock_db_class, mock_print, mock_input):
        """Test setting up a new player"""
        mock_db = Mock()
        mock_db.does_user_exist.return_value = False
        mock_db_class.return_value = mock_db
        mock_input.return_value = "NewPlayer"
        
        session = GUIPlaySession(self.input_queue, self.output_queue)
        session.db = mock_db  # Manually set the mock
        session.setup_player()
        
        self.assertEqual(session.player.name, "NewPlayer")
        self.assertEqual(session.player.tokens, 30)
        self.assertEqual(session.player.prizes, [[], [], [], [], []])
        mock_db.add_user_data.assert_called_once_with("NewPlayer")
        
    @patch('gui.GUIPlaySession.gui_input')
    @patch('gui.GUIPlaySession.gui_print')
    @patch('db.Database')
    def test_setup_player_existing(self, mock_db_class, mock_print, mock_input):
        """Test setting up an existing player"""
        mock_db = Mock()
        mock_db.does_user_exist.return_value = True
        mock_db.get_user_data.return_value = {
            "tokens": 50,
            "prizes": [["Cat"], [], [], [], []]
        }
        mock_db_class.return_value = mock_db
        mock_input.return_value = "ExistingPlayer"
        
        session = GUIPlaySession(self.input_queue, self.output_queue)
        session.db = mock_db  # Manually set the mock
        session.setup_player()
        
        self.assertEqual(session.player.name, "ExistingPlayer")
        self.assertEqual(session.player.tokens, 50)
        self.assertEqual(session.player.prizes, [["Cat"], [], [], [], []])


class TestGUIGameWrapper(unittest.TestCase):
    def test_gui_game_wrapper_init(self):
        """Test GUIGameWrapper initialization"""
        mock_game = Mock()
        mock_input = Mock()
        mock_output = Mock()
        
        wrapper = GUIGameWrapper(mock_game, mock_input, mock_output)
        
        self.assertEqual(wrapper.game, mock_game)
        self.assertEqual(wrapper.gui_input, mock_input)
        self.assertEqual(wrapper.gui_print, mock_output)
        
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
        
        self.assertEqual(result, 50)
        mock_game.play.assert_called_once()


class TestGUIPrizeBooth(unittest.TestCase):
    def setUp(self):
        self.player = Player()
        self.player.name = "TestPlayer"
        self.player.tokens = 100
        self.player.prizes = [[], [], [], [], []]
        self.mock_input = Mock()
        self.mock_output = Mock()
        self.mock_update = Mock()
        
    def test_gui_prize_booth_init(self):
        """Test GUIPrizeBooth initialization"""
        booth = GUIPrizeBooth(self.player, self.mock_input, self.mock_output, self.mock_update)
        
        self.assertEqual(booth.user, self.player)
        self.assertEqual(booth.gui_input, self.mock_input)
        self.assertEqual(booth.gui_print, self.mock_output)
        self.assertEqual(booth.update_display, self.mock_update)
        
    @patch('random.choice')
    def test_spend_for_rarity_common(self, mock_choice):
        """Test spending for common rarity"""
        mock_choice.return_value = 30
        booth = GUIPrizeBooth(self.player, self.mock_input, self.mock_output, self.mock_update)
        
        rarity, extra = booth.spend_for_rarity("common", 10)
        
        self.assertEqual(rarity, "common")
        self.assertEqual(extra, 1)  # 10 % 3 = 1
        
    @patch('random.choice')
    def test_spend_for_rarity_legendary(self, mock_choice):
        """Test spending for legendary rarity"""
        mock_choice.return_value = 110
        booth = GUIPrizeBooth(self.player, self.mock_input, self.mock_output, self.mock_update)
        
        rarity, extra = booth.spend_for_rarity("legendary", 9)
        
        self.assertEqual(rarity, "legendary")
        self.assertEqual(extra, 0)  # 9 % 3 = 0
        
    @patch('random.choice')
    def test_select_prize_common(self, mock_choice):
        """Test selecting a common prize"""
        mock_choice.return_value = "Cat"
        booth = GUIPrizeBooth(self.player, self.mock_input, self.mock_output, self.mock_update)
        
        prize = booth.select_prize("common")
        
        self.assertEqual(prize, "Cat")
        
    @patch('random.choice')
    def test_select_prize_legendary(self, mock_choice):
        """Test selecting a legendary prize"""
        mock_choice.return_value = "Elephant"
        booth = GUIPrizeBooth(self.player, self.mock_input, self.mock_output, self.mock_update)
        
        prize = booth.select_prize("legendary")
        
        self.assertEqual(prize, "Elephant")
        
    def test_select_prize_invalid_rarity(self):
        """Test selecting prize with invalid rarity"""
        booth = GUIPrizeBooth(self.player, self.mock_input, self.mock_output, self.mock_update)
        
        with self.assertRaises(ValueError):
            booth.select_prize("invalid")
            
    def test_refund_rerolls_existing_prize(self):
        """Test refund for existing prize"""
        self.player.prizes[0] = ["Cat"]  # Common prize
        booth = GUIPrizeBooth(self.player, self.mock_input, self.mock_output, self.mock_update)
        
        refund = booth.refund_rerolls("Cat", "common")
        
        self.assertEqual(refund, 3)
        
    def test_refund_rerolls_new_prize(self):
        """Test no refund for new prize"""
        booth = GUIPrizeBooth(self.player, self.mock_input, self.mock_output, self.mock_update)
        
        refund = booth.refund_rerolls("Dog", "common")
        
        self.assertEqual(refund, 0)
        
    def test_refund_rerolls_all_rarities(self):
        """Test refund amounts for all rarities"""
        booth = GUIPrizeBooth(self.player, self.mock_input, self.mock_output, self.mock_update)
        
        # Set up existing prizes
        self.player.prizes[0] = ["Cat"]      # Common
        self.player.prizes[1] = ["Bird"]     # Odd
        self.player.prizes[2] = ["Ferret"]   # Rare
        self.player.prizes[3] = ["Butterfly"] # Epic
        self.player.prizes[4] = ["Elephant"] # Legendary
        
        # Test refunds
        self.assertEqual(booth.refund_rerolls("Cat", "common"), 3)
        self.assertEqual(booth.refund_rerolls("Bird", "odd"), 5)
        self.assertEqual(booth.refund_rerolls("Ferret", "rare"), 7)
        self.assertEqual(booth.refund_rerolls("Butterfly", "epic"), 10)
        self.assertEqual(booth.refund_rerolls("Elephant", "legendary"), 20)


class TestRunGUI(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
