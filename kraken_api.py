import time
import base64
import ast
import hashlib
import hmac
from urllib.request import Request, urlopen
from urllib.parse import urlencode


class KrakenApi:
    """
    Encapsulation of Kraken api through python object.
    Easily requests Kraken's api endpoints.
    """

    api_key: str
    api_private_key: str

    def __init__(self, api_key: str, api_private_key: str):
        """
        Initialize the KrakenAPI object.

        :param api_key: Kraken api key.
        :param api_private_key: Kraken api secret key.
        """
        self.api_key = api_key
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
    def create_api_post_data(api_nonce: str) -> bytes:
        """
        Create api post data for private user methods.

        :param api_nonce: Unique API call identifier as string.
        :return: API post data.
        """
        api_post_data = {"nonce": api_nonce}
        api_post_data = urlencode(api_post_data)
        api_post_data = api_post_data.encode("ascii")
        return api_post_data

    def create_api_signature(self, api_nonce: str, api_method: str) -> str:
        """
        Create api signature for private user methods.

        :param api_nonce: Unique API call identifier as string.
        :param api_method: API method to call.
        :return: API signature to use as HTTP header.
        """
        api_post = "nonce=" + api_nonce
        # Cryptographic hash algorithms
        api_sha256 = hashlib.sha256(
            api_nonce.encode("utf-8") + api_post.encode("utf-8")
        )
        # Decode API private key from base64 format displayed in account management
        api_secret = base64.b64decode(self.api_private_key)
        api_hmac = hmac.new(
            api_secret,
            f"/0/private/{api_method}".encode("utf-8") + api_sha256.digest(),
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
        data = data.decode("UTF-8")
        data = ast.literal_eval(data)
        data = data.get("error")[0] if data.get("error") else data.get("result")
        return data

    def request(self, public_method: bool, api_method: str) -> dict:
        """
        Given a method, request the Kraken api and return the result data.

        :param public_method: Is the method a public market data.
        :param api_method: API method as string.
        :return: Result as python dictionary.
        """
        api_path = KrakenApi.create_api_path(public_method, api_method)

        if public_method:
            request = Request(api_path)
        else:  # Handle API authentication for private user methods
            api_nonce = str(int(time.time() * 1000))
            # Create POST data
            api_post_data = self.create_api_post_data(api_nonce)
            # Generate the request
            request = Request(api_path, data=api_post_data)
            # Adding HTTP headers to request
            api_signature = self.create_api_signature(api_nonce, api_method)
            request.add_header("API-Sign", api_signature)
            request.add_header("API-Key", self.api_key)

        # Request the api
        data = urlopen(request).read()
        # Decode the API response
        data = self.extract_response_data(data)
        return data

    def get_time(self) -> str:
        """
        Return current Kraken time as string.

        :return: Kraken time as string.
        """

        data = self.request(True, "Time")
        kraken_time = data.get("rfc1123")
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
