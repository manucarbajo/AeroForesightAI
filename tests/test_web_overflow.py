"""Was nur ein Browser messen kann: die Box und der Schirm (P1.7-D, P1.9-W0.1).

Zwei Fragen, ein Browser. **Tritt etwas aus seinem Kasten?** — das war P1.7-D.
**Passt ein Schritt auf einen Bildschirm?** — das ist W0.1 aus P1.9, und es ist
die Frage, die P1.7 zugesagt und niemand gemessen hat.

Beide brauchen denselben teuren Aufbau (echter Server, echter Browser, zwei
Breiten) und stehen deshalb in einer Datei. Der Dateiname bleibt
`test_web_overflow.py`, obwohl er jetzt zu eng ist: Er steht in `CLAUDE.md`, in
`.github/workflows/tests.yml` und in mehreren Absätzen des Projektplans — ein
Umbenennen wäre eine Textänderung an sechs Stellen für null Erkenntnisgewinn.

--- Teil 1: Nichts tritt aus seiner Box (P1.7-D) ---------------------------


Stufe D hat den Überlauf an der Ursache behoben: `min-width: 0` auf den Kindern
jedes Rasters, `overflow-wrap: anywhere` auf den Wertklassen, eine Textfassung
für `metric_tile`. Geprüft wurde danach **von Hand im Browser**, Bereich für
Bereich. Das war der ehrliche Stand, aber kein Wächter: Der nächste Rückfall
fällt erst beim nächsten Blick auf.

Dieser Durchlauf öffnet jede Ansicht in einem echten Browser und meldet, was
seinen Kasten verlässt. **Pixel kann eine Testsuite ohne Browser nicht messen**
— deshalb hängt er an Playwright, und deshalb ist Playwright ein eigenes Extra
(`pip install -e ".[ui]"` plus `playwright install chromium`). Fehlt eines von
beidem, überspringt sich der Test; die CI bleibt ohne Browser grün.

**Der Detektor ist die eigentliche Arbeit.** Die Gegenprobe zu P1.7 (P1.8) hat
einen ersten Anlauf mit **41, 32 und 2** Befunden zurückgewiesen — alle drei
Zahlen waren falsch, weil ein naives `scrollWidth > clientWidth` Phantome zählt:

1. **Abgeschnittenes.** Wo `overflow-x` nicht `visible` ist, schneidet der
   Browser sauber ab oder lässt scrollen. Beides ist eine Entscheidung, kein
   Überlauf — für breite Tabellen und Codeblöcke ist es sogar die vorgeschriebene
   Lösung.
2. **Nicht Gezeichnetes.** Der Inhalt eines zugeklappten `<details>` hat Maße,
   aber keine Fläche. Er kann nirgendwo herausragen, weil er nirgendwo steht.
3. **Absichtlich Überstehendes.** Ein Tooltip an einem 16 px breiten
   Reglerknopf ist definitionsgemäß breiter als sein Knopf. Alles, was aus dem
   Fluss genommen ist (`position: absolute` / `fixed`), ragt aus seinem
   Bezugsrahmen heraus, weil es das soll.
4. **SVG.** Ein viertes Phantom, gefunden beim ersten scharfen Durchlauf dieses
   Wächters: In den Plotly-Diagrammen meldete jede Achsenbeschriftung 4 bis 27
   px Überlauf. `clientWidth` ist für SVG-Elemente schlicht nicht definiert und
   liefert 0 — die Differenz war also die Textbreite selbst. SVG hat sein
   eigenes Zeichenmodell samt `viewBox`; was darin zu breit ist, findet man
   nicht mit den Maßen des Kastenmodells.

**`scrollWidth` selbst ist das fünfte Phantom** — der Fund des ersten scharfen
Durchlaufs. Ausnahme 3 auf den *Kasten* anzuwenden genügt nicht: Ein
ausgeschwebtes Kind zählt weiterhin in den `scrollWidth` seines Vorfahren. Dashs
eigenes Dropdown legt einen 241 px breiten, unsichtbaren `input` als Fokusziel in
einen 96 px breiten Wrapper; die Zeitleiste meldete daraufhin 145 px Überlauf,
obwohl nichts zu sehen war und nichts verrutschte. Gemessen wird deshalb nicht
`scrollWidth`, sondern die **rechte Kante dessen, was wirklich im Fluss steht** —
die Kästen der Kinder und die Zeilen der Textknoten. Eine Ausnahme, die nur den
Kasten kennt und nicht seine Nachkommen, ist keine.

Was übrig bleibt, ist die Frage, um die es geht: Steht ein **gezeichneter**
Kasten **im Fluss** mit Inhalt darin, der über seine rechte Kante hinausläuft,
und schneidet ihn niemand ab? Dann schiebt er seinen Nachbarn beiseite — und
genau so trat «Standard-Ausgangslage» aus seiner Kachel.

Dazu die grobe Probe, die keine Ausnahme kennt: Die Seite selbst darf sich nicht
waagerecht schieben lassen.

--- Teil 2: Jeder Schritt passt auf einen Schirm (P1.9-W0.1) ---------------

P1.7 hat zugesagt: **eine Frage auf dem Schirm.** Abgenommen wurde: *nur der
offene Schritt steht im DOM*. Das ist erfüllt — und misst Knoten statt
Bildschirme. Gemessen sind es bei 1280 px zwischen **1,01 und 3,96** Schirmen
je Schritt; keiner von acht kommt ohne Scrollen aus.

**Es ist derselbe Fehler wie in P1.6, ein Paket später.** Dort war das
Kriterium «höchstens drei Entscheidungen» grün, während der Start-Knopf 6,1
Bildschirme tief lag. Hier ist «nur ein Schritt im DOM» grün, während der
Schritt vier Schirme braucht. Zweimal derselbe Fehlertyp ist kein Zufall,
sondern eine Lücke im Verfahren — daraus ist Regel 7 des Commit-Regelwerks
geworden: *Eine Zusage kommt mit ihrer Messung, nicht mit ihrer Zählung.*
Dieser Teil ist diese Messung.

**Der Deckel ist eine Sperrklinke, kein Ziel.** Er hält den Ist-Stand fest und
schlägt an, sobald ein Schritt **wächst**. Er schlägt aber auch an, wenn ein
Schritt deutlich **schrumpft** und der Deckel nicht mitgezogen wird — sonst
stünde nach dem Umbau ein Deckel von 3,96 über einem Schritt, der 0,9 braucht,
und der Wächter wäre wieder aus dem falschen Grund grün. Das Ziel steht als
`ZIEL` daneben; W3.5 setzt den Deckel darauf.
"""

from __future__ import annotations

import re
import socket
import threading

import pytest

pytest.importorskip(
    "playwright.sync_api",
    reason='Der Überlauf-Wächter braucht Playwright: pip install -e ".[ui]"',
)

from playwright.sync_api import Error as PlaywrightError  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

#: Die Breiten, bei denen gemessen wird. 1280 ist die Breite, in der P1.6 und
#: P1.7 ihre Befunde erhoben haben; 1024 ist der Punkt, an dem die Schubladen
#: greifen und die Zonen am engsten sind.
BREITEN = [1280, 1024]

HOEHE = 800

#: Wie lange auf einen Callback gewartet wird, bevor gemessen wird. Dash
#: zeichnet einen Bereich nach dem Laden nach; ohne die Wartezeit misst man den
#: leeren Wirt.
RUHE_MS = 900


# --- Der Server ------------------------------------------------------------


def _freier_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.fixture(scope="module")
def basis_url():
    """Die Dash-App in einem Thread — dieselbe, die `python -m dashboard.web.app` startet.

    Bewusst der echte Server und keine Attrappe: Ein Überlauf entsteht aus
    Stylesheet, Schriftmetrik und tatsächlichem Inhalt. Was hier nicht wirklich
    gezeichnet wird, kann auch nicht wirklich herausragen.
    """

    from werkzeug.serving import make_server

    from dashboard.web.app import app

    port = _freier_port()
    server = make_server("127.0.0.1", port, app.server, threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}/app/"
    finally:
        server.shutdown()
        thread.join(timeout=5)


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        try:
            instanz = p.chromium.launch()
        except PlaywrightError as exc:  # kein Browser installiert
            pytest.skip(f"Kein Chromium für Playwright: {exc} — `playwright install chromium`")
        try:
            yield instanz
        finally:
            instanz.close()


# --- Der Detektor ----------------------------------------------------------

#: Läuft im Browser. Gibt die Kästen zurück, deren Inhalt breiter ist als sie
#: selbst — nach Abzug der drei Sorten Phantome aus dem Modul-Docstring.
_DETEKTOR = """
() => {
  const befunde = [];
  const gezeichnet = (el) =>
    el.checkVisibility && el.checkVisibility({ checkVisibilityCSS: true });
  const imFluss = (el) => {
    const p = getComputedStyle(el).position;
    return p !== 'absolute' && p !== 'fixed';
  };

  // Die rechte Kante dessen, was wirklich im Fluss dieses Kastens steht:
  // die Kaesten der Kinder und die Zeilen der Textknoten. **Nicht**
  // `scrollWidth` -- der zaehlt ausgeschwebte Nachkommen mit.
  const rechteKante = (el) => {
    let rechts = -Infinity;
    const bereich = document.createRange();
    for (const knoten of el.childNodes) {
      if (knoten.nodeType === Node.TEXT_NODE) {
        if (!knoten.textContent.trim()) continue;
        bereich.selectNodeContents(knoten);
        for (const zeile of bereich.getClientRects()) rechts = Math.max(rechts, zeile.right);
      } else if (knoten.nodeType === Node.ELEMENT_NODE) {
        if (!gezeichnet(knoten) || !imFluss(knoten)) continue;
        rechts = Math.max(rechts, knoten.getBoundingClientRect().right);
      }
    }
    return rechts;
  };

  for (const el of document.querySelectorAll('body *')) {
    // (2) Nicht Gezeichnetes: zugeklappte <details>, display:none, Schubladen.
    if (!gezeichnet(el)) continue;
    // (4) SVG hat sein eigenes Zeichenmodell; das Kastenmodell passt nicht.
    if (!(el instanceof HTMLElement)) continue;
    const stil = getComputedStyle(el);
    // (1) Abgeschnittenes und Scrollbares: eine Entscheidung, kein Ueberlauf.
    if (stil.overflowX !== 'visible') continue;
    // (3) Absichtlich Ueberstehendes: Tooltips, Menues, Fortschrittsfenster.
    if (!imFluss(el)) continue;
    const rechteck = el.getBoundingClientRect();
    if (rechteck.width === 0 || rechteck.height === 0) continue;

    // Grenze ist die Innenkante des Rahmens. Wer bis in die Polsterung laeuft,
    // sieht noch nicht falsch aus; wer darueber hinauslaeuft, schiebt.
    const grenze = rechteck.right - parseFloat(stil.borderRightWidth || '0');
    const ueber = Math.round(rechteKante(el) - grenze);
    if (ueber > 1) {
      befunde.push({
        marke: el.tagName.toLowerCase(),
        klasse: (el.className || '').toString().slice(0, 90),
        id: el.id || '',
        ueber: ueber,
        text: (el.textContent || '').trim().slice(0, 60),
      });
    }
  }
  return befunde;
}
"""

_SEITE_SCHIEBT = """
() => ({
  scroll: document.documentElement.scrollWidth,
  sicht: document.documentElement.clientWidth,
})
"""


def _befunde(page) -> list[dict]:
    page.wait_for_timeout(RUHE_MS)
    return page.evaluate(_DETEKTOR)


def _melde(name: str, breite: int, befunde: list[dict]) -> str:
    zeilen = [
        f"  {b['marke']}#{b['id']}.{b['klasse']} — {b['ueber']} px zu breit — «{b['text']}»"
        for b in befunde
    ]
    return f"{name} bei {breite} px: {len(befunde)} Kasten tritt heraus\n" + "\n".join(zeilen)


# --- Die Ansichten ---------------------------------------------------------

#: Bereich → wie man ihn erreicht. Der Einrichten-Bereich kommt unten dazu:
#: Er ist eine Schrittfolge, und jeder Schritt ist eine eigene Ansicht.
BEREICHE = {
    "Einstieg": "",
    "Leitstand": "lauf",
    "Ergebnisse": "runs",
    # Seit P1.9-W3.1: der Modell-Editor. Er traegt die 168 Bedienelemente, die
    # bis dahin in den Schritten 4 und 5 lagen -- also genau die dichtesten
    # Formulare der Anwendung. Wenn irgendwo etwas herausragt, dann hier.
    "Modell": "modell",
    "Handbuch": "doku",
}


@pytest.fixture(params=BREITEN, ids=[f"{b}px" for b in BREITEN])
def page(request, browser, basis_url):
    kontext = browser.new_context(viewport={"width": request.param, "height": HOEHE})
    seite = kontext.new_page()
    seite.goto(basis_url, wait_until="networkidle")
    seite.breite = request.param  # für die Meldung
    seite.basis = basis_url
    try:
        yield seite
    finally:
        kontext.close()


class TestKeineAnsichtTrittAusIhrerBox:
    @pytest.mark.parametrize("name", list(BEREICHE))
    def test_the_area_keeps_its_content_inside(self, page, name):
        page.goto(page.basis + BEREICHE[name], wait_until="networkidle")
        befunde = _befunde(page)

        assert not befunde, _melde(name, page.breite, befunde)

    def test_every_step_of_the_setup_keeps_its_content_inside(self, page):
        """Acht Schritte, acht Ansichten.

        Die vier optionalen tragen die dichtesten Formulare der ganzen App —
        Regelzeilen, Segmenttabellen, Faktorraster. Wenn irgendwo etwas
        herausragt, dann hier.
        """

        page.goto(page.basis, wait_until="networkidle")
        page.wait_for_selector(".af-way")

        page.click("#wizard-way-new")
        page.wait_for_timeout(RUHE_MS)

        from dashboard.web.config_editor import wizard

        schritte = page.locator(".af-step").count()
        assert schritte == len(
            wizard.STEPS
        ), f"Gezählt {schritte} Schritte, die Schrittfolge nennt {len(wizard.STEPS)}"

        for index in range(schritte):
            page.locator(".af-step").nth(index).click()
            befunde = _befunde(page)
            titel = page.locator(".af-wizard__counter").inner_text()
            assert not befunde, _melde(f"Einrichten / {titel}", page.breite, befunde)

    def test_every_result_view_keeps_its_content_inside(self, page):
        page.goto(page.basis + "runs", wait_until="networkidle")
        page.wait_for_selector(".af-viewbar__item")

        reiter = page.locator(".af-viewbar__item").count()
        for index in range(reiter):
            beschriftung = page.locator(".af-viewbar__item").nth(index).inner_text()
            page.locator(".af-viewbar__item").nth(index).click()
            befunde = _befunde(page)
            assert not befunde, _melde(f"Ergebnisse / {beschriftung}", page.breite, befunde)


# --- Teil 2: die Höhe (W0.1) -----------------------------------------------

#: Wohin der Deckel gehört, sobald der Umbau steht: **ein** Schirm. Eine Frage
#: auf dem Bildschirm, ohne Scrollen — die Zusage von P1.7 im Klartext. W3.5
#: setzt `DECKEL` auf diesen Wert; bis dahin ist er das Maß, an dem man abliest,
#: wie weit es noch ist.
ZIEL = 1.0

#: Der Ist-Stand, gemessen am 2026-08-28 bei 800 px Fensterhöhe (744 px sichtbar).
#:
#: **Je Breite eigene Zahlen, bewusst nicht das Maximum über beide.** Ein
#: gemeinsamer Deckel von 2,05 ließe Schritt 1 bei 1280 px von 1,92 auf 2,04
#: wachsen, ohne dass etwas rot wird — genau die Blindheit, gegen die dieses
#: Paket antritt.
#:
#: **Die Zahlen weichen vom Audit ab, und das ist kein Widerspruch.** Das Audit
#: hat bei 720 px Fensterhöhe gemessen (664 px sichtbar) und kam auf 1,13 bis
#: 4,44; hier sind es bei 800 px 1,01 bis 3,96. Derselbe Inhalt, mehr Fenster.
#: Was in beiden Messungen gleich bleibt, ist die Aussage: **kein einziger
#: Schritt kommt ohne Scrollen aus.**
DECKEL: dict[int, dict[str, float]] = {
    1280: {
        "Einstieg": 1.00,
        "Schritt 1": 1.41,
        "Schritt 2": 1.01,
        "Schritt 3": 1.05,
        "Schritt 4": 1.46,
        "Schritt 5": 2.16,
        "Schritt 6": 1.97,
        "Schritt 7": 1.07,
    },
    1024: {
        "Einstieg": 1.00,
        "Schritt 1": 1.53,
        "Schritt 2": 1.01,
        "Schritt 3": 1.14,
        "Schritt 4": 1.49,
        "Schritt 5": 2.16,
        "Schritt 6": 2.04,
        "Schritt 7": 1.09,
    },
}

#: Spielraum nach oben. Schriftmetrik und Chromium-Version schwanken zwischen
#: Rechnern um wenige Pixel; 0,05 Schirme sind rund 37 px — eine Textzeile.
#: Größer gewählt verstecken sich ganze Feldzeilen darin.
TOLERANZ = 0.05

#: Ab wann der Deckel als veraltet gilt. 0,25 Schirme sind rund 186 px — so weit
#: schrumpft nichts aus Versehen. Wer so viel gewonnen hat, schreibt den Gewinn
#: auf, sonst verfällt er still.
SCHLUPF = 0.25

_HOEHE = """
() => {
  const m = document.querySelector('.af-shell__main');
  if (!m) return null;
  return { scroll: m.scrollHeight, sicht: m.clientHeight };
}
"""


def _schirme(page) -> float:
    """Wie viele Bildschirme der offene Bereich hoch ist."""

    page.wait_for_timeout(RUHE_MS)
    masse = page.evaluate(_HOEHE)
    assert (
        masse is not None
    ), "`.af-shell__main` nicht gefunden — misst der Wächter noch das Richtige?"
    assert masse["sicht"] > 0, "Sichtbare Höhe 0 — der Bereich ist nicht gezeichnet"
    return masse["scroll"] / masse["sicht"]


def _gezeigter_schritt(page) -> int | None:
    """Welchen Schritt der Zähler nennt — als Zahl, nicht als Text.

    Die Beschriftung wird per CSS in Großbuchstaben gesetzt, und `inner_text()`
    liefert die **gerenderte** Fassung («SCHRITT 1 VON 8»). Ein Vergleich auf
    den Wortlaut hinge also an `text-transform`; die Zahl hängt an nichts.
    """

    zaehler = page.locator(".af-wizard__counter")
    if not zaehler.count():
        return None
    zahlen = re.findall(r"\d+", zaehler.first.inner_text())
    return int(zahlen[0]) if zahlen else None


class TestJederSchrittPasstAufEinenSchirm:
    """Die Zusage von P1.7, zum ersten Mal gemessen statt gezählt."""

    def test_no_step_grew_beyond_its_ratchet(self, page):
        """Kein Schritt wächst über seinen Deckel — und keiner schrumpft unbemerkt.

        Beide Richtungen in **einem** Durchlauf: Der Bildschirmwechsel kostet
        eine knappe Sekunde Ruhezeit je Schritt, und zweimal durch acht Schritte
        zu laufen wäre eine Minute für dieselbe Messung.

        Gemeldet werden **alle** Abweichungen auf einmal, nicht die erste. Wer
        den Assistenten umbaut, verschiebt selten genau eine Zahl.
        """

        deckel = DECKEL[page.breite]
        page.goto(page.basis, wait_until="networkidle")
        page.wait_for_selector(".af-way")

        gemessen: dict[str, float] = {"Einstieg": _schirme(page)}

        page.click("#wizard-way-new")
        page.wait_for_timeout(RUHE_MS)
        from dashboard.web.config_editor import wizard

        anzahl = page.locator(".af-step").count()
        assert anzahl == len(
            wizard.STEPS
        ), f"Gezählt {anzahl} Schritte, die Schrittfolge nennt {len(wizard.STEPS)}"

        for index in range(anzahl):
            page.locator(".af-step").nth(index).click()
            wert = _schirme(page)
            # Erst prüfen, ob wirklich der angeklickte Schritt offen ist. Ohne
            # das trüge eine verschluckte Navigation die Höhe des vorigen
            # Schritts unter fremdem Namen in den Deckel — und der Wächter wäre
            # ab dann grün für den falschen Schritt.
            gezeigt = _gezeigter_schritt(page)
            assert gezeigt == index + 1, (
                f"Klick auf Schritt {index + 1} zeigt Schritt {gezeigt}. "
                "Gemessen würde die Höhe des falschen Schritts."
            )
            gemessen[f"Schritt {index + 1}"] = wert

        fehlend = sorted(set(deckel) - set(gemessen))
        assert not fehlend, (
            f"Bei {page.breite} px nicht gemessen: {fehlend}. "
            "Steht der Zähler noch in `.af-wizard__counter`?"
        )

        gewachsen = [
            f"  {name}: {wert:.2f} Schirme, Deckel {deckel[name]:.2f}"
            for name, wert in sorted(gemessen.items())
            if name in deckel and wert > deckel[name] + TOLERANZ
        ]
        assert not gewachsen, (
            f"Bei {page.breite} px sind Schritte gewachsen:\n"
            + "\n".join(gewachsen)
            + "\n\nEin Schritt darf nicht länger werden, solange keiner auf einen "
            "Schirm passt. Wenn der Zuwachs gewollt ist, gehört die Begründung in "
            "die Commit-Message und die neue Zahl in `DECKEL`."
        )

        geschrumpft = [
            f"  {name}: {wert:.2f} Schirme, Deckel steht noch auf {deckel[name]:.2f}"
            for name, wert in sorted(gemessen.items())
            if name in deckel and wert < deckel[name] - SCHLUPF
        ]
        assert not geschrumpft, (
            f"Bei {page.breite} px ist der Deckel veraltet:\n"
            + "\n".join(geschrumpft)
            + f"\n\nDas ist ein Erfolg, kein Fehler — aber ein Deckel, der über dem "
            f"Ist-Stand schwebt, ist wieder aus dem falschen Grund grün. Neue Zahlen "
            f"in `DECKEL` eintragen. Ziel ist {ZIEL:.2f}."
        )


class TestDieSeiteSchiebtSichNichtWaagerecht:
    """Die grobe Probe ohne Ausnahmen.

    Der Detektor oben nimmt drei Sorten Inhalt aus, und jede Ausnahme ist eine
    Stelle, an der er blind sein könnte. Diese Probe kennt keine: Wenn die Seite
    als Ganzes waagerecht scrollt, ist etwas zu breit — gleich was.
    """

    @pytest.mark.parametrize("name", list(BEREICHE))
    def test_the_page_itself_does_not_scroll_sideways(self, page, name):
        page.goto(page.basis + BEREICHE[name], wait_until="networkidle")
        page.wait_for_timeout(RUHE_MS)
        masse = page.evaluate(_SEITE_SCHIEBT)

        assert masse["scroll"] <= masse["sicht"] + 1, (
            f"{name} bei {page.breite} px schiebt sich waagerecht: "
            f"{masse['scroll']} px Inhalt in {masse['sicht']} px Fenster"
        )


def test_the_height_guard_would_notice_a_relapse(page):
    """Der Höhenwächter hat genau eine Art, still blind zu werden.

    Er teilt `scrollHeight` durch `clientHeight` **eines bestimmten Elements**.
    Hört `.af-shell__main` auf, das scrollende Element zu sein — weil jemand den
    Scroll eine Ebene höher oder tiefer legt —, dann sind beide Maße gleich, das
    Verhältnis ist für immer 1,00, und jeder Schritt gilt als passend. Der
    Wächter wäre grün, und zwar aus demselben falschen Grund wie
    `test_the_setup_area_builds_with_the_default_draft` vor P1.8.

    Deshalb wird hier ein Schritt künstlich verlängert und nachgesehen, ob die
    Messung das überhaupt bemerkt. Tut sie es nicht, misst sie das falsche
    Element — und das ist ein Befund über den Wächter, nicht über die
    Oberfläche.
    """

    page.goto(page.basis, wait_until="networkidle")
    page.wait_for_selector(".af-way")
    page.click("#wizard-way-new")
    page.wait_for_timeout(RUHE_MS)

    vorher = _schirme(page)

    page.evaluate("""
        () => {
          const klotz = document.createElement('div');
          klotz.id = 'probe-hoch';
          klotz.style.cssText = 'height:2000px';
          document.getElementById('wizard-content').appendChild(klotz);
        }
        """)

    nachher = _schirme(page)

    assert nachher > vorher + 1.5, (
        f"Der Höhenwächter bemerkt 2000 px zusätzliche Höhe nicht "
        f"({vorher:.2f} → {nachher:.2f} Schirme). Er misst das falsche Element: "
        "`.af-shell__main` scrollt nicht mehr. Solange das so ist, ist jede grüne "
        "Zeile in `TestJederSchrittPasstAufEinenSchirm` wertlos."
    )


def test_the_detector_would_notice_a_relapse(page):
    """Ein Wächter, der aus dem falschen Grund grün ist, ist schlechter als keiner.

    Genau das war `test_the_setup_area_builds_with_the_default_draft` bis P1.8:
    Er prüfte auf eine Zeichenkette, die es nur noch in einer Kartenbeschriftung
    gab, und blieb grün, während der Abschnitt dahinter längst weg war. Hier
    wird deshalb ein Überlauf **erzeugt** und nachgesehen, ob der Detektor ihn
    findet — und ob er die drei Phantome weiterhin ignoriert.
    """

    page.goto(page.basis, wait_until="networkidle")
    page.wait_for_selector(".af-way")

    page.evaluate("""
        () => {
          const wirt = document.querySelector('.af-ways');
          const echt = document.createElement('div');
          echt.id = 'probe-echt';
          echt.style.cssText = 'width:120px;overflow-x:visible;white-space:nowrap';
          echt.textContent = 'x'.repeat(400);
          wirt.appendChild(echt);

          const abgeschnitten = echt.cloneNode(true);
          abgeschnitten.id = 'probe-abgeschnitten';
          abgeschnitten.style.overflowX = 'hidden';
          wirt.appendChild(abgeschnitten);

          const schwebend = echt.cloneNode(true);
          schwebend.id = 'probe-schwebend';
          schwebend.style.position = 'absolute';
          wirt.appendChild(schwebend);

          const wrapper = document.createElement('div');
          wrapper.id = 'probe-wrapper';
          wrapper.style.cssText = 'width:96px;position:relative;overflow-x:visible';
          const fokusziel = echt.cloneNode(true);
          fokusziel.id = 'probe-fokusziel';
          fokusziel.style.position = 'absolute';
          fokusziel.style.width = '241px';
          wrapper.appendChild(fokusziel);
          wirt.appendChild(wrapper);

          const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
          const beschriftung = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          beschriftung.id = 'probe-svg';
          beschriftung.textContent = '2035';
          svg.appendChild(beschriftung);
          wirt.appendChild(svg);

          const zugeklappt = document.createElement('details');
          const inhalt = echt.cloneNode(true);
          inhalt.id = 'probe-zugeklappt';
          zugeklappt.appendChild(document.createElement('summary'));
          zugeklappt.appendChild(inhalt);
          wirt.appendChild(zugeklappt);
        }
        """)

    gefunden = {b["id"] for b in _befunde(page)}

    assert "probe-echt" in gefunden, "Der Detektor übersieht einen echten Überlauf"
    assert not gefunden & {
        "probe-abgeschnitten",
        "probe-schwebend",
        "probe-zugeklappt",
        "probe-svg",
        # Der Wrapper ist der eigentliche Fund des ersten scharfen Durchlaufs:
        # Sein `scrollWidth` ist 145 px zu groß, weil ein ausgeschwebtes Kind
        # darin steht — zu sehen ist nichts, verrutscht ist nichts.
        "probe-wrapper",
        "probe-fokusziel",
    }, f"Der Detektor meldet Phantome: {sorted(gefunden)}"
