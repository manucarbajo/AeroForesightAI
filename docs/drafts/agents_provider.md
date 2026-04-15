Anbieterseite
---

## Agent A1: Fluggesellschaft
### Eigenschaften

```
Fluggesellschaft
├── Marktposition (Marktanteil, Streckennetz)
├── Markenidentität (Differenzierungsmerkmal)
├── Gesamtkapazität (Flottengröße)
└── Gewinnmaximierungsziel
```

---

### Subagent A1.1: Prognose-Modul

#### Funktion
Erstellt Nachfrageprognosen und überwacht deren Eintreffen während des Buchungszeitraums

#### Einflussfaktoren

```
EINGANGSGRÖSSEN
│
├── Exogene Faktoren
│   ├── Saisonalität (Peak / Off-Peak)
│   ├── Wochentag und Tageszeit
│   ├── Feiertage und Ferienzeiten
│   └── Gesamtmarktnachfrage auf der Route
│
├── Historische Daten
│   ├── Vergangene Buchungsverläufe
│   ├── Vergangene Auslastungsraten
│   └── Verhältnis Geschäfts- zu Freizeitreisenden
│
├── Aktuelle Buchungsdaten (von A1.3)
│   ├── Bisherige Buchungen im aktuellen Zyklus
│   ├── Buchungsgeschwindigkeit (Buchungen pro Zeiteinheit)
│   └── Verteilung auf Ticketkategorien
│
└── Marktinformationen (von A2)
    ├── Wettbewerberpreise
    └── Wettbewerberverfügbarkeiten
```

#### Ausgaben

| Ausgabe | Empfänger |
|---|---|
| Prognostizierte Gesamtnachfrage | A1.2 Pricing-Modul |
| Prognostizierter Nachfragemix (K1/K2-Anteil) | A1.2 Pricing-Modul |
| Soll-Ist-Abweichung der Nachfrage | A1.2 Pricing-Modul |
| Nachfrageelastizitätsschätzung | A1.2 Pricing-Modul |

---

### Subagent A1.2: Pricing-Modul

#### Funktion
Zentrale Preissetzungsinstanz mit mehreren Strategieebenen

#### Einflussfaktoren und Mechanismen

```
PREISSETZUNG
│
├── 1. Preisdifferenzierung 2. Ordnung (Selbstselektion)
│   ├── Definition von Ticketkategorien
│   │   ├── Premium/Flex-Ticket (hohe Qualität)
│   │   │   ├── Freie Umbuchung/Stornierung
│   │   │   ├── Kein Mindestaufenthalt
│   │   │   └── Hoher Preis → Zielgruppe: K1
│   │   │
│   │   └── Restriktives Ticket (niedrige Qualität)
│   │       ├── Keine/teure Umbuchung
│   │       ├── Mindestaufenthalt (z.B. Samstagnacht)
│   │       └── Niedriger Preis → Zielgruppe: K2
│   │
│   └── Anreizkompatibilitätsrestriktionen
│       ├── K1 muss Flex-Ticket gegenüber restriktivem
│       │   Ticket bevorzugen (Nettoutzen höher)
│       ├── K2 muss restriktives Ticket gegenüber
│       │   Flex-Ticket bevorzugen
│       └── Beide Typen müssen Teilnahme bevorzugen
│           (individueller Rationalitätsconstraint)
│
├── 2. Preisdifferenzierung 3. Ordnung (Gruppenmerkmale)
│   ├── Direkte Segmentierung wo möglich
│   │   ├── Studentenrabatte
│   │   ├── Seniorentarife
│   │   └── Firmenverträge
│   └── Indirekte Segmentierung über Produktattribute
│
├── 3. Dynamische Preisanpassung
│   │
│   ├── Nachfragegetrieben (von A1.1)
│   │   ├── Nachfrage > Prognose → Preiserhöhung
│   │   ├── Nachfrage < Prognose → Preissenkung
│   │   └── Günstige Kontingente schließen/öffnen
│   │
│   ├── Kapazitätsgetrieben (von A1.3)
│   │   ├── Hohe Restkapazität → Preissenkung
│   │   ├── Niedrige Restkapazität → Preiserhöhung
│   │   └── Überbuchungssteuerung
│   │
│   ├── Wettbewerbsgetrieben (von A2)
│   │   ├── Wettbewerber senkt Preis → Reaktion?
│   │   ├── Monopoleffekt (mehr Wettbewerb → weniger
│   │   │   Preisdifferenzierung möglich)
│   │   ├── Markeneffekt (mehr Wettbewerb → mehr
│   │   │   Heterogenität → mehr Dispersion)
│   │   └── Anreizkompatibilitätseffekt
│   │
│   └── Zeitgetrieben (von R3)
│       ├── Frühbucherrabatte
│       ├── Last-Minute-Preise
│       └── Peak-Load Pricing
│
└── 4. Peak-Load Pricing
    ├── Spitzenzeiten → höhere Preise
    ├── Nebenzeiten → niedrigere Preise
    └── Kapazitätsengpässe einpreisen
```

#### Zentrale Entscheidungsparameter

| Parameter | Beschreibung | Quelle |
|---|---|---|
| Reservationspreise der Segmente | Maximale Zahlungsbereitschaft K1/K2 | A1.1 (geschätzt) |
| Qualitätspräferenzparameter θ | Unterscheidet K1 (hoch) von K2 (niedrig) | Modellparameter |
| Transportkostensatz t | Kosten der Abweichung vom Wunschflug | Modellparameter |
| Wettbewerberpreise | Aktuelle Preise der Konkurrenz | A2 |
| Restkapazität | Verfügbare Plätze pro Kategorie | A1.3 |
| Nachfrageprognose-Abweichung | Soll-Ist-Differenz | A1.1 |
| Zeitpunkt im Buchungszeitraum | Früh vs. spät | R3 |

#### Ausgaben

| Ausgabe | Empfänger |
|---|---|
| Aktuelle Preise pro Ticketkategorie | A2 Vertriebsplattform |
| Verfügbare Ticketkategorien | A2 Vertriebsplattform |
| Preisänderungshistorie | R2 Monitoring |

---

### Subagent A1.3: Kapazitäts-Modul

#### Funktion
Verwaltet die physische und kommerzielle Kapazität

#### Einflussfaktoren

```
KAPAZITÄTSVERWALTUNG
│
├── Physische Kapazität
│   ├── Gesamtsitzplätze pro Flug (fix)
│   ├── Anzahl Flüge auf der Route (von A1.4)
│   └── Flugzeugtyp / Konfiguration
│
├── Kommerzielle Kontingentierung
│   ├── Kontingent Premium/Flex-Tickets
│   ├── Kontingent restriktive Tickets
│   ├── Überbuchungsrate
│   └── Nested Booking (hierarchische Verfügbarkeit)
│
├── Buchungsstatus (laufend aktualisiert)
│   ├── Gebuchte Plätze pro Kategorie
│   ├── Verbleibende Plätze pro Kategorie
│   ├── Stornierungen und Umbuchungen
│   └── No-Show-Rate (historisch)
│
└── Kapazitätsengpässe
    ├── Ausverkauft-Meldung → Nachfrage geht
    │   an Wettbewerber
    └── Warteliste bei Überbuchung
```

#### Ausgaben

| Ausgabe | Empfänger |
|---|---|
| Verbleibende Kapazität pro Kategorie | A1.1 Prognose-Modul |
| Kapazitätsauslastung in Prozent | A1.2 Pricing-Modul |
| Verfügbarkeitsstatus | A2 Vertriebsplattform |
| Gebuchte Einheiten pro Kategorie | R2 Monitoring |

---

### Subagent A1.4: Angebotsplanung

#### Funktion
Strategische Planung des Flugangebots

#### Einflussfaktoren

```
ANGEBOTSPLANUNG
│
├── Strategische Entscheidungen
│   ├── Bediente Routen (Herkunft-Ziel-Paare)
│   ├── Flugfrequenz pro Route
│   ├── Abflugzeiten (Positionierung auf Zeitachse)
│   └── Saisonale Anpassungen
│
├── Wettbewerbspositionierung
│   ├── Zeitliche Differenzierung zu Wettbewerbern
│   │   (→ beeinflusst Transportkosten der Kunden)
│   ├── Nischenbesetzung vs. Kopf-an-Kopf-Wettbewerb
│   └── Hub-and-Spoke vs. Punkt-zu-Punkt
│
├── Einflussfaktoren
│   ├── Marktstrukturvorgaben (von R1)
│   ├── Nachfrageprognosen (von A1.1)
│   ├── Verfügbare Flotte/Kapazität
│   └── Slot-Verfügbarkeit an Flughäfen
│
└── Modellbezug (Liu/Serfes 2006)
    ├── Position auf dem Hotelling-Kreis
    │   (räumliche Differenzierung = zeitliche
    │    Differenzierung über Abflugzeiten)
    ├── Anzahl Marken/Produkte pro Airline
    └── Symmetrische vs. asymmetrische Positionierung
```

#### Ausgaben

| Ausgabe | Empfänger |
|---|---|
| Flugrouten und Abflugzeiten | A1.3 Kapazitäts-Modul |
| Positionierung im Markt | A1.1 Prognose-Modul |
| Anzahl angebotener Flüge | R1 Marktstruktur |

---

## Agent A2: Vertriebsplattform

#### Funktion
Zentraler Informations- und Transaktionsbroker

```
VERTRIEBSPLATTFORM
│
├── Informationsaggregation
│   ├── Sammelt Preise ALLER Fluggesellschaften
│   ├── Sammelt Verfügbarkeiten aller Kategorien
│   ├── Sortier- und Filterfunktionen
│   └── Preisvergleichsfunktion
│
├── Transaktionsabwicklung
│   ├── Nimmt Buchungsanfragen von K1/K2 entgegen
│   ├── Leitet Buchungen an jeweilige A1 weiter
│   ├── Bestätigt Buchungen
│   └── Verarbeitet Stornierungen
│
├── Informationsflüsse
│   │
│   ├── EINGEHEND
│   │   ├── Von A1.2: Preise und Ticketkategorien
│   │   ├── Von A1.3: Verfügbarkeiten
│   │   └── Von K1/K2: Buchungsanfragen
│   │
│   └── AUSGEHEND
│       ├── An K1/K2: Gesamtmarktübersicht
│       ├── An A1.2: Wettbewerberpreise (Transparenz)
│       ├── An R2: Transaktionsdaten
│       └── An A1.3: Buchungsbestätigungen
│
└── Marktmechanismus
    ├── Erhöht Preistransparenz
    ├── Senkt Suchkosten für Konsumenten
    └── Ermöglicht Wettbewerbsbeobachtung
        zwischen Airlines
```

---

## Interaktionsdiagramm der Anbieterseite

```
                    R1 (Marktstruktur)
                         │
                         ▼
    ┌─────────── A1: Fluggesellschaft i ────────────┐
    │                                               │
    │  A1.4 ──────→ A1.3 ──────→ A1.1 ──────→ A1.2  │
    │  Angebots-    Kapazität    Prognose    Pricing│
    │  planung         │            ▲           │   │
    │                  │            │           │   │
    │                  └────────────┘           │   │
    │              (Kapazitäts-Updates)         │   │
    └───────────────────────────────────────────┘   │
                                                    │
                                                    ▼
                                        A2: Vertriebsplattform
                                               │         ▲
                                               │         │
                                               ▼         │
                                    Wettbewerberpreise───┘
                                    fließen zurück       
                                    an alle A1.2         
```
