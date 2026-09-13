"""Kein Symbol erscheint als sein eigener Text (P1.4).

Die Symbolschrift ist seit dem 2026-08-30 ein **Teilsatz**: Statt der
vollständigen variablen Schrift (Megabyte) liegen nur die gut vierzig Zeichen im
Repo, die das Projekt benutzt — **5 KiB**.

**Der Preis dafür ist eine stille Fehlerart.** Ein Symbolname, der nicht im
Ausschnitt steckt, wird nicht als Zeichen gefunden und deshalb als Text gesetzt:
Da steht dann «chevron_right» in Buchstaben, wo ein Pfeil sein sollte. Keine
Meldung, kein Fehler im Log, nur ein Wort an einer Stelle, an der niemand eines
erwartet.

Diese Datei liest die Symbolnamen **an den Aufrufstellen** aus — per
AST-Durchlauf, nicht aus einer gepflegten Liste — und hält sie gegen den
Ausschnitt. Dasselbe Muster wie `test_web_theme.py`.

**Und sie hat einen blinden Fleck, der hier stehen muss, weil er zugeschlagen
hat.** Ein Name, der nicht *im Aufruf* steht, sondern von woanders hereingereicht
wird, entgeht ihr: Die vier Zustände der Schrittliste liegen in einem
Modul-Dict (`_ZUSTAENDE` in `wizard.py`), im Aufruf steht eine Variable. Sie
fehlten im Teilsatz, wurden als Wort gesetzt, und die Schrittliste brach um bis
zu **308 px** aus — gefunden vom Überlauf-Wächter, nicht von hier.

Deshalb gibt es dazu eine **Messung** statt eines zweiten Parsers: Teil 7 des
Browser-Wächters liest den gezeichneten Text jedes Symbol-Elements und hält ihn
gegen den Teilsatz — gleich, aus welcher Quelle der Name kommt. Diese Datei
bleibt daneben, weil sie ohne Browser läuft und schneller antwortet; sie ist die
erste Verteidigungslinie, nicht die einzige.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from scripts.schriften_holen import SYMBOLE

WEB = Path("dashboard/web")
LANDINGPAGE = Path("aeroforesight-ai-landing-page")
SCHRIFT_CSS = WEB / "assets" / "01-schriften.css"

#: Wie ein Symbolname aussieht: Kleinbuchstaben, Ziffern, Unterstriche. Alles
#: andere ist kein Ligaturname und wird gar nicht erst betrachtet.
NAME = re.compile(r"^[a-z][a-z0-9_]*$")

#: Die Stellen, an denen ein Symbolname übergeben wird.
AUFRUFE = {"icon", "icon_button"}
SCHLUESSEL = {"icon_name"}


def _namen_im_baum(baum: ast.AST) -> set[str]:
    """Jeden Symbolnamen, der in einem Syntaxbaum steht.

    **Auch als Standardwert eines Parameters** (2026-09-13). `ui.empty_state`
    setzte `icon_name="inbox"` als Vorgabe — ein Name, der nicht im Teilsatz
    steckt. Aufgefallen ist das nicht, weil jeder Aufrufer ein eigenes Symbol
    mitgab; der erste, der es nicht tat, hätte «inbox» als Wort gesetzt. Die
    Suche sah nur Aufrufe, und eine Vorgabe ist keiner.
    """

    namen: set[str] = set()

    def merke(wert: ast.expr | None) -> None:
        if isinstance(wert, ast.Constant) and isinstance(wert.value, str):
            if NAME.match(wert.value):
                namen.add(wert.value)

    for knoten in ast.walk(baum):
        if isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
            argumente = knoten.args.args + knoten.args.kwonlyargs
            standards = [None] * (len(knoten.args.args) - len(knoten.args.defaults))
            standards += list(knoten.args.defaults) + list(knoten.args.kw_defaults)
            for argument, standard in zip(argumente, standards):
                if argument.arg in SCHLUESSEL:
                    merke(standard)
            continue
        if not isinstance(knoten, ast.Call):
            continue
        funktion = knoten.func
        benannt = getattr(funktion, "attr", None) or getattr(funktion, "id", None)
        if benannt in AUFRUFE and knoten.args:
            merke(knoten.args[0])
        for schluesselwort in knoten.keywords:
            if schluesselwort.arg in SCHLUESSEL:
                merke(schluesselwort.value)
    return namen


def _namen_aus_quelltext() -> dict[str, set[str]]:
    """Jeden Symbolnamen mit den Dateien, in denen er steht."""

    gefunden: dict[str, set[str]] = {}

    def merke(name: str, pfad: Path) -> None:
        if NAME.match(name):
            gefunden.setdefault(name, set()).add(str(pfad))

    for pfad in sorted(WEB.rglob("*.py")):
        for name in _namen_im_baum(ast.parse(pfad.read_text(encoding="utf-8"))):
            merke(name, pfad)

    # Die Landingpage schreibt ihre Symbole als Text in das Element.
    for seite in sorted(LANDINGPAGE.glob("*.html")):
        text = seite.read_text(encoding="utf-8")
        for treffer in re.finditer(
            r'class="[^"]*material-symbols-outlined[^"]*"[^>]*>\s*([a-z][a-z0-9_]*)\s*<', text
        ):
            merke(treffer.group(1), seite)

    return gefunden


class TestJedesBenutzteSymbolStecktImTeilsatz:
    def test_no_icon_would_render_as_its_own_name(self):
        """**Gemessen am Quelltext, nicht an einer Liste.**

        Eine gepflegte Aufzählung fände nur die Symbole, an die jemand gedacht
        hat. Der AST-Durchlauf findet auch das, was morgen dazukommt.
        """

        benutzt = _namen_aus_quelltext()
        fehlend = {name: orte for name, orte in benutzt.items() if name not in set(SYMBOLE)}

        assert not fehlend, (
            "Diese Symbole stehen nicht im Teilsatz und erscheinen als Wort:\n  "
            + "\n  ".join(f"{name} — {', '.join(sorted(orte))}" for name, orte in fehlend.items())
            + "\n\nEintragen in `SYMBOLE` (scripts/schriften_holen.py), dann\n"
            "`python scripts/schriften_holen.py` laufen lassen."
        )

    def test_the_guard_finds_something_at_all(self):
        """Ein Wächter, der nichts findet, prüft nichts.

        Bräche der AST-Durchlauf (umbenannte Hilfsfunktion, anderer Aufruf),
        wäre er stumm grün — die schlimmste Art von Wächter.
        """

        benutzt = _namen_aus_quelltext()

        assert len(benutzt) >= 20, f"Nur {len(benutzt)} Symbolnamen gefunden — sucht er noch?"
        assert "chevron_right" in benutzt

    def test_the_search_sees_calls_keywords_and_defaults(self):
        """Mutationsprobe: jede der drei Formen, in denen ein Name übergeben wird."""

        probe = (
            'ui.icon("im_aufruf")\n'
            'ui.button("Los", icon_name="als_schluessel")\n'
            'def leer(text, *, icon_name="als_vorgabe"): pass\n'
            "def ohne(text, *, icon_name=None): pass\n"
        )

        assert _namen_im_baum(ast.parse(probe)) == {"im_aufruf", "als_schluessel", "als_vorgabe"}


class TestDieSchriftenLiegenImRepo:
    def test_the_stylesheet_points_at_local_files_only(self):
        """Kein `@font-face` zeigt mehr nach draußen."""

        css = SCHRIFT_CSS.read_text(encoding="utf-8")
        entfernte = re.findall(r"url\((https?://[^)]+)\)", css)

        assert not entfernte, f"Die Schriften-CSS lädt von fremden Hosts: {entfernte}"
        assert "url(fonts/" in css, "Die CSS verweist auf gar keine Schriftdatei"

    def test_every_referenced_file_exists(self):
        css = SCHRIFT_CSS.read_text(encoding="utf-8")
        fehlend = [
            name
            for name in re.findall(r"url\(fonts/([^)]+)\)", css)
            if not (SCHRIFT_CSS.parent / "fonts" / name).is_file()
        ]

        assert not fehlend, f"Die CSS nennt Schriftdateien, die es nicht gibt: {fehlend}"

    @pytest.mark.parametrize(
        "pfad",
        [Path("dashboard/web/app.py"), *sorted(LANDINGPAGE.glob("*.html"))],
        ids=lambda p: p.name,
    )
    def test_no_page_asks_google_for_a_font(self, pfad):
        """Der Befund von P1.4, als Zusage."""

        # **Auf den Verweis, nicht auf die Erwähnung.** Die erste Fassung suchte
        # den blossen Hostnamen und schlug an — an einem Kommentar, der erklärt,
        # dass genau dieser Verweis weg ist.
        text = pfad.read_text(encoding="utf-8")
        verweise = re.findall(r'(?:href|src)\s*=\s*"(https?://fonts\.[^"]*)"', text)

        assert not verweise, f"{pfad.name} lädt Schriften von einem fremden Host: {verweise}"
