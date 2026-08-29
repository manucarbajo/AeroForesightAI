"""Kein Feld erfindet einen Wert, den niemand gewählt hat (P1.9-W5.1).

**Der Befund, aus dem dieses Paket entstand**, ist mit geleerter Sitzung
gemessen und ohne eine einzige Eingabe: Allein das Anzeigen von Schritt 3
schrieb `seed: null → 42` in den Entwurf. Der Weg dahin ist kurz und gilt für
**jedes** Feld:

1. Der Renderer setzt einen Rückfall ein, wenn im Entwurf nichts steht —
   `int(seed if seed is not None else DEFAULT_SEED)`.
2. `_sync` liest **alle sichtbaren** Felder aus dem DOM und schreibt sie in den
   Store.
3. Damit steht die 42 im Entwurf, als hätte jemand sie eingetippt.

Regel 2 der Architektur-Map sagt: Werte fließen vom Feld in den Store, nie
zurück. Das ist hier **formal eingehalten** und trotzdem gebrochen — der Wert
kommt nicht aus dem Store, sondern aus dem Quelltext. Genau deshalb reicht ein
Blick auf die Callbacks nicht, und genau deshalb steht hier ein Wächter.

**Die Folgen sind nicht kosmetisch.** `touched()` vergleicht gegen den
Auslieferungszustand und meldet danach dauerhaft «etwas eingestellt»; der
Session-Store trägt das über einen Neuladen; und beim Kostenanteil steht im
Quelltext eine **andere** Zahl als in der Konfigurationsdatei (0,33 gegen 0,25)
— fehlt der Schlüssel, spritzt die Oberfläche 0,33 in den Lauf.

Es ist dieselbe Klasse, die P0.7 in der Engine mit einem AST-Durchlauf verboten
hat («erfundene Konstante»). Dort war das Ergebnis, dass eine handgepflegte
Aufzählung nicht genügt: Der erste Anlauf nannte acht Stellen und übersah zwei
Geschwister in derselben Datei. Deshalb hier ebenfalls ein Durchlauf über den
Syntaxbaum statt einer Liste.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

WURZEL = Path("dashboard/web")

#: Die Feld-Renderer aus `controls.py`. Ihr **zweites** Argument ist der Wert,
#: der im Eingabefeld landet — und damit das, was `_sync` zurückschreibt.
RENDERER = {"number", "text", "textarea", "select", "slider", "check"}


@dataclass(frozen=True)
class Fund:
    datei: str
    zeile: int
    feld: str
    quelle: str

    def __str__(self) -> str:
        return f"{self.datei}:{self.zeile}  {self.feld}  ←  {self.quelle}"


#: Rückfälle, die bleiben dürfen — **mit Begründung**, so wie die `AUSNAHMEN`
#: des Kostendruck-Wächters. Ein Eintrag hier ist eine Aussage, kein Freibrief.
#: **Sie ist leer, und das ist das Ergebnis.** Beim ersten scharfen Durchlauf
#: standen hier siebzehn Fundstellen; keine einzige brauchte eine Ausnahme. Jede
#: war ein Literal, das den Vorgabewert ein **zweites Mal** aussprach — einmal
#: in `default_config_draft()`, einmal im Renderer daneben. Zwei Quellen für
#: dieselbe Zahl, und beim Kostenanteil liefen sie bereits auseinander (0,33 im
#: Quelltext gegen 0,25 in der Datei).
#:
#: Der erste Anlauf dieses Wächters trug fünf Einträge, von denen keiner nötig
#: war — `test_every_exception_is_still_needed` hat sie sofort gemeldet. Eine
#: Ausnahmeliste, die nicht schrumpft, wächst.
AUSNAHMEN: dict[str, str] = {}


def _ist_rueckfall(knoten: ast.AST) -> str | None:
    """Ob dieser Wertausdruck eine Konstante einsetzt, wenn nichts da ist.

    Drei Formen, alle im Bestand gefunden:

    * ``entwurf.get("feld", 0.6)`` — der zweite Parameter von `get`
    * ``entwurf.get("feld") or 40`` — die rechte Seite eines `or`
    * ``x if x is not None else DEFAULT_SEED`` — der `else`-Zweig

    **Ein leerer Text zählt nicht.** `draft.get("model", "")` erfindet nichts;
    es sagt «hier steht noch nichts», und genau das soll ein Feld ohne Wert
    zeigen.
    """

    def _konstante(n: ast.AST) -> str | None:
        if isinstance(n, ast.Constant):
            if n.value in ("", None, False):
                return None
            return repr(n.value)
        # Benannte Konstanten wie `DEFAULT_SEED` sind keine Ausrede: Sie stehen
        # ebenso im Quelltext und nicht im Entwurf.
        if isinstance(n, ast.Name) and n.id.isupper():
            return n.id
        return None

    for teil in ast.walk(knoten):
        if isinstance(teil, ast.Call) and isinstance(teil.func, ast.Attribute):
            if teil.func.attr == "get" and len(teil.args) == 2:
                treffer = _konstante(teil.args[1])
                if treffer:
                    return f".get(..., {treffer})"
        if isinstance(teil, ast.BoolOp) and isinstance(teil.op, ast.Or):
            treffer = _konstante(teil.values[-1])
            if treffer:
                return f"... or {treffer}"
        if isinstance(teil, ast.IfExp):
            treffer = _konstante(teil.orelse)
            if treffer:
                return f"... else {treffer}"
    return None


def _feldname(knoten: ast.AST) -> str:
    if isinstance(knoten, ast.Constant) and isinstance(knoten.value, str):
        return knoten.value
    if isinstance(knoten, ast.JoinedStr):
        return "".join(
            teil.value if isinstance(teil, ast.Constant) else "…" for teil in knoten.values
        )
    return "<berechnet>"


def funde() -> list[Fund]:
    """Alle Feld-Renderer mit einem erfundenen Rückfall."""

    gefunden: list[Fund] = []
    for pfad in sorted(WURZEL.rglob("*.py")):
        baum = ast.parse(pfad.read_text(encoding="utf-8"), filename=str(pfad))
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.Call) or not isinstance(knoten.func, ast.Attribute):
                continue
            if knoten.func.attr not in RENDERER or len(knoten.args) < 2:
                continue
            quelle = _ist_rueckfall(knoten.args[1])
            if quelle is None:
                continue
            gefunden.append(
                Fund(
                    datei=pfad.as_posix(),
                    zeile=knoten.lineno,
                    feld=_feldname(knoten.args[0]),
                    quelle=quelle,
                )
            )
    return gefunden


class TestKeinFeldErfindetEinenWert:
    """Der Wächter, den P1.9-W5.1 schuldet."""

    def test_no_renderer_invents_a_value(self):
        offen = [
            fund
            for fund in funde()
            if fund.feld.split(".")[-1] not in AUSNAHMEN and fund.feld not in AUSNAHMEN
        ]

        assert not offen, (
            "Diese Feld-Renderer setzen eine Konstante ein, wenn im Entwurf nichts "
            "steht — und `_sync` schreibt sie danach in den Store, als hätte sie "
            "jemand eingetippt:\n\n"
            + "\n".join(f"  {fund}" for fund in offen)
            + "\n\nEin Feld ohne Wert wird **leer** gerendert. Wo der Rückfall aus "
            "gutem Grund bleibt, gehört er mit Begründung in `AUSNAHMEN`."
        )

    def test_the_guard_would_notice_a_relapse(self, tmp_path):
        """Ein Wächter, der aus dem falschen Grund grün ist, ist schlechter als keiner."""

        probe = tmp_path / "probe.py"
        probe.write_text(
            "c.number('probe_a', draft.get('x', 42))\n"
            "c.text('probe_b', draft.get('y') or 'wert')\n"
            "c.slider('probe_c', x if x is not None else DEFAULT_SEED)\n"
            "c.text('probe_d', draft.get('z', ''))\n",
            encoding="utf-8",
        )

        import tests.test_web_rueckfall as modul

        alt = modul.WURZEL
        try:
            modul.WURZEL = tmp_path
            gefunden = {f.feld: f.quelle for f in modul.funde()}
        finally:
            modul.WURZEL = alt

        assert "probe_a" in gefunden, "Der zweite `get`-Parameter wird übersehen"
        assert "probe_b" in gefunden, "Die rechte Seite eines `or` wird übersehen"
        assert "probe_c" in gefunden, "Der `else`-Zweig wird übersehen"
        assert "probe_d" not in gefunden, "Ein leerer Text ist kein erfundener Wert"

    def test_every_exception_is_still_needed(self):
        """Eine Ausnahmeliste, die nicht schrumpft, wächst.

        Ein Eintrag für einen Rückfall, den es nicht mehr gibt, verdeckt beim
        nächsten Mal einen echten Fund.
        """

        vorhanden = {fund.feld.split(".")[-1] for fund in funde()} | {fund.feld for fund in funde()}
        verwaist = sorted(set(AUSNAHMEN) - vorhanden)

        assert not verwaist, (
            f"Diese Ausnahmen betreffen keinen Rückfall mehr: {verwaist}. "
            "Sie gehören gelöscht, sonst verdecken sie beim nächsten Mal einen echten Fund."
        )


class TestDasZeichnenAendertNichts:
    """Dieselbe Zusage, aber im Verhalten statt im Syntaxbaum.

    Der Wächter oben liest den Quelltext; er kennt die Formen, die im Bestand
    vorkamen, und würde eine vierte nicht erkennen. Diese Prüfung geht den Weg
    nach, den der Browser geht: Schritt zeichnen, jedes sichtbare Feld auslesen,
    durch `apply_inputs` in den Entwurf schreiben — genau das tut `_sync`. Was
    danach anders ist, hat der Renderer erfunden.

    **Beide zusammen sind der Wächter**, nicht einer von beiden: Der eine sagt,
    *wo* im Quelltext es steht, der andere, *dass* es passiert.
    """

    def _durch_sync(self, baum, entwurf: dict) -> dict:
        """Was `_sync` aus einem gezeichneten Schritt in den Entwurf schriebe.

        **Mit `_normalise`**, denn `_sync` endet damit. Drei Bedienelemente sind
        keine Entwurfsfelder, sondern Übersetzungen: Die Szenario-Auswahl wird zu
        `scenario_mode` und `sweep_id`, der Rechenmodus zu `mock_llm` und
        `deterministic_only`, der Startpreis-Schalter zu `base_price`. Sie landen
        kurz im Entwurf und werden im selben Zug wieder entfernt.

        Ohne diesen Schritt meldete die Prüfung sie als Lecks — beim ersten
        Durchlauf genau so geschehen. Eine Nachbildung, die den halben Callback
        nachstellt, findet Fehler, die es nicht gibt.
        """

        from dashboard.web import config_editor
        from dashboard.web.config_editor import controls as c

        eintraege = []
        for knoten in _durchlaufen(baum):
            kennung = getattr(knoten, "id", None)
            if isinstance(kennung, dict) and kennung.get("type") in {c.CFG, c.CFG_BOOL}:
                eintraege.append((kennung, getattr(knoten, "value", None)))
        return config_editor._normalise(c.apply_inputs(dict(entwurf), eintraege))

    def test_no_step_writes_while_being_drawn(self):
        from dashboard.web.config_editor import wizard
        from dashboard.web.state import initial_draft_dict

        entwurf = initial_draft_dict()

        for index in range(len(wizard.STEPS)):
            danach = self._durch_sync(wizard.content(entwurf, index), entwurf)
            geaendert = {
                feld: (entwurf.get(feld), danach.get(feld))
                for feld in set(entwurf) | set(danach)
                if entwurf.get(feld) != danach.get(feld)
            }
            assert not geaendert, (
                f"Schritt {index + 1} schreibt beim Zeichnen in den Entwurf: "
                f"{geaendert}\n"
                "Der Wert kommt dann nicht aus einer Entscheidung, sondern aus dem "
                "Quelltext — und `touched()` meldet danach Einstellungen, die niemand "
                "vorgenommen hat."
            )

    def test_the_model_area_does_not_write_either(self):
        """Auch dort liegen Felder, und `_sync` liest sie mit."""

        from dashboard.web.pages import model_editor
        from dashboard.web.state import initial_draft_dict

        entwurf = initial_draft_dict()
        danach = self._durch_sync(model_editor.layout(entwurf), entwurf)

        geaendert = [
            feld for feld in set(entwurf) | set(danach) if entwurf.get(feld) != danach.get(feld)
        ]
        assert not geaendert, f"Der Modell-Bereich schreibt beim Zeichnen: {geaendert}"

    def test_the_seed_stays_empty(self):
        """Der Befund aus dem Audit, namentlich.

        Gemessen mit geleerter Sitzung: Allein das Anzeigen von Schritt 3 schrieb
        `seed: null → 42`.
        """

        from dashboard.web.config_editor import wizard
        from dashboard.web.state import initial_draft_dict

        entwurf = initial_draft_dict()
        assert entwurf["seed"] is None, "Der Auslieferungszustand nennt keinen Startwert"

        schritt = next(i for i, s in enumerate(wizard.STEPS) if s.key == "modus")
        danach = self._durch_sync(wizard.content(entwurf, schritt), entwurf)

        assert danach["seed"] is None, f"Der Startwert wurde erfunden: {danach['seed']}"

    def test_the_check_would_notice_a_relapse(self):
        """Ein Renderer mit Rückfall muss hier auffallen — sonst prüft die Zeile nichts."""

        from dashboard.web import components as ui
        from dashboard.web.config_editor import controls as c

        entwurf = {"rounds": None}
        rueckfall = ui.card(c.number("rounds", 40))

        danach = self._durch_sync(rueckfall, entwurf)

        assert danach["rounds"] == 40, "Die Nachbildung von `_sync` schreibt gar nichts"


def _durchlaufen(knoten):
    yield knoten
    kinder = getattr(knoten, "children", None)
    if isinstance(kinder, (list, tuple)):
        for kind in kinder:
            yield from _durchlaufen(kind)
    elif kinder is not None:
        yield from _durchlaufen(kinder)
