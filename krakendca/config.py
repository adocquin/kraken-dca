import yaml
from yaml.scanner import ScannerError

CONFIG_ERROR_MSG: str = "Configuration file incorrectly formatted"


class Config:
    """
    Configuration object based on configuration file.
    """

    api_public_key: str
    api_private_key: str
    dca_pairs: list

    def __init__(self, config_file: str) -> None:
        """
        Read the configuration file and initialize the Config object.

        :param config_file: Configuration file path as string.
        :return: None
        """
        try:
            with open(config_file, "r") as stream:
                config = yaml.load(stream, Loader=yaml.SafeLoader)
            self.api_public_key = config.get("api").get("public_key")
            self.api_private_key = config.get("api").get("private_key")
            self.dca_pairs = config.get("dca_pairs")
            self.__check_configuration()
            for dca_pair in self.dca_pairs:
                self.__check_dca_pair_configuration(dca_pair)
        except EnvironmentError:
            raise FileNotFoundError("Configuration file not found.")
        except ScannerError as e:
            raise ScannerError(CONFIG_ERROR_MSG + f": {e}")

    def __check_configuration(self) -> None:
        """
        Check Config attributes and raise an error in case of missing
        parameters in configuration file.
        :return: None
        """
        try:
            if not self.api_public_key:
                raise ValueError("Please provide your Kraken API public key.")
            if not self.api_private_key:
                raise ValueError("Please provide your Kraken API private key.")
            if not self.dca_pairs or type(self.dca_pairs) is not list:
                raise ValueError("No DCA pairs specified.")
        except ValueError as e:
            raise ValueError(CONFIG_ERROR_MSG + f": {e}")

    @staticmethod
    def __check_dca_pair_configuration(dca_pair: dict) -> None:
        """
        Check DCA pair configuration parameters are currently specified.

        :param dca_pair: Dictionary with pair to DCA, and associated
        parameters.
        :return: None
        """
        try:
            # pair
            if not dca_pair.get("pair"):
                raise ValueError(
                    "Please provide the pair to dollar cost average."
                )

            # delay
            delay: int = dca_pair.get("delay")
            if not delay or type(delay) is not int or delay <= 0:
                raise ValueError(
                    "Please set the DCA days delay as a number > 0."
                )
            try:
                dca_pair["amount"]: float = float(dca_pair.get("amount"))
            except TypeError:
                raise ValueError("Please provide an amount > 0 to DCA.")

            # amount
            amount: float = dca_pair.get("amount")
            if not amount or type(amount) is not float or amount <= 0:
                raise ValueError("Please provide an amount > 0 to DCA.")

            # limit_factor
            if dca_pair.get("limit_factor"):
                try:
                    limit_factor: float = float(dca_pair.get("limit_factor"))
                    if len(str(limit_factor).split(".")[1]) > 5:
                        raise ValueError
                    dca_pair["limit_factor"]: float = limit_factor
                except ValueError:
                    raise ValueError("limit_factor option must be a number "
                                     "up to 5 digits.")

            # max_price
            if dca_pair.get("max_price"):
                try:
                    max_price: float = float(dca_pair.get("max_price"))
                    dca_pair["max_price"]: float = max_price
                except ValueError:
                    raise ValueError(
                        "max_price must be a number."
                    )
        except ValueError as e:
            raise ValueError(CONFIG_ERROR_MSG + f": {e}")
