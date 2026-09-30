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

Dazu kommt seit P3.10 eine dritte Frage, die vor beiden liegt: **ob der Strom
das Zeichen überhaupt schreiben kann.** `stdio_auf_utf8` beantwortet sie.
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

logger = logging.getLogger(__name__)


def stdio_auf_utf8() -> None:
    """`stdout` und `stderr` auf UTF-8 stellen, damit keine Meldung am Zeichensatz scheitert (P3.10).

    **Der Befund war nicht die Konsole, sondern die Umleitung** — gemessen am
    2026-09-05, und die Messung hat die Vermutung des Projektplans widerlegt:

    * Auf einer **echten Konsole** ist `sys.stdout` ein `_WindowsConsoleIO` mit
      `encoding="utf-8"`. Ein `≥` läuft dort seit jeher durch.
    * Ist die Ausgabe **umgeleitet** (Datei, Pipe, CI, ein Dienst, der `stdout`
      einsammelt), ist es ein `FileIO` mit `encoding="cp1252"` — und dann wirft
      jedes `print` mit `→`, `≥`, `₂` oder `Δ` einen `UnicodeEncodeError`.

    In `src/` stehen **46** solcher Laufzeittexte. Die schlimmsten drei Wege:

    1. **Der Vorbehalt des State Explorers** (P2.5) beginnt mit `⚠️`. Bei
       umgeleiteter Ausgabe stürzt damit ausgerechnet die Marke ab, die vor
       unbelegten Zahlen warnt.
    2. **Das Fortschrittsfenster des Dashboards verliert die Zeile ganz.** Der
       Tee in `run_launcher` schreibt **zuerst** auf die echte Konsole und ruft
       *danach* den Callback; wirft der erste Schritt, sieht das Fenster nichts
       — und die Ausnahme läuft in den Lauf hinein.
    3. `logging` verschluckt die Zeile und schreibt «--- Logging error ---»
       samt Stack auf `stderr`.

    **Warum UTF-8 und nicht 46 Umschreibungen:** `CO₂` ist der Name des Stoffs
    und `→` gehört in einen Erklärtext. Der Fehler liegt am Ausgabeende, also
    wird er dort behoben — an einer Stelle statt an sechsundvierzig.

    **Und warum ohne den befürchteten Preis:** Der Plan hatte gegen diesen Weg
    eingewendet, eine cp1252-Konsole zeige UTF-8-Bytes als Buchstabensalat.
    Diese Konsole gibt es nicht — wo cp1252 auftaucht, schreibt Python in eine
    Datei oder Pipe, und dort ist UTF-8 genau richtig. Auf einer Konsole ändert
    der Aufruf nichts, weil sie schon UTF-8 spricht.

    **Idempotent und harmlos, wo es nicht geht:** Unter `pytest` ist `sys.stdout`
    kein `TextIOWrapper` und kennt kein `reconfigure` — dann passiert nichts, und
    das ist richtig: Die Erfassung von pytest ist ohnehin UTF-8.
    """

    for name in ("stdout", "stderr"):
        strom = getattr(sys, name, None)
        neu_einstellen = getattr(strom, "reconfigure", None)
        if neu_einstellen is None:
            continue
        try:
            neu_einstellen(encoding="utf-8")
        except (ValueError, OSError) as fehler:
            # **Nicht still.** Ein Strom, der sich nicht umstellen lässt (bereits
            # abgetrennt, geschlossen), bleibt bei seinem Zeichensatz — dann
            # scheitert die nächste Meldung mit `≥` wieder, und wer das sucht,
            # soll hier fündig werden.
            logger.warning(
                "sys.%s ließ sich nicht auf UTF-8 stellen (%s) — Meldungen mit "
                "Sonderzeichen können an diesem Strom weiterhin scheitern.",
                name,
                fehler,
            )


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


#: Wessen Meldungen ins Fortschrittsfenster gehören: die des Projekts. Der
#: Empfänger hängt am Wurzel-Logger, und dort kommt auch an, was der Webserver
#: über jede Anfrage schreibt.
_PROJEKT_LOGGER = ("src", "dashboard", "__main__")


def _gehoert_zum_lauf(record: logging.LogRecord) -> bool:
    """Nur Meldungen aus dem Projekt — nicht das Zugriffsprotokoll des Webservers.

    **Gefunden im Abnahme-Durchgang am 2026-09-30:** Während ein
    Szenario-Vergleich rechnete, stand im Fortschrittsfenster und in der Konsole
    «INFO werkzeug: 127.0.0.1 - - "POST /app/_dash-update-component…"» — das
    Dashboard fragt den Fortschritt im Sekundentakt ab, und jede dieser Anfragen
    landete als Zeile im Fenster, das sie anzeigen sollte.
    """

    return record.name.split(".", 1)[0] in _PROJEKT_LOGGER


class _CallbackHandler(logging.Handler):
    """Reicht jede Zeile an einen Callback weiter statt an einen Stream."""

    def __init__(self, callback: Callable[[str], None], level: int) -> None:
        super().__init__(level)
        self._callback = callback
        self.addFilter(_gehoert_zum_lauf)
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
