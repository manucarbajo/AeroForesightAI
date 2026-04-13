# Sub-Agenten Überlegung

###

Im folgenden wird eine mögliche Modellierung des Projekts dargestellt. Diese ist lediglich eine Überlegung und hat noch keine technische Version. 

### Grundprinzipien des Modells:
- **Agenten** repräsentieren Organisationen oder Gruppen mit eigenen Zielen, Entscheidungsfähigkeiten und Verhaltensweisen.
- **Subagenten** sind spezifische Untereinheiten innerhalb eines Hauptagents, die jeweils eigene Zustände und Einflussfaktoren haben.
- **Interaktionen** beschreiben die dynamischen Beziehungen zwischen Agenten – z. B. Buchungen, Genehmigungen, Feedback oder Kooperationen.
- **Zustände** sind aktuelle Bedingungen oder Merkmale eines Agenten (z. B. Budget, Flugplan, Kapazität).
- **Einflussfaktoren** sind externe oder interne Bedingungen, die das Verhalten oder die Entscheidungen eines Agenten beeinflussen (z. B. Preise, Regulierungen, Technologie).


## Konsument Agent
**Aufgabe:** Repräsentiert die Bedürfnisse und das Verhalten der Passagiere und Nutzer des Flugverkehrs.

### Subagenten
- **Private Passagiere:** Individuelle Reisende, die nach günstigen Preisen und bequemen Flugzeiten suchen.
- **Geschäftspassagiere:** Reisende für berufliche Zwecke, die flexiblen Tarifen und Business-Class-Angeboten bevorzugen.
- **Reisebüros und Reiseveranstalter:** Vermitteln Flüge und Reisepakete an Endkunden.
- **Logistikunternehmen:** Nutzen den Flugverkehr für Fracht und Gütertransport.

### Interaktionen
- Buchung von Flügen bei Anbietern.
- Feedback über Servicequalität an Anbieter und Regulierungsstellen.
- Beeinflussung der Nachfrage durch Kaufentscheidungen.

---

## Anbieter Agent
**Aufgabe:** Repräsentiert die Unternehmen im Flugverkehrsmarkt, die Dienstleistungen und Produkte anbieten.

### Subagenten
- **Fluggesellschaften:** Linienfluggesellschaften, Billigfluggesellschaften, Charterfluggesellschaften, Frachtfluggesellschaften.
- **Flughäfen:** Großflughäfen, Regionalflughäfen, Spezialflughäfen.
- **Luftfahrtindustrie:** Flugzeughersteller, Zulieferunternehmen, Wartungsunternehmen.
- **Bodendienstleister:** Ground Handling, Flugsicherung, Flughafenbetreiber.
- **Treibstoff-/Energieversorger:** Flugtreibstofflieferanten, Anbieter nachhaltiger Energien.
- **IT- und Technologieanbieter:** Flugreservierungssysteme, Flugverkehrsmanagement-Systeme.

### Interaktionen
- Koordination von Flugplänen und Slots mit Flughäfen.
- Bestellung von Flugzeugen und Ersatzteilen von der Luftfahrtindustrie.
- Lieferung von Treibstoffen und Energien für den Flugbetrieb.
- Entwicklung und Implementierung digitaler Lösungen mit IT-Anbietern.

---

## Regulatorien Agent
**Aufgabe:** Repräsentiert die Behörden und Organisationen, die den Flugverkehrsmarkt regulieren.

### Subagenten
- **Zivilluftfahrtbehörden:** Nationale und internationale Behörden für Flugsicherheit.
- **Regierungsstellen:** Verkehrsministerien, Wirtschaftsministerien.
- **Internationale Organisationen:** ICAO, IATA, ACI.
- **Umweltbehörden:** Regulierungsstellen für Emissionen und Lärmschutz.
- **Sicherheitsbehörden:** Flughafensicherheit, biometrische Kontrollen.
- **Wettbewerbs- und Kartellbehörden:** Verhinderung von Monopolen.

### Interaktionen
- Setzen von Sicherheits-, Umwelt- und Wettbewerbsstandards.
- Genehmigung von Flugzeugen und Flughäfen.
- Überwachung der Einhaltung von Vorschriften durch Anbieter.
- Sammlung von Feedback von Konsumenten für regulatorische Anpassungen.

---

## Interaktionen zwischen den Agenten

### Konsument Agent → Anbieter Agent
- Buchung von Flügen und Reiseangeboten.
- Feedback über Servicequalität und Preise.

### Anbieter Agent → Regulator Agent
- Einholen von Genehmigungen und Zertifizierungen.
- Meldung von Sicherheitsvorfällen und Umweltdaten.

### Regulator Agent → Anbieter Agent
- Vorgaben von Sicherheits- und Umweltrichtlinien.
- Durchführung von Audits und Inspektionen.

### Konsument Agent → Regulator Agent
- Meldung von Beschwerden und Sicherheitsbedenken.
- Teilnahme an öffentlichen Anhörungen zu neuen Vorschriften.

---

## Subagenten und ihre Spezifischen Interaktionen

### Fluggesellschaften (Anbieter Subagent)
- Koordination mit Flughäfen über Start- und Landerechte.
- Bestellung von Flugzeugen und Wartungsdienstleistungen von der Luftfahrtindustrie.

### Flughäfen (Anbieter Subagent)
- Zuweisung von Slots an Fluggesellschaften.
- Bereitstellung von Bodendiensten und Sicherheitskontrollen.

### Luftfahrtindustrie (Anbieter Subagent)
- Lieferung von Flugzeugen und Ersatzteilen an Fluggesellschaften.
- Entwicklung nachhaltiger Technologien in Kooperation mit IT-Anbietern.

### IT- und Technologieanbieter (Anbieter Subagent)
- Entwicklung von Softwarelösungen für Flugreservierung und Flugverkehrsmanagement.
- Integration von digitalen Lösungen in die Betriebsabläufe von Fluggesellschaften und Flughäfen.

---

## Konsumenten Agent – Subagenten und Zustände

### Private Passagiere
- **Zustände:** Reiseziel, -zeitraum, Budget, Vorlieben.
- **Einflussfaktoren:** Preis, Flugdauer, Komfort, Servicequalität.

### Geschäftspassagiere
- **Zustände:** Geschäftstermin, Flexibilität, Bedarf an Business-Class.
- **Einflussfaktoren:** Flexibilität der Flugzeiten, Verfügbarkeit von Business-Class, Wi-Fi und Arbeitsmöglichkeiten an Bord.

### Reisebüros und Reiseveranstalter
- **Zustände:** Verfügbarkeit von Flügen, saisonale Nachfrage.
- **Einflussfaktoren:** Sondertarife, Marketingkampagnen, Kundenfeedback.

### Logistikunternehmen
- **Zustände:** Frachtvolumen, Lieferzeiten.
- **Einflussfaktoren:** Zuverlässigkeit der Lieferung, Transportkosten, Frachtterminals.

---

## Anbieter Agent – Subagenten und Zustände

### Fluggesellschaften
- **Zustände:** Flugplan, Kapazität, Treibstoffpreise.
- **Einflussfaktoren:** Wettbewerb, Treibstoffkosten, Regulierungen.

### Flughäfen
- **Zustände:** Kapazität, Wetterbedingungen.
- **Einflussfaktoren:** Flugverkehr, Infrastruktur, Sicherheit.

### Luftfahrtindustrie
- **Zustände:** Produktion, Forschung und Entwicklung.
- **Einflussfaktoren:** Technologische Innovationen, Nachfrage nach Flugzeugen, Rohstoffpreise.

### Bodendienstleister
- **Zustände:** Personal, Ausrüstung.
- **Einflussfaktoren:** Flugfrequenz, Wartungsintervalle.

### Treibstoff-/Energieversorger
- **Zustände:** Preise, Verfügbarkeit.
- **Einflussfaktoren:** Globale Nachfrage, Politische Situationen.

### IT- und Technologieanbieter
- **Zustände:** Technologische Fortschritte, Systemintegration.
- **Einflussfaktoren:** Innovationen, Datensicherheit.

---

## Regulatorien Agent – Subagenten und Zustände

### Zivilluftfahrtbehörden
- **Zustände:** Sicherheitsstandards, Zertifizierungen.
- **Einflussfaktoren:** Technologische Entwicklungen, Internationale Abkommen.

### Regierungsstellen
- **Zustände:** Politische Richtlinien, Wirtschaftliche Interessen.
- **Einflussfaktoren:** Wahlen, Wirtschaftskrisen.

### Internationale Organisationen
- **Zustände:** Globale Standards, Abkommen.
- **Einflussfaktoren:** Internationale Beziehungen, Krisen.

### Umweltbehörden
- **Zustände:** Emissionsgrenzwerte, Lärmschutz.
- **Einflussfaktoren:** Öffentliche Meinung, Technologische Fortschritte.

### Sicherheitsbehörden
- **Zustände:** Sicherheitsrisiken, Terrorgefahr.
- **Einflussfaktoren:** Globale Sicherheitslage, Technologische Überwachung.

### Wettbewerbs- und Kartellbehörden
- **Zustände:** Marktkonzentration, Fusionen.
- **Einflussfaktoren:** Wirtschaftliche Macht, Politischer Druck.

---

## Interaktionen zwischen den Agenten – Zusammenfassung

### Konsument Agent → Anbieter Agent
- **Zustände:** Buchung von Flügen, Feedback.
- **Einflussfaktoren:** Preise, Servicequalität.

### Anbieter Agent → Regulator Agent
- **Zustände:** Genehmigungen, Meldung von Vorfällen.
- **Einflussfaktoren:** Vorschriften, Strafen.

### Regulator Agent → Anbieter Agent
- **Zustände:** Richtlinien, Audits.
- **Einflussfaktoren:** Compliance, Sanktionen.

### Konsument Agent → Regulator Agent
- **Zustände:** Beschwerden, Teilnahme an Anhörungen.
- **Einflussfaktoren:** Öffentliche Meinung, Politischer Druck.

---

## Subagenten und ihre Spezifischen Zustände und Einflussfaktoren

### Fluggesellschaften
- **Zustände:** Flugpläne, Kapazität.
- **Einflussfaktoren:** Wettbewerb, Treibstoffpreise.

### Flughäfen
- **Zustände:** Kapazität, Wetter.
- **Einflussfaktoren:** Flugverkehr, Infrastruktur.

### Luftfahrtindustrie
- **Zustände:** Produktion, F&E.
- **Einflussfaktoren:** Innovationen, Rohstoffpreise.

### IT- und Technologieanbieter
- **Zustände:** Technologie, Integration.
- **Einflussfaktoren:** Innovationen, Datensicherheit.