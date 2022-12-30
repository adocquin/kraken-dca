FROM python:3.8-slim-buster

# Install cron
RUN apt-get update && apt-get -y install cron

# Set /app as working directory
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy application files
COPY krakendca/ krakendca/
COPY config-sample.yaml config.yaml
COPY __main__.py __main__.py

# Create order history file
RUN sh -c "touch orders.csv"

# Copy and install crontab command
COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

CMD ["cron", "-f"]