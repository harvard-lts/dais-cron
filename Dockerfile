FROM node:lts

ENV LANG=C.UTF-8

RUN DEBIAN_FRONTEND=non-interactive && \
    mkdir /logs && \
    apt-get -y update && \
    apt-get -y install software-properties-common gcc && \
    apt-get -y install python3 python3-pip python3-distutils python3-apt && \
    groupadd -r -g 55020 appuser && \
    useradd -u 55020 -g 55020 --create-home appuser

WORKDIR /home/appuser/cron

COPY . /home/appuser/cron

RUN chown appuser:appuser -R /home/appuser && \
    chown appuser:appuser -R /logs

USER appuser

# Append SAN section to openssl.cnf and generate a new self-signed certificate and key
RUN mkdir -p /home/node/ssl/certs && \
    cp /etc/ssl/openssl.cnf /home/node/ssl/openssl.cnf && \
    printf "[SAN]\nsubjectAltName=DNS:*.hul.harvard.edu,DNS:*.lts.harvard.edu" >> /home/node/ssl/openssl.cnf && \
    openssl req -new -newkey rsa:4096 -days 3650 -nodes -x509 -subj "/C=US/ST=Massachusetts/L=Cambridge/O=Library Technology Services/CN=*.lib.harvard.edu" -extensions SAN -reqexts SAN -config /home/node/ssl/openssl.cnf -keyout /home/node/ssl/certs/server.key -out /home/node/ssl/certs/server.crt && \
    mkdir -p /home/node/app

RUN npm install && \
    python3 -m pip install -r requirements.txt && \
    chmod +x /home/appuser/cron/monitor_dropbox.py

CMD ["node", "./cron.js"]
