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
kommt über die CDN, Schriften über Google Fonts, alle Illustrationen sind
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
3. **Tailwind und Schriften über CDN.** Betrifft Landingpage und Dashboard
   gleichermaßen. Für ein Deployment mit Datenhoheit müssen beide Ressourcen
   lokal ausgeliefert werden.

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
