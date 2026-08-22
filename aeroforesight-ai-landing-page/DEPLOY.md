# AeroForesight AI — Landing Page Deployment

## Inhalt dieses Bundles

| Datei | Zweck |
|-------|-------|
| `index.html` | Landingpage (Desktop-Layout, responsiv via Tailwind-Breakpoints) |
| `demo-anfragen.html` | Kontaktseite mit Demo-Anfrageformular |
| `impressum.html` | Impressum — **Platzhaltertext** |
| `datenschutz.html` | Datenschutzerklärung — **Platzhaltertext** |
| `agb.html` | Allgemeine Geschäftsbedingungen — **Platzhaltertext** |
| `design/DESIGN.md` | Design-System und Begründung der Gestaltungsentscheidungen |
| `design/color-tokens.json` | Design-Tokens für die Übernahme ins Dashboard-Theme |

## Design-Tokens

- **Primärfarbe:** Navy `#1E3A5F` (volle Palette `navy-50` bis `navy-950` in `color-tokens.json`)
- **Headline-Font:** Plus Jakarta Sans (Google Fonts: `Plus+Jakarta+Sans`)
- **Body-Font:** Inter (Google Fonts: `Inter`)
- **Border-Radius:** moderat abgerundet, `0.5rem` (8px) als Default
- **Color Mode:** Light
- **Color Variant:** `TONAL_SPOT`

## Vor dem Livegang

1. **Rechtstexte ersetzen.** `impressum.html`, `datenschutz.html` und `agb.html` enthalten nur ein
   Gerüst. Alle mit `[…]` markierten Stellen müssen durch die tatsächlichen Angaben ersetzt und
   rechtlich geprüft werden. Die Seiten tragen oben einen sichtbaren Platzhalter-Hinweis — dieser
   Hinweisblock muss vor Veröffentlichung entfernt werden.
2. **Login-Ziel verdrahten.** Alle „Login“-Buttons zeigen aktuell auf `http://localhost:8511`,
   den lokalen Streamlit-Port aus `.claude/launch.json`. Für das Deployment auf die öffentliche
   Dashboard-URL umbiegen (Suche nach `href="http://localhost:8511"` in allen fünf Seiten).
3. **Formular-Backend anbinden.** Das Formular in `demo-anfragen.html` hat `action="#"` und
   `method="POST"`. Ein Endpunkt muss ergänzt werden (eigener Handler, Formspree, o. ä.), sonst
   geht die Anfrage ins Leere.
4. **Tailwind für Produktion bauen.** Alle Seiten laden aktuell die Tailwind-CDN
   (`cdn.tailwindcss.com`). Das ist für einen Prototyp in Ordnung, für Produktion sollte ein
   gebautes CSS-Bundle erzeugt werden, da die CDN-Variante deutlich langsamer und offiziell
   nicht für den Produktivbetrieb vorgesehen ist.
5. **Kontaktdaten prüfen.** Aktuell hinterlegt: `info@aeroforesight.ai`, „Hochschule der Medien“.
6. **Analytics ergänzen**, falls gewünscht (Plausible, PostHog, Matomo).
7. **Mobil.** Alle fünf Seiten sind responsiv und bei 375px Breite geprüft (kein horizontaler
   Überlauf). Die Navigation klappt unterhalb von 768px in ein Burger-Menü auf, das beide CTAs
   enthält. Der Ablauf-Abschnitt wird auf schmalen Screens zur vertikalen Timeline. Eine separat
   generierte Mobile-Variante gibt es bewusst nicht, es ist ein Layout für alle Breiten.

## Lokale Vorschau

`.claude/launch.json` enthält eine Konfiguration `landing-page`, die den Bundle-Ordner unter
`http://localhost:8521` ausliefert. Alternativ direkt:

```bash
python -m http.server 8521 --directory aeroforesight-ai-landing-page
```

## Bewegung und Grafiken

Alle Illustrationen sind Inline-SVG und damit ohne externe Abhängigkeiten: die beiden Grafiken
im Abschnitt „Problem & Lösung“, die Akteurs-Symbole und die drei Verlaufskurven im Abschnitt
„Ein Lauf, drei Ausblicke“.

Die Animationen sind bewusst zurückhaltend gehalten: Inhalte blenden beim Scrollen einmalig ein
(`.reveal`, gesteuert per `IntersectionObserver`), Karten heben sich beim Hover leicht an
(`.lift`), und die Verbindungslinie im Ablauf-Abschnitt zeichnet sich beim Einblenden.
`prefers-reduced-motion: reduce` schaltet sämtliche Bewegung ab. Die zugehörigen Regeln stehen
im `<style>`-Block jeder Seite, das Skript am Seitenende.

## Deployment-Optionen

- **Statisches Hosting:** Ordner direkt zu Netlify, Vercel oder GitHub Pages deployen.
- **Neben dem Dashboard:** Da das Deployment-Ziel ohnehin ein Hetzner-Server mit Streamlit ist,
  bietet es sich an, die statischen Seiten über den vorgelagerten Reverse Proxy (nginx/Caddy)
  auszuliefern und `/dashboard` auf die Streamlit-App zu routen. Dann funktioniert der
  Login-Button ohne Anpassung.

## Gestaltungsentscheidungen

Helles Theme mit zurückhaltendem Navy-Akzent, weil die Seite Investoren und B2B-Entscheider von
der Belastbarkeit der Zahlen überzeugen muss — ein klassisches, institutionelles Blau wirkt dort
glaubwürdiger als ein Tech-Indigo. Großzügige Weißräume und große, ruhige Typografie folgen den
genannten Referenzen Apple und Notion. Der USP „Zahlen kommen aus Python, nie vom Sprachmodell“
ist bewusst zweifach platziert: einmal in der Hero-Subline und einmal als eigener dunkler
Vollbreiten-Block, damit er auch beim Überfliegen hängen bleibt.
