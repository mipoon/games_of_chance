from src.helpers.clear_output import clear_output


def test_clear_output(mocker):
    # Mock os.system to raise an exception so it falls back to print
    mocker.patch("src.helpers.clear_output.os.system", side_effect=Exception("Mock exception"))
    mock_print = mocker.patch("builtins.print")

    clear_output()

    mock_print.assert_called_once_with("\n" * 100)
