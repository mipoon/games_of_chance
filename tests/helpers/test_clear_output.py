from src.helpers.clear_output import clear_output, clear_output_simple, clear_output_ansi


def test_clear_output_windows(mocker):
    """Test clear_output on Windows."""
    mocker.patch("src.helpers.clear_output.os.name", "nt")
    mock_system = mocker.patch("src.helpers.clear_output.os.system")

    clear_output()

    mock_system.assert_called_once_with("cls")


def test_clear_output_unix(mocker):
    """Test clear_output on Unix/Linux/MacOS."""
    mocker.patch("src.helpers.clear_output.os.name", "posix")
    mock_system = mocker.patch("src.helpers.clear_output.os.system")

    clear_output()

    mock_system.assert_called_once_with("clear")


def test_clear_output_exception_fallback(mocker):
    """Test clear_output falls back to print when os.system raises exception."""
    mocker.patch("src.helpers.clear_output.os.system", side_effect=Exception("Mock exception"))
    mock_print = mocker.patch("builtins.print")

    clear_output()

    mock_print.assert_called_once_with("\n" * 100)


def test_clear_output_simple(mocker):
    """Test clear_output_simple function."""
    mock_print = mocker.patch("builtins.print")

    clear_output_simple()

    mock_print.assert_called_once_with("\n" * 100)


def test_clear_output_ansi_success(mocker):
    """Test clear_output_ansi successful execution."""
    mock_stdout = mocker.patch("src.helpers.clear_output.sys.stdout")

    clear_output_ansi()

    mock_stdout.write.assert_called_once_with('\033[2J\033[H')
    mock_stdout.flush.assert_called_once()


def test_clear_output_ansi_exception_fallback(mocker):
    """Test clear_output_ansi falls back to simple method on exception."""
    mock_stdout = mocker.patch("src.helpers.clear_output.sys.stdout")
    mock_stdout.write.side_effect = Exception("Mock exception")
    mock_print = mocker.patch("builtins.print")

    clear_output_ansi()

    mock_print.assert_called_once_with("\n" * 100)
