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

    def initialize_pairs_dca(self):
        """
        Instantiate Pair and DCA objects from pairs specified in configuration file
        and data from Kraken.
        """
        print("Hi, current DCA configuration:")
        asset_pairs = self.ka.get_asset_pairs()
        for dca_pair in self.config.dca_pairs:
            pair = Pair.get_pair_from_kraken(self.ka, asset_pairs, dca_pair.get("pair"))
            self.dcas_list.append(DCA(
                self.ka, dca_pair.get("delay"), pair, dca_pair.get("amount")
            ))

    def handle_pairs_dca(self):
        """
        Iterate though DCA objects list and execute DCA logic..
        Handle pairs Dollar Cost Averaging.
        """
        for dca in self.dcas_list:
            dca.handle_dca_logic()
