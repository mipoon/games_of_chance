from unittest.mock import patch
import main

def test_main_function_gui_only():
    """Test main function only launches GUI"""
    with patch('main.run_gui') as mock_run_gui:
        main.main()
        mock_run_gui.assert_called_once()
