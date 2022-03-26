from krakenapi import KrakenApi

from krakendca import Config, KrakenDCA

if __name__ == "__main__":
    # Get parameters from configuration file.
    config = Config("config.yaml")
    # Initialize the KrakenAPI object.
    ka = KrakenApi(config.api_public_key, config.api_private_key)
    # Initialize KrakenDCA and handle the DCA based on configuration.
    kdca = KrakenDCA(config, ka)
    kdca.initialize_pairs_dca()
    kdca.handle_pairs_dca()
