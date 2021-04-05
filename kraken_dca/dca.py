from .kraken_api import KrakenApi
from .utils import current_datetime
import math


class DCA:
    """
    Dollar Cost Averaging encapsulation.
    """

    ka: KrakenApi
    pair: str
    amount: float

    def __init__(self, ka: KrakenApi, pair: str, amount: float):
        """
        Initialize the DCA object.

        :param ka: KrakenApi object.
        :param pair: Pair to dollar cost average as string.
        :param amount: Amount to dollar cost average as float.
        """
        self.ka = ka
        self.pair = pair
        self.amount = amount
        print(f"DCA pair: {self.pair}, DCA amount: {self.amount}")

    @staticmethod
    def get_pair_orders(orders: dict, pair: str) -> dict:
        """
        Filter orders passed as dict parameters on specific pair and return the dictionary.

        :param orders: Orders as dictionary.
        :param pair: Specific pair to filter on.
        :return: Filtered orders dictionary on specific pair.
        """
        pair_orders = {
            order_id: order_infos
            for order_id, order_infos in orders.items()
            if order_infos.get("descr").get("pair") == pair
        }
        return pair_orders

    def count_pair_daily_orders(self) -> int:
        """
        Count current day open and closed orders for the DCA pair.

        :return: Count of daily orders for the dollar cost averaged pair.
        """
        # Get current open orders.
        open_orders = self.ka.get_open_orders()
        daily_open_orders = len(self.get_pair_orders(open_orders, self.pair))

        # Get daily closed orders
        current_date = current_datetime()
        current_day_datetime = current_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        current_day_unix = int(current_day_datetime.timestamp())
        closed_orders = self.ka.get_closed_orders(
            {"start": current_day_unix, "closetime": "open"}
        )
        daily_closed_orders = len(self.get_pair_orders(closed_orders, self.pair))
        # Sum the count of closed and daily open orders for the DCA pair.
        pair_daily_orders = daily_closed_orders + daily_open_orders
        return pair_daily_orders

    def get_pair_ask_price(self):
        """
        Get pair ask price from Kraken ticker.

        :return: DCA pair ask price.
        """
        pair_ticker_information = self.ka.get_pair_ticker(self.pair)
        pair_ask_price = float(pair_ticker_information.get(self.pair).get("a")[0])
        return pair_ask_price

    @staticmethod
    def get_order_volume(amount: float, pair_price: float):
        """
        Return order volume for specified DCA amount and pair price.

        :param amount: DCA amount.
        :param pair_price: Pair price.
        :return: Order volume.
        """
        return math.floor(amount/pair_price*100000)/100000

    @staticmethod
    def get_order_price(volume: float, pair_price: float):
        """
        Return order price for specified order volume and pair price.

        :param volume: Order volume.
        :param pair_price: Pair price.
        :return: order price.
        """
        return volume*pair_price
    
    def create_dca_pair_limit_order(self, pair_price: float):
        """
        Create a limit order for specified dca pair and amount.

        :return: DCA pair ask price.
        """
        volume = self.get_order_volume(self.amount, pair_price)
        price = self.get_order_price(volume, pair_price)
        print(f"Create a {self.pair} buy limit order of {volume} for {price} at {pair_price}")
        order = self.ka.create_limit_order(self.pair, True, pair_price, volume)
        print(order)
