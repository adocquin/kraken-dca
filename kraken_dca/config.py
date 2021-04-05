import yaml
from .kraken_api import KrakenApi


class Config:
    """
    Configuration file object based on config.yaml.
    """
    api_key: str
    api_secret: str
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
        with open("config.yaml", "r") as stream:
            try:
                config = yaml.load(stream, Loader=yaml.SafeLoader)
                self.api_key = config.get("api").get("key")
                self.api_secret = config.get("api").get("secret")
                self.pair = config.get("dca").get("pair")
                self.amount = config.get("dca").get("amount")
            except (AttributeError, yaml.YAMLError) as e:
                print(f"config.yaml file incorrectly formatted: {e}")
                return
        if not self.api_key:
            raise TypeError("Please provide you Kraken API key.")
        elif not self.api_secret:
            raise TypeError("Please provide you Kraken private key.")
        elif not self.pair:
            raise TypeError("Please provide the pair to dollar cost average using -p option.")
        elif not self.amount:
            raise TypeError("Please provide the amount to daily dollar cost average using -a option.")
        elif self.amount <= 0:
            raise ValueError("Amount configuration must be > 0.")
