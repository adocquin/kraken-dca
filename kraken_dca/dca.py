from .kraken_api import KrakenApi
from .utils import (
    utc_unix_time_datetime,
    current_utc_datetime,
    current_utc_day_datetime,
    datetime_as_utc_unix,
)
import math


class DCA:
    """
    Dollar Cost Averaging encapsulation.
    """

    ka: KrakenApi
    pair: str
    amount: float
    pair_altname: str
    pair_base: str
    pair_quote: str
    pair_decimals: int
    lot_decimals: int
    order_min: float

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
        print(
            f"Hi, current configuration: DCA pair: {self.pair}, DCA amount: {self.amount}."
        )

    def handle_dca_logic(self):
        """
        Handle DCA logic.

        :return: None
        """
        # Get DCA pair information.
        self.get_dca_pair_information()
        # Check current system time.
        self.check_system_time()
        # Check Kraken account balance.
        self.check_account_balance()
        # Create a buy limit order for specified pair and quote amount if didn't DCA today.
        daily_pair_orders = self.count_pair_daily_orders()
        if daily_pair_orders == 0:
            print("Didn't DCA already today.")
            pair_ask_price = self.get_pair_ask_price()
            print(f"Current {self.pair} ask price: {pair_ask_price}.")
            self.create_buy_limit_order(pair_ask_price)
        else:
            print("Already DCA today.")

    def get_dca_pair_information(self):
        """
        Get DCA pair specified in configuration file information or raise an error if not available on Kraken.

        :return: None
        """
        asset_pairs = self.ka.get_asset_pairs()
        pair_information = {
            pair_id: pair_infos
            for pair_id, pair_infos in asset_pairs.items()
            if pair_id == self.pair
        }
        if not pair_information:
            available_pairs = [pair for pair in asset_pairs]
            raise ValueError(
                f"Pair not available on Kraken. Available pairs: {available_pairs}."
            )
        pair_information = pair_information.get(self.pair)
        self.pair_altname = pair_information.get("altname")
        self.pair_base = pair_information.get("base")
        self.pair_quote = pair_information.get("quote")
        self.pair_decimals = pair_information.get("pair_decimals")
        self.lot_decimals = pair_information.get("lot_decimals")
        self.order_min = float(pair_information.get("ordermin"))

    def check_system_time(self):
        """
        Compare system and Kraken time and raise an error if too much difference (1sc).

        :return: None
        """
        kraken_time = self.ka.get_time()
        kraken_date = utc_unix_time_datetime(kraken_time)
        current_date = current_utc_datetime()
        print(f"It's {kraken_date} on Kraken, {current_date} on system.")
        lag = (current_date - kraken_date).seconds
        if lag > 1:
            raise OSError(
                "Too much lag -> Check your internet connection speed or synchronize your system time."
            )

    def check_account_balance(self):
        """
        Check account trade balance, pair base and pair quote balances and raise an error if quote pair balance
        is too low to DCA specified amount.

        :return: None
        """
        trade_balance = self.ka.get_trade_balance().get("eb")
        print(f"Current trade balance: {trade_balance} ZUSD.")
        balance = self.ka.get_balance()
        try:
            pair_base_balance = float(balance.get(self.pair_base))
        except TypeError:  # When there is no pair base balance on Kraken account
            pair_base_balance = 0
        try:
            pair_quote_balance = float(balance.get(self.pair_quote))
        except TypeError:  # When there is no pair quote balance on Kraken account
            pair_quote_balance = 0
        print(
            f"Pair balances: {pair_quote_balance} {self.pair_quote}, {pair_base_balance} {self.pair_base}."
        )
        if pair_quote_balance < self.amount:
            raise ValueError(
                f"Insufficient funds to buy {self.amount} {self.pair_quote} of {self.pair_base}"
            )

    @staticmethod
    def get_pair_orders(orders: dict, pair: str, pair_altname: str) -> dict:
        """
        Filter orders passed as dict parameters on specific pair and return the dictionary.

        :param orders: Orders as dictionary.
        :param pair: Specific pair to filter on.
        :param pair_altname: Specific pair altname to filter on.
        :return: Filtered orders dictionary on specific pair.
        """
        pair_orders = {
            order_id: order_infos
            for order_id, order_infos in orders.items()
            if order_infos.get("descr").get("pair") == pair
            or order_infos.get("descr").get("pair") == pair_altname
        }
        return pair_orders

    def count_pair_daily_orders(self) -> int:
        """
        Count current day open and closed orders for the DCA pair.

        :return: Count of daily orders for the dollar cost averaged pair.
        """
        # Get current open orders.
        open_orders = self.ka.get_open_orders()
        daily_open_orders = len(self.get_pair_orders(open_orders, self.pair, self.pair_altname))

        # Get daily closed orders
        day_datetime = current_utc_day_datetime()
        current_day_unix = datetime_as_utc_unix(day_datetime)
        closed_orders = self.ka.get_closed_orders(
            {"start": current_day_unix, "closetime": "open"}
        )
        daily_closed_orders = len(self.get_pair_orders(closed_orders, self.pair, self.pair_altname))
        # Sum the count of closed and daily open orders for the DCA pair.
        pair_daily_orders = daily_closed_orders + daily_open_orders
        return pair_daily_orders

    def get_pair_ask_price(self) -> float:
        """
        Get pair ask price from Kraken ticker.

        :return: DCA pair ask price.
        """
        pair_ticker_information = self.ka.get_pair_ticker(self.pair)
        pair_ask_price = float(pair_ticker_information.get(self.pair).get("a")[0])
        return pair_ask_price

    @staticmethod
    def set_order_volume(
        amount: float, pair_price: float, lot_decimals: float
    ) -> float:
        """
        Define order volume for specified DCA amount, pair price and pair decimals based on Kraken lot decimals.

        :param amount: DCA amount.
        :param pair_price: Pair price.
        :param lot_decimals: Lot decimals as float.
        :return: Order volume as flat.
        """
        decimals = 10 ** lot_decimals
        try:
            order_volume = math.floor(amount / pair_price * decimals) / decimals
        except ZeroDivisionError:
            raise ZeroDivisionError("DCA set_order_volume -> pair_price must not be 0.")
        return order_volume

    @staticmethod
    def set_order_price(
        volume: float, pair_price: float, pair_decimals: float
    ) -> float:
        """
        Define order price for specified order volume and pair price based on Kraken pair decimals.

        :param volume: Order volume.
        :param pair_price: Pair price.
        :param pair_decimals: Pair decimals as floar.
        :return: Order price as float.
        """
        decimals = 10 ** pair_decimals
        return math.ceil(volume * pair_price * decimals) / decimals

    def create_buy_limit_order(self, pair_price: float):
        """
        Create a limit order for specified dca pair and amount.

        :return: None.
        """
        volume = self.set_order_volume(self.amount, pair_price, self.lot_decimals)
        price = self.set_order_price(volume, pair_price, self.pair_decimals)
        print(
            f"Create a buy limit order of {volume} {self.pair_base} for {price} {self.pair_quote} at {pair_price}."
        )
        if volume < self.order_min:
            raise ValueError(
                f"Too low volume to buy {self.pair_base}: current {volume}, minimum {self.order_min}."
            )
        order = self.ka.create_limit_order(self.pair, True, pair_price, volume)
        txid = order.get("txid")[0]
        description = order.get("descr").get("order")
        print(f"Order successfully created.\nTXID: {txid}\nDescription: {description}")
