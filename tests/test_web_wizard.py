"""Die Schrittfolge des Einrichtens (P1.7-C).

Vier Zusagen, und jede ist schon einmal gebrochen worden — drei davon am
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
