#!/bin/sh
set -e

OPTIONS_FILE="/data/options.json"

CONFIG_PATH=$(jq -r '.mqtt_io_config_path' "$OPTIONS_FILE")
LOG_LEVEL=$(jq -r '.log_level' "$OPTIONS_FILE" | tr '[:lower:]' '[:upper:]')

echo "[io2mqtt] File di configurazione MQTT-IO: ${CONFIG_PATH}"
echo "[io2mqtt] Livello di log: ${LOG_LEVEL}"

if [ ! -f "$CONFIG_PATH" ]; then
    echo "[io2mqtt] ERRORE: file di configurazione non trovato in '${CONFIG_PATH}'"
    echo "[io2mqtt] Verifica il percorso nella configurazione dell'add-on (deve trovarsi in una cartella mappata, es. /config/...)."
    exit 1
fi

# Installa a runtime i binding Python GPIO (liblgpio è già compilata in fase di build)
/home/mqtt_io/venv/bin/python -m pip install --no-cache-dir lgpio gpiozero pyserial

# Genera una copia "effettiva" del file di configurazione con il livello di log
# richiesto dall'utente, senza modificare il file originale su disco
EFFECTIVE_CONFIG="/tmp/mqtt-io-effective-config.yml"

/home/mqtt_io/venv/bin/python - "$CONFIG_PATH" "$EFFECTIVE_CONFIG" "$LOG_LEVEL" <<'PYEOF'
import sys
import yaml

src_path, dst_path, level = sys.argv[1], sys.argv[2], sys.argv[3]

with open(src_path) as f:
    config = yaml.safe_load(f) or {}

logging_cfg = config.get("logging") or {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(name)s [%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
    "loggers": {"mqtt_io": {"handlers": ["console"], "propagate": True}},
}

logging_cfg.setdefault("handlers", {}).setdefault("console", {})["level"] = level
logging_cfg.setdefault("loggers", {}).setdefault("mqtt_io", {})["level"] = level
config["logging"] = logging_cfg

with open(dst_path, "w") as f:
    yaml.safe_dump(config, f, sort_keys=False)
PYEOF

sleep 2
exec /home/mqtt_io/venv/bin/python -m mqtt_io "$EFFECTIVE_CONFIG"
