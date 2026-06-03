# Zusammenfassung - Dynamische Preisgestaltung im Flugverkehr
vgl. Leibniz-Informationszentrum Wirtschaft

---

## Grundprinzip
Der -dynamisch- gebildete Preis hängt von unterschiedlichen Faktoren ab:
* Nachfrage zum jeweiligen Zeitpunkt
* Nähe zum Abflugtermin
* Wettbewerb auf der Strecke
* Restriktionen der Fluggesellschaft

→ Peak-Load-Pricing<br>
→ Luftverkehr ist ein Angebotsoligopol (große Anzahl von Fluggästen und begrenzte Anzahl von Fluggesellschaften)<br>
→ Wenige große Airline-Gruppen konkurrieren mit kleineren Low-Cost-Carrier Anbietern.

Preisunterschiede können unterschiedliche Ursachen haben:
* Geringere Preiselastizität (%-Mengenänderung / %-Preisänderung) der Nachfrage in Spitzenzeiten.<br>
Kunden sind weniger preissensibel.
* Unterschiedliche Kostenstrukturen zwischen Spitzen- und Nebenzeiten.

→ Höhere Preise sind eine Reaktion auf die höhere Zahlungsbereitschaft der Kunden und die höheren Kosten in Spitzenzeiten.

---

## Akteursnetzwerk

### Aktive Preisgestalter
* Fluggesellschaften: Hauptakteure, die Preise aktiv festlegen und anpassen.

### Passive Nachfrageseite
* Nachfrager/Konsumenten: Beeinflussen den Preis durch ihre unterschiedliche Zahlungsbereitschaft.<br>
Setzen den Preis aber nicht selbst fest.

### Indirekte Einflussfaktoren
* Konkurrenz und Regulatoren: Begrenzen den Spielraum der Preisgestaltung durch die Wettbewerbs- und Markeneffekte.
* Marktkontext: Spitzen-/Nebensaison-Bedingungen und zugehörige Kostenunterschiede.

### Vertriebskanäle
* Reisebüros und Online-Buchungsplattformen: Verteilen die Tarife an die Nachfrager/Konsumenten.

---

## Kräfte hinter der Preisbildung

| Kraft                           | Beschreibung                                            |
|---------------------------------|---------------------------------------------------------|
| **Monopoleffekt**               | Marktmacht der Airline auf bestimmten Strecken          |
| **Wettbewerbs-/Markeneffekt**   | Konkurrenzdruck und Markenpositionierung                |
| **Anreizkompatibilitätseffekt** | Selbstselektion der Kunden in verschiedene Tarifklassen |

---

## Informationsfluss

Der Informationsfluss zwischen den Akteuren ist ein Kreislauf (Feedback-Schleife) und beeinflusst die Preisbildung kontinuierlich.
1. Nachfrageinformationen der Nachfrager/Konsumenten und Wettbewerberpreise fließen zur Airline
2. Die Airline setzt einen Preis fest
3. Der Tarif wird über Buchungssysteme auf den Markt gespielt
4. Marktreaktionen fließen zurück zur Airline, die den Preis anpasst

```
┌────────────────────────────────────────────────┐
│                                                │
│                FEEDBACK-SCHLEIFE               │
│                 DER PREISBILDUNG               │
│                                                │
│  ┌──────────────┐         ┌─────────────┐      │
│  │              │         │             │      │
│  │  1. INPUT    │────────>│  2. PREIS-  │      │
│  │              │         │   SETZUNG   │      │
│  │ Nachfrage-   │         │             │      │
│  │ informationen│         │ Airline     │      │
│  │ + Wettbe-    │         │ bildet      │      │
│  │ werberpreise │         │ Tarif       │      │
│  │              │         │             │      │
│  └──────▲───────┘         └──────┬──────┘      │
│         │                        │             │
│         │                        │             │
│         │                        │             │
│         │                        │             │
│  ┌──────┴──────┐         ┌───────▼─────┐       │
│  │             │         │             │       │
│  │ 4. MARKT-   │<────────│ 3. TARIF    │       │
│  │    REAKTION │         │    AUF DEN  │       │
│  │             │         │    MARKT    │       │
│  │ Buchungen/  │         │             │       │
│  │ Nicht-      │         │ Buchungs-   │       │
│  │ Buchungen   │         │ systeme     │       │
│  │ fließen     │         │ publizieren │       │
│  │ zurück      │         │ Tarife      │       │
│  │             │         │             │       │
│  │ → Preis-    │         │             │       │
│  │   anpassung │         │             │       │
│  │             │         │             │       │
│  └─────────────┘         └─────────────┘       │
│                                                │
│  Der Kreislauf wiederholt sich kontinuierlich  │  
│  über den gesamten Buchungszeitraum            │
│                                                │
│                                                │
└────────────────────────────────────────────────┘
```

---

Soll ich dieses Feedback-Schleifen-Diagramm nun in die **Gesamtarchitektur** integrieren oder ein weiteres **Detaildiagramm** für einen bestimmten Schritt erstellen?

---

## Regulatorische Ebene

Die Regulierungen setzen den Preis nicht direkt fest. Sie bilden jedoch die Rahmenbedingungen, innerhalb derer die Fluggesellschaften ihre Preise gestalten können.
Regulierungen können beispielsweise Mindest- oder Höchstpreise festlegen, um den Wettbewerb zu fördern oder Verbraucher zu schützen.

Regulatorien können auf unterschiedlichen Ebenen agieren:
* Nationale Ebene: Department of Transportation (DOT) in den USA. Luftfahrt-Bundesamt (LBA) in Deutschland. Civil Aviation Authority (CAA) in Großbritannien.
* Internationale Ebene: International Civil Aviation Organization (ICAO). International Air Transport Association (IATA).
* Europäische Ebene: European Union Aviation Safety Agency (EASA)