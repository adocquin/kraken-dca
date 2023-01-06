# 🐙 Kraken-DCA
![Docker Pulls](https://img.shields.io/docker/pulls/futurbroke/kraken-dca)
![main-unit-testing workflow](https://github.com/adocquin/kraken-dca/actions/workflows/main-unit-testing.yaml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/adocquin/kraken-dca/badge.svg)](https://coveralls.io/github/adocquin/kraken-dca)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/krakenapi)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub](https://img.shields.io/github/license/adocquin/kraken-dca)

**Automate Dollar Cost Averaging on Kraken exchange**

## Table of Contents
1. ➤ [About the project](#-about-the-project)
2. ➤ [Orders](#-orders)
    - [What are the order settings ?](#what-are-the-order-settings-?)
    - [How are price, volume and fee computed ?](#how-are-price,-volume-and-fee-computed-?)
    - [How is order history saved ?](#how-is-order-history-saved-?)
3. ➤ [Configuration](#-configuration)
4. ➤ [Run with Docker](#-run-with-docker)
5. ➤ [Run without Docker](#-run-without-docker)
      - [Launch Kraken-DCA](#launch-kraken-dca)
      - [Automate DCA through cron](#automate-dca-through-cron)
6. ➤ [License](#-license)
7. ➤ [How to contribute](#-how-to-contribute)

# 🔍 About the project

Kraken-DCA is a python program to automate pairs
[Dollar Cost Averaging](https://www.investopedia.com/terms/d/dollarcostaveraging.asp)
on as many pairs as you want on [Kraken](https://kraken.com) exchange.<br>
At every launch, if no DCA pair order was already passed for each pair and delay in 
configuration file, it will create a buy limit order at current pair ask price for the specified amount.

Order history is saved in CSV format.

The program will need a Kraken public and private API key with permissions to:
- Consult funds
- View open orders & transactions
- View closed orders & transactions
- Create and modify orders

API keys can be created from the [API page](https://www.kraken.com/u/security/api) of your Kraken account.

# 📒 Orders
The pair and the amount to buy need to be specified in the configuration file.

## What are the order settings ?
A buy limit taker order is created by the program at its execution, 0.26% fee are assumed.<br>
Orders are created only if no one were created during the current day for the specified pair and are immediately 
executed.<br>
Pair quote asset are used to pay Kraken fee.

## How are price, volume and fee computed ?
**Limit price**: The pair ask price at the moment of the program execution.

**Volume**: The order volume is the amount*price truncated down to the pair lot decimals, then adjusted to volume/1.0026
truncated down the pair lot decimals.<br>
By adjusting the volume, the total price of the order with fee included doesn't exceed the configuration amount.<br>

**Order price**: The order price is estimated as volume*pair_ask_price rounded to the quote asset decimals.

**Fee**: Fee are included in the specified amount by adjusting down the order volume.
0.26% taker fee are assumed and are estimated as the order_price*0.0026 round to the quote asset decimals.

Kraken documentation:
- [Kraken API documentation](https://www.kraken.com/en-us/features/api)
- [Are internal calculations made in float point or with a fixed number of decimals? Are the values always rounded?](https://support.kraken.com/hc/en-us/articles/201988998-Are-internal-calculations-made-in-float-point-or-with-a-fixed-number-of-decimals-Are-the-values-always-rounded-)
- [Assets info](https://api.kraken.com/0/public/Assets)
- [Tradable asset paird](https://api.kraken.com/0/public/AssetPairs)

## How is order history saved ?

Order history is saved in CSV format with following information per order:
- **date**: Order date.
- **pair**: Order pair, the configured DCA pair.
- **type**: Buy or sell order, *buy* in this case.
- **order_type**: Order type, *limit* in this case.
- **o_flags**: Order additional flag, *fciq* in this case to pay fee in pair quote asset.
- **pair_price**: Limit order pair price. Pair ask price at the moment of the DCA.
- **volume**: Order volume.
- **price**: Order price in pair quote asset.
- **fee**: Order fee in pair quote asset.
- **total_price**: price + fee
- **txid**: TXID of the order.
- **description**: Description of the order from Kraken.

Order history is by default saved in *orders.csv* in Kraken-DCA base directory, 
the output file can be changed through docker image execution as described below.

# 🔨 Configuration
Configuration is done through a yaml file.
If you don't use docker you must create a *config.yaml* file. It may be
copied from *config-sample.yaml* and adjusted to your requirements.

```yaml
# Kraken's API public and private keys.
api:
  public_key: "KRAKEN_API_PUBLIC_KEY"
  private_key: "KRAKEN_API_PRIVATE_KEY"

# DCA pairs configuration. You can add as many pairs as you want.
# pair: Name of the pair (list of available pairs: https://api.kraken.com/0/public/AssetPairs)
# delay: Delay in days between each buy limit order.
# amount: Amount of the order in quote asset.
# limit_factor (optional): Create the limit order at a price of current price
#                          multiplied by specified factor (up to 5 digits).
# max_price (optional): Maximum price to create a limit order, after looking at
#                       limit_factor if set (up to 2 digits).
# ignore_differing_orders (optional): May be set to True to ignore any set open or
#                          closed orders within the time delay that differ more than 1%
#                          tin the desired amount. This allows to have manually set
#                          limit orders while still DCAing.
# E.g., limit_factor = 0.95 creates a limit order 5% below market price
dca_pairs:
  - pair: "XETHZEUR"
    delay: 1
    amount: 15
    limit_factor: 0.985
    max_price: 2900.10
  - pair: "XXBTZEUR"
    delay: 3
    amount: 20
    ignore_differing_orders: True
```
- In api, public_key and private_key correspond to your Kraken API key information.
- Delay is the number of days between buy orders. Set to 1 to DCA each day, 7 once per week.
- Available pairs for pair field can be found [here](https://api.kraken.com/0/public/AssetPairs) on *altname*.
- Amount is the amount of quote asset to sell to buy base asset.
- You can specify as many pairs as you want in the dca_pairs list.
- Set a `limit_factor` if you want to place the buy order that is different from the 
  current market price (up to 5 digits).<br>
  E.g., `limit_factor: 0.95` would set the limit price 5% below the market price.
- Set a `max_price` if you want to define a maximum price in quote pair to create a 
  limit buy order (after using `limit_factor` if defined).
- Set `ignore_differing_orders` to `True` to ignore orders within the time delay that 
  differ more than 1% in the desired amount. This allows to have manually set limit
  orders while still DCAing.

More information on 
[Kraken API official documentation](https://support.kraken.com/hc/en-us/articles/360000920306-Ticker-pairs).

# 🐳 Run with Docker
You can download the image directly from [Docker Hub](https://hub.docker.com/) using:
```sh
docker pull futurbroke/kraken-dca:latest
```
The program will be executed every hour as a cron job in a container.<br>
You must provide an empty order history CSV file at first launch. You can create one on unix system using:
```sh
touch orders.csv
```
To start the container with restart as system reboot use:
```sh
docker run -v CONFIGURATION_FILE_PATH:/app/config.yaml \
 -v ORDERS_FILE_PATH:/app/orders.csv \
 --name kraken-dca \
 --restart=on-failure futurbroke/kraken-dca
```
- **CONFIGURATION_FILE_PATH**: Configuration folder filepath (e.g., *~/dev/config.yaml*).
- **ORDERS_FILE_PATH**: Order history CSV filepath (e.g., *~/dev/orders.csv*).

To see container logs:
```sh
docker logs kraken-dca
```
To stop and delete the container:
```sh
docker kill kraken-dca
docker rm kraken-dca
```

# 🐍 Run without Docker
You must specify your configuration in a *config.yaml* file in the *Kraken-DCA* root folder.
## Launch Kraken-DCA
You can launch the program from the folder where you downloaded the repository folder using:
```sh
python kraken-dca
```
Or inside Kraken-DCA base directory using:
```sh
python __main__.py
```
## Automate DCA through cron
You can automate the execution by using cron on unix systems.
To execute the program every hour (it will only buy if no DCA pair order was done the current day) run in a shell:
```sh
crontab -e
```
And add:
```
0 * * * * cd PROGRAM_ROOT_FOLDER && $(which python3) kraken-dca >> OUTPUT_FILE 2>&1
```
- **PROGRAM_ROOT_FOLDER**: Folder where you downloaded the repository (e.g., *~/dev*).<br>
- **OUTPUT_FILE**: Program outputs log file (e.g., *~/cron.log*).<br>

Program outputs will be available in your output file, order history in *orders.csv* in Kraken-DCA base directory.

To deactivate the cron job remove the line using again:
```sh
crontab -e
```

More crontab execution frequency options: https://crontab.guru/

# 📔 License
Kraken-DCA  is distributed under the terms of the GNU General Public License v3.0. A
complete version of the license is available in the 
[LICENSE.md](https://github.com/FuturBroke/kraken-dca/blob/main/README.md) in
this repository. Any contribution made to this project will be licensed under
the GNU General Public License v3.0.

# 🙋‍♀️ How to contribute
Thanks for your interest in contributing to the project. You can contribute freely by 
creating an issue, fork or create a pull request. Before issuing a pull request, make 
sure the changes did not break any existing functionality and are fully covered with
unit tests by running this command in the base directory:
```sh
pytest -vv --cov
```
