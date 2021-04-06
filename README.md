# Kraken DCA

Kraken DCA is a python program to automate
[Dollar Cost Averaging](https://www.investopedia.com/terms/d/dollarcostaveraging.asp) on [Kraken](https://kraken.com) exchange.<br>
At every launch, the program will check if an order was already passed in the current day for the specified pair in the configuration file.
If not, it will buy the specified amount.

To work properly, the program will need a public and private API key from Kraken with permissions to:
- Consult funds
- View open orders & transactions
- View closed orders & transactions
- Create and modify orders

You can create API keys from the [API page](https://www.kraken.com/u/security/api) in your Kraken account.

## Configuration file example
```yaml
# Kraken's API public and private keys.
api:
  public_key: "KRAKEN_API_PUBLIC_KEY"
  private_key: "KRAKEN_API_PRIVATE_KEY"

# Pair to DCA and corresponding amount per day.
dca:
  pair: "XETHZEUR"
  amount: 20
```
- Available pairs for pair field can be found [here](https://api.kraken.com/0/public/AssetPairs) on *altname*.
- The *amount* field is the amount of *quote* pair to spend to buy *base* pair in the above link.

More information on [Kraken API official documentation](https://support.kraken.com/hc/en-us/articles/360000920306-Ticker-pairs).

Depending on your usage, you will need to pass your configuration file with the docker run command or edit the
*config.yaml* file.

## Usage with Docker
You can download the image directly from [Docker Hub](https://hub.docker.com/) using:
```sh
docker pull adocquin/kraken-dca:latest
```
The program will be executed every hour as a cron job in a container.<br>
To start the container, send your configuration file, name the container as kraken-dca and restart it on failure or at system reboot:
```sh
docker run -v CONFIGURATION_FILE_PATH:/app/config.yaml --name kraken-dca --restart=on-failure adocquin/kraken-dca
```
**CONFIGURATION_FILE_PATH**: Full local configuraiton file (e.g., *~/dev/config.yaml*).

To see program container logs:
```sh
docker logs kraken-dca
```
To stop and delete the container:
```sh
docker kill kraken-dca
docker rm kraken-dca
```

## Usage without Docker
You must specify your configuration in a *config.yaml* file in the *kraken-dca* root folder.
### From shell
You can launch the program from the folder where you downloaded the repository folder using:
```sh
python kraken-dca
```
Or inside *kraken-dca* root folder using:
```sh
python __main__.py
```
### Using cron
You can automate the execution by using cron on unix systems.
To execute the program every hour (it will only buy if no order was open during the current day) executes in a shell:
```sh
crontab -e
```
And add:
```
0 * * * * cd PROGRAM_ROOT_FOLDER && $(which python3) kraken-dca >> OUTPUT_FILE 2>&1
```
**PROGRAM_ROOT_FOLDER**: Folder where you downloaded the repository (e.g., *~/dev*).<br>
**OUTPUT_FILE**: File to log the program outputs (e.g., *~/cron.log*).<br>

Program outputs will be available in your output file.

To deactivate the cron job remove the line using again:
```sh
crontab -e
```

## How to contribute
Thanks for your interest in contributing to the project. You can contribute freely to the project by creating an issue, a pull request or fork it.
Before issuing a pull request, make sure the changes did not break any existing functionality by running unit tests in the *kraken-dca* folder:
```sh
pytest
```
