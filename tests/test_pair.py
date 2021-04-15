# ToDo: init, get_pair_from_kraken, get_pair_information
# ToDo: get_asset_information, get_pair_ask_price

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
