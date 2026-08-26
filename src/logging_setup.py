"""Ein Ort, an dem entschieden wird, wohin Meldungen gehen.

Vor P0.1 hatte das Projekt keine Logging-Konfiguration: vier Module riefen
`getLogger`, aber ohne Handler verschwand alles unterhalb von WARNING spurlos.
Wer `print` durch `logging` ersetzt, macht die Anwendung damit **leiser**, nicht
lauter — deshalb steht die Konfiguration hier, und die Umstellung folgt ihr.

Zwei Kanäle, absichtlich getrennt:

* `configure_logging` hängt einen Handler an die Konsole. Er bindet `sys.stdout`
  **jetzt**, beim Aufruf. Das ist der Punkt: `dashboard/run_launcher.py` legt
  später ein `contextlib.redirect_stdout` um den Lauf, und dieser Handler hält
  dann noch die echte Konsole — sonst liefe jede Logzeile zusätzlich durch den
  Tee und stünde im Dashboard doppelt.
* `progress_logging` hängt für die Dauer eines Laufs einen zweiten Handler an,
  der die Zeilen an das Fortschrittsfenster des Dashboards weiterreicht.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import TextIO

#: Format der Konsolenzeile. Kurz gehalten — die Fortschrittsausgabe eines Laufs
#: soll lesbar bleiben und nicht in Zeitstempeln ertrinken.
CONSOLE_FORMAT = "%(levelname)s %(name)s: %(message)s"

#: Marker am Handler, damit ein zweiter Aufruf ihn wiedererkennt statt zu doppeln.
_CONSOLE_MARKER = "_aeroforesight_console"
_PROGRESS_MARKER = "_aeroforesight_progress"


def configure_logging(level: int = logging.INFO, *, stream: TextIO | None = None) -> None:
    """Konsolen-Logging einrichten. Mehrfach aufrufbar, ohne Handler zu häufen."""

    root = logging.getLogger()
    root.setLevel(level)

    for handler in root.handlers:
        if getattr(handler, _CONSOLE_MARKER, False):
            handler.setLevel(level)
            return

    console = logging.StreamHandler(stream if stream is not None else sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(CONSOLE_FORMAT))
    setattr(console, _CONSOLE_MARKER, True)
    root.addHandler(console)


class _CallbackHandler(logging.Handler):
    """Reicht jede Zeile an einen Callback weiter statt an einen Stream."""

    def __init__(self, callback: Callable[[str], None], level: int) -> None:
        super().__init__(level)
        self._callback = callback
        setattr(self, _PROGRESS_MARKER, True)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._callback(self.format(record))
        except Exception:  # noqa: BLE001 - ein kaputtes Fortschrittsfenster darf keinen Lauf killen
            self.handleError(record)


@contextmanager
def progress_logging(
    callback: Callable[[str], None] | None,
    *,
    level: int = logging.INFO,
) -> Iterator[None]:
    """Logzeilen für die Dauer des Blocks zusätzlich an *callback* schicken."""

    if callback is None:
        yield
        return

    handler = _CallbackHandler(callback, level)
    handler.setFormatter(logging.Formatter(CONSOLE_FORMAT))

    root = logging.getLogger()
    previous_level = root.level
    if previous_level > level:
        root.setLevel(level)
    root.addHandler(handler)
    try:
        yield
    finally:
        root.removeHandler(handler)
        root.setLevel(previous_level)
        handler.close()
