import binascii
import time
import base64
import json
import hashlib
import hmac
from urllib.request import Request, urlopen
from urllib.parse import urlencode


class KrakenApi:
    """
    Encapsulation of Kraken api through python object.
    Easily requests Kraken's api endpoints.
    """

    api_public_key: str
    api_private_key: str

    def __init__(self, api_public_key: str, api_private_key: str):
        """
        Initialize the KrakenAPI object.

        :param api_public_key: Kraken api key.
        :param api_private_key: Kraken api secret key.
        """
        self.api_public_key = api_public_key
        self.api_private_key = api_private_key

    @staticmethod
    def create_api_path(public_method: bool, api_method: str) -> str:
        """
        Given a method, return the api url to request.

        :param public_method: Is the method a public market data.
        :param api_method: Api method as string.
        :return: Api url to request.
        """
        api_domain: str = "https://api.kraken.com"
        api_type = "/0/public/" if public_method else "/0/private/"
        api_path = api_domain + api_type + api_method
        return api_path

    @staticmethod
    def create_api_post_data(post_inputs: dict, api_nonce: str = "") -> bytes:
        """
        Create api post data for private user methods.

        :param api_nonce: Unique API call identifier as string.
        :param post_inputs: POST inputs as dict.
        :return: API post data.
        """
        if post_inputs and api_nonce:
            post_inputs.update({"nonce": api_nonce})
        elif api_nonce:
            post_inputs = {"nonce": api_nonce}
        api_post_data = urlencode(post_inputs).encode()
        return api_post_data

    def create_api_signature(
        self, api_nonce: str, api_post_data: bytes, api_method: str
    ) -> str:
        """
        Create api signature for private user methods.

        :param api_nonce: Unique API call identifier as string.
        :param api_post_data: Bytes encoded API POST data.
        :param api_method: API method to call.
        :return: API signature to use as HTTP header.
        """
        # Cryptographic hash algorithms
        api_sha256 = hashlib.sha256(api_nonce.encode() + api_post_data)
        # Decode API private key from base64 format displayed in account management
        try:
            api_secret = base64.b64decode(self.api_private_key)
        except binascii.Error as e:
            raise ValueError(f"Incorrect Kraken API private key: {e}")
        api_hmac = hmac.new(
            api_secret,
            f"/0/private/{api_method}".encode() + api_sha256.digest(),
            hashlib.sha512,
        )
        # Encode signature into base64 format used in API-Sign value
        api_signature = base64.b64encode(api_hmac.digest())
        # API authentication signature for use in API-Sign HTTP header
        api_signature = api_signature.decode()
        return api_signature

    @staticmethod
    def extract_response_data(data: bytes) -> dict:
        """
        Extract data from Kraken API request response.

        :return: Request response data as dict
        """
        data = data.decode()
        data = json.loads(data)
        data = data.get("error")[0] if data.get("error") else data.get("result")
        return data

    def request(
        self, public_method: bool, api_method: str, post_inputs: dict = None
    ) -> dict:
        """
        Given a method, request the Kraken api and return the result data.

        :param public_method: Is the method a public market data.
        :param api_method: API method as string.
        :param post_inputs: POST inputs as dict.
        :return: Result as python dictionary.
        """
        api_path = KrakenApi.create_api_path(public_method, api_method)

        if public_method and post_inputs:
            # Create POST data
            api_post_data = self.create_api_post_data(post_inputs)
            request = Request(api_path, data=api_post_data)
        elif public_method:
            request = Request(api_path)
        else:  # Handle API authentication for private user methods
            api_nonce = str(int(time.time() * 1000))
            # Create POST data
            api_post_data = self.create_api_post_data(post_inputs, api_nonce)
            # Generate the request
            request = Request(api_path, data=api_post_data)
            # Adding HTTP headers to request
            api_signature = self.create_api_signature(
                api_nonce, api_post_data, api_method
            )
            request.add_header("API-Sign", api_signature)
            request.add_header("API-Key", self.api_public_key)

        # Request the api
        data = urlopen(request).read()
        # Decode the API response
        data = self.extract_response_data(data)
        # Raise an error if Kraken response is a string
        if type(data) == str:
            raise ValueError(f"Kraken API error -> {data}")
        return data

    def get_asset_pairs(self) -> dict:
        """
        Return current Kraken account trade balance.

        :return: Dict of available asset pairs and their information.
        """
        data = self.request(True, "AssetPairs")
        return data

    def get_time(self) -> int:
        """
        Return current Kraken time as string.

        :return: Kraken time as string.
        """

        data = self.request(True, "Time")
        kraken_time = data.get("unixtime")
        return kraken_time

    def get_balance(self) -> dict:
        """
        Return current Kraken account balance.

        :return: Dict of asset names and balance amount.
        """
        data = self.request(False, "Balance")
        return data

    def get_trade_balance(self) -> dict:
        """
        Return current Kraken account trade balance.

        :return: Dict of asset names and balance amount.
        """
        data = self.request(False, "TradeBalance")
        return data

    def get_open_orders(self) -> dict:
        """
        Return current Kraken open orders.

        :return: Dict of open orders txid as the key.
        """
        data = self.request(False, "OpenOrders")
        data = data.get("open")
        return data

    def get_closed_orders(self, post_inputs: dict = None) -> dict:
        """
        Return current Kraken closed orders.

        :param post_inputs: POST inputs as dict.
        :return: Dict of closed orders txid as the key.
        """
        data = self.request(False, "ClosedOrders", post_inputs)
        data = data.get("closed")
        return data

    def get_pair_ticker(self, pair: str) -> dict:
        """
        Return pair ticker information.

        :param pair: Pair to get ticker information.
        :return: Pair ticker information as dict.
        """
        post_inputs = {"pair": pair}
        data = self.request(True, "Ticker", post_inputs)
        return data

    def create_limit_order(
        self, pair: str, buy: bool, price: float, volume: float
    ) -> dict:
        """
        Create a limit order.

        :param pair: Pair to get ticker information.
        :param buy: Boolean to buy if true else sell.
        :param price: Price to buy the pair.
        :param volume: Order volume in lots.
        :return: Pair ticker information as dict.
        """
        order_type = "buy" if buy else "sell"
        post_inputs = {
            "pair": pair,
            "type": order_type,
            "ordertype": "limit",
            "price": price,
            "volume": volume,
        }
        data = self.request(False, "AddOrder", post_inputs)
        return data
