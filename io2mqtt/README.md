# IO2MQTT

Add-on Home Assistant locale che incapsula [MQTT-IO](https://github.com/flyte/mqtt-io)
per l'accesso a GPIO/seriale su Raspberry Pi (3B+, 4, 5).

Vedi [DOCS.md](DOCS.md) per la documentazione utente completa.

## Sviluppo

- `Dockerfile`: build basata su `flyte/mqtt-io:latest` (Debian buster), con
  compilazione di `liblgpio` dal sorgente per supporto RPi5.
- `run.sh`: legge le opzioni dell'add-on da `/data/options.json`, genera una
  copia effettiva del config MQTT-IO con il log level richiesto.