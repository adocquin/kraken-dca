"""Main KrakenDCA object module."""
import logging
from typing import Any, Dict, List

from krakenapi import KrakenApi

from .config import Config
from .dca import DCA
from .pair import Pair

logger = logging.getLogger(__name__)


class KrakenDCA:
    """
    KrakenDCA main loop encapsulation.
    """

    config: Config
    ka: KrakenApi
    dcas_list: List[DCA]

    def __init__(self, config: Config, ka: KrakenApi) -> None:
        """
        Instantiate the KrakenDCA object.

        :param config: Config object.
        :param ka: KrakenAPI object.
        :return: None
        """
        self.config = config
        self.ka = ka
        self.dcas_list = []

    def initialize_pairs_dca(self) -> None:
        """
        Instantiate Pair and DCA objects from pairs specified in
        configuration file and data from Kraken.
        :return: None
        """
        logger.info("Hi, current configuration:")
        asset_pairs: Dict[str, Any] = self.ka.get_asset_pairs()
        for dca_pair in self.config.dca_pairs:
            pair: Pair = Pair.get_pair_from_kraken(
                self.ka, asset_pairs, dca_pair.get("pair")
            )
            dca: DCA = DCA(
                self.ka,
                dca_pair.get("delay"),
                pair,
                dca_pair.get("amount"),
                limit_factor=dca_pair.get("limit_factor", 1),
                max_price=dca_pair.get("max_price", -1),
                ignore_differing_orders=dca_pair.get(
                    "ignore_differing_orders", False
                ),
            )
            logger.info(dca)
            self.dcas_list.append(dca)

    def handle_pairs_dca(self) -> None:
        """
        Iterate though DCA objects list and execute DCA logic.
        Handle pairs Dollar Cost Averaging.
        :return: None
        """
        pair: str = "pair"
        n_dca: int = len(self.dcas_list)
        if n_dca > 1:
            pair += "s"

        logger.info(f"DCA ({n_dca} {pair}):")
        for dca in self.dcas_list:
            logger.info(dca)
            dca.handle_dca_logic()
