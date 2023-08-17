FROM node:lts

ENV LANG=C.UTF-8

RUN DEBIAN_FRONTEND=non-interactive && \
    mkdir /logs && \
    apt-get -y update && \
    apt-get -y install software-properties-common gcc libgirepository1.0-dev && \
    apt-get -y install python3 python3-pip python3-distutils python3-apt && \
    groupadd -r -g 55020 appuser && \
    groupadd -r -g 4177 epadd_secure && \
    useradd -u 55020 -g 55020 -G 4177 --create-home appuser

WORKDIR /home/appuser/cron

COPY . /home/appuser/cron

RUN chown appuser:appuser -R /home/appuser && \
    chown appuser:appuser -R /logs

USER appuser

RUN npm install && \
    python3 -m pip install -r requirements.txt --break-system-packages && \
    chmod +x /home/appuser/cron/monitor_dropbox.py && \
    chmod +x /home/appuser/cron/monitor_unprocessed_batches.py

CMD ["node", "./cron.js"]
