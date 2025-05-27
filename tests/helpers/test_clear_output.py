from helpers.clear_output import clear_output

def test_clear_output(mocker):
    mock_print = mocker.patch("builtins.print")
    clear_output()
    mock_print.assert_called_once_with("\n" * 100)