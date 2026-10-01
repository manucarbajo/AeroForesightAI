"""Das Farbfundament des Leitstands (P1.5).

Drei Zusagen tragen den Dark Mode, und alle drei sind hier **mechanisch**
geprüft statt nach Augenschein:

1. **Jede Rolle existiert in beiden Modi.** Ein Token, den es nur hell gibt,
   wirft im Dunkeln eine leere Farbe — sichtbar als schwarzer Text auf
   schwarzem Grund, und zwar erst bei dem, der die Seite öffnet.
2. **Python und Stylesheet färben mit denselben Namen.** `theme.py` färbt, was
   Python zeichnet (Plotly, `DataTable`), `dashboard.css` alles Übrige. Laufen
   die Namen auseinander, sieht man es an genau einer Komponente — und sucht
   lange.
3. **Keine rohe Tailwind-Farbklasse mehr unter `dashboard/web/`.** Das ist die
   eigentliche Zusage: `bg-white` ist im Dark Mode eine falsche Aussage, und
   eine einzelne davon reicht, um eine Karte weiß aufblitzen zu lassen.

Der dritte Punkt läuft als **Sweep über den Syntaxbaum**, nicht als gepflegte
Dateiliste. Eine Liste fängt den Rückfall an bekannter Stelle; ein Sweep fängt
auch die Datei, an die niemand gedacht hat — dieselbe Begründung wie bei
`TestKeinKontextparameterEntgehtDemSweep` in `test_cost_pressure_source.py`.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import plotly.io as pio
import pytest

from dashboard.web import theme

WEB_ROOT = Path(theme.__file__).resolve().parent
CSS_PATH = WEB_ROOT / "assets" / "dashboard.css"

#: Tailwind-Farbklassen: eine Eigenschaft, ein Farbname, optional eine Stufe.
#: Bewusst breit — es geht nicht darum, genau die heute benutzten zu finden,
#: sondern jede, die jemand künftig hinschreibt.
_COLOR_CLASS = re.compile(
    r"\b(?:hover:|focus:|active:|group-hover:|dark:)?"
    r"(?:bg|text|border|ring|divide|placeholder|from|via|to|decoration|outline|shadow|caret|accent)"
    r"-(?:white|black|slate|gray|zinc|neutral|stone|navy|teal|rose|amber|emerald|red|green|blue|"
    r"indigo|violet|purple|cyan|sky|lime|yellow|orange|pink|fuchsia)"
    r"(?:-(?:50|100|200|300|400|500|600|700|800|900|950))?\b"
)

#: Ein Hex-Farbwert im Python-Code. Erlaubt ist er nur in `theme.py` — dort
#: stehen die Paletten.
_HEX = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")

#: `theme.py` hält die Paletten, `demo_run.py` und `status.py` halten keine
#: Farben. Der Sweep nimmt alles unter `dashboard/web/` und lässt nur die
#: Dateien aus, die Farbe führen *dürfen* — jede mit Grund.
#:
#: **`theme.py`** ist die Quelle der Tokens; ohne Farbwerte darin gäbe es keine.
#:
#: **`landing_route.py`** ist die Ausnahme mit der ungewohnten Begründung: Es
#: liegt zwar unter `dashboard/web/`, rendert aber eine **Landingpage** — die
#: Bestätigungsseite der Demo-Anfrage (P1.4). Die Landingpage ist eine andere
#: Oberfläche mit einer anderen Regel: Sie kennt keinen Dark Mode, ihre fünf
#: statischen Seiten färben seit jeher über Tailwind-Klassen, und die
#: Bestätigung soll aussehen wie sie und nicht wie das Dashboard. Wer hier eine
#: Dashboard-Ansicht baut, hat die falsche Datei gewählt.
_ERLAUBT = {"theme.py", "landing_route.py"}


def _python_files() -> list[Path]:
    return sorted(
        path
        for path in WEB_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts and path.name not in _ERLAUBT
    )


def _string_literals(tree: ast.AST) -> list[tuple[int, str]]:
    """Alle Zeichenketten eines Moduls — ohne Docstrings und Kommentare.

    Docstrings beschreiben oft genau das, was verboten ist («`bg-white` ist im
    Dark Mode eine falsche Aussage»). Sie mitzuzählen hieße, die Erklärung des
    Verbots zum Verstoß zu erklären.
    """

    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                docstrings.add(id(body[0].value))

    return [
        (node.lineno, node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


# --- 1. Beide Modi sind vollständig ----------------------------------------


class TestBeideModiSindVollstaendig:
    def test_every_role_exists_in_both_modes(self):
        hell = set(theme.PALETTE[theme.LIGHT])
        dunkel = set(theme.PALETTE[theme.DARK])

        assert hell == dunkel, (
            "Rollen ohne Gegenstück: "
            f"nur hell {sorted(hell - dunkel)}, nur dunkel {sorted(dunkel - hell)}"
        )

    def test_no_role_is_empty(self):
        for mode in theme.MODES:
            for name, value in theme.PALETTE[mode].items():
                assert value.strip(), f"{mode}/{name} ist leer"

    @pytest.mark.parametrize("mode", theme.MODES)
    def test_light_and_dark_actually_differ(self, mode):
        """Kontrolle: Die beiden Paletten sind nicht dieselbe Datei zweimal."""

        gleich = [
            name
            for name in theme.PALETTE[theme.LIGHT]
            if theme.PALETTE[theme.LIGHT][name] == theme.PALETTE[theme.DARK][name]
        ]

        assert len(gleich) < len(theme.PALETTE[mode]) / 2, (
            f"{len(gleich)} Rollen tragen in beiden Modi denselben Wert — "
            "das ist kein zweites Design, das ist dasselbe."
        )

    def test_both_plotly_templates_are_registered(self):
        theme.register_template()

        for mode in theme.MODES:
            assert theme.template_for(mode) in pio.templates

    def test_the_templates_carry_the_matching_background(self):
        theme.register_template()

        for mode in theme.MODES:
            template = pio.templates[theme.template_for(mode)]
            assert template.layout.paper_bgcolor == theme.PALETTE[mode]["paper-bg"]

    def test_the_templates_write_numbers_in_german(self):
        """Dezimalkomma wie in den Kennzahlen (`formate.zahl`, P8-V6) — auch die
        Figur, die über ihr eigenes `template=` geht (Animation), nimmt eines davon."""

        theme.register_template()

        for mode in theme.MODES:
            assert pio.templates[theme.template_for(mode)].layout.separators == ",."

    @pytest.mark.parametrize(
        ("eingabe", "erwartet"),
        [("dark", "dark"), ("DARK", "dark"), ("light", "light"), (None, "light"), ("", "light")],
    )
    def test_an_unknown_mode_falls_back_to_light(self, eingabe, erwartet):
        """Der Wert kommt aus dem Browser — er darf alles sein."""

        assert theme.normalise(eingabe) == erwartet


# --- 2. Stylesheet und Python nennen dieselben Namen ------------------------


def _css_variables(block: str) -> set[str]:
    return set(re.findall(r"--([a-z0-9-]+):", block))


def _css_block(selector: str) -> str:
    text = CSS_PATH.read_text(encoding="utf-8")
    start = text.index(selector + " {")
    return text[start : text.index("}", start)]


class TestStylesheetUndPythonSindDeckungsgleich:
    """Zwei Orte färben dieselben Flächen. Sie dürfen nicht auseinanderlaufen."""

    @pytest.mark.parametrize(
        ("selector", "mode"), [(":root", theme.LIGHT), ("html.dark", theme.DARK)]
    )
    def test_every_python_token_exists_in_the_stylesheet(self, selector, mode):
        fehlt = set(theme.PALETTE[mode]) - _css_variables(_css_block(selector))

        assert not fehlt, f"In `{selector}` fehlen: {sorted(fehlt)}"

    def test_the_two_css_blocks_define_the_same_roles(self):
        hell = _css_variables(_css_block(":root")) & set(theme.PALETTE[theme.LIGHT])
        dunkel = _css_variables(_css_block("html.dark"))

        assert hell <= dunkel, f"Im Dark Mode nicht überschrieben: {sorted(hell - dunkel)}"

    def test_the_values_match_too(self):
        """Nicht nur die Namen — auch die Werte.

        Ein Diagramm auf einer Fläche, die anders eingefärbt ist als sein
        eigener Hintergrund, sieht aus wie ein Rechteck im Rechteck.
        """

        block = _css_block(":root")
        for name, value in theme.PALETTE[theme.LIGHT].items():
            treffer = re.search(rf"--{re.escape(name)}:\s*([^;]+);", block)
            assert treffer, f"--{name} fehlt"
            assert treffer.group(1).strip().lower() == value.strip().lower(), name


# --- 3. Kein Modul färbt an den Tokens vorbei -------------------------------


class TestKeineFarbklasseEntgehtDemSweep:
    """Die tragende Zusage: Farbe kommt aus den Tokens, nirgends sonst her."""

    def test_no_module_writes_a_tailwind_colour_class(self):
        befunde: list[str] = []
        for path in _python_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for lineno, text in _string_literals(tree):
                for treffer in _COLOR_CLASS.findall(text):
                    befunde.append(f"{path.relative_to(WEB_ROOT)}:{lineno} → {treffer}")

        assert not befunde, (
            "Tailwind-Farbklassen unter `dashboard/web/`:\n  "
            + "\n  ".join(befunde)
            + "\n\nFarbe gehört in die Tokens (`theme.py` / `assets/dashboard.css`); "
            "hier stehen nur die `af-*`-Klassen, die sie benutzen."
        )

    def test_no_module_writes_a_raw_hex_colour(self):
        befunde: list[str] = []
        for path in _python_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for lineno, text in _string_literals(tree):
                if _HEX.search(text):
                    befunde.append(f"{path.relative_to(WEB_ROOT)}:{lineno} → {text[:60]}")

        assert not befunde, (
            "Rohe Farbwerte unter `dashboard/web/`:\n  "
            + "\n  ".join(befunde)
            + "\n\nSie gehören als Rolle in `theme.PALETTE`, damit es sie auch dunkel gibt."
        )

    def test_the_sweep_would_notice_a_relapse(self):
        """Kontrolle: Der Sweep findet wirklich etwas, statt immer leer zu sein."""

        tree = ast.parse('x = "af-card bg-white text-slate-600"\ny = "#1E3A5F"\n')
        gefunden = [text for _lineno, text in _string_literals(tree)]

        assert _COLOR_CLASS.findall(gefunden[0]) == ["bg-white", "text-slate-600"]
        assert _HEX.search(gefunden[1])

    def test_a_docstring_explaining_the_rule_is_not_a_violation(self):
        """Kontrolle in die andere Richtung: Docstrings zählen nicht mit."""

        tree = ast.parse('"""`bg-white` ist im Dark Mode falsch."""\nx = "af-surface"\n')

        assert all("bg-white" not in text for _lineno, text in _string_literals(tree))


# **Hier stand bis zum 2026-09-12 `TestEsGibtEinLesemassUndNichtZwei`** (P3.17):
# ein Verbot von Tailwinds `max-w-prose` als **zweitem, ungeeichtem** Lesemass
# neben `af-mass`, samt der Gegenprobe, dass das erste ueberhaupt definiert ist.
#
# **Beide Zusagen sind umgezogen, nicht entfallen** — nach
# `tests/test_web_breiten.py`, wo jetzt alles ueber Breite an einer Stelle
# steht. Die zweite ist dabei umgedreht worden: Das Lesemass ist mit der
# Ruecknahme von E3 abgeschafft, `.af-mass` darf es also nicht mehr geben.
# Die erste gilt unveraendert weiter, mit neuer Begruendung — nicht mehr
# «ein zweites Mass neben dem geeichten», sondern «ein Name, der wie ein
# Lesemass aussieht, bringt es am leichtesten zurueck».
#
# Der Grund, warum die Pruefung statisch ist und nicht im Browser-Waechter
# steht, gilt weiter und ist dort wiederholt: Der ist opt-in und ueberspringt
# sich ohne Chromium — genau daran ist C5 gestorben.


class TestPngUndBildschirmSprechenDieselbeSprache:
    """Eine Größe, eine Farbe — im Bericht wie auf dem Schirm (P1.2)."""

    def test_the_chart_roles_come_from_one_source(self):
        """Nicht «zufällig gleich», sondern **dieselbe** Konstante.

        Vorher wählte jede Matplotlib-Figur ihre Farben selbst: `#2563eb` für
        die Buchungsrate, `#059669` für den Preis — das Dashboard färbte beides
        anders. Wer ein PNG neben den Bildschirm hielt, las die Legende zweimal.
        """

        from dashboard.web import theme
        from src.reporting.figure_generator.stil import FARBEN

        assert theme.PALETTE[theme.LIGHT]["price"] == FARBEN["preis"]
        assert theme.PALETTE[theme.LIGHT]["booking"] == FARBEN["buchung"]
        assert theme.PRICE == FARBEN["preis"]
        assert theme.BOOKING == FARBEN["buchung"]

    def test_no_plot_picks_its_own_colour(self):
        """**Der Wächter zeigt auf die Tat, nicht auf die Absicht.**

        Ein roher Farbwert in einer Plot-Funktion ist die nächste Abweichung:
        Er sieht für sich genommen richtig aus und passt zu nichts.
        """

        import re
        from pathlib import Path

        quelle = Path("src/reporting/figure_generator/plots.py").read_text(encoding="utf-8")
        roh = re.findall(r"#[0-9a-fA-F]{6}\b", quelle)

        assert not roh, (
            f"Rohe Farbwerte in den Plot-Funktionen: {sorted(set(roh))}\n"
            "Die Rollen stehen in `figure_generator/stil.py` — wer dort keine "
            "passende findet, legt eine an, statt eine Farbe zu erfinden."
        )
