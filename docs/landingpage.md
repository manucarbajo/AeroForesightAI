# Landingpage: Stand und Anbindung

Es gibt zwei Landingpages. Sie schließen sich nicht aus, sondern liegen auf
unterschiedlichen Branches und folgen unterschiedlichen Architekturen. Dieses
Dokument hält fest, was wo liegt und wie die neue Seite an das Dashboard
angebunden ist.

## Alte Landingpage (unverändert)

**Ort:** `dashboard/landing.py`

**Branches:** `feature/landing-page-phase1` und `feature/landing-login-redesign`
(jeweils lokal und auf `origin`). **Nicht** auf `main` und **nicht** auf diesem
Branch — deshalb liegt die Datei in diesem Worktree nicht vor.

**Art:** Kein statisches HTML, sondern eine Streamlit-Ansicht. Die Inhalte
stecken als HTML-Strings in Modul-Konstanten (`_HERO_TEXT_HTML`, `_USP_HTML`,
`_PROBLEM_HTML`, …) und werden über `st.markdown(..., unsafe_allow_html=True)`
ausgegeben. Layout-Gerüst (Spalten, Buttons) kommt aus Streamlit.

**Anbindung:** Die alte Seite ist Teil der Dashboard-App. In
`dashboard/shared_views.py`:

```python
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("show_login", False)

if not st.session_state.authenticated:
    if not st.session_state.show_login:
        render_landing()      # Landingpage ist die erste Ansicht
        return
    if not require_auth():    # danach das Login-Formular
        return
```

Ein Klick auf einen CTA setzt `show_login = True`, wodurch die Landingpage durch
das Login-Formular ersetzt wird. Die Sidebar-Buttons „AeroForesight AI" und
„Zur Startseite" rufen `_go_landing()` auf und setzen den Zustand zurück.

Landing- und Login-Ansicht teilen sich die Design-Tokens aus
`dashboard/theme.py` (Akzent `#1A5FA8`, IBM Plex Sans/Mono).

**Status:** Bewusst nicht angefasst. Die neue Seite ist eine Alternative, kein
Ersatz. Solange nicht entschieden ist, welche Variante gilt, laufen beide
nebeneinander.

## Neue Landingpage

**Ort:** `aeroforesight-ai-landing-page/`

| Datei | Zweck |
|-------|-------|
| `index.html` | Landingpage |
| `demo-anfragen.html` | Kontaktseite mit Demo-Anfrageformular |
| `impressum.html`, `datenschutz.html`, `agb.html` | Rechtsseiten, **Platzhaltertexte** |
| `design/DESIGN.md` | Design-System und Begründung |
| `design/color-tokens.json` | Farb- und Typo-Tokens als JSON |
| `DEPLOY.md` | Deployment-Checkliste |

**Art:** Eigenständige statische Website. Kein Build-Schritt, kein Framework,
keine Abhängigkeit zur Python-Anwendung. Tailwind kommt über die CDN, Schriften
über Google Fonts, alle Illustrationen sind Inline-SVG.

**Architektur-Unterschied zur alten Seite:** Die alte Landingpage lebt *in* der
Streamlit-App und wird durch das Login-Formular ersetzt. Die neue liegt *vor*
der App und verlinkt auf sie. Das Dashboard bleibt davon unberührt: an
`dashboard/` wurde für diese Variante nichts geändert.

### Anbindung ans Dashboard

Alle „Login"-Buttons (Navigation auf jeder der fünf Seiten, Desktop wie
Burger-Menü) zeigen auf:

```
http://localhost:8511
```

Das ist der Port der `dashboard`-Konfiguration aus `.claude/launch.json`
(`streamlit run dashboard/app.py --server.port=8511`). Für ein Deployment muss
diese URL auf den öffentlichen Dashboard-Einstieg umgestellt werden — Suche nach
`href="http://localhost:8511"` in allen fünf HTML-Dateien.

Empfohlene Zielarchitektur auf dem Hetzner-Server: statische Seiten und
Streamlit hinter demselben Reverse Proxy (nginx/Caddy), `/` auf die statischen
Dateien, `/dashboard` auf die Streamlit-App. Dann genügt ein relativer Link
`/dashboard` und die URL muss pro Umgebung nicht mehr angepasst werden.

### Offene Punkte

1. **Formular ohne Backend.** `demo-anfragen.html` hat `action="#"`. Anfragen
   gehen aktuell ins Leere; ein Endpunkt fehlt.
2. **Rechtstexte sind Platzhalter.** Alle mit `[…]` markierten Stellen müssen
   ersetzt und rechtlich geprüft werden. Der gelbe Hinweisblock auf den drei
   Seiten muss vor Veröffentlichung raus.
3. **Tailwind über CDN.** Für Produktion sollte ein gebautes CSS-Bundle her.

Details in `aeroforesight-ai-landing-page/DEPLOY.md`.

## Vergleich der beiden Varianten

Weil die alte Seite Streamlit braucht und ihre Quelldatei auf diesem Branch
fehlt, liegt unter `vergleich/` ein **statischer Nachbau**:

- `vergleich/build_alt_landingpage.py` liest die HTML-Konstanten per AST aus
  `dashboard/landing.py` und die Farbtokens aus `dashboard/theme.py`, ohne die
  Module zu importieren (das bräuchte Streamlit).
- `vergleich/alt-landingpage.html` ist das Ergebnis.

Inhalte, Grafiken und CSS stammen damit 1:1 aus dem Original. Nachgebaut ist nur
das Streamlit-Gerüst: die zweispaltige Hero-Aufteilung und die beiden Buttons
(„Anmelden", „Zur Plattform →"). Das Hinweisbanner am oberen Rand gehört zum
Nachbau, nicht zum Original. Für eine wirklich originalgetreue Ansicht muss das
Dashboard aus einem Branch mit `dashboard/landing.py` laufen.

Neu erzeugen (aus einem Verzeichnis, in dem `dashboard/landing.py` existiert):

```bash
python vergleich/build_alt_landingpage.py <pfad>/dashboard/landing.py <pfad>/dashboard/theme.py vergleich/alt-landingpage.html
```

### Beide Seiten lokal nebeneinander

`.claude/launch.json` enthält die Konfiguration `landing-page`, die die
Worktree-Wurzel auf Port 8522 ausliefert:

```bash
python -m http.server 8522 --directory .
```

- Neu: `http://localhost:8522/aeroforesight-ai-landing-page/index.html`
- Alt: `http://localhost:8522/vergleich/alt-landingpage.html`

### Inhaltliche Unterschiede

| | Alt | Neu |
|---|---|---|
| Akzentfarbe | `#1A5FA8` | `#1E3A5F` |
| Schrift | IBM Plex Sans / Mono | Plus Jakarta Sans + Inter |
| Hero | Zweispaltig mit animierter Routen-Grafik | Zentriert, große Typografie, animiertes Raster |
| Dichte | Kompakt, hohe Informationsdichte | Großzügiger Weißraum |
| Nur dort | Dashboard-Vorschau, CIB-Detailblock | Kontaktseite, Rechtsseiten, Burger-Menü |

Aus der alten Seite noch **nicht** übernommen: der Abschnitt „Ein Blick ins
Dashboard" und der CIB-Detailblock unter der Methodik.

## Design-Entscheidungen der neuen Seite

Hergeleitet aus einem Marken-Interview (Zielgruppe B2B-Entscheider und
Investoren, die das Produkt noch nicht kennen; Attribute innovativ, präzise,
vertrauenswürdig, premium, technisch; Referenzen Notion und Apple).

Helles Theme mit zurückhaltendem Navy-Akzent, weil die Seite von der
Belastbarkeit der Zahlen überzeugen muss — ein klassisches, institutionelles
Blau wirkt dort glaubwürdiger als ein Tech-Indigo. Der USP „Zahlen kommen aus
Python, nie vom Sprachmodell" ist zweifach platziert: in den Methodik-Säulen und
als eigener dunkler Vollbreiten-Block, damit er auch beim Überfliegen hängen
bleibt.

Bewegung ist bewusst zurückhaltend: einmaliges Einblenden beim Scrollen,
leichtes Anheben von Karten beim Hover, ein langsam driftendes Hintergrundraster
im Hero, das rund um den Mauszeiger aufleuchtet. `prefers-reduced-motion:
reduce` schaltet alles ab.

Der Zwischenstand der Design-Iterationen liegt unter `.stitch/` (Stitch-Projekt-
und Screen-IDs, generierte Zwischenversionen). Das erlaubt, später wieder in den
Design-Loop einzusteigen, statt neu zu beginnen.
