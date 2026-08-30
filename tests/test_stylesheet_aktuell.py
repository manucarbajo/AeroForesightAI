"""Das eingecheckte Stylesheet passt zu seinen Quellen (P1.4).

`dashboard/web/assets/00-tailwind.css` ist ein **Erzeugnis**: `npm run build:css`
schreibt nur Regeln für Klassen, die der Scanner im Quelltext findet. Es ist
versioniert, damit ein frischer Checkout ohne Node-Werkzeugkette richtig
aussieht — und genau daraus folgt die Fehlerart, gegen die diese Datei steht:

**Wer eine Klasse hinzufügt und vergisst neu zu bauen, hinterlässt ein
Stylesheet, dem eine Regel fehlt.** Kein Fehler, keine Meldung, nur ein Kasten,
der anders aussieht. Genau das ist am 2026-08-30 passiert: Zwei Commits gingen
mit einem veralteten Stylesheet hinaus (der Warnblock der Demo-Seite und die
Bestätigungsseite brachten neue Klassen mit).

**Gefunden hätte es der Browser-Wächter** (Teil 5 in `test_web_overflow.py`) —
aber der braucht einen Browser, läuft zwölf Minuten und ist opt-in. Diese Datei
prüft dieselbe Sache in Sekunden: Sie baut neu und vergleicht. Ohne Node
überspringt sie sich; dann bleibt der Browser-Wächter.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

WURZEL = Path(__file__).resolve().parents[1]
STYLESHEET = WURZEL / "dashboard" / "web" / "assets" / "00-tailwind.css"


def _npm() -> str | None:
    """Der Pfad zu npm — unter Windows heisst es `npm.cmd`."""

    for name in ("npm.cmd", "npm"):
        pfad = shutil.which(name)
        if pfad:
            return pfad
    return None


@pytest.mark.skipif(not (WURZEL / "node_modules").is_dir(), reason="npm install fehlt")
@pytest.mark.skipif(_npm() is None, reason="kein npm auf dem PATH")
def test_the_committed_stylesheet_matches_its_sources(tmp_path):
    """Neu bauen und vergleichen — nicht in den Arbeitsbaum, sondern daneben.

    **Der Build schreibt nicht über die eingecheckte Datei.** Ein Test, der sein
    Prüfobjekt repariert, meldet nie etwas: Er wäre grün, und der nächste
    Commit trüge die Änderung mit, ohne dass jemand sie gesehen hat.
    """

    ziel = tmp_path / "probe.css"
    ergebnis = subprocess.run(  # noqa: S603 - fester Befehl, kein Nutzereingabe
        [
            _npm(),
            "exec",
            "--",
            "tailwindcss",
            "-i",
            str(WURZEL / "styles" / "tailwind.src.css"),
            "-o",
            str(ziel),
            "--minify",
        ],
        cwd=WURZEL,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert ergebnis.returncode == 0, f"Der Build scheiterte:\n{ergebnis.stderr[-1500:]}"

    frisch = ziel.read_text(encoding="utf-8")
    eingecheckt = STYLESHEET.read_text(encoding="utf-8")

    assert frisch == eingecheckt, (
        "Das eingecheckte Stylesheet passt nicht mehr zu seinen Quellen — "
        f"{len(eingecheckt)} Zeichen gegen {len(frisch)} frisch gebaute.\n\n"
        "Jemand hat Klassen geändert und nicht neu gebaut. Den Regeln, die "
        "dabei fehlen, sieht man das nicht an: kein Fehler, nur ein Kasten, "
        "der anders aussieht.\n\n"
        "    npm run build:css"
    )


def test_the_stylesheet_is_there_at_all():
    """Ohne Node muss die Datei trotzdem im Checkout liegen.

    Sie ist versioniert, damit die Anwendung ohne Werkzeugkette richtig
    aussieht — auf dem Server läuft keine.
    """

    assert STYLESHEET.is_file(), f"{STYLESHEET.name} fehlt im Checkout"
    assert STYLESHEET.stat().st_size > 5_000, "Das Stylesheet ist verdächtig klein"
