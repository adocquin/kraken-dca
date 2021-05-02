from kraken_dca import Config, KrakenApi, Pair, DCA


if __name__ == "__main__":
    try:
        # Get parameters form configuration file.
        config = Config("config.yaml")
        # Initialize the KrakenAPI object.
        ka = KrakenApi(config.api_public_key, config.api_private_key)
        # Initialize the Pair object from pair specified in
        # configuration file and data from Kraken.
        pair = Pair.get_pair_from_kraken(ka, config.pair)
        # Initialize the DCA object.
        dca = DCA(ka, config.delay, pair, config.amount)
        # Execute DCA logic.
        dca.handle_dca_logic()
    except Exception as e:
        print(e)
