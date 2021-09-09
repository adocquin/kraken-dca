from .config import Config
from.dca import DCA
from .pair import Pair
from krakenapi import KrakenApi


class KrakenDCA():
    """
    KrakenDCA main loop encapsulation.
    """
    config: Config
    ka: KrakenApi

    def __init__(self, config: Config, ka: KrakenApi):
        """
        Instantiate the KrakenDCA object.

        :param config: Config object.
        :param ka: KrakenAPI object.
        """
        self.config = config
        self.ka = ka

    def handle_dca(self):
        """
        Handle pairs Dollar Cost Averaging.
        """
        for dca_pair in self.config.dca_pairs:
            # Initialize the Pair object from pair specified in configuration
            # file and data from Kraken.
            pair = Pair.get_pair_from_kraken(self.ka, dca_pair.get("pair"))
            # Initialize the DCA object.
            dca = DCA(self.ka, dca_pair.get("delay"), pair, dca_pair.get("amount"))
            # Execute DCA logic.
            # dca.handle_dca_logic()



