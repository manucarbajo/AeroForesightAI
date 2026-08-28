"""Der Einstieg und die Schrittfolge des Einrichtens (P1.7-C).

Sechs Zusagen, und die meisten sind schon einmal gebrochen worden — mehrere am
laufenden System, bevor sie hier festgehalten wurden:

1. **Drei Entscheidungen genügen bis zum Start** (P1.1). Eine Schrittfolge, die
   acht Stationen erzwingt, wäre ein Rückschritt. Ab dem dritten Schritt führt
   deshalb ein Weg direkt zum Schluss.
2. **Nur der offene Schritt steht im DOM.** Sonst stünden Felder doppelt, und
   eine doppelte Dash-ID ist ein Laufzeitfehler im Browser.
3. **Die Navigationsknöpfe stehen immer im DOM.** Dash führt einen Callback gar
   nicht erst aus, wenn auch nur *ein* Eingang fehlt. Am laufenden System kostete
   das die ganze Navigation: Auf Schritt 1 gab es «Direkt zum Start» nicht, also
   tat auch «Weiter» nichts, und der Zähler blieb bei «Schritt 1 von 8».
4. **Zwei Auslöser, ein Startpfad.** Der Knopf im Bedienfeld und der am Ende der
   Schrittfolge hängen am selben Callback — eine Prüfung, ein `runner.start`.
5. **Der Einstieg steht vor dem ersten Schritt.** Ohne ihn war «alle Szenarien
   nacheinander» eine Ankreuzoption hinter der Feinabstimmung des zweiten
   Schritts — vorhanden, aber unauffindbar. Seine drei Wege sind Knöpfe wie
   «Weiter» und unterliegen derselben Regel: immer im DOM, nur ausgeblendet.
6. **Jeder Weg sagt genau eine Sache — und schreibt auch nur je eine.** «Neuen
   Lauf einrichten» heißt *ein* Lauf, «Szenario-Vergleich» heißt *alle*,
   «Weiterverwenden» fasst den Entwurf nicht an. Ohne das erste Schreiben bliebe
   ein einmal gewählter Vergleich still aktiv, und man startete acht Läufe, wo
   man einen wollte.
"""

from __future__ import annotations

import pytest

from dashboard.web.config_editor import controls, wizard
from dashboard.web.state import initial_draft_dict


@pytest.fixture
def draft() -> dict:
    return initial_draft_dict()


def _walk(node):
    yield node
    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            yield from _walk(child)
    elif children is not None:
        yield from _walk(children)


def _ids(node) -> list:
    return [item.id for item in _walk(node) if getattr(item, "id", None) not in (None, "", [])]


def _fields(node) -> set[str]:
    return {
        str(item.id.get("field"))
        for item in _walk(node)
        if isinstance(getattr(item, "id", None), dict)
        and item.id.get("type") in {controls.CFG, controls.CFG_BOOL}
    }


# --- Drei Entscheidungen genuegen ------------------------------------------


class TestDreiEntscheidungenGenuegenWeiterhin:
    def test_the_shortcut_appears_once_the_three_decisions_are_made(self, draft):
        """Ab Schritt 3 führt ein Weg direkt zum Schluss."""

        versteckt = {"display": "none"}

        for schritt in range(wizard.LAST_REQUIRED):
            knopf = _knopf(wizard.navigation(schritt), wizard.SKIP)
            assert knopf.style == versteckt, f"Abkürzung schon auf Schritt {schritt + 1}"

        knopf = _knopf(wizard.navigation(wizard.LAST_REQUIRED), wizard.SKIP)
        assert knopf.style is None, "Nach den drei Entscheidungen fehlt die Abkürzung"

    def test_the_three_decisions_come_first(self):
        """Die Reihenfolge ist eine Aussage: erst entscheiden, dann feinjustieren."""

        pflicht = [step.required for step in wizard.STEPS]

        assert pflicht[: wizard.LAST_REQUIRED + 1] == [True, True, True]
        assert not any(pflicht[wizard.LAST_REQUIRED + 1 : wizard.FINAL])

    def test_the_optional_steps_say_so(self):
        """«optional» steht dran — sonst wirken sie wie Pflicht."""

        gerendert = str(wizard.rail(0))

        assert gerendert.count("optional") == sum(1 for s in wizard.STEPS if not s.required)


# --- Nur der offene Schritt steht im DOM -----------------------------------


class TestNurEinSchrittStehtImDom:
    def test_a_step_shows_only_its_own_fields(self, draft):
        """Zwei Schritte gleichzeitig hieße dieselbe Feld-ID zweimal."""

        for index in range(len(wizard.STEPS)):
            for anderer in range(len(wizard.STEPS)):
                if index == anderer:
                    continue
                gemeinsam = _fields(wizard.content(draft, index)) & _fields(
                    wizard.content(draft, anderer)
                )
                assert not gemeinsam, (
                    f"Schritt {index + 1} und {anderer + 1} zeigen dieselben Felder: "
                    f"{sorted(gemeinsam)}"
                )

    def test_no_step_renders_a_duplicate_id(self, draft):
        for index in range(len(wizard.STEPS)):
            ids = [str(i) for i in _ids(wizard.content(draft, index))]
            doppelt = {i for i in ids if ids.count(i) > 1}
            assert not doppelt, f"Schritt {index + 1} vergibt eine ID doppelt: {doppelt}"


# --- Die Knoepfe bleiben im DOM --------------------------------------------


def _knopf(baum, kennung):
    for item in _walk(baum):
        if getattr(item, "id", None) == kennung:
            return item
    raise AssertionError(f"Knopf «{kennung}» fehlt im DOM")


class TestJederKnopfBleibtImDom:
    """Dash führt einen Callback nicht aus, wenn ein Eingang fehlt.

    Deshalb werden die Knöpfe **ausgeblendet**, nicht weggelassen — dasselbe
    Muster wie bei den vier Viewport-Bereichen in `app.py`.
    """

    @pytest.mark.parametrize(
        "kennung", [wizard.BACK, wizard.NEXT, wizard.SKIP, wizard.START, wizard.SAVE]
    )
    def test_it_exists_on_every_step(self, kennung):
        for schritt in range(len(wizard.STEPS)):
            _knopf(wizard.navigation(schritt), kennung)

    def test_start_shows_up_only_at_the_end(self):
        for schritt in range(wizard.FINAL):
            assert _knopf(wizard.navigation(schritt), wizard.START).style == {"display": "none"}

        assert _knopf(wizard.navigation(wizard.FINAL), wizard.START).style is None

    def test_next_steps_aside_at_the_end(self):
        assert _knopf(wizard.navigation(wizard.FINAL), wizard.NEXT).style == {"display": "none"}
        assert _knopf(wizard.navigation(0), wizard.NEXT).style is None


# --- Der Schritt bleibt in seinen Grenzen ----------------------------------


class TestDerSchrittBleibtInSeinenGrenzen:
    @pytest.mark.parametrize(
        ("eingabe", "erwartet"), [(-5, 0), (0, 0), (3, 3), (99, wizard.FINAL), (None, 0), ("x", 0)]
    )
    def test_clamp(self, eingabe, erwartet):
        assert wizard.clamp(eingabe) == erwartet


# --- Zwei Ausloeser, ein Startpfad -----------------------------------------


def test_the_start_button_shares_the_callback_with_the_rail():
    """Ein zweiter Knopf ist kein zweiter Startpfad.

    Der Einwand aus P1.6 galt einer zweiten Prüfung und einer zweiten
    `runner.start`-Stelle. Hier hängen beide Knöpfe am selben Callback — es gibt
    weiterhin genau eine Prüfung und genau einen Start.
    """

    from dashboard.web.pages import launch as launch_page

    class _App:
        def __init__(self):
            self.eingaenge: list[list] = []

        def callback(self, *outputs, **kwargs):
            ids = [
                getattr(dep, "component_id", None)
                for dep in outputs
                if hasattr(dep, "component_id")
            ]

            def decorator(fn):
                if fn.__name__ == "_start":
                    self.eingaenge.append(ids)
                return fn

            return decorator

        def clientside_callback(self, *args, **kwargs):
            """Läuft im Browser — hier nur entgegenzunehmen."""

    app = _App()
    launch_page.register_callbacks(app)

    assert len(app.eingaenge) == 1, "Es darf genau einen Start-Callback geben"


def test_a_step_change_scrolls_back_to_the_top():
    """Nach «Weiter» steht man am Anfang der neuen Frage, nicht mittendrin.

    Die Bildlaufhöhe des vorigen Schritts bleibt sonst erhalten: Am laufenden
    System gemessen setzte ein «Zurück» aus dem 2237 px hohen vierten Schritt
    einen bei Bildlaufhöhe 1200 ab — weit unterhalb der Überschrift des
    Schritts, auf dem man gelandet war.

    Geprüft wird die **Verdrahtung**, nicht das Scrollen selbst: Das läuft im
    Browser, und ohne Browser lässt sich nur festhalten, dass der Callback
    angemeldet ist und am Schritt hängt.
    """

    class _App:
        def __init__(self):
            self.clientside: list[tuple] = []

        def callback(self, *outputs, **kwargs):
            def decorator(fn):
                return fn

            return decorator

        def clientside_callback(self, code, *deps, **kwargs):
            self.clientside.append((code, deps))

    app = _App()
    wizard.register_callbacks(app)

    assert app.clientside, "Kein clientseitiger Callback angemeldet"
    code, deps = app.clientside[0]
    assert "scrollTo" in code
    assert any(getattr(d, "component_id", None) == wizard.STEP_STORE for d in deps)


# --- Der Einstieg ----------------------------------------------------------


class TestDerEinstiegStehtVorDemErstenSchritt:
    """Drei Wege statt einer Bildlaufstrecke — und keiner davon versteckt.

    Bis P1.7-C landete man unmittelbar auf Schritt 1. Damit lag der
    Szenario-Vergleich als Kästchen hinter «Feinabstimmung» im zweiten Schritt;
    er war da, aber niemand fand ihn.
    """

    def test_the_setup_area_opens_on_the_entry(self, draft):
        from dashboard.web.pages import setup as setup_page

        baum = setup_page.layout(draft)

        assert _style(baum, wizard.ENTRY_HOST) == {}, "Der Einstieg ist nicht zu sehen"
        assert _style(baum, wizard.CONTENT_HOST) == {"display": "none"}
        assert _style(baum, wizard.RAIL) == {"display": "none"}

    def test_a_step_hides_the_entry_instead_of_dropping_it(self, draft):
        """Regel 6: Ein fehlender Eingang legt den ganzen Callback lahm.

        Die drei Wege hängen am selben Callback wie «Weiter» und «Zurück». Einen
        davon auf Schritt 3 wegzulassen nähme die ganze Navigation mit — genau
        das ist in P1.7 schon einmal passiert.
        """

        for schritt in [wizard.ENTRY, *range(len(wizard.STEPS))]:
            baum = wizard.layout(draft, schritt)
            for weg in (wizard.WAY_NEW, wizard.WAY_SWEEP, wizard.WAY_RESUME):
                _knopf(baum, weg)
            sichtbar = _style(baum, wizard.ENTRY_HOST) == {}
            assert sichtbar is (schritt is wizard.ENTRY), f"Einstieg falsch sichtbar bei {schritt}"

    def test_the_entry_offers_exactly_three_ways(self, draft):
        wege = [
            node
            for node in _walk(wizard.entry(draft))
            if "af-way" == getattr(node, "className", None)
        ]

        assert len(wege) == 3

    def test_the_entry_renders_no_input_field(self, draft):
        """Der Einstieg ist eine Weiche, kein Formular.

        Ein Feld hier stünde zusätzlich zu dem im Schritt — und dieselbe Dash-ID
        zweimal ist ein Laufzeitfehler im Browser.
        """

        assert not _fields(wizard.entry(draft))

    def test_no_duplicate_id_with_the_entry_in_the_tree(self, draft):
        for schritt in [wizard.ENTRY, 0, wizard.FINAL]:
            ids = [str(i) for i in _ids(wizard.layout(draft, schritt))]
            doppelt = {i for i in ids if ids.count(i) > 1}
            assert not doppelt, f"Doppelte ID bei Schritt {schritt}: {doppelt}"

    def test_resume_stays_shut_until_something_was_changed(self, draft):
        """«Letzte Einstellungen» darf nicht anbieten, was es nicht gibt.

        Ausgegraut statt weggelassen — der Knopf bleibt Eingang seines
        Callbacks.
        """

        assert not wizard.touched(draft)
        assert _knopf(wizard.entry(draft), wizard.WAY_RESUME).disabled

        geaendert = {**draft, "rounds": int(draft.get("rounds") or 40) + 1}

        assert wizard.touched(geaendert)
        assert not _knopf(wizard.entry(geaendert), wizard.WAY_RESUME).disabled


def _style(baum, kennung) -> dict:
    for item in _walk(baum):
        if getattr(item, "id", None) == kennung:
            return getattr(item, "style", None) or {}
    raise AssertionError(f"«{kennung}» fehlt im DOM")


# --- Jeder Weg sagt genau eine Sache ---------------------------------------


def _navigate_callback(monkeypatch, ausgeloest: str):
    """Den Navigations-Callback holen und einen Knopfdruck vortäuschen."""

    class _Ctx:
        triggered_id = ausgeloest
        triggered = [{"prop_id": f"{ausgeloest}.n_clicks", "value": 1}]

    gefangen: dict = {}

    class _App:
        def callback(self, *outputs, **kwargs):
            def decorator(fn):
                gefangen.setdefault(fn.__name__, fn)
                return fn

            return decorator

        def clientside_callback(self, *args, **kwargs):
            """Läuft im Browser."""

    wizard.register_callbacks(_App())
    monkeypatch.setattr(wizard, "ctx", _Ctx)
    return gefangen["_navigate"]


class TestJederWegSagtGenauEineSache:
    def test_a_new_run_is_one_run(self, monkeypatch, draft):
        navigate = _navigate_callback(monkeypatch, wizard.WAY_NEW)

        schritt, entwurf = navigate(
            *[None] * 6, None, wizard.ENTRY, {**draft, "run_all_sweeps": True}
        )

        assert schritt == 0
        assert entwurf["run_all_sweeps"] is False

    def test_the_comparison_says_all_of_them(self, monkeypatch, draft):
        navigate = _navigate_callback(monkeypatch, wizard.WAY_SWEEP)

        schritt, entwurf = navigate(*[None] * 6, None, wizard.ENTRY, draft)

        assert schritt == wizard.FINAL, "Der Vergleich führt direkt zu «Prüfen & Starten»"
        assert entwurf["run_all_sweeps"] is True

    def test_carrying_on_touches_nothing(self, monkeypatch, draft):
        """«Weiterverwenden» heißt: nicht anfassen.

        Ein Schreiben hier wäre der Fehler, den P1.1 bei der Lauflänge gemacht
        hat — dieselbe Zahl an zwei Stellen.
        """

        from dash import no_update

        navigate = _navigate_callback(monkeypatch, wizard.WAY_RESUME)

        schritt, entwurf = navigate(*[None] * 6, None, wizard.ENTRY, draft)

        assert schritt == wizard.FINAL
        assert entwurf is no_update

    def test_back_from_the_first_step_reaches_the_entry_again(self, monkeypatch, draft):
        """Sonst wäre die Schrittfolge eine Sackgasse.

        Vor der Korrektur war «Zurück» auf Schritt 1 abgeschaltet und
        unsichtbar; man kam nur über einen Neuladen zurück zum Einstieg.
        """

        navigate = _navigate_callback(monkeypatch, wizard.BACK)

        schritt, _ = navigate(*[None] * 6, None, 0, draft)

        assert schritt is wizard.ENTRY
        assert not getattr(_knopf(wizard.navigation(0), wizard.BACK), "disabled", False)
