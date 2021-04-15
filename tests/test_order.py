# ToDo: init, buy_limit_order, send_order
# ToDo: save_order_csv, estimate_order_price
# ToDo: estimate_order_fee


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
