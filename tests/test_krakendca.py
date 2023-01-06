"""krakendca.py tests module."""
import vcr
from freezegun import freeze_time
from krakenapi import KrakenApi

from krakendca.config import Config
from krakendca.dca import DCA
from krakendca.krakendca import KrakenDCA


class TestKrakenDCA:
    config: Config
    ka: KrakenApi
    kdca: KrakenDCA

    @vcr.use_cassette(
        "tests/fixtures/vcr_cassettes/test_krakendca_setup.yaml",
        filter_headers=["API-Key", "API-Sign"],
    )
    def setup(self):
        # Initialize DCA test object - Fake keys.
        self.ka = KrakenApi(
            "R6/OvXmIQEv1E8nyJd7+a9Zmaf84yJ7uifwe2yj5BgV1N+lgqURsxQwQ",
            "MWZ9lFF/mreK4Fdk/SEpFLvVn//nbKUbCytGShSwvCvYlgRkn4K8i7VY"
            "18UQEgOHzBIEsqg78BZJCEhvFIzw1Q==",
        )
        # Initialize Config object
        self.config = Config("tests/fixtures/config.yaml")
        # Initialize the KrakenDCA object.
        self.kdca = KrakenDCA(self.config, self.ka)
        # Instantiate KrakenDCA DCA pairs.
        self.kdca.initialize_pairs_dca()

    def test_init(self) -> None:
        assert self.kdca.config == self.config
        assert self.kdca.ka == self.ka

    def assert_kdca_pair(
        self,
        dca_pair: DCA,
        amount: float,
        delay: int,
        alt_name: str,
        base: str,
        lot_decimals: int,
        name: str,
        order_min: float,
        pair_decimals: int,
        quote: str,
        quote_decimals: int,
    ):
        assert dca_pair.amount == amount
        assert dca_pair.delay == delay
        assert dca_pair.ka == self.ka
        assert dca_pair.orders_filepath == "orders.csv"
        assert dca_pair.pair.alt_name == alt_name
        assert dca_pair.pair.base == base
        assert dca_pair.pair.lot_decimals == lot_decimals
        assert dca_pair.pair.name == name
        assert dca_pair.pair.order_min == order_min
        assert dca_pair.pair.pair_decimals == pair_decimals
        assert dca_pair.pair.quote == quote
        assert dca_pair.pair.quote_decimals == quote_decimals

    def test_initialize_pairs_dca(self) -> None:
        self.assert_kdca_pair(
            dca_pair=self.kdca.dcas_list[0],
            amount=15.0,
            delay=1,
            alt_name="ETHEUR",
            base="XETH",
            lot_decimals=8,
            name="XETHZEUR",
            order_min=0.004,
            pair_decimals=2,
            quote="ZEUR",
            quote_decimals=4,
        )
        self.assert_kdca_pair(
            dca_pair=self.kdca.dcas_list[1],
            amount=20.0,
            delay=3,
            alt_name="XBTEUR",
            base="XXBT",
            lot_decimals=8,
            name="XXBTZEUR",
            order_min=0.0001,
            pair_decimals=1,
            quote="ZEUR",
            quote_decimals=4,
        )

    @freeze_time("2021-09-12 19:50:08")
    @vcr.use_cassette(
        "tests/fixtures/vcr_cassettes/test_handle_pairs_dca.yaml",
        filter_headers=["API-Key", "API-Sign"],
    )
    def test_handle_pairs_dca(self, logging_capture) -> None:
        self.kdca.handle_pairs_dca()
        captured = logging_capture.read()
        assert "buy 0.00519042 ETHEUR @ limit 2882.44" in captured
        assert "buy 0.00051336 XBTEUR @ limit 38857.2" in captured

    @freeze_time("2022-03-26 18:37:46")
    @vcr.use_cassette(
        "tests/fixtures/vcr_cassettes/test_handle_pars_dca_max_price.yaml",
        filter_headers=["API-Key", "API-Sign"],
    )
    def test_handle_pairs_dca_max_price(self, logging_capture) -> None:
        self.kdca.dcas_list.pop()
        self.kdca.dcas_list[0].max_price = 0
        self.kdca.handle_pairs_dca()
        captured = logging_capture.read()
        assert (
            "No DCA for XETHZEUR: Limit price (2797.99) greater "
            "than maximum price (0)." in captured
        )

    @freeze_time("2022-03-26 18:37:46")
    @vcr.use_cassette(
        "tests/fixtures/vcr_cassettes/test_handle_pars_dca_max_price.yaml",
        filter_headers=["API-Key", "API-Sign"],
    )
    def test_handle_pairs_dca_limit_factor(self, logging_capture) -> None:
        self.kdca.dcas_list.pop()
        self.kdca.dcas_list[0].max_price = 0
        self.kdca.handle_pairs_dca()
        captured = logging_capture.read()
        assert "Factor adjusted limit price (0.9850): 2797.99." in captured
