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
    """Erst warten, bis die **Schriften** da sind, dann messen.

    **Sonst misst man Ersatzzeichen.** Bis zum 2026-08-30 kam Tailwind als
    CDN-Skript, das die Regeln zur Laufzeit erzeugte — das dauerte lange genug,
    dass die Symbolschrift nebenher ankam. Mit dem lokalen Stylesheet ist die
    Seite schneller da als die Schrift, und `chevron_right` wird für einen
    Moment in der Ersatzschrift gesetzt: zwei Pixel breiter als sein Kasten.
    Der Wächter meldete daraufhin einen Überlauf, den niemand je sieht.

    Ein Wächter, der vom Ladezeitpunkt einer Schrift abhängt, ist keiner.
    """

    # **Auf das Versprechen warten, nicht auf den Status.** `document.fonts.status`
    # steht schon auf `loaded`, wenn die Schriften der *vorigen* Ansicht da sind
    # — fordert die neue eine weitere Schnittvariante an, misst man trotzdem zu
    # früh. `document.fonts.ready` wartet auf alles, was gerade lauft.
    try:
        page.evaluate("() => document.fonts.ready.then(() => true)")
    except PlaywrightError:
        # Ohne Netz laedt keine Webschrift; dann misst man eben die Ersatzschrift
        # — besser als gar nicht zu messen, und der Fall faellt woanders auf.
        pass
    page.wait_for_timeout(RUHE_MS)
    try:
        page.evaluate("() => document.fonts.ready.then(() => true)")
    except PlaywrightError:
        pass
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

#: Wohin der Deckel gehörte, wenn der Inhalt es zuließe: **ein** Schirm. Eine
#: Frage auf dem Bildschirm, ohne Scrollen — die Zusage von P1.7 im Klartext.
#:
#: **Der Deckel steht bewusst darüber, und das ist entschieden, kein Rückstand**
#: (W3.5, 2026-08-30). Vier der sieben Schritte stehen auf 1,00; die übrigen drei
#: tragen Inhalt, der sich nur durch Weglassen kürzen ließe — zehn Szenarien mit
#: ihrer Kennzahl, sieben Faktoren mit ihrer Leitfrage, die Benennung eines
#: Laufs. Ohne Kennzahl sind es zehn Namen, ohne Leitfrage sieben Fachbegriffe,
#: und ein Lauf ohne Namen ist später nicht wiederzufinden.
#:
#: `ZIEL` bleibt deshalb stehen: **als Maßstab, nicht als offene Aufgabe.** Wer
#: einen Schritt kürzer bekommt, sieht hier, woran er ihn misst — und die
#: Sperrklinke unten meldet den Gewinn ein, statt ihn verfallen zu lassen.
ZIEL = 1.0

#: Der Ist-Stand, gemessen am 2026-08-28 bei 800 px Fensterhöhe (744 px sichtbar).
#:
#: **Je Breite eigene Zahlen, bewusst nicht das Maximum über beide.** Ein
#: gemeinsamer Deckel von 2,05 ließe Schritt 1 bei 1280 px von 1,92 auf 2,04
#: wachsen, ohne dass etwas rot wird — genau die Blindheit, gegen die dieses
#: Paket antritt.
#:
#: **Stand nach P1.9-W3 und W4.1.** Die Schritte 2, 3 und 6 stehen auf 1,00 —
#: sie passen. Die übrigen liegen zwischen 1,13 und 1,34.
#:
#: Der Ausgangspunkt zum Vergleich: Beim Audit am 2026-08-28 brauchte **kein
#: einziger** der damals acht Schritte weniger als einen Bildschirm, der höchste
#: 4,44 (gemessen bei 720 px Fensterhöhe; hier sind es 800). Den Unterschied
#: machte nicht Sparsamkeit an einer Stelle, sondern dreierlei: die 168
#: Bedienelemente der beiden dichten Schritte in einen eigenen Bereich (W3.1),
#: ein Rahmen ohne den auf jedem Schritt wiederholten Einführungstext (−116 px,
#: W3.5) und eine Gliederungsebene weniger innerhalb der Schritte.
#:
#: **Der letzte Schritt ist mit W4.1, W4.2 und W4.4 von 1,00 auf 1,29 gewachsen**
#: (er hiess bis P2.0-C «Schritt 7», seither «Schritt 6»), und beides
#: war eine bewusste Abwägung. Der Name des Laufs steht seither dort, weil das
#: der einzige Schritt ist, den jeder Startweg passiert; die Abweichungsliste
#: ebenso, weil «was habe ich geändert» vor dem Start beantwortet gehört. Ein
#: die Herkunftsangaben ebenso, weil ein Lauf mit anderem Codestand nicht neben
#: einen anderen gehört und man das besser vor der Rechenzeit merkt. Ein Lauf,
#: den niemand benennen konnte, eine Änderung, die niemand mehr findet, und
#: zwei Läufe, die man fälschlich vergleicht, kosten später mehr als 0,29
#: Bildschirme. **Alle drei Zuwächse liegen auf dem Schritt, auf dem man
#: innehält** — nicht auf einem, den man durchläuft.
#:
#: `ZIEL` steht weiterhin auf 1,0, und der Deckel steht darüber: Der Wächter ist
#: scharf gegen Wachstum, behauptet aber nicht, das Ziel sei erfüllt. Die
#: verbliebenen Schritte tragen Inhalt, der sich nur durch **Weglassen** kürzen
#: ließe — zehn Szenarien mit Kennzahl, sieben Faktoren mit ihrer Leitfrage, der
#: Name des Laufs. Ob das den Tausch wert ist, ist eine Produktentscheidung.
DECKEL: dict[int, dict[str, float]] = {
    1280: {
        "Einstieg": 1.00,
        # **1,20 → 1,34 mit P2.0-C, und der Zuwachs ist gemessen zugeordnet.**
        # Der Schalter «Eigene Werte anwenden» ist mit P2.0-C von seinem
        # eigenen Schritt hierher gezogen, hinter «Feinabstimmung» — die
        # Faktorlage ist seither keine Eingabe mehr, und der Schritt
        # «Ausgangslage» ist entfallen. Nachgemessen liegt der Zuwachs
        # **vollständig** daran: Mit und ohne das Lesemaß auf den
        # Glossar-Erklärungen (`ui.explainer`, 2026-09-03) misst der Schritt
        # dieselben 1,34 — der Erklärungskörper steckt in einem zugeklappten
        # `<details>` und trägt keine Höhe.
        "Schritt 1": 1.34,
        "Schritt 2": 1.00,
        "Schritt 3": 1.00,
        # Ab hier sind es **dieselben Schritte wie vorher, eine Nummer
        # weiter**: P2.0-C hat den vierten entfernt. Der alte Schritt 5 (1,31)
        # ist der neue 4 und misst 1,22, der alte 6 (1,00) ist der neue 5 und
        # misst 1,02. Nicht gewachsen, nur umnummeriert.
        "Schritt 4": 1.22,
        "Schritt 5": 1.02,
        # **1,29 → 1,45 mit W5.4, und das ist bezahlt, nicht verrutscht.** Das
        # Lesemaß bricht den Preflight-Text bei 75 statt bei 124 Zeichen um;
        # dieselben Sätze brauchen dadurch mehr Zeilen. Der Handel: 0,16
        # Bildschirme Höhe gegen eine Zeilenlänge, der das Auge folgen kann.
        # Auf «Prüfen & Starten» hält man ohnehin inne — von den drei
        # Zuwächsen aus W4 lagen alle drei auf diesem Schritt, aus demselben
        # Grund. **Die Zahl steht hier, damit der nächste Zuwachs wieder
        # auffällt**; sie ist keine Freigabe für den übernächsten. Er hiess bis
        # P2.0-C «Schritt 7».
        "Schritt 6": 1.45,
    },
    1024: {
        "Einstieg": 1.00,
        # **1,31 → 1,37, und das ist keine Aenderung am Schritt** (P1.4).
        # Bis dahin kamen die Schriften von Google, und der Waechter mass,
        # bevor sie da waren -- teils also die Ersatzschrift, die schmaler
        # setzt. Mit den lokalen Schriften und dem Warten auf
        # `document.fonts.ready` misst er zum ersten Mal durchgehend die
        # echten Metriken. Die alte Zahl war zu guenstig, nicht diese zu hoch.
        # **1,37 → 1,42 mit P2.0-C**, aus demselben Grund wie bei 1280: der
        # zugezogene Schalter. Bei der engeren Breite kostet er 0,05 statt 0,14,
        # weil hier schon vorher mehr umbrach.
        "Schritt 1": 1.42,
        "Schritt 2": 1.00,
        "Schritt 3": 1.00,
        # Umnummeriert wie bei 1280: alter 5 (1,31) → neuer 4, misst 1,22;
        # alter 6 (1,08) → neuer 5, misst 1,08.
        "Schritt 4": 1.22,
        "Schritt 5": 1.08,
        "Schritt 6": 1.45,  # siehe die Begründung bei 1280
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
    """Wie viele Bildschirme der offene Bereich hoch ist.

    **Erst warten, bis wirklich gezeichnet ist.** Eine feste Wartezeit allein
    genügt nicht: Unter Last kam der Callback später, und gemessen wurde der
    noch leere Wirt — einmal grün, weil der Schritt scheinbar auf einen
    Bildschirm passte, einmal rot, weil er halb gezeichnet war. Ein Wächter,
    der je nach Auslastung ein anderes Ergebnis liefert, ist keiner.

    Am eigenen Messskript zuerst aufgefallen: Dort meldete derselbe Fehler
    einen Gewinn von 275 px, den es nicht gab.
    """

    # **Der Einstieg zählt mit.** Dort ist der Inhalt bewusst ausgeblendet und
    # bleibt es; auf ihn zu warten hieße, in einen Timeout zu laufen. Gewartet
    # wird deshalb darauf, dass *einer* von beiden gezeichnet ist.
    page.wait_for_function(
        "() => { const hoehe = (id) => { const e = document.getElementById(id);"
        " return e ? e.getBoundingClientRect().height : 0; };"
        " return hoehe('wizard-content') > 50 || hoehe('wizard-entry-host') > 50; }",
        timeout=10_000,
    )
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


# --- Teil 3: Breite je Schritt (P1.9-W5.4) ----------------------------------
#
# Bis W5.4 trug **eine** Breite alles: `grid-template-columns: 15rem
# minmax(0, 1fr)`, gemessen `240px 760px` bei 1040 px Zone. Dieselben 760 px
# trugen einen Schritt mit drei Feldern und ein Raster aus sieben Auswahlen.
#
# Zwei Dinge werden hier gemessen, und ein drittes am Einstieg:
#
# 1. **Wie viel seiner Spalte ein Schritt füllt.** Nicht das breiteste
#    Einzelfeld: Ein Raster aus sieben schmalen Auswahlen füllt seine Spalte
#    vollständig und meldet trotzdem 32 %. Gemessen wird die Ausdehnung aller
#    Tinte im Rumpf, bezogen auf die Breite des Rumpfes.
# 2. **Wie lang die Zeilen werden** — in Zeichen, gezählt, nicht aus der
#    Pixelbreite geschätzt. Der Schätzer lag um rund 10 % daneben, genug, um
#    einen Deckel für wirkungslos zu halten, der wirkt. Gemessen wurden vorher
#    bis zu **124** Zeichen; die typografische Spanne ist 45 bis 75.
# 3. **Ob der Einstieg eine Spalte für eine Liste vorhält, die er nicht hat.**

#: Was eine Zeile höchstens tragen darf. Über 75 Zeichen verliert das Auge am
#: Zeilenende die Spur zum nächsten Anfang.
ZEILE_MAX = 75

#: Wie viel seiner Spalte ein Schritt mindestens füllen muss. Darunter steht
#: der Inhalt in einer Spalte, die für ihn zu breit ist.
FUELLUNG_MIN = 60.0

_BREITE = """
() => {
    const spalte = document.getElementById("wizard-content");
    const rumpf = document.getElementById("wizard-body");
    if (!spalte || !rumpf) return null;
    const AUSSEN = ".af-wizard__nav, .af-wizard__navhost, .af-wizard__counter";
    const sichtbar = (el) => {
        if (!el || (el.closest && el.closest(AUSSEN))) return false;
        for (let n = el; n && n !== document.body; n = n.parentElement) {
            const st = getComputedStyle(n);
            if (st.display === "none" || st.visibility === "hidden") return false;
            if (n.classList && n.classList.contains("af-nur-vorlesen")) return false;
        }
        return true;
    };

    // (1) Fuellung: die Ausdehnung aller Tinte im Rumpf, an dessen Breite.
    const rb = rumpf.getBoundingClientRect();
    let links = Infinity, rechts = -Infinity;
    const nimm = (r) => {
        if (r.width < 1 || r.height < 1) return;
        // An den Rumpf klemmen: Was darueber hinausragt, ist entweder
        // Ueberlauf (dafuer gibt es Teil 1) oder beschnitten und unsichtbar.
        const l = Math.max(r.left, rb.left), re = Math.min(r.right, rb.right);
        if (re <= l) return;
        if (l < links) links = l;
        if (re > rechts) rechts = re;
    };
    rumpf.querySelectorAll("input, select, textarea, button, img, svg").forEach(
        (el) => { if (sichtbar(el)) nimm(el.getBoundingClientRect()); });

    // (2) Zeichen je Zeile: jedes Zeichen bekommt sein eigenes Rechteck,
    //     Zeichen mit derselben Oberkante stehen auf derselben Zeile.
    let zeile = 0, probe = null, wo = null;
    const lauf = document.createTreeWalker(spalte, NodeFilter.SHOW_TEXT);
    let k;
    while ((k = lauf.nextNode())) {
        const text = k.textContent || "";
        if (!text.trim()) continue;
        if (!sichtbar(k.parentElement)) continue;
        if (rumpf.contains(k)) {
            const rr = document.createRange();
            rr.selectNodeContents(k);
            Array.from(rr.getClientRects()).forEach(nimm);
        }
        if (text.trim().length < 40) continue;      // Beschriftungen sind kein Fliesstext
        // Code bricht nicht bei 75 Zeichen um, er wird gescrollt.
        if (k.parentElement.closest("pre, code")) continue;
        const zeilen = new Map();
        for (let i = 0; i < text.length; i++) {
            const r = document.createRange();
            r.setStart(k, i);
            r.setEnd(k, i + 1);
            const rect = r.getBoundingClientRect();
            if (rect.width < 0.01 && rect.height < 0.01) continue;
            const oben = Math.round(rect.top);
            zeilen.set(oben, (zeilen.get(oben) || 0) + 1);
        }
        zeilen.forEach((anzahl) => {
            if (anzahl > zeile) {
                zeile = anzahl;
                probe = text.trim().slice(0, 40);
                wo = k.parentElement.tagName + "." + String(k.parentElement.className).slice(0, 40);
            }
        });
    }

    return {
        rumpf: Math.round(rb.width),
        fuellung: rechts > 0 ? +(((rechts - links) / rb.width) * 100).toFixed(1) : null,
        zeichen: zeile, probe: probe, wo: wo,
    };
}
"""

_EINSTIEG_RASTER = """
() => {
    const w = document.querySelector(".af-wizard");
    const rail = document.querySelector(".af-wizard__rail");
    if (!w) return null;
    return {
        spalten: getComputedStyle(w).gridTemplateColumns,
        railBreite: rail ? Math.round(rail.getBoundingClientRect().width) : null,
    };
}
"""


def _durch_die_schritte(page):
    """Jeden Schritt öffnen und vermessen — als `(titel, maße)` je Schritt."""

    from dashboard.web.config_editor import wizard

    page.goto(page.basis, wait_until="networkidle")
    page.wait_for_selector(".af-way")
    page.click("#wizard-way-new")
    page.wait_for_timeout(RUHE_MS)

    for index in range(len(wizard.STEPS)):
        if index:
            page.click("#wizard-next")
            page.wait_for_timeout(RUHE_MS)
        page.wait_for_function(
            "() => { const e = document.getElementById('wizard-content');"
            " return e && e.getBoundingClientRect().height > 50; }",
            timeout=10_000,
        )
        yield wizard.STEPS[index].title, page.evaluate(_BREITE)


class TestJederSchrittHatSeineBreite:
    """Eine Breite für alles war für jeden Schritt die falsche."""

    def test_no_step_sits_in_a_column_too_wide_for_it(self, page):
        """Kein Schritt lässt seine Spalte zur Hälfte leer.

        **Gemessen an der Tinte, nicht am breitesten Feld.** Die erste Fassung
        dieses Maßes nahm das breiteste Bedienelement und meldete für die
        Ausgangslage 32 % — dabei füllt deren Raster aus sieben Auswahlen die
        Spalte vollständig. Ein Maß, das ein gefülltes Raster als leer meldet,
        misst nicht, was es zu messen vorgibt.
        """

        schmal = [
            f"{titel}: {mass['fuellung']} % von {mass['rumpf']} px"
            for titel, mass in _durch_die_schritte(page)
            if mass and mass["fuellung"] is not None and mass["fuellung"] < FUELLUNG_MIN
        ]

        assert not schmal, (
            f"Diese Schritte füllen bei {page.breite} px weniger als "
            f"{FUELLUNG_MIN:.0f} % ihrer Spalte:\n  " + "\n  ".join(schmal)
        )

    def test_no_line_runs_longer_than_the_eye_can_follow(self, page):
        """Keine Zeile über 75 Zeichen — gezählt, nicht geschätzt.

        Aus der Pixelbreite mit einer angenommenen halben Geviertbreite
        zurückzurechnen lag um rund 10 % daneben. Das genügte, um einen Deckel
        für wirkungslos zu halten, der wirkte.
        """

        lang = [
            f"{titel}: {mass['zeichen']} Zeichen in {mass['wo']} — {mass['probe']!r}"
            for titel, mass in _durch_die_schritte(page)
            if mass and mass["zeichen"] > ZEILE_MAX
        ]

        assert not lang, (
            f"Diese Zeilen laufen bei {page.breite} px über {ZEILE_MAX} Zeichen:\n  "
            + "\n  ".join(lang)
            + "\n\nDas Lesemaß (`af-mass`) fehlt dort — oder es ist zu weit."
        )

    def test_the_entry_reserves_no_column_for_a_list_it_does_not_have(self, page):
        """Am Einstieg gibt es keine Schrittliste — und keine Spalte dafür.

        Gemessen wurden 240 px Leere links neben der Frage, mit der alles
        anfängt: Das Raster hielt die Spalte der Liste vor, während die Liste
        selbst `display: none` war.
        """

        page.goto(page.basis, wait_until="networkidle")
        page.wait_for_selector(".af-way")
        raster = page.evaluate(_EINSTIEG_RASTER)

        assert raster, ".af-wizard nicht gefunden — misst der Wächter noch das Richtige?"
        assert not raster["railBreite"], "Die Schrittliste ist am Einstieg doch sichtbar"
        assert len(raster["spalten"].split()) == 1, (
            f"Der Einstieg hält bei {page.breite} px eine zweite Spalte vor "
            f"({raster['spalten']}) — für eine Liste, die dort nicht steht."
        )


def test_the_width_guard_would_notice_a_relapse(page):
    """Beide Maße müssen anschlagen, sonst sind sie Zierde.

    Erzeugt wird je ein echter Rückfall: ein Rumpf, der nur ein Viertel seiner
    Spalte füllt, und ein Satz ohne Lesemaß.
    """

    page.goto(page.basis, wait_until="networkidle")
    page.wait_for_selector(".af-way")
    page.click("#wizard-way-new")
    # **Erst warten, bis gezeichnet ist** — derselbe Fehler, an dem der
    # Höhenwächter schon einmal hing: Ohne die Bedingung misst man den leeren
    # Wirt, und `fuellung` kommt als `None` zurück.
    page.wait_for_function(
        "() => { const e = document.getElementById('wizard-body');"
        " return e && e.getBoundingClientRect().height > 50; }",
        timeout=10_000,
    )
    page.wait_for_timeout(RUHE_MS)

    vorher = page.evaluate(_BREITE)
    assert vorher["fuellung"] >= FUELLUNG_MIN and vorher["zeichen"] <= ZEILE_MAX

    page.evaluate("""
        () => {
          const rumpf = document.getElementById('wizard-body');
          rumpf.innerHTML = '';
          const eng = document.createElement('div');
          eng.style.width = '25%';
          eng.appendChild(document.createTextNode('kurz'));
          rumpf.appendChild(eng);
        }
        """)
    schmal = page.evaluate(_BREITE)
    assert (
        schmal["fuellung"] < FUELLUNG_MIN
    ), f"Der Wächter übersieht eine viertelvolle Spalte ({schmal['fuellung']} %)"

    page.evaluate("""
        () => {
          const p = document.createElement('p');
          p.style.maxWidth = 'none';
          p.style.fontSize = '10px';
          p.textContent = 'A'.repeat(400);
          document.getElementById('wizard-body').appendChild(p);
        }
        """)
    lang = page.evaluate(_BREITE)
    assert (
        lang["zeichen"] > ZEILE_MAX
    ), f"Der Wächter übersieht eine Zeile ohne Lesemaß ({lang['zeichen']} Zeichen)"


# --- Teil 4: Die schmale Breite (P1.9-W5.5) ---------------------------------
#
# Gemessen bei 375 px: Die Schrittliste stand als **358 px hoher** Stapel aus
# sieben Knöpfen über der Frage — man scrollte an der Navigation vorbei, um zum
# Inhalt zu kommen. Die Fußleiste brach auf **133 px** um, auf «Prüfen &
# Starten» auf 153.
#
# Beides wird hier gemessen, und zwar **an jedem Schritt**: Die Höhe der
# Fußleiste hing genau daran, wie viele Knöpfe der Schritt zeigt.

#: Die Breite, bei der gemessen wird — dieselbe wie im Audit vom 2026-08-28.
SCHMAL = 375

#: Was die Fußleiste bei dieser Breite höchstens hoch sein darf. Ein Knopf plus
#: Luft; darüber ist sie umgebrochen.
FUSS_MAX = 72

#: Dasselbe für die Schrittliste. Als Balken ist sie eine Zeile hoch; als
#: Stapel war sie 358 px und schob den Inhalt aus dem Bild.
LISTE_MAX = 72

_MOBIL = """
() => {
    const hoehe = (sel) => {
        const e = document.querySelector(sel);
        if (!e) return null;
        const st = getComputedStyle(e);
        if (st.display === "none") return 0;
        return Math.round(e.getBoundingClientRect().height);
    };
    return {
        fussleiste: hoehe(".af-wizard__nav"),
        liste: hoehe(".af-wizard__rail"),
        seitlich: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    };
}
"""


@pytest.fixture
def schmale_seite(browser, basis_url):
    """Eine eigene Seite bei 375 px — die anderen Tests laufen bei 1280/1024."""

    kontext = browser.new_context(viewport={"width": SCHMAL, "height": HOEHE})
    seite = kontext.new_page()
    seite.goto(basis_url, wait_until="networkidle")
    seite.breite = SCHMAL
    seite.basis = basis_url
    try:
        yield seite
    finally:
        kontext.close()


class TestAufDemTelefonBleibtPlatzFuerDieFrage:
    """Navigation ist der Weg zum Inhalt, nicht der Inhalt."""

    def test_the_footer_stays_one_row_on_every_step(self, schmale_seite):
        """Kein Schritt bricht die Fußleiste um.

        **Je Schritt gemessen**, nicht einmal: Die Höhe hing daran, wie viele
        Knöpfe der Schritt zeigt — «Prüfen & Starten» trug mit «Als Szenario
        speichern» und «Lauf starten» zwei zusätzliche und war mit 153 px der
        höchste.
        """

        zu_hoch = [
            f"{titel}: {mass['fussleiste']} px"
            for titel, mass in _schmal_durch_die_schritte(schmale_seite)
            if mass["fussleiste"] > FUSS_MAX
        ]

        assert (
            not zu_hoch
        ), f"Die Fußleiste bricht bei {SCHMAL} px um (mehr als {FUSS_MAX} px):\n  " + "\n  ".join(
            zu_hoch
        )

    def test_the_step_list_is_a_bar_not_a_stack(self, schmale_seite):
        """Sieben Marken nebeneinander statt sieben Knöpfe untereinander."""

        hoch = [
            f"{titel}: {mass['liste']} px"
            for titel, mass in _schmal_durch_die_schritte(schmale_seite)
            if mass["liste"] > LISTE_MAX
        ]

        assert not hoch, (
            f"Die Schrittliste steht bei {SCHMAL} px als Stapel (mehr als "
            f"{LISTE_MAX} px):\n  " + "\n  ".join(hoch)
        )

    def test_nothing_forces_the_page_sideways(self, schmale_seite):
        """Ein Balken, der breiter ist als das Telefon, ist kein Gewinn."""

        seitlich = [
            titel for titel, mass in _schmal_durch_die_schritte(schmale_seite) if mass["seitlich"]
        ]

        assert (
            not seitlich
        ), f"Diese Schritte schieben die Seite bei {SCHMAL} px zur Seite: {seitlich}"


def _schmal_durch_die_schritte(page):
    """Jeden Schritt öffnen und die beiden Höhen nehmen."""

    from dashboard.web.config_editor import wizard

    page.goto(page.basis, wait_until="networkidle")
    page.wait_for_selector(".af-way")
    page.click("#wizard-way-new")
    page.wait_for_timeout(RUHE_MS)

    for index in range(len(wizard.STEPS)):
        if index:
            page.click("#wizard-next")
            page.wait_for_timeout(RUHE_MS)
        page.wait_for_function(
            "() => { const e = document.getElementById('wizard-content');"
            " return e && e.getBoundingClientRect().height > 50; }",
            timeout=10_000,
        )
        yield wizard.STEPS[index].title, page.evaluate(_MOBIL)


def test_the_narrow_guard_would_notice_a_relapse(schmale_seite):
    """Der Umbruch muss auffallen, sonst misst der Wächter nichts.

    Nachgestellt wird genau der Zustand von vorher: eine Fußleiste, die
    umbricht, und eine Schrittliste, die stapelt.
    """

    page = schmale_seite
    page.click("#wizard-way-new")
    # **Erst warten, bis der Schritt wirklich steht.** Ohne das hängt der Test
    # an der Auslastung: Im vollen Durchlauf kam die Antwort des Servers später,
    # Dash tauschte die Fußleiste **nach** der Einspritzung aus und wischte sie
    # damit weg — der Test meldete einen blinden Wächter, wo nur zu früh
    # gemessen wurde. Allein gelaufen war er grün. Genau dieser Fehler steckte
    # schon einmal im Höhenwächter.
    page.wait_for_function(
        "() => { const e = document.getElementById('wizard-content');"
        " return e && e.getBoundingClientRect().height > 50; }",
        timeout=10_000,
    )
    page.wait_for_timeout(RUHE_MS)

    vorher = page.evaluate(_MOBIL)
    assert vorher["fussleiste"] <= FUSS_MAX and vorher["liste"] <= LISTE_MAX

    # **Ein echter Umbruch, kein zurueckgedrehtes Stylesheet.** Der erste
    # Anlauf nahm den Beschriftungen ihre Beschneidung zurueck und hoffte, dass
    # die Leiste davon umbricht -- sie tat es nicht, und der Test meldete einen
    # blinden Waechter, wo nur die Nachstellung zu zaghaft war. Jetzt wird ein
    # Block eingehaengt, der nicht danebenpasst, und die Liste wirklich
    # gestapelt.
    page.evaluate("""
        () => {
          const nav = document.querySelector('.af-wizard__nav');
          nav.style.flexWrap = 'wrap';
          const klotz = document.createElement('div');
          klotz.style.cssText = 'width: 320px; height: 40px; flex: 0 0 320px;';
          klotz.setAttribute('data-probe', '1');
          nav.appendChild(klotz);
          document.querySelector('.af-steps').style.flexDirection = 'column';
        }
        """)
    # Ob die Einspritzung überhaupt noch dasteht — sonst misst der Test etwas
    # anderes, als er zu messen glaubt, und meldet den Wächter zu Unrecht blind.
    assert page.evaluate(
        "() => !!document.querySelector('.af-wizard__nav [data-probe]')"
    ), "Der eingehängte Klotz ist verschwunden — Dash hat die Fußleiste neu gezeichnet."

    nachher = page.evaluate(_MOBIL)

    assert (
        nachher["fussleiste"] > FUSS_MAX
    ), f"Der Wächter übersieht eine umgebrochene Fußleiste ({nachher['fussleiste']} px)"
    assert (
        nachher["liste"] > LISTE_MAX
    ), f"Der Wächter übersieht eine gestapelte Schrittliste ({nachher['liste']} px)"


# --- Teil 5: Jede benutzte Klasse hat eine Regel (P1.4) ----------------------
#
# Tailwind kommt seit dem 2026-08-30 aus einem Build statt vom CDN. Das
# CDN-Skript erzeugte die Regeln zur Laufzeit aus dem, was im DOM stand — es
# konnte gar nichts übersehen. Der Build kann: Er schreibt nur Regeln für
# Klassen, die sein Scanner im Quelltext **findet**. Eine Klasse, die zur
# Laufzeit aus Bruchstücken entsteht, fehlt dann **stumm** — kein Fehler, nur
# ein Kasten, der anders aussieht.
#
# Dieser Wächter geht jede Ansicht durch, sammelt alle benutzten Klassennamen
# aus dem gezeichneten DOM und hält sie gegen die Regeln in `document.styleSheets`.

#: Klassen ohne eigene Gestaltung. Sie **markieren** etwas, statt es zu
#: formen — für sie gibt es berechtigterweise keine Regel.
#:
#: `light` und `dark` sind die eigenen: Sie stehen am `<html>` und schalten
#: das Design um (`darkMode: "class"`); jede Regel, die davon abhängt, nennt
#: sie als Vorfahren, nicht als eigenes Ziel. Der Rest kommt von Dash und
#: Plotly und markiert Elemente für deren eigenes JavaScript.
FREMDE_KLASSEN = {
    "light",
    "dark",
    "active",
    "selected",
    "_dash-loading-callback",
}

#: Präfixe derselben Art. Plotly bringt allein für seine Zeichenfläche ein
#: Dutzend Marker mit (`gl-canvas`, `modebar-container`, …).
FREMDE_PRAEFIXE = ("dash-", "plot-", "svg-", "gl-", "modebar", "js-plotly")

_KLASSEN_OHNE_REGEL = """
() => {
    // **CSS-Escapes zurueckuebersetzen.** Eine Klasse, die mit einer Ziffer
    // beginnt, steht als Hex-Escape im Stylesheet: `2xl:grid-cols-3` wird zu
    // `.\\32 xl\\:grid-cols-3` -- mit einem Leerzeichen, das die Escape-Sequenz
    // beendet. Ein naiver Ausdruck bricht dort ab und meldet die Klasse als
    // regellos. Genau das ist beim ersten Durchlauf passiert.
    const entschluesseln = (s) => s.replace(
        /\\\\([0-9a-fA-F]{1,6})[ ]?|\\\\(.)/g,
        (_, hex, roh) => hex ? String.fromCodePoint(parseInt(hex, 16)) : roh
    );

    const regeln = new Set();
    const sammeln = (liste) => {
        for (const r of liste) {
            // In `@media` und `@supports` steigen: Dort liegen alle
            // responsiven Varianten. Ohne das meldet der Waechter jede
            // `sm:`- und `lg:`-Klasse als fehlend.
            if (r.cssRules) { sammeln(r.cssRules); }
            const sel = r.selectorText;
            if (!sel) { continue; }
            const treffer = sel.match(/\\.(?:\\\\[0-9a-fA-F]{1,6}[ ]?|\\\\.|[-_a-zA-Z0-9])+/g) || [];
            treffer.forEach((m) => regeln.add(entschluesseln(m.slice(1))));
        }
    };
    for (const sheet of document.styleSheets) {
        try { sammeln(sheet.cssRules); } catch (e) { /* fremdes Blatt */ }
    }

    const benutzt = new Set();
    document.querySelectorAll("*").forEach((el) => {
        if (typeof el.className === "string") {
            el.className.split(/\\s+/).filter(Boolean).forEach((c) => benutzt.add(c));
        }
    });

    return [...benutzt].filter((c) => !c.startsWith("af-") && !regeln.has(c));
}
"""


def _klassen_ohne_regel(page) -> list[str]:
    roh = page.evaluate(_KLASSEN_OHNE_REGEL)
    return sorted(c for c in roh if c not in FREMDE_KLASSEN and not c.startswith(FREMDE_PRAEFIXE))


class TestJedeBenutzteKlasseHatEineRegel:
    """Der Build darf nichts übersehen, was das CDN noch gefunden hätte."""

    @pytest.mark.parametrize("name", list(BEREICHE))
    def test_no_class_lost_its_rule(self, page, name):
        page.goto(page.basis + BEREICHE[name], wait_until="networkidle")
        page.wait_for_timeout(RUHE_MS)

        ohne = _klassen_ohne_regel(page)

        assert not ohne, (
            f"Diese Klassen werden in «{name}» benutzt, haben aber keine Regel:\n  "
            + "\n  ".join(ohne)
            + "\n\nTailwind schreibt nur Regeln für Klassen, die sein Scanner im "
            "Quelltext findet (`content` in `tailwind.config.js`). Eine zur "
            "Laufzeit zusammengesetzte Klasse findet er nicht."
        )

    def test_the_landing_page_too(self, page):
        """Sie teilt sich das Stylesheet mit dem Dashboard."""

        page.goto(page.basis.replace("/app/", "/"), wait_until="networkidle")
        page.wait_for_timeout(RUHE_MS)

        assert not _klassen_ohne_regel(page)


def test_the_class_guard_would_notice_a_relapse(page):
    """Eine Klasse, die der Build nicht kennt, muss auffallen.

    `mt-[999px]` ist gültiges Tailwind und steht in keinem Quelltext — genau
    der Fall, den eine zur Laufzeit zusammengesetzte Klasse erzeugt.
    """

    page.goto(page.basis, wait_until="networkidle")
    page.wait_for_timeout(RUHE_MS)
    assert not _klassen_ohne_regel(page)

    page.evaluate("""
        () => {
          const d = document.createElement('div');
          d.className = 'mt-[999px] af-echt-egal';
          document.body.appendChild(d);
        }
        """)

    assert "mt-[999px]" in _klassen_ohne_regel(page), (
        "Der Wächter übersieht eine Klasse ohne Regel — dann bricht der nächste "
        "Build die Darstellung still."
    )


# --- Teil 6: Kein Aufruf verlässt den eigenen Server (P1.4) ------------------
#
# **Die Zusage von P1.4 im Wortlaut**, als Messung statt als Behauptung: «Ein
# Seitenaufruf erzeugt keine Anfrage an einen externen Host.»
#
# Bis zum 2026-08-30 meldete jeder Aufruf die IP des Betrachters an
# `cdn.tailwindcss.com` und `fonts.googleapis.com` — auf allen fünf
# Landingpage-Seiten und im Dashboard. Das widerspricht dem Deployment-Ziel
# Datenhoheit direkt; bei Google Fonts kommt die deutsche Rechtslage dazu.
#
# Ein Test, der die Quelltexte nach Hostnamen durchsucht, fände nur, was jemand
# hingeschrieben hat. Dieser hört zu, **was der Browser wirklich tut**.


def _fremde_anfragen(page, url: str) -> list[str]:
    """Jede Anfrage, die nicht an den eigenen Server geht."""

    from urllib.parse import urlparse

    eigener = urlparse(page.basis).netloc
    fremd: list[str] = []

    def mithoeren(anfrage) -> None:
        ziel = urlparse(anfrage.url)
        if ziel.scheme in ("http", "https") and ziel.netloc != eigener:
            fremd.append(anfrage.url)

    page.on("request", mithoeren)
    try:
        page.goto(url, wait_until="networkidle")
        # Schriften werden erst angefordert, wenn ein Zeichen sie braucht.
        page.evaluate("() => document.fonts.ready.then(() => true)")
        page.wait_for_timeout(RUHE_MS)
    finally:
        page.remove_listener("request", mithoeren)
    return fremd


class TestKeinAufrufVerlaesstDenServer:
    """Datenhoheit ist kein Vorsatz, sondern eine messbare Eigenschaft."""

    @pytest.mark.parametrize("name", list(BEREICHE))
    def test_no_area_of_the_dashboard_phones_home(self, page, name):
        fremd = _fremde_anfragen(page, page.basis + BEREICHE[name])

        assert not fremd, f"«{name}» lädt von fremden Hosts:\n  " + "\n  ".join(sorted(set(fremd)))

    def test_no_page_of_the_landing_site_phones_home(self, page):
        """Sie ist die einzige öffentlich sichtbare Oberfläche."""

        basis = page.basis.replace("/app/", "/")
        befunde: dict[str, list[str]] = {}
        for seite in ("", "demo-anfragen.html", "impressum.html", "datenschutz.html", "agb.html"):
            fremd = _fremde_anfragen(page, basis + seite)
            if fremd:
                befunde[seite or "index.html"] = sorted(set(fremd))

        assert not befunde, f"Diese Seiten laden von fremden Hosts: {befunde}"


def test_the_network_guard_would_notice_a_relapse(page):
    """Ein Wächter, der nie etwas sieht, könnte auch blind sein.

    Nachgestellt wird genau der alte Zustand: ein Stylesheet von einem fremden
    Host. Der Browser darf es ruhig nicht laden — **die Anfrage** ist der
    Befund, nicht die Antwort.
    """

    page.goto(page.basis, wait_until="networkidle")

    from urllib.parse import urlparse

    eigener = urlparse(page.basis).netloc
    gesehen: list[str] = []
    page.on(
        "request",
        lambda a: gesehen.append(a.url) if urlparse(a.url).netloc != eigener else None,
    )
    page.evaluate("""
        () => {
          const l = document.createElement('link');
          l.rel = 'stylesheet';
          l.href = 'https://fonts.googleapis.com/css2?family=Inter';
          document.head.appendChild(l);
        }
        """)
    page.wait_for_timeout(RUHE_MS)

    assert any("fonts.googleapis.com" in u for u in gesehen), (
        "Der Wächter übersieht eine Anfrage an einen fremden Host — dann ist " "seine Zusage keine."
    )


# --- Teil 7: Kein Symbol steht als Wort da (P1.4) ---------------------------
#
# **Dieser Wächter ist aus einem Fehlschlag entstanden.** Die Symbolschrift ist
# ein Teilsatz — 5 KiB statt Megabyte —, und ein Name, der nicht darin steckt,
# wird als Text gesetzt: «radio_button_unchecked» in Buchstaben statt als
# Kreis. Dagegen stand ein AST-Durchlauf über `dashboard/web/`
# (`tests/test_symbolschrift.py`), der jeden Symbolnamen an einer Aufrufstelle
# einsammelt.
#
# Er hat vier übersehen. Die Zustände der Schrittliste stehen in einem
# Modul-Dict (`_ZUSTAENDE` in `wizard.py`) und werden von dort in den Aufruf
# gereicht — im Aufruf selbst steht eine Variable. Der Überlauf-Wächter meldete
# daraufhin sieben Kästen, die um bis zu **308 px** aus der Schrittliste traten.
#
# **Ein Parser findet, was jemand hingeschrieben hat. Eine Messung findet, was
# wirklich dasteht.** Dieser Wächter liest den gezeichneten Text jedes
# Symbol-Elements und hält ihn gegen den Teilsatz — gleich, aus welcher Quelle
# der Name kommt.

_SYMBOLE_IM_DOM = """
() => {
    const namen = new Set();
    document.querySelectorAll(".material-symbols-outlined").forEach((el) => {
        const text = (el.textContent || "").trim();
        if (text) { namen.add(text); }
    });
    return [...namen];
}
"""


def _symbole_der_ansicht(page) -> set[str]:
    page.evaluate("() => document.fonts.ready.then(() => true)")
    page.wait_for_timeout(RUHE_MS)
    return set(page.evaluate(_SYMBOLE_IM_DOM))


class TestKeinSymbolStehtAlsWortDa:
    """Der Teilsatz deckt, was gezeichnet wird — nicht, was jemand aufgeschrieben hat."""

    @pytest.mark.parametrize("name", list(BEREICHE))
    def test_every_rendered_icon_is_in_the_subset(self, page, name):
        from scripts.schriften_holen import SYMBOLE

        page.goto(page.basis + BEREICHE[name], wait_until="networkidle")
        fehlend = sorted(_symbole_der_ansicht(page) - set(SYMBOLE))

        assert not fehlend, (
            f"«{name}» zeichnet Symbole, die nicht im Teilsatz stecken:\n  "
            + "\n  ".join(fehlend)
            + "\n\nSie erscheinen als Wort. Eintragen in `SYMBOLE` "
            "(scripts/schriften_holen.py), dann das Skript laufen lassen."
        )

    def test_the_steps_of_the_wizard_too(self, page):
        """Genau hier ist es passiert: vier Namen aus einem Modul-Dict."""

        from scripts.schriften_holen import SYMBOLE

        page.goto(page.basis, wait_until="networkidle")
        page.wait_for_selector(".af-way")
        page.click("#wizard-way-new")
        page.wait_for_timeout(RUHE_MS)

        gezeichnet = _symbole_der_ansicht(page)

        assert "radio_button_checked" in gezeichnet, "Die Schrittliste wird nicht gezeichnet"
        assert not gezeichnet - set(SYMBOLE)

    def test_the_landing_page_too(self, page):
        from scripts.schriften_holen import SYMBOLE

        page.goto(page.basis.replace("/app/", "/"), wait_until="networkidle")

        assert not _symbole_der_ansicht(page) - set(SYMBOLE)


def test_the_symbol_guard_would_notice_a_relapse(page):
    """Ein Name, den der Teilsatz nicht kennt, muss auffallen."""

    from scripts.schriften_holen import SYMBOLE

    page.goto(page.basis, wait_until="networkidle")
    assert not _symbole_der_ansicht(page) - set(SYMBOLE)

    page.evaluate("""
        () => {
          const s = document.createElement('span');
          s.className = 'material-symbols-outlined';
          s.textContent = 'rocket_launch';
          document.body.appendChild(s);
        }
        """)

    assert "rocket_launch" in _symbole_der_ansicht(page) - set(SYMBOLE), (
        "Der Wächter übersieht ein Symbol außerhalb des Teilsatzes — dann steht "
        "beim nächsten Mal wieder ein Wort im Bild."
    )
