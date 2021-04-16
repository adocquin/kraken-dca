from kraken_dca import Order, KrakenApi
from datetime import datetime
import vcr
import pandas as pd
import os
import pytest


class TestOrder:
    order: Order

    def setup(self):
        self.order = Order(
            datetime.strptime("2021-04-15 21:33:28", "%Y-%m-%d %H:%M:%S"),
            "XETHZEUR",
            "buy",
            "limit",
            "fciq",
            2083.16,
            0.00957589,
            19.9481,
            0.0519,
        )
        self.ka = KrakenApi(
            "R6/OvXmIQEv1E8nyJd7+a9Zmaf84yJ7uifwe2yj5BgV1N+lgqURsxQwQ",
            "MWZ9lFF/mreK4Fdk/SEpFLvVn//nbKUbCytGShSwvCvYlgRkn4K8i7VY18UQEgOHzBIEsqg78BZJCEhvFIzw1Q==",
        )

    def test_init(self):
        assert type(self.order.date) == datetime
        assert self.order.date == datetime.strptime(
            "2021-04-15 21:33:28", "%Y-%m-%d %H:%M:%S"
        )
        assert type(self.order.pair) == str
        assert self.order.pair == "XETHZEUR"
        assert type(self.order.type) == str
        assert self.order.type == "buy"
        assert type(self.order.order_type) == str
        assert self.order.order_type == "limit"
        assert type(self.order.o_flags) == str
        assert self.order.o_flags == "fciq"
        assert type(self.order.pair_price) == float
        assert self.order.pair_price == 2083.16
        assert type(self.order.volume) == float
        assert self.order.volume == 0.00957589
        assert type(self.order.price) == float
        assert self.order.price == 19.9481
        assert type(self.order.fee) == float
        assert self.order.fee == 0.0519
        assert type(self.order.total_price) == float
        assert self.order.total_price == 19.9481 + 0.0519

    def test_buy_limit_order(self):
        self.order = Order.buy_limit_order(
            datetime.strptime("2021-04-15 21:33:28", "%Y-%m-%d %H:%M:%S"),
            "XETHZEUR",
            20,
            2083.16,
            8,
            4,
        )
        assert type(self.order.fee) == float
        assert self.order.fee == 0.0519
        assert type(self.order.o_flags) == str
        assert self.order.o_flags == "fciq"
        assert type(self.order.order_type) == str
        assert self.order.order_type == "limit"
        assert type(self.order.pair) == str
        assert self.order.pair == "XETHZEUR"
        assert type(self.order.pair_price) == float
        assert self.order.pair_price == 2083.16
        assert type(self.order.price) == float
        assert self.order.price == 19.9481
        assert type(self.order.total_price) == float
        assert self.order.total_price == 20
        assert type(self.order.type) == str
        assert self.order.type == "buy"
        assert type(self.order.volume) == float
        assert self.order.volume == 0.00957589

    @vcr.use_cassette(
        "tests/fixtures/vcr_cassettes/test_create_order.yaml",
        filter_headers=["API-Key", "API-Sign"],
    )
    def test_send_order(self):
        self.order.send_order(self.ka)
        assert type(self.order.txid) == str
        assert self.order.txid == "OUHXFN-RTP6W-ART4VP"
        assert type(self.order.description) == str
        assert self.order.description == "buy 0.01029256 ETHEUR @ limit 1938.11"

    def test_save_order_csv(self):
        # Test order history CSV saving
        self.order.txid = "OCYS4K-OILOE-36HPAE"
        self.order.description = "buy 0.00957589 ETHEUR @ limit 2083.16"

        self.order.save_order_csv("tests/fixtures/orders.csv")
        self.order.save_order_csv("tests/fixtures/orders.csv")
        history = pd.read_csv("tests/fixtures/orders.csv")
        test_history = pd.read_csv("tests/fixtures/test_handle_dca_logic.csv")
        os.remove("tests/fixtures/orders.csv")
        assert history.equals(test_history)

    def test_set_order_volume(self):
        # Test with valid parameters
        order_volume = Order.set_order_volume(20, 1802.82, 8)
        assert type(order_volume) == float
        assert order_volume == 0.01106496

        with pytest.raises(ZeroDivisionError) as e_info:
            Order.set_order_volume(1802.82, 0, 8)
        assert "Order set_order_volume -> pair_price must not be 0." in str(
            e_info.value
        )

    def test_estimate_order_price(self):
        # Test with valid parameters
        order_price = Order.estimate_order_price(0.01105373, 1802.82, 2)
        assert type(order_price) == float
        assert order_price == 19.93

    def test_estimate_order_fee(self):
        # Test with valid parameters
        order_fee = Order.estimate_order_fee(0.01105373, 1802.82, 2)
        assert type(order_fee) == float
        assert order_fee == 0.05
