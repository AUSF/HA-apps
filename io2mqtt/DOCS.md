# IO2MQTT

Wrapper locale attorno all'immagine Docker ufficiale di [MQTT-IO](https://github.com/flyte/mqtt-io),
per esporre GPIO, seriale e sensori del Raspberry Pi via MQTT a Home Assistant.

## Hardware supportato

- Raspberry Pi 3B+
- Raspberry Pi 4
- Raspberry Pi 5

Accesso GPIO tramite `gpiozero` con backend `lgpio` (nessun demone esterno richiesto,
a differenza di soluzioni basate su `pigpio`, non compatibile con Raspberry Pi 5).

## Configurazione

| Opzione                | Descrizione                                                              | Default                        |
|-------------------------|---------------------------------------------------------------------------|---------------------------------|
| `mqtt_io_config_path`   | Percorso del file YAML di configurazione di MQTT-IO                      | `/config/mqtt-io/config.yml`   |
| `log_level`             | Livello di log di MQTT-IO (`debug`, `info`, `warning`, `error`)          | `info`                          |

Il percorso indicato in `mqtt_io_config_path` deve trovarsi dentro una cartella
mappata nell'add-on (di default `/config`).

## Note

- Il file di configurazione di MQTT-IO segue la sintassi standard del progetto upstream;
  fai riferimento alla [documentazione ufficiale](https://github.com/flyte/mqtt-io/wiki/Configuration).
- Il livello di log impostato tramite l'opzione dell'add-on ha priorità sulla sezione
  `logging:` eventualmente presente nel file di configurazione.