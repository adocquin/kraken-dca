import os
from kraken_api import KrakenApi


def print_hi():
    api_key = os.environ.get("KRAKEN_API_KEY")
    api_private_key = os.environ.get("KRAKEN_PRIVATE_KEY")
    ka = KrakenApi(api_key, api_private_key)

    kraken_time = ka.get_time()
    print(f"Hi, it's {kraken_time} on Kraken.")
    kraken_balance = ka.get_balance()
    print(kraken_balance)
    kraken_trade_balance = ka.get_trade_balance()
    print(kraken_trade_balance)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
