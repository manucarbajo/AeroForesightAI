"""Die Musterseite zeigt jeden Baustein in jedem Zustand (P7.1-U1.6).

**Die Zusage aus dem Audit:** eine Musterseite unter einem internen Pfad, jeder
Baustein in allen Zuständen, hell und dunkel — und die Wächter aus P7.0 laufen
auch gegen sie. Ein Ton, den kein Bereich benutzt, oder eine Variante, die
heute nirgends steht, wurde bis dahin nie gemessen, weil sie nie gezeichnet
wurde.

**Gesucht, nicht aufgezählt.** Was «jeder Baustein» und «jeder Zustand» ist,
liest dieser Wächter aus `components.py` und dem Stylesheet:

* **jede öffentliche Funktion** von `components.py`;
* **jeder Wahrheitswert** in ihrer Signatur, mit beiden Werten;
* **jede Zustandsmenge**, die sie liest — eine Konstante auf Modulebene, deren
  Einträge Zeichenketten sind (`HINWEIS_TOENE`, `LOG_LEVELS`, …);
* **jeder Modifikator**, den sie als `af-…--{parameter}` zusammensetzt, mit den
  Werten, die das Stylesheet dafür kennt.

Ein neuer Baustein, ein neuer Ton oder eine neue Variante im Stylesheet fällt
damit auf, ohne dass jemand ihn hier einträgt. **Gemessen wird am gerenderten
Rumpf:** Jede Probe trägt `data-baustein` und `data-zustand`. Eine zweite
Prüfung hält fest, dass eine Probe den Baustein, den sie nennt, auch aufruft —
sonst ließe sich jeder Zustand mit einer Beschriftung behaupten.

**Nicht gemeint** sind Zustände, die erst der Browser herstellt (Zeigen, Fokus,
Drücken): Die wählt kein Aufruf.
"""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

from dash import html

from dashboard.web import components as ui
from dashboard.web import shell
from dashboard.web.pages import muster

WEB_ROOT = Path(__file__).resolve().parents[1] / "dashboard" / "web"
KOMPONENTEN = WEB_ROOT / "components.py"
STYLESHEET = WEB_ROOT / "assets" / "dashboard.css"
MUSTERSEITE = WEB_ROOT / "pages" / "muster.py"

#: Der Schlüssel für Zustände aus einer Menge statt aus einem benannten Parameter.
JEDER = "*"

#: Wie viele Zustände die Suche mindestens findet — gegen die eigene Blindheit.
#: Gemessen am 2026-09-13 über 32 Bausteine: 44 — acht Wahrheitswerte mit je
#: zwei Werten (16), fünf Zustandsmengen mit 20 Einträgen und drei Modifikatoren
#: mit 8 Werten.
ZUSTAENDE_MIN = 40

_MODIFIKATOR = re.compile(r"(af-[a-z0-9_-]*?--)$")


def _kinder(knoten) -> list:
    kinder = getattr(knoten, "children", None)
    if kinder is None:
        return []
    return list(kinder) if isinstance(kinder, (list, tuple)) else [kinder]


def _rumpf():
    return muster.rumpf_fuer(f"/app/{muster.ROUTE}")


def _proben(baum) -> dict[str, list[dict[str, str]]]:
    """Baustein → die Zustände seiner Proben, gelesen aus dem gerenderten Baum."""

    proben: dict[str, list[dict[str, str]]] = {}
    stapel = [baum]
    while stapel:
        knoten = stapel.pop()
        if isinstance(knoten, str) or knoten is None:
            continue
        stapel.extend(_kinder(knoten))
        baustein = getattr(knoten, "data-baustein", None)
        if baustein is None:
            continue
        zeichen = getattr(knoten, "data-zustand", None) or ""
        zustand = dict(teil.split("=", 1) for teil in zeichen.split())
        proben.setdefault(baustein, []).append(zustand)
    return proben


def _bausteine() -> set[str]:
    return {
        name
        for name, funktion in inspect.getmembers(ui, inspect.isfunction)
        if not name.startswith("_") and funktion.__module__ == ui.__name__
    }


def _mengen(baum: ast.Module) -> dict[str, set[str]]:
    """Jede Konstante auf Modulebene, deren Einträge Zeichenketten sind."""

    mengen: dict[str, set[str]] = {}
    for knoten in baum.body:
        if (
            isinstance(knoten, ast.Assign)
            and len(knoten.targets) == 1
            and isinstance(knoten.targets[0], ast.Name)
        ):
            name, wert = knoten.targets[0].id, knoten.value
        elif isinstance(knoten, ast.AnnAssign) and isinstance(knoten.target, ast.Name):
            name, wert = knoten.target.id, knoten.value
        else:
            continue
        if isinstance(wert, ast.Dict):
            eintraege = list(wert.keys)
        elif isinstance(wert, (ast.Tuple, ast.List, ast.Set)):
            eintraege = list(wert.elts)
        else:
            continue
        if eintraege and all(
            isinstance(e, ast.Constant) and isinstance(e.value, str) for e in eintraege
        ):
            mengen[name] = {e.value for e in eintraege}  # type: ignore[union-attr]
    return mengen


def _erwartet(quelle: str, stylesheet: str) -> dict[str, dict[str, set[str]]]:
    """Baustein → Parameter (oder `JEDER`) → die Werte, die gezeigt werden müssen."""

    baum = ast.parse(quelle)
    mengen = _mengen(baum)
    erwartet: dict[str, dict[str, set[str]]] = {}
    for funktion in baum.body:
        if not isinstance(funktion, ast.FunctionDef) or funktion.name.startswith("_"):
            continue
        argumente = funktion.args.args + funktion.args.kwonlyargs
        parameter = {a.arg for a in argumente}
        zustaende: dict[str, set[str]] = {}
        for argument in argumente:
            if argument.annotation is not None and ast.unparse(argument.annotation) == "bool":
                zustaende[argument.arg] = {"True", "False"}
        for knoten in ast.walk(funktion):
            if isinstance(knoten, ast.Name) and knoten.id in mengen:
                zustaende.setdefault(JEDER, set()).update(mengen[knoten.id])
            if not isinstance(knoten, ast.JoinedStr):
                continue
            for vorher, teil in zip(knoten.values, knoten.values[1:]):
                if not (isinstance(vorher, ast.Constant) and isinstance(teil, ast.FormattedValue)):
                    continue
                treffer = _MODIFIKATOR.search(str(vorher.value))
                if treffer and isinstance(teil.value, ast.Name) and teil.value.id in parameter:
                    werte = re.findall(
                        rf"\.{re.escape(treffer.group(1))}([a-z][a-z0-9-]*)", stylesheet
                    )
                    zustaende.setdefault(teil.value.id, set()).update(werte)
        erwartet[funktion.name] = zustaende
    return erwartet


def _fehlend(
    erwartet: dict[str, dict[str, set[str]]], proben: dict[str, list[dict[str, str]]]
) -> list[str]:
    befunde: list[str] = []
    for baustein, zustaende in sorted(erwartet.items()):
        gezeigt = proben.get(baustein)
        if not gezeigt:
            befunde.append(f"ui.{baustein}: keine Probe")
            continue
        for parameter, werte in sorted(zustaende.items()):
            if parameter == JEDER:
                vorhanden = {wert for probe in gezeigt for wert in probe.values()}
                wofuer = "Zustand"
            else:
                vorhanden = {probe[parameter] for probe in gezeigt if parameter in probe}
                wofuer = parameter
            befunde += [
                f"ui.{baustein}: {wofuer} {wert!r} fehlt" for wert in sorted(werte - vorhanden)
            ]
    return befunde


def _falsche_proben(quelle: str) -> list[str]:
    """Jede Probe, die einen Baustein nennt, den sie nicht aufruft."""

    befunde: list[str] = []
    for knoten in ast.walk(ast.parse(quelle)):
        if not (
            isinstance(knoten, ast.Call)
            and isinstance(knoten.func, ast.Name)
            and knoten.func.id == "_probe"
            and len(knoten.args) >= 2
        ):
            continue
        name = knoten.args[0]
        if not (isinstance(name, ast.Constant) and isinstance(name.value, str)):
            befunde.append(f"Zeile {knoten.lineno}: Der Baustein steht nicht wörtlich da")
            continue
        aufgerufen = {
            k.func.attr
            for k in ast.walk(knoten.args[1])
            if isinstance(k, ast.Call)
            and isinstance(k.func, ast.Attribute)
            and isinstance(k.func.value, ast.Name)
            and k.func.value.id == "ui"
        }
        if name.value not in aufgerufen:
            befunde.append(
                f"Zeile {knoten.lineno}: nennt ui.{name.value}, ruft {sorted(aufgerufen)}"
            )
    return befunde


def _erwartet_heute() -> dict[str, dict[str, set[str]]]:
    return _erwartet(
        KOMPONENTEN.read_text(encoding="utf-8"), STYLESHEET.read_text(encoding="utf-8")
    )


class TestJederBausteinInJedemZustand:
    def test_every_building_block_is_shown_in_every_state(self):
        befunde = _fehlend(_erwartet_heute(), _proben(_rumpf()))

        assert not befunde, "\n  ".join(
            [
                "Die Musterseite zeigt nicht alles, was `components.py` kennt:",
                *befunde,
                "Eine Probe dazu in `dashboard/web/pages/muster.py` — `_probe(name, "
                "ui.name(…), parameter=wert)`.",
            ]
        )

    def test_every_probe_calls_the_building_block_it_names(self):
        befunde = _falsche_proben(MUSTERSEITE.read_text(encoding="utf-8"))

        assert not befunde, "\n  ".join(["Diese Proben zeigen etwas anderes:", *befunde])

    def test_no_probe_names_a_building_block_that_is_gone(self):
        fremd = sorted(set(_proben(_rumpf())) - _bausteine())

        assert not fremd, f"Proben für Bausteine, die es nicht mehr gibt: {fremd}"

    def test_the_search_finds_what_is_there(self):
        """Gegen die eigene Blindheit: Die Suche findet jede Form, die es heute gibt."""

        erwartet = _erwartet_heute()

        assert set(erwartet) == _bausteine()
        assert erwartet["hinweis"][JEDER] == set(ui.HINWEIS_TOENE)
        assert erwartet["log_line"][JEDER] == set(ui.LOG_LEVELS)
        assert erwartet["accordion"]["open"] == {"True", "False"}
        assert {"demo", "warning"} <= erwartet["badge"]["variant"]
        assert erwartet["kachel"]["direction"] == {"up", "down"}
        gesamt = sum(len(werte) for z in erwartet.values() for werte in z.values())
        assert gesamt >= ZUSTAENDE_MIN, f"Nur {gesamt} Zustände gefunden — sucht die Suche noch?"

    def test_the_guard_would_notice_a_missing_state(self):
        quelle = (
            'TOENE = ("a", "b")\n'
            'def probe(x, *, offen: bool = False, art: str = "x"):\n'
            '    return f"af-probe af-probe--{art}" + TOENE[0]\n'
            "def ungezeigt():\n    pass\n"
        )
        css = ".af-probe--eins { color: red }\n.af-probe--zwei { color: red }\n"
        erwartet = _erwartet(quelle, css)
        baum = html.Div(
            html.Div(**{"data-baustein": "probe", "data-zustand": "offen=True art=eins"})
        )

        assert erwartet["probe"] == {
            "offen": {"True", "False"},
            JEDER: {"a", "b"},
            "art": {"eins", "zwei"},
        }
        assert _fehlend(erwartet, _proben(baum)) == [
            "ui.probe: Zustand 'a' fehlt",
            "ui.probe: Zustand 'b' fehlt",
            "ui.probe: art 'zwei' fehlt",
            "ui.probe: offen 'False' fehlt",
            "ui.ungezeigt: keine Probe",
        ]
        assert _falsche_proben('_probe("hinweis", ui.card(x))\n_probe("card", ui.card(x))\n') == [
            "Zeile 1: nennt ui.hinweis, ruft ['card']"
        ]


class TestDieSeiteLiegtAbseits:
    """Nicht verlinkt, erst beim Aufsuchen gebaut — wie der Modell-Bereich (P3.12)."""

    def test_it_has_an_address_but_no_link(self):
        assert muster.ROUTE in {route for route, _ in shell.INTERNE_ROUTES}
        assert muster.ROUTE not in {route for route, _ in shell.ROUTES}
        assert shell.active_route(f"/app/{muster.ROUTE}") == muster.ROUTE
        assert muster.ROUTE not in str(shell.nav_links(""))
        assert shell.seitentitel(muster.ROUTE) == f"{shell.MARKE} · Musterseite"

    def test_it_is_built_only_when_visited(self):
        for pfad in ("/app/", "/app/lauf", "/app/runs", "/app/modell", "/app/doku", None):
            assert muster.rumpf_fuer(pfad) == [], pfad
        assert _proben(_rumpf()), "Auf der eigenen Adresse entsteht kein Rumpf"

    def test_the_body_carries_no_fixed_id(self):
        """Regel 6: Ein ausgehängter Rumpf mit fester Kennung legte Callbacks lahm."""

        fest: list[str] = []
        stapel = [_rumpf()]
        while stapel:
            knoten = stapel.pop()
            if isinstance(knoten, (list, tuple)):
                stapel.extend(knoten)
                continue
            if isinstance(knoten, str) or knoten is None:
                continue
            if isinstance(getattr(knoten, "id", None), str):
                fest.append(knoten.id)
            stapel.extend(_kinder(knoten))

        assert not fest, f"Der Rumpf der Musterseite trägt feste Kennungen: {fest}"

    def test_the_frame_carries_the_host(self):
        assert muster.HOST in str(muster.layout())
