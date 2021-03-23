import argparse
import os
from kraken_dca import KrakenApi, unix_time_datetime, current_datetime, DCA


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--pair", type=str, help="Pair to dollar cost average (e.g, XBT/EUR)."
    )
    parser.add_argument(
        "-a",
        "--amount",
        type=float,
        help="Amount to daily dollar cost average (e.g, 30 for 30€).",
    )
    args = parser.parse_args()

    if not args.pair:
        print("Please provide the pair to dollar cost average using -p option.")
    elif not args.amount:
        print("Please provide the amount to daily dollar cost average using -a option.")
    else:
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

        dca = DCA(ka, args.pair, args.amount)
        print(dca.count_pair_daily_orders())
