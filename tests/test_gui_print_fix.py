"""
Test for the GUI print fix - ensuring multiple arguments to print work correctly.
This test covers the specific bug that was causing the GUI to crash.
"""
from unittest.mock import Mock, patch
import queue
from src.gui import GameWrapper, GameIOHandler


class TestGUIPrintFix:
    """Test the fix for the GUI print issue with multiple arguments"""

    def test_gui_print_wrapper_single_argument(self):
        """Test _print_wrapper with single argument"""
        mock_game = Mock()
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)
        wrapper = GameWrapper(mock_game, io_handler)

        # Test single argument
        wrapper._print_wrapper("Hello")
        
        # Check that the message was sent to the output queue
        assert not output_queue.empty()
        message = output_queue.get()
        assert message == "Hello\n\n"  # GameIOHandler adds extra \n

    def test_gui_print_wrapper_multiple_arguments(self):
        """Test _print_wrapper with multiple arguments (the bug fix)"""
        mock_game = Mock()
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)
        wrapper = GameWrapper(mock_game, io_handler)

        # Test multiple arguments (this was causing the original error)
        wrapper._print_wrapper("Tokens earned:", 50, "\n")
        
        # Check that the message was sent to the output queue
        assert not output_queue.empty()
        message = output_queue.get()
        assert message == "Tokens earned: 50 \n\n\n"  # GameIOHandler adds extra \n

    def test_gui_print_wrapper_with_separator(self):
        """Test _print_wrapper with custom separator"""
        mock_game = Mock()
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)
        wrapper = GameWrapper(mock_game, io_handler)

        # Test with custom separator
        wrapper._print_wrapper("A", "B", "C", sep="-")
        
        # Check that the message was sent to the output queue
        assert not output_queue.empty()
        message = output_queue.get()
        assert message == "A-B-C\n\n"  # GameIOHandler adds extra \n

    def test_gui_print_wrapper_with_end(self):
        """Test _print_wrapper with custom end"""
        mock_game = Mock()
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)
        wrapper = GameWrapper(mock_game, io_handler)

        # Test with custom end
        wrapper._print_wrapper("Hello", end="!!!")
        
        # Check that the message was sent to the output queue
        assert not output_queue.empty()
        message = output_queue.get()
        assert message == "Hello!!!\n"  # GameIOHandler adds \n

    def test_gui_print_wrapper_empty_args(self):
        """Test _print_wrapper with no arguments"""
        mock_game = Mock()
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)
        wrapper = GameWrapper(mock_game, io_handler)

        # Test with no arguments
        wrapper._print_wrapper()
        
        # Check that the message was sent to the output queue
        assert not output_queue.empty()
        message = output_queue.get()
        assert message == "\n\n"  # GameIOHandler adds extra \n

    def test_gui_print_wrapper_mixed_types(self):
        """Test _print_wrapper with mixed argument types"""
        mock_game = Mock()
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)
        wrapper = GameWrapper(mock_game, io_handler)

        # Test with mixed types (int, float, bool, None)
        wrapper._print_wrapper("Value:", 42, 3.14, True, None)
        
        # Check that the message was sent to the output queue
        assert not output_queue.empty()
        message = output_queue.get()
        assert message == "Value: 42 3.14 True None\n\n"  # GameIOHandler adds extra \n

    @patch('builtins.print')
    def test_monkey_patching_print_with_multiple_args(self, mock_original_print):
        """Test that the monkey patching correctly handles multiple print arguments"""
        mock_game = Mock()
        input_queue = queue.Queue()
        output_queue = queue.Queue()
        io_handler = GameIOHandler(input_queue, output_queue)

        # Create a mock game that calls print with multiple arguments
        def mock_play():
            print("Tokens earned:", 50, "\n")
            return 50

        mock_game.play = mock_play

        wrapper = GameWrapper(mock_game, io_handler)
        result = wrapper.play()

        # Verify the game returned the expected result
        assert result == 50

        # Verify that our output was sent to the queue
        assert not output_queue.empty()
        message = output_queue.get()
        assert message == "Tokens earned: 50 \n\n\n"  # GameIOHandler adds extra \n

        # Verify original print was not called (it was monkey patched)
        mock_original_print.assert_not_called()
