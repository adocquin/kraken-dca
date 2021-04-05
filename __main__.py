from kraken_dca import Config, KrakenApi, DCA


if __name__ == "__main__":
    try:
        # Check configuration file.
        config = Config()
        # Initialize the KrakenAPI object.
        ka = KrakenApi(config.api_key, config.api_secret)
        # Initialize the DCA object
        dca = DCA(ka, config.pair, config.amount)
        # Get DCA pair information
        dca.get_dca_pair_information()
        # Check current system time
        dca.check_system_time()
        # Check Kraken account balance
        dca.check_account_balance()
        # Create a buy limit order for specified pair and quote amount if didn't DCA today.
        daily_pair_orders = dca.count_pair_daily_orders()
        if daily_pair_orders == 0:
            print("Didn't DCA already today.")
            pair_ask_price = dca.get_pair_ask_price()
            print(f"Current {config.pair} ask price: {pair_ask_price}.")
            dca.create_buy_limit_order(pair_ask_price)
        else:
            print("Already DCA today.")
    except Exception as e:
        print(e)
