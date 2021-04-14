from kraken_dca import DCA, KrakenApi, Pair
import vcr
import pytest
from freezegun import freeze_time

# ToDo: handle_dca_logic, send_buy_limit_order

# Initialize DCA test object - Fake keys.
ka = KrakenApi(
    "R6/OvXmIQEv1E8nyJd7+a9Zmaf84yJ7uifwe2yj5BgV1N+lgqURsxQwQ",
    "MWZ9lFF/mreK4Fdk/SEpFLvVn//nbKUbCytGShSwvCvYlgRkn4K8i7VY18UQEgOHzBIEsqg78BZJCEhvFIzw1Q==",
)
# Initialize the Pair object
pair = Pair.get_pair_from_kraken(ka, "XETHZEUR")
# Initialize the DCA object
dca = DCA(ka, pair, 20)


@freeze_time("2012-01-13 23:10:34.069731")
@vcr.use_cassette("tests/fixtures/vcr_cassettes/test_get_time.yaml")
def test_check_system_time():
    with pytest.raises(OSError) as e_info:
        dca.check_system_time()
    error_message = "Too much lag -> Check your internet connection speed or synchronize your system time."
    assert error_message in str(e_info.value)


@vcr.use_cassette(
    "tests/fixtures/vcr_cassettes/test_check_account_balance.yaml",
    filter_headers=["API-Key", "API-Sign"],
)
def test_check_account_balance():
    with pytest.raises(ValueError) as e_info:
        dca.check_account_balance()
    assert "Insufficient funds to buy 20 ZEUR of XETH" in str(e_info.value)


@vcr.use_cassette(
    "tests/fixtures/vcr_cassettes/test_count_pair_daily_orders.yaml",
    filter_headers=["API-Key", "API-Sign"],
)
def test_count_pair_daily_orders():
    order_count = dca.count_pair_daily_orders()
    assert type(order_count) == int
    assert order_count == 1


def test_extract_pair_orders():
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
    pair_orders = dca.extract_pair_orders(orders, "XETHZEUR", "ETHEUR")
    assert type(pair_orders) == dict
    key = next(iter(pair_orders))
    assert type(key) == str
    assert key == "O7JHTY-754IO-YU46NZ"

    # Test with non-existing pair order
    value = next(iter(pair_orders.values()))
    assert type(value) == dict
    pair_orders = dca.extract_pair_orders(orders, "XETHZUSD", "ETHUSD")
    assert type(pair_orders) == dict
    assert len(pair_orders) == 0


# def test_get_dca_pair_information():
#     # Test with existing pair.
#     with vcr.use_cassette("tests/fixtures/vcr_cassettes/test_get_asset_pairs.yaml"):
#         dca.get_dca_pair_information()
#     assert dca.amount == 20
#     assert dca.ka == ka
#     assert dca.lot_decimals == 8
#     assert dca.order_min == 0.005
#     assert dca.pair == "XETHZEUR"
#     assert dca.pair_base == "XETH"
#     assert dca.pair_decimals == 2
#     assert dca.pair_quote == "ZEUR"
#
#     # Test with fake pair.
#     dca_fake = DCA(ka, "FakePair", 20)
#     with vcr.use_cassette("tests/fixtures/vcr_cassettes/test_get_asset_pairs.yaml"):
#         with pytest.raises(ValueError) as e_info:
#             dca_fake.get_dca_pair_information()
#     assert "Pair not available on Kraken. Available pairs:" in str(e_info.value)


# @vcr.use_cassette("tests/fixtures/vcr_cassettes/test_get_pair_ticker_xethzeur.yaml")
# def test_get_pair_ask_price():
#     pair_ask_price = dca.get_pair_ask_price()
#     assert pair_ask_price == 1749.76


# def test_set_order_volume():
#     # Test with valid parameters
#     order_volume = dca.set_order_volume(20, 1802.82, 8)
#     assert type(order_volume) == float
#     assert order_volume == 0.01109373
#
#     with pytest.raises(ZeroDivisionError) as e_info:
#         dca.set_order_volume(1802.82, 0, 8)
#     assert "DCA set_order_volume -> pair_price must not be 0." in str(e_info.value)


# def test_set_order_price():
#     # Test with valid parameters
#     order_price = dca.set_order_price(0.01109373, 1802.82, 2)
#     assert type(order_price) == float
#     assert order_price == 20
