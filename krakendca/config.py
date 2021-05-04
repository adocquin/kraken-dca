import yaml


class Config:
    """
    Configuration object based on configuration file.
    """

    api_public_key: str
    api_private_key: str
    delay: int
    pair: str
    amount: float

    def __init__(self, config_file: str) -> None:
        """
        Read the configuration file and initialize the Config object.

        :param config_file: Configuration file path as string.
        """
        try:
            with open(config_file, "r") as stream:
                try:
                    config = yaml.load(stream, Loader=yaml.SafeLoader)
                    self.api_public_key = config.get("api").get("public_key")
                    self.api_private_key = config.get("api").get("private_key")
                    self.delay = config.get("dca").get("delay")
                    self.pair = config.get("dca").get("pair")
                    self.amount = float(config.get("dca").get("amount"))
                except (ValueError, TypeError, AttributeError, yaml.YAMLError) as e:
                    raise ValueError(f"Configuration file incorrectly formatted: {e}")
        except EnvironmentError:
            raise FileNotFoundError("Configuration file not found.")
        if not self.api_public_key:
            raise TypeError("Please provide your Kraken API public key.")
        elif not self.api_private_key:
            raise TypeError("Please provide your Kraken API private key.")
        elif not self.delay or type(self.delay) is not int or self.delay <= 0:
            raise TypeError("Please set the DCA days delay as a number > 0.")
        elif not self.pair:
            raise TypeError("Please provide the pair to dollar cost average.")
        elif not self.amount or type(self.amount) is not float or self.amount <= 0:
            raise TypeError(
                "Please provide an amount > 0 to daily dollar cost average."
            )
