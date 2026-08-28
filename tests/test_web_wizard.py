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

import dataclasses

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


class TestModellUndExperimentSindZweiOrte:
    """W3.1 — der Schnitt zwischen Assistent und Modell-Editor.

    Bis hierher lagen beide in derselben Schrittfolge. Die Schritte 4 und 5
    trugen zusammen **168 Bedienelemente** und brauchten 3,0 bzw. 4,0
    Bildschirme, während die drei Entscheidungsschritte davor mit drei, fünf und
    zehn Feldern auskamen. «Schritt 5 von 8» war damit keine Ortsangabe: Der
    fünfte Schritt war das Vielfache aller anderen zusammen.

    Der wichtigste Test hier ist der zweite. Beide Bereiche liegen **gleichzeitig
    im DOM** — `app.py` blendet nur um. Stünde ein Feld in beiden, wäre das eine
    doppelte Dash-ID und damit ein Laufzeitfehler im Browser, den keine
    Testsuite ohne diesen Abgleich bemerkt.
    """

    def test_the_dense_areas_left_the_step_sequence(self, draft):
        schluessel = [s.key for s in wizard.STEPS]

        assert "rahmen" not in schluessel
        assert "nachfrage" not in schluessel
        assert schluessel == ["szenario", "umfang", "modus", "ablage", "technik", "start"]

    def test_no_field_is_rendered_in_both_places(self, draft):
        """Beide Bereiche liegen gleichzeitig im DOM — ein Feld darf nur in einem stehen."""

        from dashboard.web.pages import model_editor

        im_modell = _fields(model_editor.layout(draft))
        in_schritten = set()
        for index in range(len(wizard.STEPS)):
            in_schritten |= _fields(wizard.content(draft, index))

        doppelt = im_modell & in_schritten
        assert not doppelt, (
            f"Diese Felder stehen im Modell-Editor **und** in der Schrittfolge: "
            f"{sorted(doppelt)}\nEine doppelt vergebene Dash-ID ist ein "
            "Laufzeitfehler im Browser."
        )

    def test_the_model_area_actually_carries_them(self, draft):
        """Und sie sind nicht verschwunden, sondern umgezogen."""

        from dashboard.web.pages import model_editor

        felder = _fields(model_editor.layout(draft))

        assert any(f.startswith("factor_states.") for f in felder), "Die Faktorlage fehlt"
        assert any(f.startswith("property_edits.") for f in felder), "Die Systemgrößen fehlen"
        assert any(f.startswith("population_edits.") for f in felder), "Die Bevölkerung fehlt"
        assert any(f.startswith("market_feedback_edit.") for f in felder), "Die Preisbildung fehlt"

    def test_the_model_area_survives_a_broken_config(self, draft):
        """Eine kaputte Config ist ein Befund, kein leerer Bereich."""

        from dashboard.web.pages import model_editor

        kaputt = dict(draft)
        kaputt["properties_file"] = "gibt-es-nicht.json"

        gerendert = str(model_editor.layout(kaputt))

        assert gerendert
        assert "Traceback" not in gerendert


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


class TestDieSchrittlisteBehauptetNichts:
    """W2.1 — ein Haken nur für Schritte, die wirklich offen waren.

    Der gemessene Ausgangspunkt: Ein Klick auf «Szenario-Vergleich starten»
    führt auf Schritt 8, und die Liste zeigte danach

        ["done","done","done","done","done","done","done","current"]

    also sieben Häkchen für sieben Schritte, die nie auf dem Schirm standen.
    Der Zustand hing allein an der Position. Ein Fortschrittsanzeiger, der
    Übersprungenes als Erledigt ausweist, ist schlechter als keiner: Er nimmt
    genau die Information weg, für die er da ist.
    """

    def _zustaende(self, current, besucht):
        baum = wizard.rail(current, set(besucht))
        return [
            item.className.replace("af-step af-step--", "")
            for item in _walk(baum)
            if isinstance(getattr(item, "id", None), dict) and item.id.get("type") == wizard.JUMP
        ]

    def test_a_jump_to_the_end_marks_nothing_as_done(self):
        """Der Befund selbst, als Zeile."""

        zustaende = self._zustaende(wizard.FINAL, {wizard.FINAL})

        assert (
            "besucht" not in zustaende
        ), f"Nach einem Sprung ans Ende gilt etwas als besucht: {zustaende}"
        assert zustaende[wizard.FINAL] == "current"
        assert set(zustaende[: wizard.FINAL]) == {"uebersprungen"}

    def test_walking_through_leaves_real_marks(self):
        """Wer die Schritte durchgeht, sieht seinen Weg."""

        zustaende = self._zustaende(3, {0, 1, 2, 3})

        assert zustaende[:3] == ["besucht"] * 3
        assert zustaende[3] == "current"
        assert set(zustaende[4:]) == {"offen"}

    def test_skipped_and_upcoming_are_told_apart(self):
        """«Noch nicht dran» und «übergangen» sehen verschieden aus.

        Beides als «offen» zu zeigen wäre nicht falsch, aber es beantwortet die
        Frage nicht, die man auf Schritt 8 hat: *Habe ich etwas übergangen?*
        """

        # Bewusst nicht der letzte Schritt: Danach muss noch etwas kommen,
        # sonst prueft der Fall nur die Haelfte. Die Zahl ist deshalb aus
        # `STEPS` abgeleitet und nicht hingeschrieben -- W3.1 hat die
        # Schrittfolge schon einmal von acht auf sechs gekuerzt.
        offen = wizard.FINAL - 1
        zustaende = self._zustaende(offen, {0, offen})

        assert zustaende[0] == "besucht"
        assert zustaende[1:offen] == ["uebersprungen"] * (offen - 1)
        assert zustaende[offen] == "current"
        assert set(zustaende[offen + 1 :]) == {"offen"}

    def test_the_open_step_counts_as_seen_without_being_recorded(self):
        """Der offene Schritt braucht keinen Eintrag im Speicher.

        Sonst müsste jeder Schreiber daran denken, und ein vergessener Fall
        hieße, dass ein gerade betrachteter Schritt als übersprungen dasteht.
        """

        assert wizard._besucht_aus([], 4) == {4}
        assert wizard._besucht_aus([1, 2], 4) == {1, 2, 4}
        assert wizard._besucht_aus(None, None) == set()

    def test_the_rail_says_how_many_were_skipped(self):
        """Und die Zahl steht darunter, wenn es etwas zu sagen gibt."""

        text = str(wizard.rail(wizard.FINAL, {wizard.FINAL}))
        assert f"{wizard.FINAL} übersprungen" in text

        sauber = str(wizard.rail(0, {0}))
        assert "übersprungen" not in sauber, (
            "Ohne übersprungene Schritte gehört die Zeile weg — sonst liest sie "
            "nach dem zweiten Mal niemand mehr."
        )

    def test_the_current_step_is_marked_for_screen_readers(self):
        """`aria-current="step"` — bisher steckte der Zustand nur in der Farbe.

        Ein Vorgriff auf W5.3, aber er gehört hierher: Diese Funktion vergibt
        gerade die Zustände, und ihn später nachzurüsten hieße, dieselbe Stelle
        ein zweites Mal aufzuschlagen.
        """

        aria = [
            item.to_plotly_json()["props"].get("aria-current")
            for item in _walk(wizard.rail(2, {0, 1, 2}))
            if isinstance(getattr(item, "id", None), dict) and item.id.get("type") == wizard.JUMP
        ]

        assert aria.count("step") == 1, f"Genau ein Schritt ist der offene: {aria}"
        assert aria[2] == "step", f"Markiert ist der falsche Schritt: {aria}"


class TestDasTorHaeltWasEsZusagt:
    """W2.2 — «Weiter» garantiert wieder etwas.

    Bis hierher prüfte die Navigation nichts: «Weiter» war nie gesperrt, «Lauf
    starten» nur während eines laufenden Laufs, und die Fehler wurden zwar
    angezeigt, hielten aber nichts auf. Man konnte durch acht Schritte laufen und
    erst beim Start erfahren, dass Schritt 2 ungültig war.

    Ein Wizard unterscheidet sich von einer Reiterleiste dadurch, dass «Weiter»
    etwas garantiert. Ohne Tor war diese Schrittfolge eine Reiterleiste mit
    zusätzlichen Klicks — und die Reiterleiste hatte P1.7 gerade abgeschafft.
    """

    def _kaputt(self, draft):
        entwurf = dict(draft)
        entwurf["rounds"] = 0  # `max_ticks muss mindestens 1 sein`, Feld `rounds`
        return entwurf

    def test_a_clean_draft_blocks_nothing(self, draft):
        weiter, start, meldung = wizard.gate(draft, 1)

        assert (weiter, start) == (False, False)
        assert meldung is None, "Ohne Befund gehört keine Meldung in die Leiste"

    def test_it_blocks_next_where_the_finding_can_be_fixed(self, draft):
        weiter, start, meldung = wizard.gate(self._kaputt(draft), wizard.FELD_SCHRITT["rounds"])

        assert weiter is True
        assert start is True
        assert meldung is not None

    def test_it_does_not_block_next_elsewhere(self, draft):
        """Sonst wäre es eine Sackgasse, keine Führung.

        Auf Schritt 1 kann man die Lauflänge nicht einstellen. «Weiter» dort zu
        sperren hieße, jemanden für einen Fehler festzuhalten, den er an dieser
        Stelle gar nicht beheben kann.
        """

        weiter, start, meldung = wizard.gate(self._kaputt(draft), 0)

        assert weiter is False, "«Weiter» sperrt in einem Schritt ohne den Befund"
        assert start is True, "«Lauf starten» muss trotzdem sperren"
        assert "Schritt 2" in str(meldung), "Die Meldung sagt nicht, wohin"

    def test_start_is_blocked_by_any_finding(self, draft):
        """Von «Prüfen & Starten» geht es nicht weiter, sondern los."""

        for schritt in range(len(wizard.STEPS)):
            _, start, _ = wizard.gate(self._kaputt(draft), schritt)
            assert start is True, f"Start ist auf Schritt {schritt + 1} offen"

    def test_the_entry_is_not_a_step(self, draft):
        """Am Einstieg gibt es weder «Weiter» noch «Starten» — also nichts zu sperren."""

        assert wizard.gate(self._kaputt(draft), wizard.ENTRY) == (False, False, None)

    def test_a_finding_without_a_field_lands_at_the_end(self):
        """Etwa eine unlesbare Konfigurationsdatei — sie hat keinen anderen Ort."""

        verteilt = wizard.blocker_je_schritt(["Konfiguration konnte nicht geladen werden: kaputt"])

        assert list(verteilt) == [wizard.SCHRITT_OHNE_FELD]

    def test_the_field_to_step_table_matches_what_the_steps_render(self, draft):
        """**Die Tabelle wird nicht geglaubt, sondern geprüft.**

        `FELD_SCHRITT` sagt, in welchem Schritt ein beanstandetes Feld
        eingestellt wird. Eine handgepflegte Zuordnung ist genau die Sorte
        Tabelle, die P1.1 im Dashboard abgelehnt hat — sie bricht still, sobald
        jemand ein Feld in einen anderen Schritt verschiebt.

        Hier wird sie gegen die Wirklichkeit gehalten: Jeder Schritt wird
        gerendert, seine Felder ausgelesen, und die Zeile muss stimmen.
        """

        tatsaechlich = {
            index: _fields(wizard.content(draft, index)) for index in range(len(wizard.STEPS))
        }

        falsch = []
        for feld, schritt in sorted(wizard.FELD_SCHRITT.items()):
            wo = [i for i, felder in tatsaechlich.items() if feld in felder]
            if wo != [schritt]:
                falsch.append(
                    f"  `{feld}`: Tabelle sagt Schritt {schritt + 1}, gerendert in "
                    f"{[i + 1 for i in wo] or 'keinem Schritt'}"
                )

        assert not falsch, (
            "`FELD_SCHRITT` stimmt nicht mehr mit den Schritten überein:\n"
            + "\n".join(falsch)
            + "\n\nSolange sie falsch ist, sperrt «Weiter» im falschen Schritt — "
            "oder gar nicht."
        )

    def test_every_field_validation_can_flag_is_in_the_table(self):
        """Und umgekehrt: kein Befund, der keinen Schritt findet.

        Ein Feld, das die Prüfung beanstanden kann und das die Tabelle nicht
        kennt, landet stillschweigend auf «Prüfen & Starten». Das ist der
        richtige Notnagel für Befunde **ohne** Feld — für eines **mit** Feld ist
        es eine verpasste Führung.
        """

        import re
        from pathlib import Path

        quelle = Path("src/validation.py").read_text(encoding="utf-8")
        vergeben = set(re.findall(r'issue\(\s*(?:f?"[^"]*"\s*)+,\s*"([a-z_.]+)"', quelle))
        vergeben |= set(re.findall(r'^\s*"([a-z_.]+)",\s*$', quelle, re.M))

        # `tick_unit` und Konsorten sind Konstanten im Modul, keine Feldnamen —
        # gezählt wird nur, was auch ein Draft-Feld ist.
        from dashboard.config_catalog import ConfigDraft

        felder = {f.name for f in dataclasses.fields(ConfigDraft)}
        beanstandbar = {name for name in vergeben if name in felder}

        fehlend = sorted(beanstandbar - set(wizard.FELD_SCHRITT))
        assert not fehlend, (
            f"Diese Felder kann die Prüfung beanstanden, aber `FELD_SCHRITT` kennt "
            f"sie nicht: {fehlend}. Ihr Befund landet dann auf «Prüfen & Starten», "
            "statt in dem Schritt, in dem man ihn beheben kann."
        )


class TestZurueckFuehrtDorthinWoManWar:
    """W2.3 — «Zurück» folgt einem Verlauf statt einer Subtraktion.

    `aktuell - 1` stimmt für den geraden Weg durch die Schritte und für keinen
    anderen. Wer über «Szenario-Vergleich starten» auf Schritt 8 kam, landete
    mit einem Klick in Schritt 7 «Technik» — in Feineinstellungen zum
    Sprachmodell, die er nie sehen wollte und die auf seinem Pfad ohnehin nicht
    gelten. Wer über die Liste von Schritt 1 auf 7 sprang, landete auf 6.
    """

    def _navigate(self, monkeypatch, ausgeloest):
        return _navigate_callback(monkeypatch, ausgeloest)

    def test_the_comparison_leads_back_to_the_entry(self, monkeypatch, draft):
        """Der Befund selbst: Schritt 8, betreten über den Einstieg."""

        navigate = self._navigate(monkeypatch, wizard.BACK)

        schritt, _e, _b, verlauf = navigate(
            *[None] * 6, None, wizard.FINAL, draft, [], [wizard.ENTRY]
        )

        assert schritt is wizard.ENTRY, "«Zurück» führt in einen Schritt, in dem man nie war"
        assert verlauf == []

    def test_a_jump_is_undone_by_back(self, monkeypatch, draft):
        """Von 1 auf 7 gesprungen, «Zurück» führt auf 1 — nicht auf 6."""

        navigate = self._navigate(monkeypatch, wizard.BACK)

        schritt, _e, _b, verlauf = navigate(*[None] * 6, None, 6, draft, [], [wizard.ENTRY, 0])

        assert schritt == 0
        assert verlauf == [wizard.ENTRY]

    def test_the_straight_path_is_unchanged(self, monkeypatch, draft):
        """Wer der Reihe nach geht, merkt von alldem nichts.

        Der Verlauf darf den Normalfall nicht verbiegen: 1 → 2 → 3 und zurück
        muss weiterhin 2 ergeben.
        """

        weiter = self._navigate(monkeypatch, wizard.NEXT)
        schritt, _e, _b, verlauf = weiter(*[None] * 6, None, 1, draft, [], [wizard.ENTRY, 0])
        assert (schritt, verlauf) == (2, [wizard.ENTRY, 0, 1])

        zurueck = self._navigate(monkeypatch, wizard.BACK)
        schritt, _e, _b, verlauf = zurueck(*[None] * 6, None, 2, draft, [], verlauf)
        assert schritt == 1
        assert verlauf == [wizard.ENTRY, 0]

    def test_an_empty_history_lands_at_the_entry(self, monkeypatch, draft):
        """Wer keinen Weg hinter sich hat, steht am Anfang.

        Keine Notlösung, sondern die richtige Antwort — und vor allem keine
        Sackgasse: Ohne sie käme man aus einem Schritt ohne Verlauf gar nicht
        mehr heraus.
        """

        navigate = self._navigate(monkeypatch, wizard.BACK)

        schritt, _e, _b, verlauf = navigate(*[None] * 6, None, 4, draft, [], [])

        assert schritt is wizard.ENTRY
        assert verlauf == []

    def test_the_ways_start_a_fresh_history(self, monkeypatch, draft):
        """Sonst führte «Zurück» in einen Weg, den es nicht mehr gibt."""

        for weg in (wizard.WAY_NEW, wizard.WAY_SWEEP, wizard.WAY_RESUME):
            navigate = self._navigate(monkeypatch, weg)
            _s, _e, besucht, verlauf = navigate(
                *[None] * 6, None, 5, draft, [1, 2, 3], [wizard.ENTRY, 1, 2]
            )
            assert verlauf == [wizard.ENTRY], f"{weg} erbt einen alten Verlauf"
            assert besucht == [], f"{weg} erbt alte Häkchen"


class TestJederWegSagtGenauEineSache:
    def test_a_new_run_is_one_run(self, monkeypatch, draft):
        navigate = _navigate_callback(monkeypatch, wizard.WAY_NEW)

        schritt, entwurf, _besucht, _verlauf = navigate(
            *[None] * 6, None, wizard.ENTRY, {**draft, "run_all_sweeps": True}, [], []
        )

        assert schritt == 0
        assert entwurf["run_all_sweeps"] is False

    def test_the_comparison_says_all_of_them(self, monkeypatch, draft):
        navigate = _navigate_callback(monkeypatch, wizard.WAY_SWEEP)

        schritt, entwurf, _besucht, _verlauf = navigate(
            *[None] * 6, None, wizard.ENTRY, draft, [], []
        )

        assert schritt == wizard.FINAL, "Der Vergleich führt direkt zu «Prüfen & Starten»"
        assert entwurf["run_all_sweeps"] is True

    def test_carrying_on_touches_nothing(self, monkeypatch, draft):
        """«Weiterverwenden» heißt: nicht anfassen.

        Ein Schreiben hier wäre der Fehler, den P1.1 bei der Lauflänge gemacht
        hat — dieselbe Zahl an zwei Stellen.
        """

        from dash import no_update

        navigate = _navigate_callback(monkeypatch, wizard.WAY_RESUME)

        schritt, entwurf, _besucht, _verlauf = navigate(
            *[None] * 6, None, wizard.ENTRY, draft, [], []
        )

        assert schritt == wizard.FINAL
        assert entwurf is no_update

    def test_back_from_the_first_step_reaches_the_entry_again(self, monkeypatch, draft):
        """Sonst wäre die Schrittfolge eine Sackgasse.

        Vor der Korrektur war «Zurück» auf Schritt 1 abgeschaltet und
        unsichtbar; man kam nur über einen Neuladen zurück zum Einstieg.
        """

        navigate = _navigate_callback(monkeypatch, wizard.BACK)

        schritt, _entwurf, _besucht, _verlauf = navigate(
            *[None] * 6, None, 0, draft, [], [wizard.ENTRY]
        )

        assert schritt is wizard.ENTRY
        assert not getattr(_knopf(wizard.navigation(0), wizard.BACK), "disabled", False)
