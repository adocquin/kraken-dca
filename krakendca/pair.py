from typing import TypeVar

from krakenapi import KrakenApi

from .utils import find_nested_dictionary

T = TypeVar("T", bound="Pair")


class Pair:
    """
    Kraken pair encapsulation.
    """

    name: str
    alt_name: str
    base: str
    quote: str
    pair_decimals: int
    lot_decimals: int
    quote_decimals: int
    order_min: float

    def __init__(
            self,
            name: str,
            alt_name: str,
            base: str,
            quote: str,
            pair_decimals: int,
            lot_decimals: int,
            quote_decimals: int,
            order_min: float,
    ) -> None:
        """
        Initialize the Pair object.

        :param name:  Pair name.
        :param alt_name: Pair alternative name.
        :param base: Pair base asset.
        :param quote: Pair quote asset.
        :param pair_decimals: Pair decimals.
        :param lot_decimals: Pair lot decimals.
        :param quote_decimals: Pair quote asset decimals.
        :param order_min: Pair minimum order size.
        """
        self.name = name
        self.alt_name = alt_name
        self.base = base
        self.quote = quote
        self.pair_decimals = pair_decimals
        self.lot_decimals = lot_decimals
        self.quote_decimals = quote_decimals
        self.order_min = order_min

    @classmethod
    def get_pair_from_kraken(cls, ka: KrakenApi, asset_pairs: dict,
                             pair: str) -> T:
        """
        Initialize the Pair object using KrakenAPI and provided pair.

        :param ka: KrakenApi object.
        :param asset_pairs: Dictionary of available pairs on Kraken got through the API.
        :param pair: Pair to dollar cost average as string.
        :return: Instanced Pair object.
        """
        pair_information = cls.get_pair_information(asset_pairs, pair)
        alt_name = pair_information.get("altname")
        base = pair_information.get("base")
        quote = pair_information.get("quote")
        pair_decimals = pair_information.get("pair_decimals")
        lot_decimals = pair_information.get("lot_decimals")
        order_min = float(pair_information.get("ordermin"))
        quote_information = cls.get_asset_information(ka, quote)
        quote_decimals = quote_information.get("decimals")
        return cls(
            pair,
            alt_name,
            base,
            quote,
            pair_decimals,
            lot_decimals,
            quote_decimals,
            order_min,
        )

    @staticmethod
    def get_pair_information(asset_pairs: dict, pair: str) -> dict:
        """
        Return pair information from Kraken API.

        :param asset_pairs: Dictionary of available pairs on Kraken got through the API.
        :param pair: Pair to find.
        :return: Dict of pair information.
        """
        pair_information = find_nested_dictionary(asset_pairs, pair)
        if not pair_information:
            available_pairs = [pair for pair in asset_pairs]
            raise ValueError(
                f"{pair} pair not available on Kraken. Available pairs: {available_pairs}."
            )
        return pair_information

    @staticmethod
    def get_asset_information(ka: KrakenApi, asset: str) -> dict:
        """
        Return asset information from Kraken API.

        :param ka: KrakenAPI object.
        :param asset: Asset to find.
        :return: Dict of asset information.
        """
        assets = ka.get_assets()
        asset_information = find_nested_dictionary(assets, asset)
        if not asset_information:
            available_assets = [asset for asset in assets]
            raise ValueError(
                f"{asset} asset not available on Kraken. Available assets: {available_assets}."
            )
        return asset_information

    @staticmethod
    def get_pair_ask_price(ka: KrakenApi, pair_name: str) -> float:
        """
        Get pair ask price from Kraken ticker.

        :param ka: KrakenApi object.
        :param pair_name: Pair name to find ask price.
        :return: Current pair ask price.
        """
        pair_ticker_information = ka.get_pair_ticker(pair_name)
        pair_ask_price = float(
            pair_ticker_information.get(pair_name).get("a")[0])
        return pair_ask_price
