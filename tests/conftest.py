"""Was für jeden Test der Sitzung gilt.

**Die Suite schreibt nicht nach `outputs/`** (P7.3-U3.3, von Haiko entschieden am
2026-09-14: «an der Quelle»). Bis dahin legte jeder Durchlauf dort Laufordner an
— gemessen am 2026-09-13 96 Stück, die meisten nur mit `checkpoints/` —, und
`test_scenario_sweeps.py` überschrieb `outputs/sweeps/sweep_summary.json`, also
die Zusammenfassung des letzten **echten** Szenario-Vergleichs. In der
Lauf-Auswahl standen danach 630 Einträge, 440 davon ohne jede Laufdatei.

**Gesucht, nicht aufgezählt.** Die Umleitung nimmt nicht die heute bekannten
Konstanten, sondern jede Modulvariable unter `src.` und `dashboard.`, deren Wert
in das echte `outputs/` zeigt — auch eine, die jemand morgen als Wert
importiert. Und ob das reicht, beantwortet nicht diese Datei, sondern der
Vergleich am Ende der Sitzung: Hat sich unter `outputs/` etwas geändert, wird
der Lauf rot, gleich über welchen Weg geschrieben wurde.
"""

from __future__ import annotations

import importlib
import pkgutil
import sys
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[1]
ECHTE_AUSGABE = (WURZEL / "outputs").resolve()

#: Unter diesen Präfixen liegen die Module, deren Schreibwurzeln umgeleitet werden.
#:
#: **`tests.` gehört dazu**, und der Anlass war ein rotes Ergebnis, kein Plan:
#: `test_run_output_layout.py` hielt `OUTPUT_DIR` als Wert und verglich den
#: umgeleiteten Lauf mit dem echten Pfad. Eine Kopie in einem Testmodul ist
#: dieselbe Klasse wie eine in `src` — nur diese Datei selbst ist ausgenommen,
#: weil sie das echte Verzeichnis kennen muss, um es zu vergleichen.
PAKETE = ("src.", "dashboard.", "tests.")

#: Die Umgebungsvariable, aus der `paths.OUTPUT_DIR` in **jedem** Prozess liest.
#: Eine Modulvariable umzuleiten erreicht keinen Unterprozess —
#: `test_fehlermeldungen_greifen.py` startet `python -m src.run_simulation`, weil
#: nur so der Exit-Code echt ist, und legte dabei Laufordner im echten
#: `outputs/` an. Gesetzt für die ganze Sitzung, erbt sie jeder Unterprozess,
#: auch einer, den morgen jemand hinzufügt.
AUSGABE_VARIABLE = "AF_AUSGABE"


def _zeigt_in_die_ausgabe(wert: object) -> Path | None:
    """Der Teil unterhalb von `outputs/`, wenn `wert` dorthin zeigt — sonst `None`."""

    if not isinstance(wert, (str, Path)) or not str(wert):
        return None
    try:
        pfad = Path(wert).resolve()
    except (OSError, ValueError):
        return None
    if pfad == ECHTE_AUSGABE or pfad.is_relative_to(ECHTE_AUSGABE):
        return pfad.relative_to(ECHTE_AUSGABE)
    return None


def alle_module_laden() -> list[str]:
    """Jedes Modul unter `src` und `dashboard` importieren — und sagen, welche nicht gingen.

    **Ohne das bliebe eine Lücke:** Ein Modul, das erst mitten in der Sitzung
    importiert wird (`run_launcher` holt `scenario_sweeps` in einem
    Funktionsrumpf), brächte seine Konstante unumgeleitet mit. Wer vorher
    alles lädt, findet sie beim Suchen. Ein Modul, das sich nicht laden lässt,
    weil ein optionales Extra fehlt, wird übersprungen und genannt.
    """

    nicht_geladen = []
    for paket in ("src", "dashboard"):
        wurzel = importlib.import_module(paket)
        for eintrag in pkgutil.walk_packages(wurzel.__path__, prefix=f"{paket}."):
            try:
                importlib.import_module(eintrag.name)
            except Exception as fehler:  # noqa: BLE001 — optionale Extras
                nicht_geladen.append(f"{eintrag.name}: {type(fehler).__name__}")
    return nicht_geladen


def schreibwurzeln() -> list[tuple[str, str, object]]:
    """(Modul, Name, Wert) jeder Modulvariable, die in das echte `outputs/` zeigt."""

    funde = []
    for modulname, modul in list(sys.modules.items()):
        if modul is None or not modulname.startswith(PAKETE) or modulname == __name__:
            continue
        for name, wert in list(vars(modul).items()):
            if name.startswith("__"):
                continue
            if _zeigt_in_die_ausgabe(wert) is not None:
                funde.append((modulname, name, wert))
    return funde


def _bestand(wurzel: Path) -> dict[str, int]:
    """Jede Datei mit ihrer Änderungszeit **und jedes Verzeichnis** (Wert -1).

    **Verzeichnisse zählen mit, und das ist der Anlass selbst:** Die 440
    Einträge der Lauf-Auswahl ohne Laufdaten waren Ordner mit einem leeren
    `checkpoints/` darin — ein Vergleich nur über Dateien hätte keinen einzigen
    davon gesehen. Die Änderungszeit eines Verzeichnisses zählt dagegen nicht:
    Sie springt mit jedem Eintrag darin und sagt nichts, was die Dateien nicht
    schon sagen.
    """

    if not wurzel.is_dir():
        return {}
    return {
        pfad.relative_to(wurzel).as_posix(): (pfad.stat().st_mtime_ns if pfad.is_file() else -1)
        for pfad in wurzel.rglob("*")
    }


@pytest.fixture(autouse=True, scope="session")
def ausgabe_im_temp(tmp_path_factory):
    """Jede Schreibwurzel zeigt für die ganze Sitzung in ein Temp-Verzeichnis."""

    ersatz = tmp_path_factory.mktemp("outputs")
    alle_module_laden()
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv(AUSGABE_VARIABLE, str(ersatz))
        for modulname, name, wert in schreibwurzeln():
            teil = _zeigt_in_die_ausgabe(wert)
            neu = ersatz / teil
            mp.setattr(sys.modules[modulname], name, str(neu) if isinstance(wert, str) else neu)
        yield ersatz


def pytest_sessionstart(session):
    session.config._ausgabe_vorher = _bestand(ECHTE_AUSGABE)


def pytest_sessionfinish(session, exitstatus):
    vorher = getattr(session.config, "_ausgabe_vorher", None)
    if vorher is None:
        return
    nachher = _bestand(ECHTE_AUSGABE)
    neu = sorted(k for k in nachher if k not in vorher)
    geaendert = sorted(k for k in nachher if k in vorher and nachher[k] != vorher[k])
    if not neu and not geaendert:
        return
    zeilen = [
        "",
        "Die Suite hat nach outputs/ geschrieben — das darf sie nicht (P7.3-U3.3).",
        f"  neu: {len(neu)}, geändert: {len(geaendert)}",
        *[f"    + {k}" for k in neu[:15]],
        *[f"    ~ {k}" for k in geaendert[:15]],
        "Eine Schreibwurzel, die conftest.ausgabe_im_temp nicht findet, zeigt nicht",
        "als Modulvariable nach outputs/ — etwa ein relativer Pfad oder ein Literal.",
    ]
    session.config.get_terminal_writer().line("\n".join(zeilen), red=True)
    session.exitstatus = 1
