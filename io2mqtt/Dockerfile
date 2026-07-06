FROM flyte/mqtt-io:latest
USER root

# Debian buster è EOL: puntiamo all'archivio storico e ignoriamo la scadenza dei Release file.
# jq serve per leggere le opzioni dell'add-on da /data/options.json in run.sh.
RUN sed -i \
      -e 's|deb.debian.org|archive.debian.org|g' \
      -e 's|security.debian.org|archive.debian.org|g' \
      /etc/apt/sources.list \
    && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcc swig python3-dev make curl jq ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    # L'header linux/gpio.h di buster è troppo vecchio (API GPIO chardev v1, kernel ~4.19):
    # la libreria lg richiede la v2 (kernel 5.10+), che il kernel reale della Pi già supporta.
    && curl -sL https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/linux/gpio.h \
         -o /usr/include/linux/gpio.h \
    && curl -sL https://github.com/joan2937/lg/archive/refs/heads/master.tar.gz | tar xz -C /tmp \
    && cd /tmp/lg-master \
    && make \
    && make install \
    && ldconfig \
    && rm -rf /tmp/lg-master

# Pin factory nativo per gpiozero: parla a /dev/gpiochip* in-process, niente demone/add-on esterno
ENV GPIOZERO_PIN_FACTORY=lgpio

COPY run.sh /run.sh
RUN sed -i 's/\r$//' /run.sh && chmod a+x /run.sh

ENTRYPOINT ["/run.sh"]