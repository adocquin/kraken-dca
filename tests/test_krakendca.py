import vcr
from freezegun import freeze_time
from krakendca import Config, KrakenDCA, DCA
from krakenapi import KrakenApi


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
            "MWZ9lFF/mreK4Fdk/SEpFLvVn//nbKUbCytGShSwvCvYlgRkn4K8i7VY18UQEgOHzBIEsqg78B"
            "ZJCEhvFIzw1Q==",
        )
        # Initialize Config object
        self.config = Config("tests/fixtures/config.yaml")
        # Initialize the KrakenDCA object.
        self.kdca = KrakenDCA(self.config, self.ka)
        # Instantiate KrakenDCA DCA pairs.
        self.kdca.initialize_pairs_dca()

    def test_init(self):
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

    def test_initialize_pairs_dca(self):
        self.assert_kdca_pair(
            self.kdca.dcas_list[0],
            15.0,
            1,
            "ETHEUR",
            "XETH",
            8,
            "XETHZEUR",
            0.004,
            2,
            "ZEUR",
            4,
        )
        self.assert_kdca_pair(
            self.kdca.dcas_list[1],
            20.0,
            3,
            "XBTEUR",
            "XXBT",
            8,
            "XXBTZEUR",
            0.0001,
            1,
            "ZEUR",
            4,
        )

    @freeze_time("2021-09-12 19:50:08")
    @vcr.use_cassette(
        "tests/fixtures/vcr_cassettes/test_handle_dca_pairs.yaml",
        filter_headers=["API-Key", "API-Sign"],
    )
    def test_handle_dca_pairs(self, capfd):
        self.kdca.handle_pairs_dca()
        captured = capfd.readouterr()
        assert "buy 0.00519042 ETHEUR @ limit 2882.44" in captured.out
        assert "buy 0.00051336 XBTEUR @ limit 38857.2" in captured.out
