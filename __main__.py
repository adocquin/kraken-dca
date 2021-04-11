from kraken_dca import Config, KrakenApi, DCA


if __name__ == "__main__":
    try:
        # Check configuration file.
        config = Config.read_config_file("config.yaml")
        # Initialize the KrakenAPI object.
        ka = KrakenApi(config.api_public_key, config.api_private_key)
        # Initialize the DCA object.
        dca = DCA(ka, config.pair, config.amount)
        # Execute DCA logic.
        dca.handle_dca_logic()
    except Exception as e:
        print(e)
