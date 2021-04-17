from kraken_dca import DCA, KrakenApi, Pair, Order
import vcr
import pytest
from freezegun import freeze_time
from datetime import datetime
import os


class TestDCA:
    test_orders_filepath = "tests/fixtures/orders.csv"
    dca: DCA

    def setup(self):
        # Initialize DCA test object - Fake keys.
        ka = KrakenApi(
            "R6/OvXmIQEv1E8nyJd7+a9Zmaf84yJ7uifwe2yj5BgV1N+lgqURsxQwQ",
            "MWZ9lFF/mreK4Fdk/SEpFLvVn//nbKUbCytGShSwvCvYlgRkn4K8i7VY18UQEgOHzBIEsqg78BZJCEhvFIzw1Q==",
        )
        # Initialize the Pair object
        pair = Pair("XETHZEUR", "ETHEUR", "XETH", "ZEUR", 2, 8, 4, 0.005)
        # Initialize the DCA object
        self.dca = DCA(ka, pair, 20, self.test_orders_filepath)

    def test_init(self):
        assert type(self.dca.ka) == KrakenApi
        assert type(self.dca.pair) == Pair
        assert type(self.dca.amount) == float
        assert self.dca.amount == 20
        assert self.dca.orders_filepath == self.test_orders_filepath

    @freeze_time("2021-04-15 21:33:28.069731")
    def test_handle_dca_logic(self, capfd):
        # Test normal execution
        with vcr.use_cassette(
            "tests/fixtures/vcr_cassettes/test_handle_dca_logic.yaml",
            filter_headers=["API-Key", "API-Sign"],
        ):
            self.dca.handle_dca_logic()
        captured = capfd.readouterr()
        test_output = (
            "Hi, current configuration: DCA pair: XETHZEUR, DCA amount: 20.0.\nIt's 2021-04-15 21:33:28 on "
            "Kraken, 2021-04-15 21:33:28 on system.\nCurrent trade balance: 1650.3006 ZUSD.\nPair balances: "
            "39.728 ZEUR, 0.109598362 XETH.\nDidn't DCA already today.\nCurrent XETHZEUR ask price: "
            "2083.16.\nCreate a 19.9481ZEUR buy limit order of 0.00957589XETH at 2083.16ZEUR.\nFee "
            "expected: 0.0519ZEUR (0.26% taker fee).\nTotal price expected: 0.00957589XETH for "
            "20.0ZEUR.\nOrder successfully created.\nTXID: OCYS4K-OILOE-36HPAE\nDescription: buy 0.00957589 "
            "ETHEUR @ limit 2083.16\nOrder information saved to CSV.\n"
        )
        os.remove(self.test_orders_filepath)
        assert captured.out == test_output

    @freeze_time("2021-04-16 18:54:53.069731")
    def test_handle_dca_logic_error(self, capfd):
        # Test execution while already DCA
        with vcr.use_cassette(
            "tests/fixtures/vcr_cassettes/test_handle_dca_logic_error.yaml",
            filter_headers=["API-Key", "API-Sign"],
        ):
            self.dca.handle_dca_logic()
        captured = capfd.readouterr()
        test_output = (
            "Hi, current configuration: DCA pair: XETHZEUR, DCA amount: 20.0.\nIt's 2021-04-16 18:54:53 on "
            "Kraken, 2021-04-16 18:54:53 on system.\nCurrent trade balance: 16524.7595 ZUSD.\nPair "
            "balances: 359.728 ZEUR, 0.128994332 XETH.\nAlready DCA today.\n"
        )
        assert captured.out == test_output

    def test_get_system_time(self):
        # Test with system time in the past
        with freeze_time("2012-01-13 23:10:34.069731"):
            with vcr.use_cassette("tests/fixtures/vcr_cassettes/test_get_time.yaml"):
                with pytest.raises(OSError) as e_info:
                    self.dca.get_system_time()
        error_message = "Too much lag -> Check your internet connection speed or synchronize your system time."
        assert error_message in str(e_info.value)
        # Test with correct system time
        test_date = datetime.strptime("2021-04-09 20:47:40", "%Y-%m-%d %H:%M:%S")
        with freeze_time(test_date):
            with vcr.use_cassette("tests/fixtures/vcr_cassettes/test_get_time.yaml"):
                date = self.dca.get_system_time()
        assert date == test_date

    @vcr.use_cassette(
        "tests/fixtures/vcr_cassettes/test_check_account_balance.yaml",
        filter_headers=["API-Key", "API-Sign"],
    )
    def test_check_account_balance(self):
        with pytest.raises(ValueError) as e_info:
            self.dca.check_account_balance()
        assert "Insufficient funds to buy 20.0 ZEUR of XETH" in str(e_info.value)

    @vcr.use_cassette(
        "tests/fixtures/vcr_cassettes/test_count_pair_daily_orders.yaml",
        filter_headers=["API-Key", "API-Sign"],
    )
    def test_count_pair_daily_orders(self):
        order_count = self.dca.count_pair_daily_orders()
        assert type(order_count) == int
        assert order_count == 1

    def test_extract_pair_orders(self):
        # Pairs orders dictionary
        orders = {
            "O7JHTY-754IO-YU46NZ": {
                "refid": None,
                "userref": 0,
                "status": "open",
                "opentm": 1618250841.6683,
                "starttm": 0,
                "expiretm": 0,
                "descr": {
                    "pair": "ETHEUR",
                    "type": "buy",
                    "ordertype": "limit",
                    "price": "1.00",
                    "price2": "0",
                    "leverage": "none",
                    "order": "buy 500.00000000 ETHEUR @ limit 1.00",
                    "close": "",
                },
                "vol": "500.00000000",
                "vol_exec": "0.00000000",
                "cost": "0.00000",
                "fee": "0.00000",
                "price": "0.00000",
                "stopprice": "0.00000",
                "limitprice": "0.00000",
                "misc": "",
                "oflags": "fciq",
            }
        }

        # Test with existing pair order
        pair_orders = self.dca.extract_pair_orders(orders, "XETHZEUR", "ETHEUR")
        assert type(pair_orders) == dict
        assert len(pair_orders) == 1
        key = next(iter(pair_orders))
        assert type(key) == str
        assert key == "O7JHTY-754IO-YU46NZ"
        value = next(iter(pair_orders.values()))
        assert type(value) == dict

        # Test with non-existing pair order
        pair_orders = self.dca.extract_pair_orders(orders, "XETHZUSD", "ETHUSD")
        assert type(pair_orders) == dict
        assert len(pair_orders) == 0

    def test_send_buy_limit_order_error(self):
        # Test error with order volume < pair minimum volume
        order = Order(
            datetime.strptime("2021-03-11 23:33:28", "%Y-%m-%d %H:%M:%S"),
            "XETHZEUR",
            "buy",
            "limit",
            "fciq",
            1960.86,
            0.001,
            1.9608,
            0.0052,
        )
        with pytest.raises(ValueError) as e_info:
            self.dca.send_buy_limit_order(order)
        error_message = "Too low volume to buy XETH: current 0.001, minimum 0.005."
        assert error_message in str(e_info.value)

    @vcr.use_cassette(
        "tests/fixtures/vcr_cassettes/test_create_order.yaml",
        filter_headers=["API-Key", "API-Sign"],
    )
    def test_send_buy_limit_order(self, capfd):
        # Test valid order
        order = Order(
            datetime.strptime("2021-03-11 23:33:28", "%Y-%m-%d %H:%M:%S"),
            "XETHZEUR",
            "buy",
            "limit",
            "fciq",
            1938.11,
            0.01029256,
            19.9481,
            0.0519,
        )
        self.dca.send_buy_limit_order(order)
        captured = capfd.readouterr()
        test_output = (
            "Hi, current configuration: DCA pair: XETHZEUR, DCA amount: 20.0.\nCreate a 19.9481ZEUR buy "
            "limit order of 0.01029256XETH at 1938.11ZEUR.\nFee expected: 0.0519ZEUR (0.26% taker "
            "fee).\nTotal price expected: 0.01029256XETH for 20.0ZEUR.\nOrder successfully created.\nTXID: "
            "OUHXFN-RTP6W-ART4VP\nDescription: buy 0.01029256 ETHEUR @ limit 1938.11\n"
        )
        assert captured.out == test_output
