import argparse
from kraken_dca import KrakenApi, unix_time_datetime, current_datetime, DCA


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-k", "--api_key", type=str, help="Kraken API key."
    )
    parser.add_argument(
        "-s", "--private_key", type=str, help="Kraken private key."
    )
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
    if not args.api_key:
        print("Please provide you Kraken API key.")
    elif not args.private_key:
        print("Please provide you Kraken private key.")
    elif not args.pair:
        print("Please provide the pair to dollar cost average using -p option.")
    elif not args.amount:
        print("Please provide the amount to daily dollar cost average using -a option.")
    else:
        ka = KrakenApi(args.api_key, args.private_key)

        kraken_time = ka.get_time()
        kraken_date = unix_time_datetime(kraken_time)
        current_date = current_datetime()
        print(f"Hi, it's {kraken_date} on Kraken, {current_date} on computer.")

        balance = ka.get_balance()
        print(f"Current balance: {balance}")

        trade_balance = ka.get_trade_balance()
        print(f"Current trade balance: {trade_balance}")

        dca = DCA(ka, args.pair, args.amount)
        daily_pair_orders = dca.count_pair_daily_orders()
        if daily_pair_orders == 0:
            print("Didn't DCA already today.")
            pair_ask_price = dca.get_pair_ask_price()
            print(f"Current {args.pair} ask price: {pair_ask_price}")
            dca.create_dca_pair_limit_order(pair_ask_price)
        else:
            print("Already DCA today.")
