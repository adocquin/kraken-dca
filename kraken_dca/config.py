import yaml


class Config:
    """
    Configuration object based on configuration file.
    """

    api_public_key: str
    api_private_key: str
    pair: str
    amount: float

    @classmethod
    def read_config_file(cls, config_file: str):
        """
        Read the configuration file and initialize the Config object.

        :param config_file: Configuration file path as string.
        :return: Created Config object.
        """
        try:
            with open(config_file, "r") as stream:
                try:
                    config = yaml.load(stream, Loader=yaml.SafeLoader)
                    cls.api_public_key = config.get("api").get("public_key")
                    cls.api_private_key = config.get("api").get("private_key")
                    cls.pair = config.get("dca").get("pair")
                    cls.amount = float(config.get("dca").get("amount"))
                except (TypeError, AttributeError, yaml.YAMLError) as e:
                    raise ValueError(f"config.yaml file incorrectly formatted: {e}")
        except EnvironmentError:
            raise FileNotFoundError("config.yaml file not found.")
        if not cls.api_public_key:
            raise TypeError("Please provide your Kraken API public key.")
        elif not cls.api_private_key:
            raise TypeError("Please provide your Kraken API private key.")
        elif not cls.pair:
            raise TypeError("Please provide the pair to dollar cost average.")
        elif not cls.amount or cls.amount <= 0:
            raise TypeError(
                "Please provide an amount > 0 to daily dollar cost average."
            )
        return cls
