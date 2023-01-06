"""config.py tests module."""
from unittest import mock

import pytest
from krakendca.config import Config
from yaml.scanner import ScannerError


def get_config() -> str:
    """
    Open correct config.yaml file in tests/fixtures folder and return
    content as string.

    :return: Correct config.yaml file content as string.
    """
    with open("tests/fixtures/config.yaml", "r") as stream:
        config = stream.read()
    return config


def test_default_config_file_is_correct() -> None:
    """Test if config.yaml has changed."""
    correct_config: str = get_config()
    with open("config-sample.yaml", "r") as stream:
        config: str = stream.read()
    assert config == correct_config


def assert_dca_pair(
    dca_pair: dict,
    pair: str,
    delay: int,
    amount: float,
    limit_factor: float = None,
    max_price: float = None,
    ignore_differing_orders: bool = False,
) -> None:
    assert type(dca_pair.get("pair")) == str
    assert dca_pair.get("pair") == pair
    assert type(dca_pair.get("delay")) == int
    assert dca_pair.get("delay") == delay
    assert type(dca_pair.get("amount")) == float
    assert dca_pair.get("amount") == amount
    if limit_factor:
        assert type(dca_pair.get("limit_factor")) == float
        assert dca_pair.get("limit_factor") == limit_factor
    if max_price:
        assert type(dca_pair.get("max_price")) == float
        assert dca_pair.get("max_price") == max_price
    if ignore_differing_orders:
        assert (
            dca_pair.get("ignore_differing_orders") == ignore_differing_orders
        )


def test_config_properties() -> None:
    # Test object properties are correctly assigned.
    config = Config("config-sample.yaml")
    assert type(config.api_public_key) == str
    assert config.api_public_key == "KRAKEN_API_PUBLIC_KEY"
    assert type(config.api_private_key) == str
    assert config.api_private_key == "KRAKEN_API_PRIVATE_KEY"
    assert type(config.dca_pairs) == list
    assert len(config.dca_pairs) == 2
    assert_dca_pair(config.dca_pairs[0], "XETHZEUR", 1, 15, 0.985, 2900.10)
    assert_dca_pair(
        config.dca_pairs[1], "XXBTZEUR", 3, 20, ignore_differing_orders=True
    )


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
            Config("config-sample.yaml")
    e_info: str = str(e_info.value)
    return e_info


class TestConfig:
    """Test Config class"""

    config: str

    def setup(self) -> None:
        """Load test config.yaml file."""
        self.config = get_config()

    def test_raise_file_not_found_error(self) -> None:
        """Test raise FileNotFoundError."""
        e_info: str = mock_config_error(self.config, FileNotFoundError)
        assert "Configuration file not found." in e_info

    def test_raise_scanner_error(self) -> None:
        """Test raise ScannerError."""
        bad_config: str = self.config.replace("api:", "api")
        e_info: str = mock_config_error(bad_config, ScannerError)
        assert "Configuration file incorrectly formatted:" in e_info

    def test_missing_public_key(self) -> None:
        """Test missing public key."""
        bad_config: str = self.config.replace(
            'public_key: "KRAKEN_API_PUBLIC_KEY"', ""
        )
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "Please provide your Kraken API public key." in e_info

    def test_missing_private_key(self) -> None:
        """Test missing private key."""
        bad_config: str = self.config.replace(
            'private_key: "KRAKEN_API_PRIVATE_KEY"', ""
        )
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "Please provide your Kraken API private key." in e_info

    def test_missing_pairs(self) -> None:
        """Test missing pairs."""
        bad_config: str = self.config.replace("dca_pairs:", "dca:")
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "No DCA pairs specified." in e_info

    def test_missing_pair_name(self) -> None:
        """Test missing pair name."""
        bad_config: str = self.config.replace('pair: "XETHZEUR"', "")
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "Please provide the pair to dollar cost average." in e_info

    def test_missing_amount(self) -> None:
        """Test missing amount."""
        bad_config: str = self.config.replace("amount: 20", "")
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "Configuration file incorrectly formatted:" in e_info

    def test_delay_below_zero(self) -> None:
        """Test delay < 0."""
        bad_config: str = self.config.replace("delay: 1", "delay: -100")
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "Please set the DCA days delay as a number > 0." in e_info

    def test_delay_not_int(self) -> None:
        """Test delay is not an int."""
        bad_config: str = self.config.replace("delay: 1", "delay: error")
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "Please set the DCA days delay as a number > 0." in e_info

    def test_zero_amount(self) -> None:
        """Test amount = 0."""
        bad_config: str = self.config.replace("amount: 20", "amount: 0")
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "Please provide an amount > 0 to DCA." in e_info

    def test_amount_below_zero(self) -> None:
        """Test amount < 0."""
        bad_config: str = self.config.replace("amount: 20", "amount: -100")
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "Please provide an amount > 0 to DCA." in e_info

    def test_limit_factor_is_not_a_number(self) -> None:
        """Test limit_factor is not a number."""
        bad_config: str = self.config.replace(
            "limit_factor: 0.985", "limit_factor: error"
        )
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "limit_factor option must be a number up to 5 digits." in e_info

    def test_limit_factor_must_have_five_digits(self) -> None:
        """Test limit_factor have more than 5 digits."""
        bad_config: str = self.config.replace(
            "limit_factor: 0.985", "limit_factor: 0.985123"
        )
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "limit_factor option must be a number up to 5 digits." in e_info

    def test_max_price_is_not_a_number(self) -> None:
        """Test max_price is not a number."""
        bad_config: str = self.config.replace(
            "max_price: 2900.10", "max_price: error"
        )
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "max_price must be a number." in e_info

    def test_ignore_differing_orders_is_not_boolean(self) -> None:
        """Test ignore_differing_orders is not boolean."""
        bad_config: str = self.config.replace(
            "ignore_differing_orders: True", "ignore_differing_orders: error"
        )
        e_info: str = mock_config_error(bad_config, ValueError)
        assert "ignore_differing_orders must be a boolean." in e_info
