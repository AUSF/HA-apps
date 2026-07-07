# IO2MQTT

A local Home Assistant add-on that wraps the official [MQTT-IO](https://github.com/flyte/mqtt-io)
Docker image, exposing Raspberry Pi GPIO, serial communication, and sensors to
Home Assistant via MQTT.

## Supported hardware

- Raspberry Pi 3B+
- Raspberry Pi 4
- Raspberry Pi 5

GPIO access uses `gpiozero` with the `lgpio` backend, compiled from source at
build time. No external daemon or add-on is required (unlike solutions based
on `pigpio`, which does not support the Raspberry Pi 5).

## Configuration

| Option                | Description                                                        | Default                       |
|------------------------|----------------------------------------------------------------------|---------------------------------|
| `mqtt_io_config_path`  | Path to the MQTT-IO YAML configuration file                         | `/config/mqtt-io/config.yml`   |
| `log_level`            | MQTT-IO logging verbosity (`debug`, `info`, `warning`, `error`)     | `info`                          |

`mqtt_io_config_path` must point to a location inside a folder mapped into
the add-on (by default, `/config`).

The log level set via this option takes priority over any `logging:` section
already present in your MQTT-IO configuration file.

## The MQTT-IO configuration file

The file itself follows the standard MQTT-IO syntax — see the
[upstream documentation](https://github.com/flyte/mqtt-io/wiki/Configuration)
for the full reference (`mqtt`, `gpio_modules`, `digital_inputs`,
`digital_outputs`, `sensor_modules`, `stream_modules`, etc).

### Custom serial module: `serial_term`

This add-on ships an additional stream module, `serial_term`, alongside the
stock `serial` module from upstream MQTT-IO. Use it when your device talks
line-based text over a serial connection (e.g. an Arduino), and you want the
add-on itself to guarantee correct framing on both directions — instead of
relying on the sender/receiver to always append the right terminator.

```yaml
stream_modules:
  - name: serial
    module: serial_term
    device: /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0
    baud: 9600
    read_interval: 5
    read: true
    write: true
    terminator: "\n"
    read_timeout: 5.0
```

Behaviour:

- **Writing**: the configured `terminator` is automatically appended to every
  command received on `<topic_prefix>/stream/<name>/send`, before it's
  written to the serial port. You no longer need to embed `\n` (or worry
  about it being stripped by a template editor) in your Home Assistant
  scripts/automations — just publish the plain command text.
- **Reading**: incoming bytes are buffered until a full `terminator`-delimited
  line is available; only complete lines are published (the terminator
  itself is stripped from the published payload). This correctly reassembles
  data split across multiple USB packets.
- **`read_timeout`** (seconds, default `5.0`): if a partial line sits in the
  read buffer for longer than this without ever receiving a terminator (e.g.
  after a device reset, or a dropped byte), it is discarded and logged as a
  warning, instead of silently corrupting the next good read. Set to `0` to
  disable this safeguard.

## Notes

- Startup logs are the fastest way to confirm the `lgpio` pin factory loaded
  correctly — enable `log_level: debug` if you run into GPIO issues.
- Raspberry Pi 5 support relies on a fairly young code path in `gpiozero`;
  if you hit GPIO issues specifically on a Pi 5, please open an issue with
  the output of `gpiodetect` and `gpioinfo` from the host.
  