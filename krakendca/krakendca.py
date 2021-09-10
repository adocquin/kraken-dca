from typing import List

from .config import Config
from .dca import DCA
from .pair import Pair
from krakenapi import KrakenApi


class KrakenDCA:
    """
    KrakenDCA main loop encapsulation.
    """

    config: Config
    ka: KrakenApi
    dcas_list: List[DCA]

    def __init__(self, config: Config, ka: KrakenApi):
        """
        Instantiate the KrakenDCA object.

        :param config: Config object.
        :param ka: KrakenAPI object.
        """
        self.config = config
        self.ka = ka
        self.dcas_list = []

    def initialize_dca(self):
        """
        Check if pairs exist and initialize DCA objects List
        """
        print("Hi, current DCA configuration:")
        for dca_pair in self.config.dca_pairs:
            # Initialize the Pair object from pair specified in configuration
            # file and data from Kraken.
            pair = Pair.get_pair_from_kraken(self.ka, dca_pair.get("pair"))
            # Initialize the DCA objects.
            self.dcas_list.append(DCA(
                self.ka, dca_pair.get("delay"), pair, dca_pair.get("amount")
            ))

    def handle_dca(self):
        """
        Handle pairs Dollar Cost Averaging.
        """
        # Iterate though DCA objects list and launch DCA logic.
        for dca in self.dcas_list:
            # Execute DCA logic.
            dca.handle_dca_logic()
