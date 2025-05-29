import pytest
from unittest.mock import patch
import main
from importlib import reload

def test_main_function():
    with patch('play_session.PlaySession.run_session') as mock_run_session:
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
