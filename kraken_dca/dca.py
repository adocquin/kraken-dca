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

    def get_daily_orders(self):
        open_orders = self.ka.get_open_orders()
        print(open_orders)
        current_date = current_datetime()
        current_day_datetime = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
        current_day_unix = int(current_day_datetime.timestamp())
        closed_orders = self.ka.get_closed_orders({"start": current_day_unix,
                                                   "closetime": "open"})
        print(closed_orders)
