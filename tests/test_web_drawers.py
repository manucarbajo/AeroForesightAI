"""Ein Schubladen-Knopf erscheint genau dann, wenn seine Zone eine Schublade ist.

Der Leitstand hat zwei überlagernde Zonen mit **verschiedenen** Haltepunkten:
die Telemetrie weicht unter 1280 px aus, die Parameterspalte erst unter 1024 px.
Beide Umschalter trugen dieselbe Klasse und dieselbe Sichtbarkeitsregel (die des
breiteren Haltepunkts). Zwischen 1024 und 1279 px stand der linke Knopf damit da,
während die Spalte noch als Rasterspalte im Raster lag: Am laufenden System
gemessen setzte der Klick `af-shell--left-open`, die Spalte blieb aber
`position: static` bei x=0 — **nichts bewegte sich**. Schlimmer als folgenlos:
Der so gesetzte Zustand blieb stehen, und beim nächsten Verkleinern unter 1024 px
sprang die Schublade samt Verdunkler ungefragt auf.

Dieser Wächter prüft deshalb nicht, *dass* es zwei Klassen gibt — das wäre nur
das Nachsprechen der Lösung. Er liest **beide Zahlen aus dem Stylesheet** und
vergleicht sie: den Haltepunkt, ab dem eine Zone zur Schublade wird, mit dem, ab
dem ihr Knopf erscheint. Wer künftig einen der beiden verschiebt und den anderen
vergisst, bekommt einen roten Test statt eines toten Knopfes.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from dashboard.web import shell

CSS = Path(__file__).resolve().parents[1] / "dashboard" / "web" / "assets" / "dashboard.css"


def _bloecke() -> list[tuple[int | None, str]]:
    """Das Stylesheet in (max-width, Inhalt)-Paare zerlegen.

    `None` steht für alles außerhalb einer `@media`-Abfrage. Bewusst ein
    einfacher Klammerzähler statt eines CSS-Parsers: Die Datei ist handgepflegt
    und flach verschachtelt, und eine Abhängigkeit für drei Zahlen wäre zu viel.
    """

    text = CSS.read_text(encoding="utf-8")
    bloecke: list[tuple[int | None, str]] = []
    rest = []
    i = 0
    while i < len(text):
        treffer = re.compile(r"@media\s*\(max-width:\s*(\d+)px\)\s*\{").search(text, i)
        if treffer is None:
            rest.append(text[i:])
            break
        rest.append(text[i : treffer.start()])
        tiefe = 1
        j = treffer.end()
        while j < len(text) and tiefe:
            if text[j] == "{":
                tiefe += 1
            elif text[j] == "}":
                tiefe -= 1
            j += 1
        bloecke.append((int(treffer.group(1)), text[treffer.end() : j - 1]))
        i = j
    bloecke.append((None, "".join(rest)))
    return bloecke


def _sieger(klassen: set[str], eigenschaft: str) -> tuple[str, str]:
    """Welche bedingungslose Regel für ein Element mit *klassen* gewinnt.

    Nachgebaut wird genau das, was der Browser tut: Unter allen Regeln, deren
    Selektor ausschließlich aus Klassen dieses Elements besteht, gewinnt die mit
    der höchsten Spezifität — bei Gleichstand die **spätere** in der Datei.

    Ohne diese Prüfung sähe der Wächter die Haltepunkte richtig und den Fehler
    trotzdem nicht: `.af-drawer-toggle { display: none }` stand korrekt da, wurde
    aber von `.af-icon-btn { display: inline-flex }` geschlagen, weil beide eine
    Klasse tragen und `.af-icon-btn` weiter unten steht.
    """

    muster = re.compile(r"([.\w\s-]+?)\s*\{([^}]*)\}")
    beste: tuple[int, int] | None = None
    treffer = ("", "")
    for grenze, inhalt in _bloecke():
        if grenze is not None:
            continue
        for stelle, regel in enumerate(muster.finditer(inhalt)):
            selektor = regel.group(1).strip()
            if not selektor.startswith(".") or " " in selektor or "," in selektor:
                continue
            benutzte = set(selektor.split(".")) - {""}
            if not benutzte <= klassen:
                continue
            wert = re.search(rf"(?:^|;)\s*{eigenschaft}\s*:\s*([^;]+)", regel.group(2))
            if wert is None:
                continue
            rang = (len(benutzte), stelle)
            if beste is None or rang >= beste:
                beste, treffer = rang, (selektor, wert.group(1).strip())
    return treffer


def _haltepunkt(selektor: str, eigenschaft: str) -> int | None:
    """Ab welcher Fensterbreite ein Selektor diese Eigenschaft gesetzt bekommt.

    Gesucht wird der **engste** Block, der die Regel trägt — bei mehreren gilt
    für die Frage «ab wann wirkt sie» der größte Haltepunkt.
    """

    treffer: list[int] = []
    for grenze, inhalt in _bloecke():
        if grenze is None:
            continue
        for regel in re.findall(re.escape(selektor) + r"\s*\{([^}]*)\}", inhalt):
            if eigenschaft in regel:
                treffer.append(grenze)
    return max(treffer) if treffer else None


#: Zone, Umschalter-Klasse — und die beiden Regeln, die zusammenpassen müssen.
ZONEN = [
    pytest.param(".af-shell__left", ".af-drawer-toggle--left", id="parameterspalte"),
    pytest.param(".af-shell__right", ".af-drawer-toggle--right", id="telemetrie"),
]

#: Die Klassen, die ein Umschalter im DOM wirklich trägt. `ui.icon_button` setzt
#: `af-icon-btn` immer dazu — genau daher kam der Kaskadenfehler.
TOGGLE_KLASSEN = {"af-icon-btn", "af-drawer-toggle", "af-drawer-toggle--left"}


class TestDerKnopfIstStandardmaessigWirklichVersteckt:
    """Nicht «eine Regel sagt none», sondern «diese Regel gewinnt auch»."""

    def test_the_hiding_rule_beats_the_icon_button_base(self):
        selektor, wert = _sieger(TOGGLE_KLASSEN, "display")

        assert wert == "none", (
            f"Bedingungslos gewinnt «{selektor}: display: {wert}». Damit steht der "
            "Umschalter auch dort, wo seine Zone gar keine Schublade ist."
        )

    def test_the_competing_rule_still_exists(self):
        """Kontrolltest: Ohne den Gegenspieler prüfte der obige nichts.

        Verschwände `.af-icon-btn { display: … }`, bliebe der Test grün, ohne
        etwas zu sichern — dann wäre er zu streichen, nicht stillschweigend zu
        behalten.
        """

        assert _sieger({"af-icon-btn"}, "display") == (".af-icon-btn", "inline-flex")


class TestJederKnopfPasstZuSeinerZone:
    @pytest.mark.parametrize(("zone", "knopf"), ZONEN)
    def test_toggle_appears_exactly_where_its_zone_becomes_a_drawer(self, zone, knopf):
        """Schubladen-Haltepunkt und Knopf-Haltepunkt sind dieselbe Zahl."""

        zone_ab = _haltepunkt(zone, "position: fixed")
        knopf_ab = _haltepunkt(knopf, "display: inline-flex")

        assert zone_ab is not None, f"{zone} wird nirgends zur Schublade"
        assert knopf_ab is not None, f"{knopf} wird nirgends eingeblendet"
        assert knopf_ab == zone_ab, (
            f"{knopf} erscheint ab {knopf_ab} px, aber {zone} wird erst ab "
            f"{zone_ab} px zur Schublade. Dazwischen ist der Knopf wirkungslos."
        )

    def test_the_two_zones_really_have_different_breakpoints(self):
        """Der Kontrolltest: Ohne verschiedene Haltepunkte prüfte der obige nichts.

        Fielen beide Zahlen zusammen, wäre eine gemeinsame Klasse richtig und
        dieser Wächter überflüssig — er würde dann grün bleiben, ohne etwas zu
        sichern. Genau das war der Zustand, in dem der Fehler entstand.
        """

        links = _haltepunkt(".af-shell__left", "position: fixed")
        rechts = _haltepunkt(".af-shell__right", "position: fixed")
        assert links != rechts

    def test_each_toggle_carries_its_own_modifier(self):
        """Die Verdrahtung: Ohne eigene Klasse könnten die Regeln nicht greifen."""

        gerendert = str(shell.navbar("")) + str(
            shell.header(
                "",
                state=shell.status.derive(running=False, demo=False),
                lauf_bezeichnung=None,
            )
        )
        assert "af-drawer-toggle--left" in gerendert
        assert "af-drawer-toggle--right" in gerendert


# --- Ziehgriffe (P1.7) -----------------------------------------------------


class TestDieGriffeGehoerenZuIhrenSpalten:
    """Ein Griff kann nur ziehen, solange seine Zone eine Rasterspalte ist.

    Sobald sie zur Schublade wird, hat er nichts mehr zu greifen — und schlimmer:
    Er waere dann ein Rasterelement ohne benannten Bereich und wuerde vom Raster
    selbsttaetig irgendwohin einsortiert. Der Haltepunkt, ab dem ein Griff
    verschwindet, muss deshalb derselbe sein, ab dem der zugehoerige
    Schubladen-Knopf erscheint. Zwei Zahlen fuer dieselbe Grenze sind genau die
    Drift, an der schon die Umschalter gescheitert sind.
    """

    #: Griff, zugehoeriger Umschalter — beide haengen an derselben Zone.
    PAARE = [
        pytest.param(".af-shell__gutter--left", ".af-drawer-toggle--left", id="bedienfeld"),
        pytest.param(".af-shell__gutter--right", ".af-drawer-toggle--right", id="telemetrie"),
    ]

    @pytest.mark.parametrize(("griff", "knopf"), PAARE)
    def test_the_gutter_disappears_where_the_toggle_appears(self, griff, knopf):
        griff_weg_ab = _haltepunkt(griff, "display: none")
        knopf_da_ab = _haltepunkt(knopf, "display: inline-flex")

        assert griff_weg_ab is not None, f"{griff} wird nirgends ausgeblendet"
        assert griff_weg_ab == knopf_da_ab, (
            f"{griff} verschwindet ab {griff_weg_ab} px, {knopf} erscheint ab "
            f"{knopf_da_ab} px. Dazwischen steht ein Griff ohne Spalte."
        )

    def test_the_shell_renders_both_gutters(self):
        gerendert = str(
            shell.layout(
                active="",
                state=shell.status.derive(running=False, demo=False),
                lauf_bezeichnung=None,
                left="l",
                main="m",
                timeline="t",
                right="r",
            )
        )

        assert "af-shell__gutter--left" in gerendert
        assert "af-shell__gutter--right" in gerendert

    def test_a_gutter_carries_no_dash_id(self):
        """Das Ziehen laeuft im Browser — der Server hat dazu nichts zu sagen.

        Eine Dash-ID hier waere die Einladung, spaeter doch einen Callback
        daranzuhaengen; dann liefe je Mausbewegung eine Serverrunde, und genau
        deshalb steht das Ziehen in `assets/shell_resize.js`.
        """

        griff = shell._gutter("left", "Test")

        assert getattr(griff, "id", None) is None
