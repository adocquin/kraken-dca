from kraken_dca import KrakenApi
from freezegun import freeze_time
import pytest

# KrakenAPI object for public API endpoints
ka_public = KrakenApi("api_public_key", "api_private_key")
# KrakenAPI object for private API endpoints - Fake keys
ka_private = KrakenApi(
    "R6/OvXmIQEv1E8nyJd7+a9Zmaf84yJ7uifwe2yj5BgV1N+lgqURsxQwQ",
    "MWZ9lFF/mreK4Fdk/SEpFLvVn//nbKUbCytGShSwvCvYlgRkn4K8i7VY18UQEgOHzBIEsqg78BZJCEhvFIzw1Q==",
)


def test_create_api_path():
    # Test public API endpoint path
    api_path = ka_public.create_api_path(True, "Time")
    assert api_path == "https://api.kraken.com/0/public/Time"

    # Test private API endpoint path
    api_path = ka_public.create_api_path(False, "Balance")
    assert api_path == "https://api.kraken.com/0/private/Balance"


@freeze_time("2012-01-13 23:10:34.069731")
def test_create_api_nonce():
    api_nonce = ka_public.create_api_nonce()
    assert api_nonce == "1326496234069"


def test_create_api_post_data():
    # Test with post inputs and api nonce
    post_inputs = {"start": 1617753600, "closetime": "open"}
    api_nonce = "1326496234069"
    api_post_data = ka_public.create_api_post_data(post_inputs, api_nonce)
    assert api_post_data == b"start=1617753600&closetime=open&nonce=1326496234069"

    # Test with only post inputs
    post_inputs = {"pair": "XETHZEUR"}
    api_post_data = ka_public.create_api_post_data(post_inputs)
    assert api_post_data == b"pair=XETHZEUR"

    # Test with only api_nonce
    api_nonce = "1617824500528"
    api_post_data = ka_public.create_api_post_data(None, api_nonce)
    assert api_post_data == b"nonce=1617824500528"

    # Should raise a TypeError if post inputs and api nonce are missing
    with pytest.raises(TypeError) as e_info:
        ka_public.create_api_post_data()
    assert "API Post with missing post inputs and nonce ->" in str(e_info.value)


def test_create_api_signature():
    api_nonce = "1617828062628"

    # Test signature with method with only nonce as parameters,
    # using an incorrectly and correctly formatted API keys
    api_method = "TradeBalance"
    api_post_data = b"nonce=1617828062628"
    with pytest.raises(ValueError) as e_info:
        ka_public.create_api_signature(api_nonce, api_post_data, api_method)
    assert "Incorrect Kraken API private key ->" in str(e_info.value)
    api_signature = ka_private.create_api_signature(
        api_nonce, api_post_data, api_method
    )
    correct_api_signature = "Q7QwKIQu+8wlTtkcF2vwkPFkAP+10diymNsOIoOy+x1PoSUJFz5SAg5TRrvoBlzrgA9oxqjOWcAFqvqcarJZ3w=="
    assert api_signature == correct_api_signature

    # Test signature with method using start,
    # closedtime and nonce as parameters
    api_method = "ClosedOrders"
    api_post_data = b"start=1617753600&closetime=open&nonce=1617828329075"
    api_signature = ka_private.create_api_signature(
        api_nonce, api_post_data, api_method
    )
    correct_api_signature = "RsNkND1GcQmKpayw/o3CJzWheC8dYxyEjWXtha0tPqQVzfLOxtpyd2zLM4vB8ajFqTmO/GXkoqzmkwTJxNAHcw=="
    assert api_signature == correct_api_signature

    # Test signature with method using pair, type,
    # ordertype, price, volume and nonce as parameters
    api_method = "AddOrder"
    api_post_data = b"pair=XETHZUSD&type=buy&ordertype=limit&price=1985.42&volume=0.00755507&nonce=1617828386991"
    api_signature = ka_private.create_api_signature(
        api_nonce, api_post_data, api_method
    )
    correct_api_signature = "q5vxW9cvCBY5kmCfjl0JC8/cQeEaKM4i4vprNsqmyd9jshoB0cybg7IRddYEkxdBKxQF/ima/InTjJUJgQMnIg=="
    assert api_signature == correct_api_signature


def test_extract_response_data():
    # Raise error when wrong data format received
    data = b"Wrong data"
    with pytest.raises(ValueError) as e_info:
        ka_public.extract_response_data(data)
    assert "Response received from API was wrongly formatted ->" in str(e_info.value)

    # Test extract data from Kraken API as dict from bytes
    # with format {"error": list, result: dit}
    data = b'{"error":[],"result":{"unixtime":1617831335,"rfc1123":"Wed,  7 Apr 21 21:35:35 +0000"}}'
    data = ka_public.extract_response_data(data)
    correct_data = {"unixtime": 1617831335, "rfc1123": "Wed,  7 Apr 21 21:35:35 +0000"}
    assert data == correct_data

    # Extract error message when received one
    data = b'{"error":["EOrder:Insufficient funds"]}'
    data = ka_public.extract_response_data(data)
    assert data == "EOrder:Insufficient funds"

