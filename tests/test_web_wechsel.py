"""Ein Wechsel der Ergebnis-Ansicht lässt niemanden im Dunkeln (P7.0-U0.5).

**Der Befund (Q7 des UI/UX-Audits vom 2026-09-11):** «Animation» braucht auf
einem echten Lauf serverseitig **8,5 s** und schickt **9,1 MiB** an den Browser
(nachgemessen am 2026-09-12 an `outputs/audit_auslastung_1.0`; das Audit maß
10,5 s und 19,3 MB an einem größeren). Im Browser stand die ganze Zeit der
Inhalt der *vorigen* Ansicht unter dem bereits markierten Reiter — ohne
Ladeanzeige, ohne Meldung. Jede andere Ansicht bleibt unter 90 ms.

**Die Zusage ist ein «oder»**, so wie U0.5 sie formuliert: sichtbarer neuer
Inhalt nach unter einer Sekunde **oder** eine Ladeanzeige. Gemessen wird hier
die zweite Hälfte, und zwar strukturell statt in Millisekunden: Eine Zeitmessung
in einem Unit-Test misst die Maschinenlast mit, und auf einem kleinen Lauf war
dieselbe Ansicht 737 ms schnell — der Wächter hätte von der Größe des
Testlaufs abgehängt, was er über den Code sagen soll.

**Eine Korrektur am Audit gehört dazu**, weil sie sonst zur falschen Reparatur
führt: Es nennt `._dash-loading { display: none }` als Grund und schließt, die
Ladeanzeige sei global abgeschaltet. `._dash-loading` ist aber **nicht** die
Anzeige eines Callbacks, sondern der Platzhalter, den Dash vor dem ersten
Rendern ins HTML schreibt — das Wort «Loading...» ungestaltet im Dokumentfluss
(`dash/dash.py::_app_entry`). Ihn zu verstecken hat mit `dcc.Loading` nichts zu
tun. Gefehlt hat die Anzeige am **Wirt** des Ansichtswechsels.

**Warum sie am Wirt hängt und nicht in der Ansicht:** `dcc.Loading` zeigt sich,
solange ein Callback etwas *innerhalb* von ihm füllt. Der Wirt bleibt beim
Wechsel im Baum, die Ansicht darin wird ausgetauscht. In eine Ansicht gelegt
käme die Anzeige erst mit der Antwort, auf die sie warten soll.

**Die zweite Zusage ist die Nutzlast, und sie ist die interessantere.** Sechs
der sieben Ansichten sind auf Byte genau gleich groß, ob die Bevölkerung 100
oder 400 Personen zählt; «Animation» wächst mit (335 → 658 KiB). Das ist der
Mechanismus hinter den 9,1 MiB — sie schickt Personen, nicht Ergebnisse. Der
Wächter sucht diese Eigenschaft über **alle** Ansichten, statt die eine bekannte
aufzuzählen; «Animation» steht als benannte Ausnahme mit dem Paket daneben, das
sie auflöst.
"""

from __future__ import annotations

import importlib
import json
import pkgutil
import random
from pathlib import Path

import pytest
from dash import dcc, html
from dash._utils import to_json

from dashboard.web import components as ui
from dashboard.web import pages, theme
from dashboard.web.pages import runs as runs_page
from dashboard.web.views import animation, explorer, figures, files, narrative, overview, scenario

#: Der Wirt, in den der Reiter-Callback jede Ansicht zeichnet.
WIRT = "runs-tab-content"

ANSICHTEN = {
    "overview": overview,
    "scenario": scenario,
    "narrative": narrative,
    "animation": animation,
    "figures": figures,
    "files": files,
    "explorer": explorer,
}

#: Ansichten, deren Nutzlast **darf** mit der Bevölkerung wachsen — je Eintrag
#: der Grund und das Paket, das ihn auflöst.
#:
#: Eine Ausnahme hier ist keine Freigabe auf Dauer: `test_no_exception_is_free`
#: verlangt, dass sie noch zutrifft, damit sie nicht stehen bleibt, nachdem das
#: Paket sie erledigt hat.
WACHSEN_DARF: dict[str, str] = {}
#: Bis zum 2026-10-01 stand hier «animation»: neun animierte Diagramme über jede
#: Person und jeden Tick, 335 → 658 KiB bei vierfacher Bevölkerung. Seit P8-V11
#: zeichnet die Ansicht kein Diagramm mehr beim Öffnen, sondern jedes auf Klick,
#: und die Punktwolke nimmt eine Stichprobe — die Ausnahme ist erledigt.

#: Wie viel größer die Nutzlast bei vierfacher Bevölkerung höchstens werden
#: darf. **1,0 wäre zu scharf**: Eine Ansicht darf die Zahl der Personen
#: *nennen*, und «4000» ist drei Zeichen länger als «1000». Gemessen am
#: 2026-09-12 liegen sechs der sieben Ansichten bei exakt 1,00 und «Animation»
#: bei 1,96.
WACHSTUM_MAX = 1.02

_SPALTEN = (
    "tick,id,age,wtp_eur,environmental_awareness,substitution_readiness,price_sensitivity,"
    "income_factor,saturation_level,booked,last_booked_tick,family,business,price_sensitive,"
    "eco_conscious,frequent_flyer"
)


@pytest.fixture(scope="module", autouse=True)
def plotly_vorlagen():
    theme.register_template()


def _lauf(wurzel: Path, personen: int, ticks: int = 10) -> Path:
    """Ein Lauf mit genau `personen` Individuen je Tick — sonst überall gleich.

    Die Größe ist der **einzige** Unterschied zwischen den beiden Läufen, an
    denen die Nutzlast verglichen wird; alles andere ist Zeichen für Zeichen
    dasselbe. Nur so sagt der Vergleich etwas über die Bevölkerung.
    """

    ordner = wurzel / f"run_{personen}"
    (ordner / "timeseries").mkdir(parents=True, exist_ok=True)
    (ordner / "run_metadata.json").write_text(
        json.dumps(
            {
                "ticks_completed": ticks,
                "ticks_max": ticks,
                "total_events": 3,
                "model": "llama3.2",
                "market_enabled": True,
                "timestamp": "2026-09-07T18:25:55Z",
                "compute_mode": "llm",
            }
        ),
        encoding="utf-8",
    )
    (ordner / "tick_mechanics.json").write_text(
        json.dumps(
            {
                "ticks": [
                    {"tick": t, "booking_rate": 0.4, "ticket_price": 100.0 + t}
                    for t in range(1, ticks + 1)
                ]
            }
        ),
        encoding="utf-8",
    )
    (ordner / "price_history.json").write_text(
        json.dumps([{"round_number": t, "price": 100.0 + t} for t in range(1, ticks + 1)]),
        encoding="utf-8",
    )
    (ordner / "final_narrative.md").write_text("# Bericht\n\nInhalt.", encoding="utf-8")
    (ordner / "timeseries" / "properties.csv").write_text(
        "tick,carbon_tax_level,income_index\n"
        + "".join(f"{t},50,1.0\n" for t in range(1, ticks + 1)),
        encoding="utf-8",
    )
    (ordner / "timeseries" / "factors.csv").write_text(
        "tick,F1,F2\n" + "".join(f"{t},F1.1,F2.1\n" for t in range(1, ticks + 1)),
        encoding="utf-8",
    )
    rng = random.Random(42)
    zeilen = [_SPALTEN]
    for tick in range(1, ticks + 1):
        for person in range(personen):
            zeilen.append(
                f"{tick},{person},{30 + person % 40},{100 + person % 80}.0,"
                f"{rng.random():.3f},0.2,0.5,1.0,0.0,False,None,False,False,False,False,False"
            )
    (ordner / "individuals_history.csv").write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    return ordner


@pytest.fixture(scope="module")
def klein(tmp_path_factory) -> Path:
    return _lauf(tmp_path_factory.mktemp("klein"), personen=100)


@pytest.fixture(scope="module")
def gross(tmp_path_factory) -> Path:
    return _lauf(tmp_path_factory.mktemp("gross"), personen=400)


def _kib(ansicht, lauf: Path) -> float:
    return len(to_json(ansicht.render(lauf, lauf.name))) / 1024


# --- Die Ladeanzeige am Wirt -------------------------------------------------


def _finde(knoten, kennung: str, vorfahren: tuple = ()) -> tuple | None:
    """Der Pfad der Vorfahren bis zum Knoten mit dieser Kennung — oder `None`."""

    if isinstance(knoten, (list, tuple)):
        for kind in knoten:
            treffer = _finde(kind, kennung, vorfahren)
            if treffer is not None:
                return treffer
        return None
    if not hasattr(knoten, "children") and not hasattr(knoten, "id"):
        return None
    if getattr(knoten, "id", None) == kennung:
        return vorfahren
    return _finde(getattr(knoten, "children", None), kennung, vorfahren + (knoten,))


class TestDerWechselHatEineLadeanzeige:
    def test_the_view_host_sits_inside_a_loading_indicator(self):
        pfad = _finde(runs_page.layout(), WIRT)

        assert pfad is not None, f"«{WIRT}» ist nicht im Baum — der Wächter sieht nichts"
        assert any(isinstance(knoten, dcc.Loading) for knoten in pfad), (
            f"«{WIRT}» liegt in keiner `dcc.Loading`. Beim Wechsel der Ansicht stand "
            "damit bis zu acht Sekunden der Inhalt der vorigen unter dem bereits "
            "markierten Reiter."
        )

    def test_the_indicator_does_not_freeze_one_theme(self):
        """Die Farbe kommt aus dem Stylesheet, nicht vom Aufruf.

        `runs.layout()` läuft **einmal** beim Start. Ein `color=` von dort wäre
        für immer die Farbe des Startdesigns — im dunklen Modus das dunkle Navy
        (`#1E3A5F`) auf dunklem Grund, während das dunkle Design `#94b8d7`
        trägt. Die drei Ansichten mit eigener Anzeige dürfen `color=` setzen:
        Sie werden bei jedem Themenwechsel neu gezeichnet.
        """

        pfad = _finde(runs_page.layout(), WIRT)
        anzeige = next(k for k in pfad if isinstance(k, dcc.Loading))

        assert getattr(anzeige, "color", None) is None, (
            "Die Ladeanzeige am Wirt setzt eine Farbe am Aufruf. Sie wird nie neu "
            "gezeichnet und trägt damit für immer das Startdesign."
        )
        assert "af-ladeanzeige" in (getattr(anzeige, "className", "") or ""), (
            "Ohne die Klasse färbt Dash den Punkt mit seinem eigenen Blau — ein "
            "Farbwert, der aus keinem Token kommt (Regel 4)."
        )

    def test_the_guard_would_notice_a_relapse(self):
        """Ohne Wirt in einer Anzeige muss die Prüfung anschlagen."""

        ohne = html.Div([html.Div("Reiter"), html.Div("Inhalt", id=WIRT)])
        mit = html.Div(dcc.Loading(html.Div("Inhalt", id=WIRT)))

        assert not any(isinstance(k, dcc.Loading) for k in _finde(ohne, WIRT))
        assert any(isinstance(k, dcc.Loading) for k in _finde(mit, WIRT))


def _neu_gebaute_bereiche() -> list:
    """Jedes Seitenmodul, dessen Rumpf erst beim Aufsuchen entsteht: `HOST` und `rumpf_fuer`.

    Gesucht statt aufgezählt — ein Bereich, der morgen dasselbe Muster bekommt,
    fällt ohne Eintrag unter die Zusage (P7.3-U3.5).
    """

    gefunden = []
    for eintrag in pkgutil.iter_modules(pages.__path__):
        modul = importlib.import_module(f"{pages.__name__}.{eintrag.name}")
        if hasattr(modul, "HOST") and hasattr(modul, "rumpf_fuer"):
            gefunden.append(modul)
    return gefunden


#: Wie viele neu gebaute Bereiche die Suche mindestens findet — gegen die eigene
#: Blindheit. Gemessen am 2026-09-14: zwei (Modell, Musterseite).
NEU_GEBAUT_MIN = 2


class TestJederNeuGebauteBereichWartetMitDerAnzeige:
    """P7.3-U3.5: Eine Ladeanzeige erscheint nach 300 ms für jeden Bereich, der neu gebaut wird.

    Das Audit schloss aus `._dash-loading { display: none }`, die Ladeanzeige sei
    global abgeschaltet; das war der Platzhalter vor dem ersten Rendern (U0.5). Offen
    blieb, was das Paket wirklich verlangt: **jeder** Bereich, der beim Aufsuchen neu
    entsteht, nicht nur die Ergebnis-Ansicht — und die zeigte ihre Anzeige sofort,
    auch bei Ansichten, die in 90 ms stehen.
    """

    def test_the_search_finds_the_rebuilt_areas(self):
        assert len(_neu_gebaute_bereiche()) >= NEU_GEBAUT_MIN

    @pytest.mark.parametrize("modul", _neu_gebaute_bereiche(), ids=lambda m: m.__name__)
    def test_every_rebuilt_area_sits_in_a_delayed_indicator(self, modul):
        pfad = _finde(modul.layout(), modul.HOST)

        assert pfad is not None, f"«{modul.HOST}» ist nicht im Baum von {modul.__name__}"
        anzeige = next((k for k in pfad if isinstance(k, dcc.Loading)), None)
        assert anzeige is not None, f"«{modul.HOST}» liegt in keiner `dcc.Loading`"
        assert getattr(anzeige, "delay_show", None) == ui.LADEANZEIGE_NACH_MS
        assert "af-ladeanzeige" in (getattr(anzeige, "className", "") or "")
        assert getattr(anzeige, "color", None) is None

    def test_the_result_views_wait_as_well(self):
        pfad = _finde(runs_page.layout(), WIRT)
        anzeige = next(k for k in pfad if isinstance(k, dcc.Loading))

        assert getattr(anzeige, "delay_show", None) == ui.LADEANZEIGE_NACH_MS


# --- Die Nutzlast ------------------------------------------------------------


class TestKeineAnsichtWaechstMitDerBevoelkerung:
    """**Die Zusage, die den Befund wirklich beschreibt.**

    «Animation» ist nicht langsam, weil sie viel rechnet, sondern weil sie die
    Personen selbst überträgt. Ein Deckel in KiB wäre an den Testlauf gebunden;
    das **Wachstum** ist eine Eigenschaft des Codes.
    """

    @pytest.mark.parametrize("name", sorted(ANSICHTEN))
    def test_the_payload_does_not_grow_with_the_population(self, name, klein, gross):
        ansicht = ANSICHTEN[name]
        wenig, viel = _kib(ansicht, klein), _kib(ansicht, gross)
        wachstum = viel / wenig if wenig else 1.0

        if name in WACHSEN_DARF:
            pytest.skip(f"benannte Ausnahme: {WACHSEN_DARF[name]}")

        assert wachstum <= WACHSTUM_MAX, (
            f"«{name}» wächst mit der Bevölkerung: {wenig:.1f} KiB bei 100 Personen, "
            f"{viel:.1f} KiB bei 400 (Faktor {wachstum:.2f}, erlaubt {WACHSTUM_MAX}). "
            "Eine Ansicht zeigt Ergebnisse, keine Personen — und was über die Leitung "
            "geht, wartet der Betrachter ab."
        )

    def test_no_exception_is_free(self, klein, gross):
        """Eine Ausnahme, die nicht mehr zutrifft, gehört gelöscht.

        Sonst bleibt sie stehen, nachdem P7.6-U6.2 sie erledigt hat, und deckt
        beim nächsten Mal einen echten Rückfall.
        """

        unnoetig = []
        for name in WACHSEN_DARF:
            wenig, viel = _kib(ANSICHTEN[name], klein), _kib(ANSICHTEN[name], gross)
            if wenig and viel / wenig <= WACHSTUM_MAX:
                unnoetig.append(f"{name}: {wenig:.1f} → {viel:.1f} KiB")

        assert not unnoetig, (
            "Diese Ansichten wachsen nicht mehr mit der Bevölkerung — die Ausnahme "
            "ist zu löschen:\n  " + "\n  ".join(unnoetig)
        )

    def test_the_measurement_sees_a_difference_at_all(self, klein, gross):
        """**Ein Wächter, der überall 1,00 misst, könnte auch blind sein.**

        Gemessen wird, dass die beiden Läufe wirklich verschieden groß sind —
        sonst verglichen alle Zusagen oben denselben Lauf mit sich selbst und
        wären für immer grün.
        """

        wenig = (klein / "individuals_history.csv").stat().st_size
        viel = (gross / "individuals_history.csv").stat().st_size

        assert viel > wenig * 3, f"Die Testläufe unterscheiden sich kaum: {wenig} / {viel} Bytes"

        # Seit P8-V11 wächst keine Ansicht mehr; die Punktwolke **ohne** Stichprobe
        # tut es weiterhin — an ihr zeigt sich, dass die Messung Wachstum sieht.
        def _ungekuerzt(lauf: Path) -> float:
            return len(to_json(animation._population_figure(animation.load_history(lauf)))) / 1024

        assert _ungekuerzt(gross) > _ungekuerzt(klein) * 1.5, (
            "Eine Figur über alle Personen wächst in dieser Messung nicht — "
            "dann misst der Wächter etwas anderes als die Bevölkerung."
        )
