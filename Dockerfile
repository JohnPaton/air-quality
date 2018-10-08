FROM python:3.6

WORKDIR /usr/src

# --- Install requirements
RUN apt-get update && apt-get install -y cron
COPY requirements.txt /usr/src
RUN grep -v "\-e" -i requirements.txt > requirements_nonlocal.txt
RUN pip install -r requirements_nonlocal.txt

# --- Install local package
RUN mkdir air-quality
COPY . air-quality
WORKDIR air-quality
RUN pip install .

# --- Set up background jobs
COPY scripts/crontab /etc/cron.d/air-quality
RUN mkdir /usr/openaq-temp
RUN chmod 0644 /etc/cron.d/air-quality
RUN crontab /etc/cron.d/air-quality

# --- Mount points for data
VOLUME /usr/db
VOLUME /usr/models

WORKDIR /usr/src/air-quality
CMD cron && python air_quality/server.py -m /usr/models -d /usr/db/aq.db

