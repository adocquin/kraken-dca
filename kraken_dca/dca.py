from .kraken_api import KrakenApi
from .order import Order
from .pair import Pair
from .utils import (
    utc_unix_time_datetime,
    current_utc_datetime,
    current_utc_day_datetime,
    datetime_as_utc_unix,
)


class DCA:
    """
    Dollar Cost Averaging encapsulation.
    """

    ka: KrakenApi
    pair: Pair
    amount: float
    pair_quote_balance: float

    def __init__(self, ka: KrakenApi, pair: Pair, amount: float) -> None:
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
            f"Hi, current configuration: DCA pair: {self.pair.name}, DCA amount: {self.amount}."
        )

    def handle_dca_logic(self) -> None:
        """
        Handle DCA logic.

        :return: None
        """
        # Check current system time.
        self.check_system_time()
        # Check Kraken account balance.
        self.check_account_balance()
        # Create a buy limit order for specified
        # pair and quote amount if didn't DCA today.
        daily_pair_orders = self.count_pair_daily_orders()
        if daily_pair_orders == 0:
            print("Didn't DCA already today.")
            pair_ask_price = self.pair.get_pair_ask_price(self.ka, self.pair.name)
            print(f"Current {self.pair.name} ask price: {pair_ask_price}.")
            order = Order.buy_limit_order(
                self.pair.name,
                self.amount,
                pair_ask_price,
                self.pair.lot_decimals,
                self.pair.quote_decimals,
            )
            self.send_buy_limit_order(order)
        else:
            print("Already DCA today.")

    def check_system_time(self) -> None:
        """
        Compare system and Kraken time.
        Raise an error if too much difference (1sc).

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

    def check_account_balance(self) -> None:
        """
        Check account trade balance, pair base and pair quote balances.
        Raise an error if quote pair balance
        is too low to DCA specified amount.

        :return: None
        """
        trade_balance = self.ka.get_trade_balance().get("eb")
        print(f"Current trade balance: {trade_balance} ZUSD.")
        balance = self.ka.get_balance()
        try:
            pair_base_balance = float(balance.get(self.pair.base))
        except TypeError:  # When there is no pair base balance on Kraken account
            pair_base_balance = 0
        try:
            self.pair_quote_balance = float(balance.get(self.pair.quote))
        except TypeError:  # When there is no pair quote balance on Kraken account
            self.pair_quote_balance = 0
        print(
            f"Pair balances: {self.pair_quote_balance} {self.pair.quote}, {pair_base_balance} {self.pair.base}."
        )
        if self.pair_quote_balance < self.amount:
            raise ValueError(
                f"Insufficient funds to buy {self.amount} {self.pair.quote} of {self.pair.base}"
            )

    @staticmethod
    def get_pair_orders(orders: dict, pair: str, pair_alt_name: str) -> dict:
        """
        Filter orders passed as dict parameters
        on specific pair and return the dictionary.

        :param orders: Orders as dictionary.
        :param pair: Specific pair to filter on.
        :param pair_alt_name: Specific pair alternative name to filter on.
        :return: Filtered orders dictionary on specific pair.
        """
        pair_orders = {
            order_id: order_infos
            for order_id, order_infos in orders.items()
            if order_infos.get("descr").get("pair") == pair
            or order_infos.get("descr").get("pair") == pair_alt_name
        }
        return pair_orders

    def count_pair_daily_orders(self) -> int:
        """
        Count current day open and closed orders for the DCA pair.

        :return: Count of daily orders for the dollar cost averaged pair.
        """
        # Get current open orders.
        open_orders = self.ka.get_open_orders()
        daily_open_orders = len(
            self.get_pair_orders(open_orders, self.pair.name, self.pair.alt_name)
        )

        # Get daily closed orders
        day_datetime = current_utc_day_datetime()
        current_day_unix = datetime_as_utc_unix(day_datetime)
        closed_orders = self.ka.get_closed_orders(
            {"start": current_day_unix, "closetime": "open"}
        )
        daily_closed_orders = len(
            self.get_pair_orders(closed_orders, self.pair.name, self.pair.alt_name)
        )
        # Sum the count of closed and daily open orders for the DCA pair.
        pair_daily_orders = daily_closed_orders + daily_open_orders
        return pair_daily_orders

    def send_buy_limit_order(self, order: Order) -> None:
        """
        Send a limit order for specified dca pair and amount to Kraken.

        :return: None.
        """
        if order.volume < self.pair.order_min:
            raise ValueError(
                f"Too low volume to buy {self.pair.base}: current {order.volume}, minimum {self.pair.order_min}."
            )
        print(
            f"Create a {order.price}{self.pair.quote} buy limit order of {order.volume}{self.pair.base} at {order.pair_price}{self.pair.quote}."
        )
        print(f"Fee expected: {order.fee}{self.pair.quote} (0.26% taker fee).")
        print(
            f"Total price expected: {order.volume}{self.pair.base} for {order.total_price}{self.pair.quote}."
        )
        order.send_order(self.ka)
        print(f"Order successfully created.")
        print(f"TXID: {order.txid}")
        print(f"Description: {order.description}")
