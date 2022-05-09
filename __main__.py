import os

from krakenapi import KrakenApi

from krakendca import Config, KrakenDCA

if __name__ == "__main__":
    # Get parameters from configuration file.
    current_directory: str = os.getcwd()
    config_file: str = current_directory + "/config.yaml"
    config: Config = Config(config_file)
    # Initialize the KrakenAPI object.
    ka: KrakenApi = KrakenApi(config.api_public_key, config.api_private_key)
    # Initialize KrakenDCA and handle the DCA based on configuration.
    kdca: KrakenDCA = KrakenDCA(config, ka)
    kdca.initialize_pairs_dca()
    kdca.handle_pairs_dca()
