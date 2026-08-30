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

1. ~~**Formular ohne Backend.**~~ **Erledigt am 2026-08-30.** Das Formular zeigt
   auf `POST /demo-anfrage` (`dashboard/web/landing_route.py`); jede Anfrage
   wird als Zeile JSON angehängt — Vorgabe `outputs/demo_anfragen.jsonl`, über
   `AF_DEMO_ANFRAGEN` verlegbar. **Kein Mailversand, kein externer Dienst**:
   Eine Anfrage über einen fremden Server zu leiten wäre genau der Widerspruch,
   den Punkt 3 abräumt. Die Pflichtfelder prüft der **Server** — ein
   `required`-Attribut ist eine Bitte an den Browser, keine Schranke —, und der
   Absender sieht in beiden Fällen, was passiert ist.

   **Solange Punkt 2 offen ist, trägt die Seite einen sichtbaren Hinweis**, dass
   die verlinkte Datenschutzerklärung ein Entwurf ist. Die Ablage enthält
   personenbezogene Daten; sie gehört in die Sicherung und nicht in ein
   öffentlich erreichbares Verzeichnis.
2. **Rechtstexte sind ein Gerüst.** Die Gliederung steht — § 5 DDG, Art. 13
   DSGVO, die üblichen Vertragsteile —, und **jede Pflichtangabe ist als
   benannte Lücke markiert**: `[Straße und Hausnummer]`, nicht `[…]`. Man sieht,
   *was* fehlt, nicht nur *dass* etwas fehlt. Die Inhalte brauchen die
   Firmendaten und eine juristische Prüfung; erfundene Rechtstexte wären
   schlimmer als erkennbar unfertige.

   Der gelbe Hinweisblock bleibt, **solange eine Lücke offen ist** — er ist das
   Einzige, was einen Besucher davor bewahrt, den Entwurf für verbindlich zu
   halten. `tests/test_rechtstexte.py` hält ihn fest, prüft die Vollständigkeit
   der Abschnitte und dass **jede** Lücke in der Liste unten steht.

### Was zu liefern ist

**Impressum** — Quelle: Handelsregisterauszug und Gesellschaftsvertrag.

| Lücke | Anmerkung |
| --- | --- |
| Rechtsform und vollständiger Name des Anbieters | wie im Register eingetragen |
| Straße und Hausnummer · PLZ und Ort · Land | ladungsfähige Anschrift, kein Postfach |
| Name der vertretungsberechtigten Person | Geschäftsführung |
| Telefonnummer | § 5 DDG verlangt einen zweiten Kanal neben der E-Mail |
| Registergericht und Registernummer, sofern vorhanden | entfällt bei Einzelunternehmen |
| USt-IdNr. | nur wenn vorhanden; sonst Abschnitt streichen |
| Name · Anschrift (§ 18 Abs. 2 MStV) | inhaltlich Verantwortlicher, oft identisch mit der Geschäftsführung |

**Datenschutzerklärung** — Quelle: Verarbeitungsverzeichnis, Auftragsverarbeiter-Verträge.

| Lücke | Anmerkung |
| --- | --- |
| Name und Anschrift des Verantwortlichen | Art. 13 Abs. 1 lit. a DSGVO |
| Auflistung eingesetzter Dienstleister … | Hosting-Provider und jeder weitere Auftragsverarbeiter |
| Angabe, ob und welche Cookies eingesetzt werden … | **Stand heute setzt die Seite keine** — auch das gehört hin |
| Aufbewahrungsdauer | je Verarbeitungszweck; die Demo-Anfragen liegen in `outputs/demo_anfragen.jsonl` |
| Behörde und Anschrift | zuständige Aufsichtsbehörde nach Sitz |
| Datum | Stand der Erklärung |

**AGB** — Quelle: Vertragsmuster, kaufmännische Festlegung.

| Lücke | Anmerkung |
| --- | --- |
| Anbieter | wie im Impressum |
| Beschreibung des Vertragsschlusses … | Angebotsannahme in Textform o. Ä. |
| Zahlungsziel · netto/brutto | kaufmännisch festzulegen |
| Laufzeit · Verlängerungsregelung · Kündigungsfrist | ebenso |
| Service-Level-Vereinbarung | falls zugesagt; sonst Abschnitt streichen |
| Gerichtsstand | Sitz des Anbieters, bei Verbrauchern eingeschränkt |
| Datum | Stand der AGB |

Sind alle Lücken gefüllt, entfällt der Hinweisblock — und der Test darüber
überspringt sich von selbst.
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
