"""
Modulo stream seriale con gestione esplicita di un terminatore di riga:
- in lettura, bufferizza i byte in arrivo e restituisce solo righe complete,
  delimitate dal terminatore configurato (rimosso dall'output); se un
  frammento incompleto resta senza terminatore oltre 'read_timeout' secondi,
  viene scartato con un warning, per non corrompere le letture successive;
- in scrittura, aggiunge automaticamente il terminatore ad ogni comando inviato.
"""
import logging
import time
from typing import Optional

from . import GenericStream

REQUIREMENTS = ("pyserial",)
BYTESIZE_CHOICES = (5, 6, 7, 8)
PARITY_CHOICES = ("none", "odd", "even", "mark", "space")
STOPBITS_CHOICES = (1, 1.5, 2)

_LOG = logging.getLogger(__name__)

CONFIG_SCHEMA = {
    "device": {"type": "string", "required": True, "empty": False},
    "baud": {"type": "integer", "required": True, "empty": False},
    "timeout": {"type": "integer", "required": False, "empty": False, "default": 20},
    "bytesize": {
        "type": "integer",
        "required": False,
        "default": 8,
        "empty": False,
        "allowed": BYTESIZE_CHOICES,
    },
    "parity": {
        "type": "string",
        "required": False,
        "default": "none",
        "empty": False,
        "allowed": PARITY_CHOICES,
    },
    "stopbits": {
        "type": "float",
        "required": False,
        "default": 1,
        "empty": False,
        "allowed": STOPBITS_CHOICES,
    },
    "terminator": {
        "type": "string",
        "required": False,
        "default": "\n",
        "empty": False,
    },
    "read_timeout": {
        "type": "float",
        "required": False,
        "default": 5.0,
        "empty": False,
    },
}


# pylint: disable=no-member
class Stream(GenericStream):
    """
    Stream module per porte seriali con terminatore esplicito e timeout sui frammenti incompleti.
    """

    def setup_module(self) -> None:
        # pylint: disable=import-error,import-outside-toplevel
        import serial  # type: ignore

        self.ser = serial.Serial(
            port=self.config["device"],
            baudrate=self.config["baud"],
            timeout=self.config["timeout"],
            bytesize={
                5: serial.FIVEBITS,
                6: serial.SIXBITS,
                7: serial.SEVENBITS,
                8: serial.EIGHTBITS,
            }[self.config["bytesize"]],
            parity={
                "none": serial.PARITY_NONE,
                "odd": serial.PARITY_ODD,
                "even": serial.PARITY_EVEN,
                "mark": serial.PARITY_MARK,
                "space": serial.PARITY_SPACE,
            }[self.config["parity"]],
            stopbits={
                1: serial.STOPBITS_ONE,
                1.5: serial.STOPBITS_ONE_POINT_FIVE,
                2: serial.STOPBITS_TWO,
            }[self.config["stopbits"]],
        )
        self.ser.flushInput()
        self._terminator: bytes = self.config["terminator"].encode("utf8")
        self._read_timeout: float = self.config["read_timeout"]
        self._read_buffer: bytes = b""
        self._buffer_started_at: Optional[float] = None

    def read(self) -> Optional[bytes]:
        chunk = self.ser.read(self.ser.in_waiting)
        if chunk:
            if not self._read_buffer:
                self._buffer_started_at = time.monotonic()
            self._read_buffer += chunk

        term_index = self._read_buffer.find(self._terminator)

        if term_index == -1:
            if (
                self._read_timeout > 0
                and self._buffer_started_at is not None
                and (time.monotonic() - self._buffer_started_at) > self._read_timeout
            ):
                _LOG.warning(
                    "Scarto %d byte dal buffer seriale: terminatore non ricevuto "
                    "entro %.1fs: %r",
                    len(self._read_buffer),
                    self._read_timeout,
                    self._read_buffer,
                )
                self._read_buffer = b""
                self._buffer_started_at = None
            return None

        line = self._read_buffer[:term_index]
        remainder = self._read_buffer[term_index + len(self._terminator):]
        self._read_buffer = remainder
        self._buffer_started_at = time.monotonic() if remainder else None
        return line or None

    def write(self, data: bytes) -> None:
        self.ser.write(data + self._terminator)

    def cleanup(self) -> None:
        self.ser.close()
