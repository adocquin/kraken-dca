from yaml.scanner import ScannerError
from krakendca import Config
from unittest import mock
import pytest


def get_correct_config() -> str:
    """
    Open correct config.yaml file in tests/fixtures folder and return content as string.

    :return: Correct config.yaml file content as string.
    """
    with open("tests/fixtures/config.yaml", "r") as stream:
        correct_config = stream.read()
    return correct_config


def test_default_config_file_is_correct():
    # Test if config.yaml has changed.
    correct_config = get_correct_config()
    with open("config.yaml", "r") as stream:
        config = stream.read()
    assert config == correct_config


def assert_dca_pair(dca_pair: dict, pair: str, delay: int, amount: float):
    assert type(dca_pair.get("pair")) == str
    assert dca_pair.get("pair") == pair
    assert type(dca_pair.get("delay")) == int
    assert dca_pair.get("delay") == delay
    assert type(dca_pair.get("amount")) == float
    assert dca_pair.get("amount") == amount


def test_config_properties():
    # Test object properties are correctly assigned.
    config = Config("config.yaml")
    assert type(config.api_public_key) == str
    assert config.api_public_key == "KRAKEN_API_PUBLIC_KEY"
    assert type(config.api_private_key) == str
    assert config.api_private_key == "KRAKEN_API_PRIVATE_KEY"
    assert type(config.dca_pairs) == list
    assert len(config.dca_pairs) == 2
    assert_dca_pair(config.dca_pairs[0], "XETHZEUR", 1, 15)
    assert_dca_pair(config.dca_pairs[1], "XXBTZEUR", 3, 20)


def mock_config_error(config: str, error_type: type) -> str:
    """
    Mock configuration file error and return the error.

    :param config: Configuration to use as string.
    :param error_type: Raised error type to catch.
    :return: Error value as string.
    """
    mock_file = mock.mock_open(read_data=config)
    with mock.patch("builtins.open", mock_file) as mock_open:
        if error_type == FileNotFoundError:
            mock_open.side_effect = FileNotFoundError()
        with pytest.raises(error_type) as e_info:
            Config("config.yaml")
    e_info_value = str(e_info.value)
    return e_info_value


def test_config_errors():
    # Load test config.yaml file.
    correct_config = get_correct_config()

    # Test raise FileNotFoundError.
    e_info_value = mock_config_error(correct_config, FileNotFoundError)
    assert "Configuration file not found." in e_info_value

    # Test raise ScannerError.
    config_scanner_error = correct_config.replace("api:", "api")
    e_info_value = mock_config_error(config_scanner_error, ScannerError)
    assert "Configuration file incorrectly formatted:" in e_info_value

    # Test missing public key.
    config_empty_api_public_key = correct_config.replace(
        'public_key: "KRAKEN_API_PUBLIC_KEY"', ""
    )
    e_info_value = mock_config_error(config_empty_api_public_key, ValueError)
    assert "Please provide your Kraken API public key." in e_info_value

    # Test missing private key.
    config_empty_api_private_key = correct_config.replace(
        'private_key: "KRAKEN_API_PRIVATE_KEY"', ""
    )
    e_info_value = mock_config_error(config_empty_api_private_key, ValueError)
    assert "Please provide your Kraken API private key." in e_info_value

    # Test missing pairs
    config_missing_pairs = correct_config.replace("dca_pairs:", "dca:")
    e_info_value = mock_config_error(config_missing_pairs, ValueError)
    assert "No DCA pairs specified." in e_info_value

    # Test missing pair name.
    config_empty_pair = correct_config.replace('pair: "XETHZEUR"', "")
    e_info_value = mock_config_error(config_empty_pair, ValueError)
    assert "Please provide the pair to dollar cost average." in e_info_value

    # Test missing amount.
    config_missing_amount = correct_config.replace("amount: 20", "")
    e_info_value = mock_config_error(config_missing_amount, ValueError)
    assert "Configuration file incorrectly formatted:" in e_info_value

    # Test amount = 0.
    config_zero_amount = correct_config.replace("amount: 20", "amount: 0")
    e_info_value = mock_config_error(config_zero_amount, ValueError)
    assert "Please provide an amount > 0 to DCA." in e_info_value

    # Test amount < 0.
    config_below_zero_amount = correct_config.replace("amount: 20", "amount: -100")
    e_info_value = mock_config_error(config_below_zero_amount, ValueError)
    assert "Please provide an amount > 0 to DCA." in e_info_value
