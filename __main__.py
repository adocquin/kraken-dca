from krakendca import Config, KrakenDCA
from krakenapi import KrakenApi


if __name__ == "__main__":
    # Get parameters from configuration file.
    config = Config("config.yaml")
    # Initialize the KrakenAPI object.
    ka = KrakenApi(config.api_public_key, config.api_private_key)
    # Initialize the KrakenDCA object and handle the DCA based on configuration.
    kdca = KrakenDCA(config, ka)
    kdca.initialize_dca()
    kdca.handle_dca()

