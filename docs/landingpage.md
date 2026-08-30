# Landingpage

Die Landingpage liegt unter `aeroforesight-ai-landing-page/` und wird von
derselben Anwendung ausgeliefert wie das Dashboard.

## Adressen

```
python -m dashboard.web.app --port 8511
```

| Adresse | Inhalt |
|---|---|
| `/` | Landingpage |
| `/demo-anfragen.html` | Kontaktseite mit Anfrageformular |
| `/impressum.html`, `/datenschutz.html`, `/agb.html` | Rechtsseiten, **Platzhaltertexte** |
| `/app/` | Dashboard — Simulation starten |
| `/app/runs` | Ergebnisse ansehen |
| `/app/doku` | Handbuch |

Ein Server, eine Adresse. Der Login-Button der Landingpage zeigt auf `/app/`,
das Logo im Dashboard zurück auf `/`. Beide Verweise sind relativ und
funktionieren damit unter jeder Domain, ohne Anpassung.

## Aufbau

Statische HTML-Seiten ohne Build-Schritt und ohne lokale Dateien: Tailwind
kommt seit dem 2026-08-30 aus einem lokalen Build, die Schriften liegen im Repo, alle Illustrationen sind
Inline-SVG. Deshalb genügt es, sie zu servieren —
`dashboard/web/landing_route.py` meldet dafür zwei Flask-Routen an und prüft
jede Anfrage gegen die tatsächlich vorhandenen Dateien.

Die Design-Tokens in `design/color-tokens.json` sind zugleich die Quelle für
das Dashboard-Theme; die Werte stehen im Code in `dashboard/web/theme.py` und
in der Tailwind-Konfiguration in `dashboard/web/app.py`.

## Offene Punkte

1. **Formular ohne Backend.** `demo-anfragen.html` hat `action="#"`. Anfragen
   gehen ins Leere; ein Endpunkt fehlt.
2. **Rechtstexte sind Platzhalter.** Alle mit `[…]` markierten Stellen müssen
   ersetzt und rechtlich geprüft werden. Der gelbe Hinweisblock auf den drei
   Seiten muss vor Veröffentlichung raus.
3. ~~**Tailwind und Schriften über CDN.**~~ **Erledigt am 2026-08-30.**
   Tailwind kommt aus einem lokalen Build (`npm run build:css` →
   `assets/00-tailwind.css`), die Schriften aus dem Repo
   (`scripts/schriften_holen.py` → `assets/fonts/` und `01-schriften.css`).
   Material Symbols ist ein Teilsatz von 5 KiB statt der vollständigen
   variablen Schrift. Drei Wächter halten das: keine benutzte Klasse ohne
   Regel, kein benutztes Symbol außerhalb des Teilsatzes, und — die Zusage
   selbst — **keine Netzwerkanfrage an einen fremden Host**, gemessen über
   alle Bereiche und alle fünf Seiten.

Deployment-Schritte: `aeroforesight-ai-landing-page/DEPLOY.md`.

## Historie

Es gab zwei Vorgänger, beide abgelöst:

Eine **Streamlit-Landingpage** (`dashboard/landing.py`) lebte *in* der
Dashboard-App und wurde beim Klick auf einen CTA durch ein Login-Formular
ersetzt. Sie liegt nur noch auf den Branches `feature/landing-page-phase1` und
`feature/landing-login-redesign`, nicht auf `main`.

Ein **statischer Nachbau** davon lag unter `vergleich/`, um beide Varianten
nebeneinander stellen zu können. Er wurde nach der Entscheidung für die neue
Seite entfernt.
