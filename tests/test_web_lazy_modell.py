"""P3.12: Der Modell-Bereich entsteht erst, wenn jemand ihn aufsucht (2026-09-05).

**Aus P3.9, und mit einer korrigierten Ursache.** Dort war gemessen, dass ein
Klick in der Schrittfolge rund eine Sekunde kostet und die Zeit *nicht* in den
Server-Rundläufen liegt. Die Zuschreibung — «React vergleicht den Baum aller
fünf Bereiche» — war eine Schlussfolgerung und **falsch**. Das CPU-Profil eines
Klicks sagt:

| Anteil | Zeit | Wo |
| ---: | ---: | --- |
| **71,6 %** | **1218 ms** | `dash_renderer` (Dashs eigenes JS) |
| 10,5 % | 179 ms | React-DOM |
| — | — | Plotly kommt gar nicht vor |

Darin `notifyNestedSubs`: Redux benachrichtigt bei **jeder** Callback-Antwort
alle angeschlossenen Komponenten. Die Kosten hängen an deren **Zahl**, nicht an
der Größe des sichtbaren Bereichs — und der Modell-Bereich stellte mit seinen
168 Bedienelementen **1404 der 2882 Knoten** der ganzen Anwendung, auch während
niemand hinsah.

**Gemessen am laufenden System, vorher/nachher:**

| | vorher | nachher |
| --- | ---: | ---: |
| bis der Schritt im DOM steht | 665–1426 ms | **213–487 ms** |
| längste Browser-Aufgabe | 1144 ms | **271 ms** |
| `dash_renderer` im Profil | 1218 ms | **252 ms** |
| DOM-Knoten in der Schrittfolge | 2882 | **1477** |

Damit ist das 500-ms-Kriterium von P3.9 erfüllt — **ohne** Regel 1 oder Regel 6
zu ändern.
"""

from __future__ import annotations

from dashboard.web import shell
from dashboard.web.pages import model_editor
from dashboard.web.state import initial_draft_dict


def _ids(knoten, fest: set[str], muster: set[str]) -> None:
    """Alle Kennungen unter einem Komponentenbaum einsammeln."""

    ident = getattr(knoten, "id", None)
    if isinstance(ident, str):
        fest.add(ident)
    elif isinstance(ident, dict):
        muster.add(str(ident.get("type")))

    kinder = getattr(knoten, "children", None)
    if kinder is None:
        return
    if not isinstance(kinder, list | tuple):
        kinder = [kinder]
    for kind in kinder:
        if hasattr(kind, "children") or hasattr(kind, "id"):
            _ids(kind, fest, muster)


class TestDerBereichEntstehtErstBeimAufsuchen:
    """Die Entscheidung ohne laufende App — sie ist eine eigene Funktion."""

    def test_der_rahmen_traegt_den_rumpf_nicht(self):
        """`layout()` baut nur Überschrift, Statuszeile und den leeren Wirt."""

        fest: set[str] = set()
        muster: set[str] = set()
        _ids(model_editor.layout(), fest, muster)

        assert model_editor.HOST in fest
        assert not muster, (
            f"Der Rahmen trägt selbst Bedienelemente ({sorted(muster)}) — dann "
            "liegen sie weiterhin dauernd im DOM, und der Gewinn ist weg."
        )

    def test_auf_einem_anderen_bereich_bleibt_er_leer(self):
        entwurf = initial_draft_dict()

        for pfad in ("/app/", "/app/lauf", "/app/runs", "/app/doku", "/app/doku/cib", None):
            assert model_editor.rumpf_fuer(pfad, entwurf) == [], pfad

    def test_auf_dem_eigenen_bereich_wird_er_gebaut(self):
        rumpf = model_editor.rumpf_fuer("/app/modell", initial_draft_dict())

        fest: set[str] = set()
        muster: set[str] = set()
        _ids(rumpf, fest, muster)

        assert muster, "Der Rumpf enthält keine Bedienelemente"
        assert len(muster) >= 5, f"Verdächtig wenige Kennungen: {sorted(muster)}"

    def test_ohne_entwurf_scheitert_er_nicht(self):
        """Der Callback reicht `State(STORE_ID)` durch, und der kann `None` sein."""

        assert model_editor.rumpf_fuer("/app/modell", None) is not None

    def test_die_adresse_steht_an_einer_stelle(self):
        """`ROUTE` gegen `shell.ROUTES` — sonst baut sich der Bereich nach einer
        Umbenennung lautlos nie mehr auf."""

        assert model_editor.ROUTE in {route for route, _ in shell.ROUTES}
        assert shell.active_route(f"/app/{model_editor.ROUTE}") == model_editor.ROUTE


class TestRegel6IstNichtBeruehrt:
    """**Die tragende Zusage dieses Pakets**, und sie ist strukturell.

    Regel 6 sagt: Ein Eingang, den es nicht gibt, legt den ganzen Callback lahm —
    deshalb wird bedingt Sichtbares ausgeblendet statt weggelassen. Hier wird es
    trotzdem weggelassen, und das ist nur erlaubt, weil der Rumpf **keine
    einzige feste ID** trägt: Alle Kennungen darin sind Muster, und ein
    Muster-Eingang mit `ALL` verträgt null Treffer von Haus aus.

    Wer hier eine Komponente mit fester ID einbaut, an der ein Callback hängt,
    nimmt diesen Callback mit aus dem DOM — und *dieser* Test sagt es ihm,
    bevor es jemand im Browser merkt.
    """

    def test_der_rumpf_traegt_keine_feste_id(self):
        fest: set[str] = set()
        muster: set[str] = set()
        _ids(model_editor.rumpf_fuer("/app/modell", initial_draft_dict()), fest, muster)

        assert not fest, (
            f"Der Modell-Rumpf trägt feste Kennungen: {sorted(fest)}.\n"
            "Er wird beim Verlassen des Bereichs aus dem DOM genommen — hängt ein "
            "Callback mit festem `Input` daran, führt Dash ihn gar nicht mehr aus "
            "(Regel 6, und in P1.7 hat genau das «Weiter» stillgelegt). Entweder "
            "eine Muster-Kennung nehmen oder die Komponente in den Rahmen heben, "
            "der stehen bleibt."
        )

    def test_die_statuszeile_bleibt_im_rahmen(self):
        """Sie ist der Gegenbeweis: eine feste ID, die **absichtlich** außerhalb
        des Rumpfs liegt.

        `_actions` schreibt seine Rückmeldung dorthin («Segment gelöscht»). Läge
        sie im Rumpf, wäre sie beim Verlassen weg — und der Callback, der sie
        füllt, hätte einen Ausgang, den es nicht gibt.
        """

        fest: set[str] = set()
        _ids(model_editor.layout(), fest, set())

        assert model_editor.STATUS in fest
