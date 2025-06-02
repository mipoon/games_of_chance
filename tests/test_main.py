from unittest.mock import patch, Mock
import sys
import main

def test_main_function_console_default():
    """Test main function defaults to console mode"""
    with patch('builtins.input', return_value='1'), \
         patch('play_session.PlaySession.run_session') as mock_run_session:
        main.main()
        mock_run_session.assert_called_once()

def test_main_function_console_explicit():
    """Test main function with explicit console choice"""
    with patch('builtins.input', return_value='1'), \
         patch('play_session.PlaySession.run_session') as mock_run_session:
        main.main()
        mock_run_session.assert_called_once()

def test_main_function_gui_choice():
    """Test main function with GUI choice"""
    with patch('builtins.input', return_value='2'), \
         patch('main.run_gui') as mock_run_gui:
        main.main()
        mock_run_gui.assert_called_once()

def test_main_function_gui_argument():
    """Test main function with --gui argument"""
    original_argv = sys.argv.copy()
    try:
        sys.argv = ['main.py', '--gui']
        with patch('main.run_gui') as mock_run_gui:
            main.main()
            mock_run_gui.assert_called_once()
    finally:
        sys.argv = original_argv

def test_main_function_empty_input():
    """Test main function with empty input (defaults to console)"""
    with patch('builtins.input', return_value=''), \
         patch('play_session.PlaySession.run_session') as mock_run_session:
        main.main()
        mock_run_session.assert_called_once()

def test_main_function_invalid_input():
    """Test main function with invalid input (defaults to console)"""
    with patch('builtins.input', return_value='invalid'), \
         patch('play_session.PlaySession.run_session') as mock_run_session:
        main.main()
        mock_run_session.assert_called_once()

# def test_entry_point():
#     with patch('main.main') as mock_main:
#         original_name = main.__name__
#         main.__name__ = '__main__'
#         try:
#             reload(main)
#         finally:
#             main.__name__ = original_name
#         mock_main.assert_called_once()
