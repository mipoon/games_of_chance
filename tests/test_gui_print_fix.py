"""
Test for the GUI print fix - ensuring multiple arguments to print work correctly.
This test covers the specific bug that was causing the GUI to crash.
"""
from unittest.mock import Mock, patch
from src.gui import GUIGameWrapper


class TestGUIPrintFix:
    """Test the fix for the GUI print issue with multiple arguments"""

    def test_gui_print_wrapper_single_argument(self):
        """Test gui_print_wrapper with single argument"""
        mock_game = Mock()
        mock_input = Mock()
        mock_output = Mock()

        wrapper = GUIGameWrapper(mock_game, mock_input, mock_output)

        # Test single argument
        wrapper.gui_print_wrapper("Hello")
        mock_output.assert_called_once_with("Hello\n")

    def test_gui_print_wrapper_multiple_arguments(self):
        """Test gui_print_wrapper with multiple arguments (the bug fix)"""
        mock_game = Mock()
        mock_input = Mock()
        mock_output = Mock()

        wrapper = GUIGameWrapper(mock_game, mock_input, mock_output)

        # Test multiple arguments (this was causing the original error)
        wrapper.gui_print_wrapper("Tokens earned:", 50, "\n")
        mock_output.assert_called_once_with("Tokens earned: 50 \n\n")

    def test_gui_print_wrapper_with_separator(self):
        """Test gui_print_wrapper with custom separator"""
        mock_game = Mock()
        mock_input = Mock()
        mock_output = Mock()

        wrapper = GUIGameWrapper(mock_game, mock_input, mock_output)

        # Test with custom separator
        wrapper.gui_print_wrapper("A", "B", "C", sep="-")
        mock_output.assert_called_once_with("A-B-C\n")

    def test_gui_print_wrapper_with_end(self):
        """Test gui_print_wrapper with custom end"""
        mock_game = Mock()
        mock_input = Mock()
        mock_output = Mock()

        wrapper = GUIGameWrapper(mock_game, mock_input, mock_output)

        # Test with custom end
        wrapper.gui_print_wrapper("Hello", end="!!!")
        mock_output.assert_called_once_with("Hello!!!")

    def test_gui_print_wrapper_empty_args(self):
        """Test gui_print_wrapper with no arguments"""
        mock_game = Mock()
        mock_input = Mock()
        mock_output = Mock()

        wrapper = GUIGameWrapper(mock_game, mock_input, mock_output)

        # Test with no arguments
        wrapper.gui_print_wrapper()
        mock_output.assert_called_once_with("\n")

    def test_gui_print_wrapper_mixed_types(self):
        """Test gui_print_wrapper with mixed argument types"""
        mock_game = Mock()
        mock_input = Mock()
        mock_output = Mock()

        wrapper = GUIGameWrapper(mock_game, mock_input, mock_output)

        # Test with mixed types (int, float, bool, None)
        wrapper.gui_print_wrapper("Value:", 42, 3.14, True, None)
        mock_output.assert_called_once_with("Value: 42 3.14 True None\n")

    @patch('builtins.print')
    def test_monkey_patching_print_with_multiple_args(self, mock_original_print):
        """Test that the monkey patching correctly handles multiple print arguments"""
        mock_game = Mock()
        mock_gui_input = Mock()
        mock_gui_output = Mock()

        # Create a mock game that calls print with multiple arguments
        def mock_play():
            print("Tokens earned:", 50, "\n")
            return 50

        mock_game.play = mock_play

        wrapper = GUIGameWrapper(mock_game, mock_gui_input, mock_gui_output)
        result = wrapper.play()

        # Verify the game returned the expected result
        assert result == 50

        # Verify that our gui_print was called with the properly formatted string
        mock_gui_output.assert_called_once_with("Tokens earned: 50 \n\n")

        # Verify original print was not called (it was monkey patched)
        mock_original_print.assert_not_called()
