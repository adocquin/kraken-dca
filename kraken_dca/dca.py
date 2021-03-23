from .kraken_api import KrakenApi
from .utils import current_datetime


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
