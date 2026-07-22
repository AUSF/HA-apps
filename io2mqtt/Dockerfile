FROM flyte/mqtt-io:latest
USER root

RUN sed -i \
      -e 's|deb.debian.org|archive.debian.org|g' \
      -e 's|security.debian.org|archive.debian.org|g' \
      /etc/apt/sources.list \
    && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcc swig python3-dev make curl jq ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sL https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/linux/gpio.h \
         -o /usr/include/linux/gpio.h \
    && curl -sL https://github.com/joan2937/lg/archive/refs/heads/master.tar.gz | tar xz -C /tmp \
    && cd /tmp/lg-master \
    && make \
    && make install \
    && ldconfig \
    && cd / \
    && rm -rf /tmp/lg-master \
    && /home/mqtt_io/venv/bin/python -m pip install --no-cache-dir lgpio gpiozero pyserial

ENV GPIOZERO_PIN_FACTORY=lgpio

COPY run.sh /run.sh
COPY serial_term.py /home/mqtt_io/mqtt_io/modules/stream/serial_term.py
RUN chmod a+x /run.sh

ENTRYPOINT ["/run.sh"]
