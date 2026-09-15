"""P4.3: Zahlen in der Doku, die den heutigen Stand beschreiben, werden gemessen (2026-09-11).

**Der Befund war eine Lücke, kein einzelner Fehler.** `test_packaging.py` liest
CLAUDE.md auf tote Anker und Modulpfade — keine einzige *Zahl* darin wurde
gehalten. Tests hielten den Code (`len(wizard.STEPS) == 6`), aber nichts band die
Doku an ihn: Wer die Schrittzahl ändert und den Test nachzieht, lässt «Sechs
Schritte» in CLAUDE.md still veralten.

**Beim Anlegen hat das Register vier veraltete Aussagen gefunden**, und jede
folgte demselben Muster — richtig beim Schreiben, nicht mitgezogen von dem
Commit, der sie später änderte:

* «**Acht** Zahlen» im Buchungsmodell (P2.1) — seit B2 sind es neun
* «der höchste **2,02** (1024 px: 2,10)» (P3.17) — seit dem schmaleren Lesemaß
  vom 2026-09-07 sind es 2,09 und 2,17
* «die **vier** Viewport-Bereiche» in CLAUDE.md und zweimal im Docstring von
  `app.visibility` — seit W3.1 sind es fünf
* «Alle **drei** Viewport-Bereiche» im Modul-Docstring von `app.py` (P1.5)

**Warum ein Register und keine Suche:** Eine automatische Suche nach Zahlen, die
nach heutigem Stand klingen, wäre der bessere Wächter, wenn sie ginge. Sie geht
nicht: Von den Stellen in CLAUDE.md mit Zahl und Hauptwort, aber ohne Messwort in
der Nähe, war beim Durchsehen die Mehrheit Erzählung («der acht Stellen nannte»,
«zwölf Tage lang»). Das wären Fehlalarme, und die sind teurer als übersehene
Fälle, weil sie dazu erziehen, den Wächter zu überlesen.

**Was das Register leistet und was nicht:** Jede eingetragene Zahl wird gegen
ihre Messung gehalten, und ein umformulierter Satz fällt auf, statt still den
Bezug zu verlieren. **Eine neu geschriebene Zahl ist erst gehalten, wenn jemand
sie einträgt** — dafür steht eine Zeile in der Doku-Pflicht. **Datierte Messungen
werden bewusst nicht gehalten**: «nachgemessen am 2026-09-06: 1886 von 3364
Knoten» ist Geschichte, und eine Geschichte, die mitwandert, erzählt nichts mehr.

**Jede Zahl trägt ihre Zähldefinition.** Das ist die Lehre aus C1 des
Phase-3-Audits: Bei den «46 Zeichenketten» kommen je nach Lesart 46, 55 oder 23
heraus, und alle drei wären mit demselben Satz vereinbar gewesen.
"""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

ZAHLWOERTER = {
    "ein": 1,
    "eine": 1,
    "zwei": 2,
    "drei": 3,
    "vier": 4,
    "fünf": 5,
    "sechs": 6,
    "sieben": 7,
    "acht": 8,
    "neun": 9,
    "zehn": 10,
    "elf": 11,
    "zwölf": 12,
}


def zahl_aus(wort: str) -> float:
    """«Sechs» → 6, «46» → 46, «2,09» → 2.09."""

    klein = wort.strip().lower()
    if klein in ZAHLWOERTER:
        return ZAHLWOERTER[klein]
    return float(klein.replace(",", "."))


@dataclass(frozen=True)
class Zahl:
    """Eine Zahl in der Doku, die den heutigen Stand beschreibt."""

    #: Kurzname für die Testausgabe.
    kennung: str
    #: Datei relativ zum Repo.
    datei: str
    #: Regulärer Ausdruck für den Satz, mit **genau einer** Gruppe: der Zahl.
    satz: str
    #: Wie die Zahl heute gemessen wird.
    messung: Callable[[], float]
    #: **Wie** gezählt wird — ohne sie ist die Zahl nicht prüfbar.
    definition: str


def pruefe(zahl: Zahl, wurzel: Path = ROOT) -> list[str]:
    """Befunde zu einer Zahl: Satz nicht genau einmal da, oder Zahl ≠ Messung."""

    text = (wurzel / zahl.datei).read_text(encoding="utf-8")
    treffer = list(re.finditer(zahl.satz, text))
    if len(treffer) != 1:
        return [
            f"{zahl.datei}: Der Satz steht {len(treffer)}-mal da, erwartet genau einmal — "
            f"umformuliert oder verdoppelt? Muster: {zahl.satz}"
        ]
    # **Ein Wort, wo die Zahl stehen sollte, ist ein Befund und kein Absturz.**
    # Das Muster `(\w+) Regeln gelten hier:` passt auch auf «Diese Regeln
    # gelten hier:». Die erste Fassung reichte «Diese» an `zahl_aus` weiter und
    # brach mit einem `ValueError` ab — rot war es trotzdem, aber als
    # Traceback statt als Satz, der sagt, was passiert ist. Aufgefallen ist es
    # an der Mutationsprobe am echten CLAUDE.md.
    try:
        in_der_doku = zahl_aus(treffer[0].group(1))
    except ValueError:
        return [
            f"{zahl.datei}: «{treffer[0].group(0)}» — dort, wo die Zahl stehen sollte, "
            f"steht «{treffer[0].group(1)}». Umformuliert?"
        ]
    gemessen = zahl.messung()
    if in_der_doku != gemessen:
        return [
            f"{zahl.datei}: «{treffer[0].group(0)}» — gemessen: {gemessen}. "
            f"Gezählt wird: {zahl.definition}"
        ]
    return []


# --- Messungen --------------------------------------------------------------


def _json(pfad: str) -> object:
    return json.loads((ROOT / pfad).read_text(encoding="utf-8"))


def _laufzeittexte(*, mit_docstrings: bool) -> int:
    anzahl = 0
    for pfad in sorted((ROOT / "src").rglob("*.py")):
        if "__pycache__" in pfad.parts:
            continue
        baum = ast.parse(pfad.read_text(encoding="utf-8-sig"))
        docstrings: set[int] = set()
        for knoten in ast.walk(baum):
            if (
                isinstance(
                    knoten, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
                )
                and knoten.body
            ):
                erst = knoten.body[0]
                if (
                    isinstance(erst, ast.Expr)
                    and isinstance(erst.value, ast.Constant)
                    and isinstance(erst.value.value, str)
                ):
                    docstrings.add(id(erst.value))
        for knoten in ast.walk(baum):
            if not (isinstance(knoten, ast.Constant) and isinstance(knoten.value, str)):
                continue
            try:
                knoten.value.encode("cp1252")
                continue
            except UnicodeEncodeError:
                pass
            if id(knoten) in docstrings and not mit_docstrings:
                continue
            anzahl += 1
    return anzahl


def _faktoren() -> list[dict]:
    daten = _json("configs/factors.json")
    eintraege = daten.get("factors", daten) if isinstance(daten, dict) else daten
    return list(eintraege.values()) if isinstance(eintraege, dict) else list(eintraege)


def _zustaende_je_faktor() -> int:
    laengen = {len(f.get("states", f.get("possible_states", {}))) for f in _faktoren()}
    assert len(laengen) == 1, f"Nicht jeder Faktor hat gleich viele Zustände: {laengen}"
    return laengen.pop()


def _akteure() -> int:
    daten = _json("configs/agents.json")
    return len(daten.get("agents", daten) if isinstance(daten, dict) else daten)


def _bereiche() -> int:
    from dashboard.web import shell

    return len(shell.BEREICHE)


def _zonen() -> int:
    from tests.test_web_shell import TestFuenfZonen

    return len(TestFuenfZonen.ZONEN)


def _wege() -> int:
    from dashboard.web.config_editor import wizard
    from dashboard.web.state import initial_draft_dict
    from tests.test_web_wizard import _wege as wege

    return len(wege(wizard.entry(initial_draft_dict())))


def _entscheidungen() -> int:
    from tests.test_web_start_flow import MAX_ENTSCHEIDUNGEN

    return MAX_ENTSCHEIDUNGEN


def _schritte() -> int:
    from dashboard.web.config_editor import wizard

    return len(wizard.STEPS)


def _kennungen_im_modell_rumpf() -> int:
    from dashboard.web.pages import model_editor
    from dashboard.web.state import initial_draft_dict
    from tests.test_web_lazy_modell import _ids

    fest: set[str] = set()
    muster: set[str] = set()
    _ids(model_editor.rumpf_fuer(f"/app/{model_editor.ROUTE}", initial_draft_dict()), fest, muster)
    return len(muster)


def _nummerierte_punkte(datei: str, nach: str, bis: str, punkt: str) -> int:
    """Wie viele durchnummerierte Punkte zwischen *nach* und *bis* stehen.

    Verlangt eine lückenlose Folge 1, 2, 3 … — eine Liste, deren Nummern springen,
    ist selbst ein Befund und kein Zählergebnis.
    """

    zeilen = (ROOT / datei).read_text(encoding="utf-8").split("\n")
    start = next(i for i, z in enumerate(zeilen) if nach in z)
    nummern: list[int] = []
    for zeile in zeilen[start + 1 :]:
        if re.match(bis, zeile):
            break
        treffer = re.match(punkt, zeile)
        if treffer:
            nummern.append(int(treffer.group(1)))
    assert nummern == list(range(1, len(nummern) + 1)), f"Nummern nicht lückenlos: {nummern}"
    return len(nummern)


def _buchungskoeffizienten() -> int:
    modell = _json("configs/properties.json")["booking_model"]
    return sum(1 for wert in modell.values() if isinstance(wert, dict) and "quelle" in wert)


def _helfer_ohne_utf8() -> int:
    from tests.test_zeichensatz import AUSNAHMEN

    return len(AUSNAHMEN)


def _hoechster_deckel(breite: int) -> float:
    baum = ast.parse((ROOT / "tests" / "test_web_overflow.py").read_text(encoding="utf-8"))
    for knoten in baum.body:
        if isinstance(knoten, ast.AnnAssign) and getattr(knoten.target, "id", "") == "DECKEL":
            return max(ast.literal_eval(knoten.value)[breite].values())
    raise AssertionError("DECKEL steht nicht mehr in tests/test_web_overflow.py")


def _rahmen() -> list[dict]:
    dateien = sorted((ROOT / "configs" / "sweeps").glob("*.json"))
    daten = [json.loads(p.read_text(encoding="utf-8")) for p in dateien]
    return [d for d in daten if d.get("art") == "rahmen"]


def _rahmen_ticks() -> int:
    ticks = {d["max_ticks"] for d in _rahmen()}
    assert len(ticks) == 1, f"Die Rahmen laufen verschieden lang: {ticks}"
    return ticks.pop()


# --- Das Register -----------------------------------------------------------

REGISTER: tuple[Zahl, ...] = (
    Zahl(
        "akteure",
        "CLAUDE.md",
        r"(\w+) Akteure — Consumer, Provider, Regulator",
        _akteure,
        "Einträge in configs/agents.json.",
    ),
    Zahl(
        "backtest_reihen",
        "CLAUDE.md",
        r"\*\*(\w+) Reihen seit P2\.8\*\*",
        lambda: len(_json("configs/backtest/quellen.json")["reihen"]),
        "Einträge unter `reihen` in configs/backtest/quellen.json.",
    ),
    Zahl(
        "zonen",
        "CLAUDE.md",
        r"ein Bildschirm mit (\w+) Zonen \(`shell\.py`\)",
        _zonen,
        "Die Zonen, deren Klassen test_web_shell.TestFuenfZonen im gerenderten Rahmen verlangt.",
    ),
    Zahl(
        "bereiche_im_dom",
        "CLAUDE.md",
        r"alle (\w+) Bereiche liegen gleichzeitig im DOM",
        _bereiche,
        "Einträge in shell.BEREICHE (Navigation und Bereiche ohne Link) — jeder ist ein Bereich mit eigenem Wirt im Layout.",
    ),
    Zahl(
        "viewport_bereiche",
        "CLAUDE.md",
        r"`app\.py` für die (\w+) Viewport-Bereiche schon benutzt",
        _bereiche,
        "Einträge in shell.BEREICHE (Navigation und Bereiche ohne Link); app.visibility liefert je Eintrag genau einen Stil.",
    ),
    Zahl(
        "wege_des_einstiegs",
        "CLAUDE.md",
        r"der \*\*Einstieg\*\* mit (\w+) Wegen",
        _wege,
        "Elemente mit der Klasse `af-way` in wizard.entry(...) — dieselbe Zählung wie "
        "test_web_wizard._wege.",
    ),
    Zahl(
        "entscheidungen",
        "CLAUDE.md",
        r"dann die (\w+) Entscheidungen aus P1\.1",
        _entscheidungen,
        "Die Obergrenze test_web_start_flow.MAX_ENTSCHEIDUNGEN, die der Wächter dort am "
        "gerenderten ersten Schritt misst.",
    ),
    Zahl(
        "schritte",
        "CLAUDE.md",
        r"\*\*(\w+) Schritte seit P7\.13-U13\.1\*\*",
        _schritte,
        "Einträge in wizard.STEPS — ohne den Einstieg davor.",
    ),
    Zahl(
        "regeln_dashboard",
        "CLAUDE.md",
        r"(\w+) Regeln gelten hier:",
        lambda: _nummerierte_punkte(
            "CLAUDE.md", "Regeln gelten hier:", r"^\s{0,2}- ", r"^\s{4}(\d+)\. "
        ),
        "Durchnummerierte Punkte (vier Leerzeichen Einzug) direkt unter dem Satz in CLAUDE.md, "
        "bis zum nächsten Aufzählungspunkt der Architektur-Map.",
    ),
    Zahl(
        "kennungen_modell_rumpf",
        "CLAUDE.md",
        r"alle (\w+) Kennungen darin sind Muster",
        _kennungen_im_modell_rumpf,
        "Muster-Kennungen (Dict-IDs) im Rumpf von model_editor.rumpf_fuer auf dem eigenen "
        "Bereich — dieselbe Zählung wie test_web_lazy_modell._ids.",
    ),
    Zahl(
        "faktoren",
        "CLAUDE.md",
        r"\*\*Faktoren F1–F(\d+)\*\*",
        lambda: len(_faktoren()),
        "Einträge in configs/factors.json.",
    ),
    Zahl(
        "zustaende_je_faktor",
        "CLAUDE.md",
        r"Geopolitik\), je (\w+) Zustände",
        _zustaende_je_faktor,
        "Zustände je Faktor in configs/factors.json — und zwar bei jedem gleich viele.",
    ),
    Zahl(
        "buchungskoeffizienten",
        "CLAUDE.md",
        r"\(zweite Hälfte von P2\.1\): (\w+) Zahlen —",
        _buchungskoeffizienten,
        "Einträge in `booking_model` von configs/properties.json, die ein Feld `quelle` tragen.",
    ),
    Zahl(
        "laufzeittexte_ohne_docstrings",
        "CLAUDE.md",
        r"In `src/` stehen (\d+) solcher Laufzeittexte",
        lambda: _laufzeittexte(mit_docstrings=False),
        "Zeichenketten-KNOTEN (ast.Constant) in src/, die cp1252 nicht kodieren kann, ohne "
        "Docstrings (erste Anweisung eines Moduls, einer Klasse oder Funktion). Nicht "
        "verschiedene Texte — die ergäben 23.",
    ),
    Zahl(
        "laufzeittexte_mit_docstrings",
        "CLAUDE.md",
        r"wer alle zählt, kommt auf (\d+)",
        lambda: _laufzeittexte(mit_docstrings=True),
        "Dieselben Knoten wie oben, Docstrings eingeschlossen.",
    ),
    Zahl(
        "helfer_ohne_utf8",
        "CLAUDE.md",
        r"die (\w+) Helfer in `scripts/` sind die einzigen",
        _helfer_ohne_utf8,
        "Einträge in test_zeichensatz.AUSNAHMEN.",
    ),
    Zahl(
        "commit_regeln",
        "CLAUDE.md",
        r"Die (\w+) Regeln stehen vollständig im \[Commit-Regelwerk\]",
        lambda: _nummerierte_punkte(
            "docs/projektplan.md", "### Regelwerk: atomare Commits", r"^#{1,6} ", r"^(\d+)\. "
        ),
        "Durchnummerierte Punkte unter der Überschrift «Regelwerk: atomare Commits» in "
        "docs/projektplan.md, bis zur nächsten Überschrift.",
    ),
    Zahl(
        "hoechster_deckel_1280",
        "CLAUDE.md",
        r"sieben Schritte, \*\*vier davon auf 1,00\*\*, der höchste \*\*(\d+,\d+)\*\*",
        lambda: _hoechster_deckel(1280),
        "Größter Wert in DECKEL[1280] von tests/test_web_overflow.py, gelesen über den "
        "Syntaxbaum (ohne Playwright zu importieren).",
    ),
    Zahl(
        "hoechster_deckel_1024",
        "CLAUDE.md",
        r"der höchste \*\*\d+,\d+\*\* \(1024 px: (\d+,\d+)\)",
        lambda: _hoechster_deckel(1024),
        "Größter Wert in DECKEL[1024] von tests/test_web_overflow.py.",
    ),
    Zahl(
        "rahmen",
        "CLAUDE.md",
        r"über das Angebot\*\* \(2026-09-03\): Alle (\w+) tragen",
        lambda: len(_rahmen()),
        "Dateien in configs/sweeps/ mit `art: rahmen`.",
    ),
    Zahl(
        "rahmen_ticks",
        "CLAUDE.md",
        r"Horizont der Rahmenszenarien:\*\* Sie laufen (\d+) Ticks",
        _rahmen_ticks,
        "`max_ticks` der Rahmenszenarien — alle gleich lang, sonst ist die Aussage falsch.",
    ),
    Zahl(
        "standardlauf_ticks",
        "CLAUDE.md",
        r"Ein Lauf über (\d+) Ticks deckt gut drei Jahre ab",
        lambda: _json("configs/simulation_config.json")["clock"]["max_ticks"],
        "`clock.max_ticks` in configs/simulation_config.json.",
    ),
    # --- dashboard/web/app.py: dort ist die Drift wirklich passiert ---------
    #
    # Der Modul-Docstring sagte seit P1.5 «drei», der Docstring von
    # `visibility` seit P1.6 zweimal «vier». Fünf sind es seit W3.1. Gehalten
    # wird die Zahl deshalb auch an der Stelle, an der sie veraltet ist, und
    # nicht nur in CLAUDE.md.
    Zahl(
        "app_modul_viewport_bereiche",
        "dashboard/web/app.py",
        r"Alle (\w+) Viewport-Bereiche liegen dauerhaft im Layout",
        _bereiche,
        "Einträge in shell.BEREICHE (Navigation und Bereiche ohne Link).",
    ),
    Zahl(
        "app_visibility_welcher",
        "dashboard/web/app.py",
        r"Welcher der (\w+) Viewport-Bereiche sichtbar ist",
        _bereiche,
        "Einträge in shell.BEREICHE (Navigation und Bereiche ohne Link) — visibility liefert je Eintrag genau einen Stil.",
    ),
    Zahl(
        "app_visibility_alle",
        "dashboard/web/app.py",
        r"Alle (\w+) bleiben im DOM",
        _bereiche,
        "Einträge in shell.BEREICHE (Navigation und Bereiche ohne Link) — jeder Bereich hat einen Wirt, der im DOM bleibt.",
    ),
)


class TestJedeEingetrageneZahlStimmt:
    """**Die tragende Zusage von P4.3:** Eine veraltete Zahl lässt die Suite rot werden."""

    @pytest.mark.parametrize("zahl", REGISTER, ids=lambda z: z.kennung)
    def test_die_zahl_in_der_doku_ist_die_gemessene(self, zahl):
        befunde = pruefe(zahl)

        assert not befunde, "\n".join(befunde)


class TestDasRegisterIstSelbstPruefbar:
    def test_jede_zahl_traegt_ihre_zaehldefinition(self):
        ohne = [z.kennung for z in REGISTER if len(z.definition.strip()) < 25]

        assert not ohne, f"Ohne Zähldefinition ist die Zahl nicht prüfbar: {ohne}"

    def test_jedes_muster_hat_genau_eine_gruppe(self):
        falsch = [z.kennung for z in REGISTER if re.compile(z.satz).groups != 1]

        assert not falsch, f"Muster mit mehr oder weniger als einer Gruppe: {falsch}"

    def test_die_kennungen_sind_eindeutig(self):
        kennungen = [z.kennung for z in REGISTER]

        assert len(kennungen) == len(set(kennungen))


class TestDasRegisterSaeheEineVeralteteZahl:
    """Ohne diese Zusagen wäre grün nur die Abwesenheit einer Messung."""

    def _zahl(self, gemessen: float) -> Zahl:
        return Zahl("probe", "doku.md", r"(\w+) Regeln gelten hier:", lambda: gemessen, "x" * 30)

    def test_eine_veraltete_zahl_wird_gemeldet(self, tmp_path):
        (tmp_path / "doku.md").write_text("Sieben Regeln gelten hier:\n", encoding="utf-8")

        befunde = pruefe(self._zahl(8), tmp_path)

        assert len(befunde) == 1 and "gemessen: 8" in befunde[0], befunde

    def test_ein_umformulierter_satz_wird_gemeldet(self, tmp_path):
        (tmp_path / "doku.md").write_text("Es gelten sieben Regeln:\n", encoding="utf-8")

        befunde = pruefe(self._zahl(7), tmp_path)

        assert len(befunde) == 1 and "0-mal" in befunde[0], befunde

    def test_ein_verdoppelter_satz_wird_gemeldet(self, tmp_path):
        (tmp_path / "doku.md").write_text(
            "Sieben Regeln gelten hier:\nSieben Regeln gelten hier:\n", encoding="utf-8"
        )

        befunde = pruefe(self._zahl(7), tmp_path)

        assert len(befunde) == 1 and "2-mal" in befunde[0], befunde

    def test_eine_stimmende_zahl_ist_kein_befund(self, tmp_path):
        (tmp_path / "doku.md").write_text("Sieben Regeln gelten hier:\n", encoding="utf-8")

        assert pruefe(self._zahl(7), tmp_path) == []

    def test_ein_wort_statt_einer_zahl_wird_gemeldet_und_stuerzt_nicht_ab(self, tmp_path):
        """Die erste Fassung brach hier mit `ValueError` ab (siehe `pruefe`)."""

        (tmp_path / "doku.md").write_text("Diese Regeln gelten hier:\n", encoding="utf-8")

        befunde = pruefe(self._zahl(7), tmp_path)

        assert len(befunde) == 1 and "«Diese»" in befunde[0], befunde

    def test_dezimalzahlen_und_zahlwoerter_werden_gelesen(self):
        assert zahl_aus("Sechs") == 6
        assert zahl_aus("46") == 46
        assert zahl_aus("2,09") == 2.09
