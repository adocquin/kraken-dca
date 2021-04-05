import yaml


class Config:
    """
    Configuration file object based on config.yaml.
    """
    api_public_key: str
    api_private_key: str
    pair: str
    amount: float

    def __init__(self):
        """
        Initialize the Config object.
        """
        self.read_config_file()

    def read_config_file(self):
        """
        Read config file and raise an error if incorrectly specified.

        :return: None
        """
        try:
            with open("config.yaml", "r") as stream:
                try:
                    config = yaml.load(stream, Loader=yaml.SafeLoader)
                    self.api_public_key = config.get("api").get("public_key")
                    self.api_private_key = config.get("api").get("private_key")
                    self.pair = config.get("dca").get("pair")
                    self.amount = config.get("dca").get("amount")
                except (AttributeError, yaml.YAMLError) as e:
                    raise ValueError(f"config.yaml file incorrectly formatted: {e}")
        except EnvironmentError:
            raise FileNotFoundError("config.yaml file not found.")
        if not self.api_public_key:
            raise TypeError("Please provide you Kraken API public key.")
        elif not self.api_private_key:
            raise TypeError("Please provide you Kraken API private key.")
        elif not self.pair:
            raise TypeError("Please provide the pair to dollar cost average.")
        elif not self.amount or self.amount <= 0:
            raise TypeError("Please provide an amount > 0 to daily dollar cost average.")
