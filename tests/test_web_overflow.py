"""Nichts tritt aus seiner Box — mechanisch geprüft (P1.7-D).

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
"""

from __future__ import annotations

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

        schritte = page.locator(".af-step").count()
        assert schritte == 8, f"Erwartet acht Schritte, gezählt {schritte}"

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
