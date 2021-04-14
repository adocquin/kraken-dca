from kraken_dca import Config
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


def test_config_is_correct():
    # Test if config.yaml has changed.
    correct_config = get_correct_config()
    with open("config.yaml", "r") as stream:
        config = stream.read()
    assert config == correct_config


def test_config_properties():
    # Test object properties are correctly assigned.
    config = Config("config.yaml")
    assert type(config.api_public_key) == str
    assert config.api_public_key
    assert type(config.api_private_key) == str
    assert config.api_private_key
    assert type(config.pair) == str
    assert config.pair
    assert type(config.amount) == float
    assert config.amount > 0


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
    assert "config.yaml file not found." in e_info_value

    # Test missing public key.
    config_empty_api_public_key = correct_config.replace(
        'public_key: "KRAKEN_API_PUBLIC_KEY"', ""
    )
    e_info_value = mock_config_error(config_empty_api_public_key, TypeError)
    assert "Please provide your Kraken API public key." in e_info_value

    # Test missing private key.
    config_empty_api_private_key = correct_config.replace(
        'private_key: "KRAKEN_API_PRIVATE_KEY"', ""
    )
    e_info_value = mock_config_error(config_empty_api_private_key, TypeError)
    assert "Please provide your Kraken API private key." in e_info_value

    # Test missing pair.
    config_empty_pair = correct_config.replace('pair: "XETHZEUR"', "")
    e_info_value = mock_config_error(config_empty_pair, TypeError)
    assert "Please provide the pair to dollar cost average." in e_info_value

    # Test missing amount.
    config_missing_amount = correct_config.replace("amount: 20", "")
    e_info_value = mock_config_error(config_missing_amount, ValueError)
    assert "config.yaml file incorrectly formatted:" in e_info_value

    # Test amount = 0.
    config_zero_amount = correct_config.replace("amount: 20", "amount: 0")
    e_info_value = mock_config_error(config_zero_amount, TypeError)
    assert "Please provide an amount > 0 to daily dollar cost average." in e_info_value

    # Test amount < 0.
    config_below_zero_amount = correct_config.replace("amount: 20", "amount: -100")
    e_info_value = mock_config_error(config_below_zero_amount, TypeError)
    assert "Please provide an amount > 0 to daily dollar cost average." in e_info_value
