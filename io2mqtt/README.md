# IO2MQTT

A local Home Assistant add-on wrapping [MQTT-IO](https://github.com/flyte/mqtt-io)
for GPIO/serial access on Raspberry Pi (3B+, 4, 5).

See [DOCS.md](io2mqtt/DOCS.md) for full user documentation.

## Repository structure

```text
.
├── repository.yaml
├── .github/
│   └── workflows/
│       └── build.yml          # multi-arch build & publish to GHCR
└── io2mqtt/
    ├── config.yaml
    ├── Dockerfile
    ├── run.sh                 # reads add-on options, launches MQTT-IO
    ├── serial_term.py         # custom stream module (terminator + timeout)
    ├── icon.png
    ├── logo.png
    ├── DOCS.md
    └── translations/
```

## Installation

In Home Assistant: **Settings → Add-ons → Store → ⋮ → Repositories**, add
this repository's URL. The IO2MQTT add-on will then appear in the store.

Images are pre-built for `aarch64`, `armv7`, and `amd64` and published to
GHCR — no compilation happens on the target device.

## Development notes

- **Base image**: `flyte/mqtt-io:latest` (Debian buster). `pigpio` is
  intentionally not used, since it does not support the Raspberry Pi 5;
  `lgpio` is compiled from source at build time (`joan2937/lg`), along with
  an updated `linux/gpio.h` kernel header (buster's is too old for the GPIO
  v2 chardev API that `lg` requires).
- **`run.sh`**: reads `/data/options.json` (via `jq`), generates an
  effective copy of the user's MQTT-IO config with the requested log level
  injected, and launches MQTT-IO against that copy — the user's original
  file is never modified in place.
- **Releasing**: push a tag matching `v*.*.*` (e.g. `v0.4.0`) to trigger the
  build workflow. After the first push of a new image, remember to set the
  GHCR package visibility to **public**, or Supervisor's anonymous pull will
  fail.
