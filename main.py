import os
from kraken_dca import KrakenApi, unix_time_datetime, current_datetime, DCA


if __name__ == '__main__':
    api_key = os.environ.get("KRAKEN_API_KEY")
    api_private_key = os.environ.get("KRAKEN_PRIVATE_KEY")
    ka = KrakenApi(api_key, api_private_key)

    kraken_time = ka.get_time()
    kraken_date = unix_time_datetime(kraken_time)
    current_date = current_datetime()
    print(f"Hi, it's {kraken_date} on Kraken, {current_date} on computer.")

    balance = ka.get_balance()
    print(balance)

    trade_balance = ka.get_trade_balance()
    print(trade_balance)

    dca = DCA(ka)
    dca.get_daily_orders()

