"""P3.10: Keine Meldung scheitert am Zeichensatz ihres Stroms (2026-09-05).

**Der Befund war nicht die Konsole, sondern die Umleitung**, und diese Messung
hat die Vermutung des Projektplans widerlegt:

| `sys.stdout` ist … | `encoding` | `print("≥")` |
| --- | --- | --- |
| eine echte Konsole | `utf-8` (`_WindowsConsoleIO`) | läuft durch |
| umgeleitet (Datei, Pipe, CI, Dienst) | `cp1252` (`FileIO`) | `UnicodeEncodeError` |

Der Plan hatte gegen den einfachen Weg — Ströme auf UTF-8 stellen — eingewendet,
eine cp1252-Konsole zeige UTF-8-Bytes als Buchstabensalat. **Diese Konsole gibt
es nicht:** Wo cp1252 auftaucht, schreibt Python in eine Datei oder eine Pipe,
und dort ist UTF-8 genau richtig. Damit fällt der Grund weg, 46 Zeichenketten
umzuschreiben oder jede Ausgabestelle einzeln festzumachen.

**Was der Fehler anrichtete, an drei Stellen gemessen:**

1. **Der Vorbehalt des State Explorers** (P2.5) beginnt mit `⚠️` — bei
   umgeleiteter Ausgabe riss ausgerechnet die Warnung vor unbelegten Zahlen den
   Aufruf ab.
2. **Das Fortschrittsfenster des Dashboards verlor die Zeile ganz.** Der Tee
   schreibt *zuerst* auf die echte Konsole und ruft *danach* den Callback.
3. `logging` verschluckte die Zeile und schrieb «--- Logging error ---» samt
   Stack auf `stderr`.

**Deshalb messen die Zusagen hier beide Enden**, wie das Paket es verlangt: den
Strom *und* das Fortschrittsfenster. Eine Zusage über nur eines davon hätte
Punkt 2 nicht gefunden.
"""

from __future__ import annotations

import ast
import io
import logging
from pathlib import Path

import pytest

from src.logging_setup import progress_logging, stdio_auf_utf8

ROOT = Path(__file__).resolve().parent.parent

#: Eine Zeile mit allem, was in `src/` wirklich vorkommt und cp1252 nicht kann.
HEIKLE_ZEILE = "Bedingung: cost_pressure ≥ 0,8 (CO₂-Abgabe) → aktiv ⚠️"

#: Einstiegspunkte, die ihre Ausgabe **nicht** sichern — mit Grund.
#:
#: **Der Ordner `scripts/` ist die Ausnahme, und das ist eine Entscheidung.**
#: Die drei Helfer holen einmalig Schriften, Backtest-Reihen bzw. bauen die
#: eingefrorene Matrix neu. Keiner importiert sonst etwas aus `src`, und keiner
#: trägt eine einzige Zeichenkette, die cp1252 nicht kann (gemessen). Sie an
#: `src.logging_setup` zu koppeln, hätte einer von ihnen sogar einen
#: `sys.path`-Eingriff gekostet — mehr Schaden als Nutzen. **Beim ersten Anlauf
#: von P3.10 war die Kopplung drin und hat zwei der drei gebrochen**
#: (`ModuleNotFoundError: No module named 'src'`), was diese Ausnahme erst
#: begründet hat.
AUSNAHMEN = {
    "scripts/schriften_holen.py": "eigenständiger Helfer, keine src-Abhängigkeit, druckt nur ASCII",
    "scripts/backtest_daten_holen.py": "dito; hängt am optionalen Extra `backtest`",
    "scripts/rebuild_cib_frozen.py": "dito; bräuchte einen sys.path-Eingriff für den Import",
}


def _quelle(pfad: Path) -> str:
    """Quelltext lesen — **mit `utf-8-sig`**, nicht `utf-8`.

    `langgraph_studio/__init__.py` trug ein BOM, und `ast.parse` scheitert daran
    mit `SyntaxError: invalid non-printable character U+FEFF`. Der erste Anlauf
    dieses Wächters ist genau daran gestorben — kein Befund über den Zeichensatz
    der *Ausgabe*, sondern einer über den der *Quelle*. Das BOM ist mit P3.10
    weg; `utf-8-sig` steht hier, damit das nächste diesen Test nicht umbringt.
    """

    return pfad.read_text(encoding="utf-8-sig")


def _einstiegspunkte() -> list[Path]:
    """Jede Datei mit einem `__main__`-Block."""

    gefunden: list[Path] = []
    for baum in ("src", "dashboard", "scripts", "langgraph_studio"):
        for pfad in sorted((ROOT / baum).rglob("*.py")):
            if '__name__ == "__main__"' in _quelle(pfad):
                gefunden.append(pfad)
    return gefunden


def _ruft_stdio_auf_utf8(pfad: Path) -> bool:
    baum = ast.parse(_quelle(pfad))
    return any(
        isinstance(knoten, ast.Call)
        and isinstance(knoten.func, ast.Name)
        and knoten.func.id == "stdio_auf_utf8"
        for knoten in ast.walk(baum)
    )


class TestJederEinstiegSichertSeineAusgabe:
    """Mechanisch geprüft, nicht zugesagt — die Liste der Einstiege wächst."""

    def test_es_gibt_ueberhaupt_einstiegspunkte(self):
        """Sonst prüfte der Test unten gegen eine leere Menge."""

        assert len(_einstiegspunkte()) >= 10

    def test_jeder_einstieg_sichert_oder_steht_in_den_ausnahmen(self):
        offen: list[str] = []
        for pfad in _einstiegspunkte():
            relativ = pfad.relative_to(ROOT).as_posix()
            if relativ in AUSNAHMEN:
                continue
            if not _ruft_stdio_auf_utf8(pfad):
                offen.append(relativ)

        assert not offen, (
            "Diese Einstiegspunkte sichern ihre Ausgabe nicht:\n  "
            + "\n  ".join(offen)
            + "\n\nUmgeleitet spricht `sys.stdout` unter Windows cp1252, und dann "
            "wirft jede Meldung mit `→`, `≥` oder `₂`. `stdio_auf_utf8()` ist "
            "idempotent und auf einer Konsole wirkungslos — wer eine begründete "
            "Ausnahme braucht, trägt sie mit Grund in `AUSNAHMEN` ein."
        )

    def test_keine_ausnahme_ohne_grund(self):
        """Eine wachsende Ausnahmeliste wäre der Anfang derselben Umgehung."""

        for pfad, grund in AUSNAHMEN.items():
            assert (ROOT / pfad).is_file(), f"{pfad} gibt es nicht mehr"
            assert len(grund) > 25, f"{pfad}: der Grund ist keiner"

    def test_die_ausnahmen_tragen_wirklich_keine_sonderzeichen(self):
        """**Der Grund wird nachgemessen, nicht geglaubt.**

        Die Ausnahme steht auf der Aussage «druckt nur ASCII». Schreibt jemand
        dort ein `→` in eine Meldung, ist die Begründung hinfällig — und dieser
        Test sagt es, statt die Liste weiter zu tragen.
        """

        befunde: list[str] = []
        for pfad in AUSNAHMEN:
            baum = ast.parse(_quelle(ROOT / pfad))
            docstrings = {
                id(knoten.body[0].value)
                for knoten in ast.walk(baum)
                if isinstance(
                    knoten, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
                )
                and knoten.body
                and isinstance(knoten.body[0], ast.Expr)
                and isinstance(knoten.body[0].value, ast.Constant)
            }
            for knoten in ast.walk(baum):
                if not (isinstance(knoten, ast.Constant) and isinstance(knoten.value, str)):
                    continue
                if id(knoten) in docstrings:
                    continue
                try:
                    knoten.value.encode("cp1252")
                except UnicodeEncodeError:
                    befunde.append(f"{pfad}:{knoten.lineno}")

        assert not befunde, (
            "Diese Ausnahmen tragen jetzt selbst Zeichen, die cp1252 nicht kann:\n  "
            + "\n  ".join(befunde)
            + "\n\nDamit ist ihre Begründung hinfällig — entweder das Zeichen weg "
            "oder die Ausgabe sichern."
        )


class TestDieHeikleZeileKommtAnBeidenEndenAn:
    """**Die Zusage des Pakets im Wortlaut** — an beiden Enden, nicht an einem."""

    def test_am_strom(self, monkeypatch):
        """Ende eins: die (umgeleitete) Ausgabe selbst."""

        import sys

        strom = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="")
        monkeypatch.setattr(sys, "stdout", strom)

        stdio_auf_utf8()
        print(HEIKLE_ZEILE)
        strom.flush()

        geschrieben = strom.buffer.getvalue().decode("utf-8")
        assert "≥" in geschrieben and "CO₂" in geschrieben
        assert "⚠" in geschrieben, "Der Vorbehalt des State Explorers fehlt"

    def test_ohne_die_sicherung_geht_sie_verloren(self):
        """Ein Wächter, der nie etwas sieht, könnte auch blind sein."""

        strom = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="")

        with pytest.raises(UnicodeEncodeError):
            print(HEIKLE_ZEILE, file=strom)

    def test_am_fortschrittsfenster(self, monkeypatch):
        """Ende zwei: der Callback des Dashboards, **durch den Tee**.

        Der Tee aus `run_launcher` schreibt zuerst auf die echte Konsole und ruft
        erst danach den Callback. Ohne die Sicherung wirft der erste Schritt, und
        das Fortschrittsfenster sieht die Zeile **nie** — gemessen, nicht
        vermutet. Deshalb steht hier der Tee und nicht nur der Callback.
        """

        import sys

        echt = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="")
        monkeypatch.setattr(sys, "stdout", echt)
        stdio_auf_utf8()

        gesehen: list[str] = []

        class Tee:
            def write(self, data: str) -> None:
                echt.write(data)
                for zeile in data.splitlines():
                    if zeile.strip():
                        gesehen.append(zeile.strip())

            def flush(self) -> None:
                echt.flush()

        print(HEIKLE_ZEILE, file=Tee())

        assert gesehen == [HEIKLE_ZEILE], f"Das Fortschrittsfenster sah: {gesehen}"

    def test_am_log(self, monkeypatch):
        """Und über `logging`, das die Zeile sonst still verschluckt."""

        import sys

        strom = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="")
        monkeypatch.setattr(sys, "stdout", strom)
        stdio_auf_utf8()

        zeilen: list[str] = []
        with progress_logging(zeilen.append):
            handler = logging.StreamHandler(strom)
            log = logging.getLogger("test_zeichensatz")
            log.handlers = [handler]
            log.propagate = True
            log.setLevel(logging.INFO)
            log.info(HEIKLE_ZEILE)
            handler.flush()

        assert "≥" in strom.buffer.getvalue().decode("utf-8")
        assert any("≥" in z for z in zeilen), f"Das Fortschrittsfenster sah: {zeilen}"


class TestDieSicherungIstHarmlos:
    """Sie darf nichts kaputt machen, wo sie nichts zu tun hat."""

    def test_zweimal_aufrufen_aendert_nichts(self):
        import sys

        stdio_auf_utf8()
        einmal = sys.stdout.encoding if hasattr(sys.stdout, "encoding") else None
        stdio_auf_utf8()

        assert (sys.stdout.encoding if hasattr(sys.stdout, "encoding") else None) == einmal

    def test_ein_strom_ohne_reconfigure_wird_uebersprungen(self, monkeypatch):
        """Unter `pytest` ist `sys.stdout` kein `TextIOWrapper` — das darf nicht werfen."""

        import sys

        monkeypatch.setattr(sys, "stdout", io.StringIO())
        monkeypatch.setattr(sys, "stderr", io.StringIO())

        stdio_auf_utf8()  # darf einfach nichts tun

    def test_ein_strom_der_sich_weigert_wird_gemeldet(self, monkeypatch, caplog):
        """**Nicht still.** Ein Strom, der bei cp1252 bleibt, lässt die nächste
        Meldung wieder scheitern — wer das sucht, soll hier fündig werden."""

        import sys

        class Widerspenstig(io.StringIO):
            encoding = "cp1252"

            def reconfigure(self, **_kwargs):
                raise ValueError("Strom ist abgetrennt")

        monkeypatch.setattr(sys, "stdout", Widerspenstig())

        with caplog.at_level(logging.WARNING):
            stdio_auf_utf8()

        assert "UTF-8" in caplog.text and "stdout" in caplog.text


class TestKeinImportStelltDieAusgabeHeimlichUm:
    """P3.10 hat den Fix **vorgefunden** — an der falschen Stelle.

    In `src/orchestration/scenario_sweeps.py` standen auf Modulebene zwei
    Zeilen, die `sys.stdout` prozessglobal umstellten. Ausgelöst wurden sie
    dadurch, dass irgendjemand irgendetwas aus `src.orchestration` importiert:
    das Paket-`__init__` zieht das Sweep-Modul mit.

    **Gemessen deckte das 7 von 11 Einstiegspunkten ab** — ohne dass es irgendwo
    stand. Der CLI-Lauf, das Dashboard und der State Explorer waren *zufällig*
    sicher; `create_graph.py`, `serve_graph.py` und `cib_visualizer.py` nicht.
    Und **`stderr` war nirgends gesichert**, obwohl dort die Logging-Fehler und
    die Befundliste aus P3.3 landen.

    Ein Prozess, dessen Zeichensatz von der Importreihenfolge abhängt, sagt
    niemandem, warum er es tut — und die nächste Umsortierung nimmt ihn weg.
    """

    def test_ein_import_aendert_die_ausgabe_nicht(self, monkeypatch):
        import importlib
        import sys

        strom = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="")
        monkeypatch.setattr(sys, "stdout", strom)

        # Frisch importieren, sonst ist das Modul schon geladen und tut nichts.
        for name in [n for n in list(sys.modules) if n.startswith("src.orchestration")]:
            monkeypatch.delitem(sys.modules, name, raising=False)
        importlib.import_module("src.orchestration.scenario_sweeps")

        assert strom.encoding == "cp1252", (
            "Ein Import hat den Zeichensatz des Prozesses geändert. Das war der "
            "Zustand vor P3.10: unsichtbar, an der Importreihenfolge hängend und "
            "nur für `stdout`."
        )

    def test_die_umstellung_steht_an_einer_stelle(self):
        """Sonst hätte der nächste Einstieg wieder seine eigene Fassung."""

        befunde: list[str] = []
        erlaubt = (Path("src") / "logging_setup.py").as_posix()
        for baum in ("src", "dashboard", "langgraph_studio", "scripts"):
            for pfad in sorted((ROOT / baum).rglob("*.py")):
                relativ = pfad.relative_to(ROOT).as_posix()
                if relativ == erlaubt:
                    continue
                knoten = ast.parse(_quelle(pfad))
                for k in ast.walk(knoten):
                    if (
                        isinstance(k, ast.Call)
                        and isinstance(k.func, ast.Attribute)
                        and k.func.attr == "reconfigure"
                    ):
                        befunde.append(f"{relativ}:{k.lineno}")

        assert not befunde, (
            "Diese Stellen stellen einen Strom selbst um:\n  "
            + "\n  ".join(befunde)
            + f"\n\nDas gehört in `{erlaubt}` — eine zweite Fassung liefe beim "
            "nächsten Mal mit anderen Argumenten (die alte hatte "
            '`errors="replace"`, also stillen Verlust statt UTF-8).'
        )

    def test_stderr_wird_mitgesichert(self, monkeypatch):
        """**Die alte Fassung ließ `stderr` aus** — und dort landet, was schiefgeht.

        `_melde_befunde` aus P3.3 schreibt die Befundliste einer kaputten
        Konfiguration dorthin, und `logging` seine eigenen Fehler.
        """

        import sys

        monkeypatch.setattr(
            sys, "stderr", io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="")
        )
        stdio_auf_utf8()

        print(HEIKLE_ZEILE, file=sys.stderr)
        sys.stderr.flush()

        assert "≥" in sys.stderr.buffer.getvalue().decode("utf-8")
