# Regulatorenseite

---

## Agent R1: Marktstruktur-Agent

### Grundcharakterisierung

```
Marktstruktur-Agent
├── Definiert den Rahmen des Marktes
├── Steuert Marktein- und -austritte
├── Bestimmt Wettbewerbsintensität
├── Berechnet Konzentrationsmaße
└── Ermöglicht Szenarienvariation
```

---

### Konfigurationsparameter

```
MARKTSTRUKTUR-KONFIGURATION
│
├── 1. Marktform
│   ├── Monopol (n = 1 Fluggesellschaft)
│   ├── Duopol (n = 2 Fluggesellschaften)
│   ├── Oligopol (n > 2 Fluggesellschaften)
│   └── Variabel einstellbar für Szenarienvergleich
│
├── 2. Routenstruktur
│   ├── Anzahl simulierter Routen
│   ├── Routencharakteristik
│   │   ├── Kurz- vs. Langstrecke
│   │   ├── Hub-Verbindung vs. Punkt-zu-Punkt
│   │   └── Touristisch vs. geschäftlich dominiert
│   └── Routenzuweisung an Fluggesellschaften
│
├── 3. Marktgröße
│   ├── Gesamtnachfrage pro Route
│   │   ├── Anzahl potentieller Passagiere
│   │   └── Verhältnis K1 zu K2
│   │       (z.B. 30% Geschäft / 70% Freizeit)
│   └── Saisonale Nachfrageschwankungen
│
├── 4. Wettbewerbsparameter
│   ├── Markteintrittsbarrieren
│   │   ├── Slot-Verfügbarkeit
│   │   ├── Kapitalanforderungen
│   │   └── Netzwerkeffekte bestehender Airlines
│   │
│   ├── Marktaustrittsbarrieren
│   │   ├── Versunkene Kosten
│   │   └── Langfristige Verträge
│   │
│   └── Symmetrie der Wettbewerber
│       ├── Symmetrisch (gleiche Größe/Kapazität)
│       └── Asymmetrisch (unterschiedliche Marktanteile)
│
├── 5. Kostenstruktur
│   ├── Fixkosten pro Flug (flugzeugabhängig)
│   ├── Variable Kosten pro Passagier
│   ├── Grenzkosten der Kapazitätserweiterung
│   └── Kostenasymmetrien zwischen Airlines
│
└── 6. Produktdifferenzierung
    ├── Horizontale Differenzierung
    │   ├── Abflugzeiten (Hotelling-Modell)
    │   ├── Positionierung auf dem Zeitkreis
    │   └── Grad der zeitlichen Überlappung
    │
    └── Vertikale Differenzierung
        ├── Ticketkategorien (Qualitätsstufen)
        ├── Servicequalität der Airlines
        └── Markenwahrnehmung
```

---

### Konzentrationsmaße

```
BERECHNUNG KONZENTRATIONSMASZE
│
├── Herfindahl-Hirschman-Index (HHI)
│   │
│   │  HHI = Σ (s_i)²
│   │
│   │  s_i = Marktanteil der Fluggesellschaft i
│   │
│   ├── HHI = 10.000 → Monopol
│   ├── HHI > 2.500  → Hoch konzentriert
│   ├── HHI 1.500–2.500 → Mäßig konzentriert
│   └── HHI < 1.500  → Gering konzentriert
│
├── Konzentrationsrate CR_k
│   │
│   │  CR_k = Σ_{i=1}^{k} s_i
│   │
│   │  (Summe der k größten Marktanteile)
│   │
│   ├── CR_1 → Anteil der größten Airline
│   ├── CR_4 → Anteil der vier größten Airlines
│   └── Ermöglicht Vergleich über Szenarien
│
├── Anzahl effektiver Wettbewerber
│   │
│   │  n_eff = 1 / HHI (normiert auf 10.000)
│   │
│   └── Maß für tatsächliche Wettbewerbsintensität
│
└── Dynamische Aktualisierung
    ├── Neuberechnung nach jedem Buchungszyklus
    ├── Berücksichtigt tatsächliche Buchungsanteile
    └── Meldet Veränderungen an R2
```

---

### Marktein- und -austrittsmechanismus

```
MARKTDYNAMIK
│
├── Markteintritt
│   ├── Auslöser
│   │   ├── Hohe Profitabilität auf Route
│   │   ├── Übersteigt Eintrittsbarrieren-Schwelle
│   │   └── Szenariogesteuert (exogen vorgegeben)
│   │
│   ├── Ablauf
│   │   ├── Neue A1-Instanz wird erzeugt
│   │   ├── A1.4 erhält Routenzuweisung
│   │   ├── A1.3 erhält Kapazitätszuweisung
│   │   └── HHI wird neu berechnet
│   │
│   └── Auswirkungen
│       ├── Wettbewerbsintensität steigt
│       ├── Preise tendenziell sinkend
│       └── Preisdispersion verändert sich
│           (zentrale Untersuchungsfrage)
│
└── Marktaustritt
    ├── Auslöser
    │   ├── Verluste über definierte Periodenzahl
    │   ├── Unterschreitung Mindestauslastung
    │   └── Szenariogesteuert (exogen vorgegeben)
    │
    ├── Ablauf
    │   ├── A1-Instanz wird deaktiviert
    │   ├── Kapazität wird aus Markt entfernt
    │   ├── Bestehende Buchungen werden behandelt
    │   └── HHI wird neu berechnet
    │
    └── Auswirkungen
        ├── Wettbewerbsintensität sinkt
        ├── Restliche Airlines gewinnen Marktanteile
        └── Preisdispersion verändert sich
```

---

### Ausgaben

| Ausgabe | Empfänger |
|---|---|
| Marktstrukturvorgaben (Anzahl Airlines, Routen) | A1 (alle Instanzen) |
| Routenzuweisungen | A1.4 Angebotsplanung |
| Wettbewerbssymmetrie-Parameter | A1 (alle Instanzen) |
| HHI und Konzentrationsmaße | R2 Monitoring |
| Marktein-/-austrittsereignisse | A1, A2, R2 |
| Marktgröße und Nachfragepotential | A1.1 Prognose-Modul |
| K1/K2-Verhältnis | A1.1 Prognose-Modul |

---

## Agent R2: Monitoring-/Messungs-Agent (1 Instanz)

### Grundcharakterisierung

```
Monitoring-/Messungs-Agent
├── Zentraler Datensammler der Simulation
├── Berechnet alle relevanten Metriken
├── Prüft theoretische Vorhersagen
├── Ermöglicht Ex-post-Analyse
└── Erzeugt Simulationsergebnisse
```

---

### Datenerfassung

```
DATENERFASSUNG
│
├── 1. Transaktionsdaten (von A2)
│   ├── Pro Buchung
│   │   ├── Gezahlter Preis
│   │   ├── Route
│   │   ├── Fluggesellschaft
│   │   ├── Ticketkategorie (Flex/Restriktiv)
│   │   ├── Buchungszeitpunkt
│   │   ├── Abflugzeitpunkt
│   │   ├── Konsumententyp (K1/K2)
│   │   └── Konsumentennutzen (realisiert)
│   │
│   └── Aggregiert pro Zeitschritt
│       ├── Anzahl Buchungen
│       ├── Durchschnittspreis
│       ├── Preisrange (Min/Max)
│       └── Buchungsverteilung auf Airlines
│
├── 2. Angebotsdaten (von A1 über A2)
│   ├── Pro Fluggesellschaft pro Zeitschritt
│   │   ├── Angebotene Preise pro Kategorie
│   │   ├── Verfügbare Kapazität
│   │   ├── Auslastungsrate
│   │   ├── Umsatz
│   │   └── Gewinn/Verlust
│   │
│   └── Preishistorie
│       ├── Alle Preisänderungen mit Zeitstempel
│       ├── Preispfad über Buchungszeitraum
│       └── Preisanpassungsrichtung und -ausmaß
│
├── 3. Marktstrukturdaten (von R1)
│   ├── Anzahl aktiver Fluggesellschaften
│   ├── HHI pro Zeitschritt
│   ├── Konzentrationsraten
│   ├── Marktein-/-austritte
│   └── Marktanteile pro Airline
│
└── 4. Zeitdaten (von R3)
    ├── Aktuelle Periode (Peak/Off-Peak)
    ├── Aktueller Zeitschritt im Buchungszeitraum
    └── Verbleibende Zeit bis Abflug
```

---

### Preisdispersionsmaße

```
PREISDISPERSIONSBERECHNUNG
│
├── 1. Gini-Koeffizient
│   │
│   │  G = (Σ_i Σ_j |p_i − p_j|) / (2n² × p̄)
│   │
│   ├── G = 0 → Keine Dispersion
│   │         (alle Preise identisch)
│   ├── G → 1 → Maximale Dispersion
│   └── Standardmaß im Paper
│
├── 2. Standardabweichung der Preise
│   │
│   │  σ_p = √(Σ(p_i − p̄)² / n)
│   │
│   └── Absolutes Streuungsmaß
│
├── 3. Variationskoeffizient
│   │
│   │  CV = σ_p / p̄
│   │
│   └── Relatives Streuungsmaß
│       (vergleichbar über verschiedene
│        Preisniveaus)
│
├── 4. Preisrange
│   │
│   │  Range = p_max − p_min
│   │
│   └── Einfachstes Dispersionsmaß
│
├── 5. Interquartilsabstand
│   │
│   │  IQR = Q_75 − Q_25
│   │
│   └── Robustes Streuungsmaß
│
└── 6. Zerlegung der Preisdispersion
    │
    ├── Intra-Airline-Dispersion
    │   ├── Preisvariation innerhalb einer
    │   │   Fluggesellschaft
    │   ├── Resultiert aus Preisdifferenzierung
    │   │   (verschiedene Ticketkategorien)
    │   └── Resultiert aus dynamischer Preissetzung
    │       (Preisänderungen über Buchungszeitraum)
    │
    └── Inter-Airline-Dispersion
        ├── Preisvariation zwischen
        │   verschiedenen Fluggesellschaften
        ├── Resultiert aus Wettbewerb
        └── Resultiert aus Produktdifferenzierung
            (unterschiedliche Abflugzeiten/Marken)
```

---

### Theoretische Vorhersagenprüfung

```
VORHERSAGENPRÜFUNG
│
├── 1. Zusammenhang Wettbewerb ↔ Preisdispersion
│   │
│   ├── Hypothese A: Negativer Zusammenhang
│   │   ├── Mehr Wettbewerb → weniger Dispersion
│   │   ├── Begründung: Monopoleffekt dominiert
│   │   │   (Monopolist kann stärker differenzieren)
│   │   └── Prüfe: Korrelation HHI ↔ Gini positiv?
│   │
│   ├── Hypothese B: Positiver Zusammenhang
│   │   ├── Mehr Wettbewerb → mehr Dispersion
│   │   ├── Begründung: Markeneffekt dominiert
│   │   │   (mehr Airlines → mehr Heterogenität
│   │   │    → mehr Preisvariation)
│   │   └── Prüfe: Korrelation HHI ↔ Gini negativ?
│   │
│   └── Hypothese C: Umgekehrt U-förmiger Zusammenhang
│       ├── Moderate Konzentration → maximale Dispersion
│       ├── Monopol und perfekter Wettbewerb →
│       │   weniger Dispersion
│       ├── Begründung: Anreizkompatibilitätseffekt
│       │   wirkt nichtlinear
│       └── Prüfe: Quadratische Regression
│           HHI auf Gini
│
├── 2. Effekt der Preisdifferenzierung
│   ├── Anteil der Dispersion durch Selbstselektion
│   │   (K1 wählt teuer, K2 wählt günstig)
│   ├── Anteil durch dynamische Preissetzung
│   │   (gleicher Sitz, verschiedene Zeitpunkte)
│   └── Anteil durch Peak-Load Pricing
│       (gleiche Route, verschiedene Tageszeiten)
│
├── 3. Effekt der Marktstruktur auf Wohlfahrt
│   ├── Konsumentenrente K1 vs. K2
│   ├── Produzentenrente pro Airline
│   ├── Gesamtwohlfahrt
│   └── Deadweight Loss
│
└── 4. Vergleich der Szenarien
    ├── Monopol-Ergebnis als Benchmark
    ├── Duopol-Ergebnis
    ├── Oligopol-Ergebnis
    └── Sensitivitätsanalyse über Parameter
```

---

### Reporting

```
REPORTING-FUNKTIONEN
│
├── Pro Buchungszyklus
│   ├── Zusammenfassung aller Metriken
│   ├── Preisdispersionsmaße
│   ├── Marktstrukturmaße
│   └── Vergleich mit Vorhersagen
│
├── Pro Szenario
│   ├── Durchschnittswerte über alle Zyklen
│   ├── Zeitreihen der Metriken
│   ├── Konfidenzintervalle
│   └── Signifikanztests
│
├── Szenarienvergleich
│   ├── Monopol vs. Duopol vs. Oligopol
│   ├── Symmetrisch vs. Asymmetrisch
│   ├── Hoher vs. niedriger K1-Anteil
│   └── Peak vs. Off-Peak
│
└── Visualisierungen
    ├── Preisdispersion vs. HHI (Scatterplot)
    ├── Preispfade über Buchungszeitraum
    ├── Buchungsverteilung auf Airlines
    ├── Konsumentenrente nach Typ
    └── Gini-Koeffizient über Szenarien
```

---

### Ausgaben

| Ausgabe | Empfänger |
|---|---|
| Preisdispersionsmaße | Simulationsauswertung (extern) |
| Konzentrationsmaße | Simulationsauswertung (extern) |
| Vorhersagenvergleich | Simulationsauswertung (extern) |
| Wohlfahrtsmaße | Simulationsauswertung (extern) |
| Szenarienvergleich | Simulationsauswertung (extern) |
| Zwischenergebnisse pro Zeitschritt | Optional an R1 (für dynamische Marktanpassung) |

---

## Agent R3: Zeitsteuerungs-Agent (1 Instanz)

### Grundcharakterisierung

```
Zeitsteuerungs-Agent
├── Orchestriert den zeitlichen Ablauf
├── Definiert Simulationshorizont
├── Steuert Phasenwechsel
├── Synchronisiert alle Agenten
└── Taktgeber der Simulation
```

---

### Zeitstruktur

```
ZEITSTRUKTUR DER SIMULATION
│
├── 1. Simulationshorizont
│   ├── Gesamtdauer (z.B. 1 Jahr = 365 Tage)
│   ├── Anzahl Buchungszyklen
│   └── Wiederholungen pro Szenario
│       (für statistische Robustheit)
│
├── 2. Buchungszeitraum pro Flug
│   │
│   │  ◄─────── Buchungszeitraum ───────►
│   │  │                                │
│   │  t_open                      t_departure
│   │  (Buchungs-                  (Abflug)
│   │   öffnung)
│   │
│   ├── Dauer (z.B. 90 Tage vor Abflug)
│   ├── Diskretisierung in Zeitschritte
│   │   ├── Grob: Wochen (13 Schritte)
│   │   ├── Mittel: Tage (90 Schritte)
│   │   └── Fein: Stunden (2160 Schritte)
│   └── Pro Zeitschritt wird Phase 4
│       (Buchungszyklus) durchlaufen
│
├── 3. Peak-/Off-Peak-Perioden
│   │
│   ├── Peak-Perioden
│   │   ├── Morgendlicher Geschäftsreise-Peak
│   │   │   (z.B. 06:00–09:00)
│   │   ├── Abendlicher Rückreise-Peak
│   │   │   (z.B. 17:00–20:00)
│   │   ├── Saisonale Peaks
│   │   │   (Ferienzeiten, Feiertage)
│   │   └── Wochentags-Peaks
│   │       (Mo–Fr höher als Sa–So)
│   │
│   └── Off-Peak-Perioden
│       ├── Mittagszeit (10:00–16:00)
│       ├── Späte Abend-/Nachtflüge
│       ├── Nebensaison
│       └── Wochenenden (für Geschäftsreisen)
│
├── 4. Buchungszeitpunkt-Verteilung
│   │
│   ├── K1 (Geschäftsreisende)
│   │   ├── Buchung eher kurzfristig
│   │   ├── Häufung in letzten 14 Tagen
│   │   └── Verteilung: rechtssteil
│   │
│   └── K2 (Freizeitreisende)
│       ├── Buchung eher frühzeitig
│       ├── Häufung 30–90 Tage vor Abflug
│       └── Verteilung: linkssteil
│
└── 5. Dynamische Preisanpassungsfrequenz
    ├── Wie oft dürfen Airlines Preise ändern?
    ├── Jeden Zeitschritt (Standard)
    ├── Alle n Zeitschritte (Trägheit)
    └── Eventgesteuert (bei Schwellenüberschreitung)
```

---

### Phasensteuerung

```
PHASENSTEUERUNG
│
├── Phase 1: Marktinitialisierung
│   ├── Zeitpunkt: Simulationsstart
│   ├── R3 → R1: Startsignal
│   ├── R1 konfiguriert Marktstruktur
│   ├── A1-Instanzen werden erzeugt
│   └── Dauer: 1 Zeitschritt
│
├── Phase 2: Angebotsplanung
│   ├── Zeitpunkt: Nach Initialisierung
│   ├── R3 → A1.4: Planungssignal
│   ├── Interne Kette A1.4→A1.3→A1.1→A1.2
│   └── Dauer: 1 Zeitschritt
│
├── Phase 3: Preisveröffentlichung
│   ├── Zeitpunkt: Nach Angebotsplanung
│   ├── R3 → A1.2: Veröffentlichungssignal
│   ├── A1.2 → A2: Preise werden publiziert
│   └── Dauer: 1 Zeitschritt
│
├── Phase 4: Buchungszyklus (iterativ)
│   ├── Zeitpunkt: Buchungsöffnung bis Abflug
│   ├── R3 steuert jeden Zeitschritt
│   │
│   │   Für t = 1 bis T:
│   │   │
│   │   ├── R3 → Alle Agenten: Tick-Signal
│   │   │
│   │   ├── 4a: R3 → A2 → K1/K2
│   │   │   (Information)
│   │   │
│   │   ├── 4b: R3 → K1/K2 → A2 → A1
│   │   │   (Kaufentscheidung)
│   │   │
│   │   ├── 4c: R3 → A1.3 → A1.1
│   │   │   (Kapazitätsaktualisierung)
│   │   │
│   │   ├── 4d: R3 → A1.1 → A1.2
│   │   │   (Dynamische Preisanpassung)
│   │   │
│   │   ├── 4e: R3 → A2 → A1.2
│   │   │   (Wettbewerbsreaktion)
│   │   │
│   │   └── 4f: R3 → A1.2 → A2
│   │       (Neue Preisveröffentlichung)
│   │
│   └── Dauer: T Zeitschritte
│
└── Phase 5: Messung und Auswertung
    ├── Zeitpunkt: Nach jedem Buchungszyklus
    ├── R3 → R2: Auswertungssignal
    ├── R2 sammelt und analysiert
    └── Dauer: 1 Zeitschritt
```

---

### Synchronisationsmechanismus

```
SYNCHRONISATION
│
├── Sequentielles Modell (Standard)
│   ├── Agenten handeln in fester Reihenfolge
│   ├── Jeder Zeitschritt ist vollständig
│   │   abgeschlossen bevor nächster beginnt
│   ├── Deterministisch reproduzierbar
│   └── Reihenfolge pro Zeitschritt:
│       R3 → A2 → K1/K2 → A2 → A1 → A2 → R2
│
├── Paralleles Modell (Alternative)
│   ├── Alle K1/K2 entscheiden gleichzeitig
│   ├── Alle A1 passen Preise gleichzeitig an
│   ├── Konflikte bei Kapazitätsengpässen
│   │   → First-Come-First-Served oder
│   │   → Zufällige Zuweisung
│   └── Realistischer aber komplexer
│
└── Eventbasiertes Modell (Alternative)
    ├── Agenten handeln bei bestimmten Events
    ├── Keine feste Zeitschrittlänge
    ├── Events: Buchung, Preisänderung,
    │   Kapazitätswarnung
    └── Höchste Realitätsnähe
```

---

### Ausgaben

| Ausgabe | Empfänger |
|---|---|
| Tick-Signal (Zeitschritt-Fortschritt) | Alle Agenten |
| Phasenwechsel-Signal | Alle Agenten |
| Aktuelle Periode (Peak/Off-Peak) | A1.1, A1.2 |
| Verbleibende Zeit bis Abflug | A1.2 Pricing |
| Buchungszeitpunkt-Information | K1, K2 |
| Auswertungssignal | R2 Monitoring |
| Simulationsende-Signal | Alle Agenten |

---

## Interaktionsdiagramm der Regulatorien

```
                ┌──────────────────┐
                │  R3: Zeitsteuerung│
                │                  │
                │  • Taktgeber     │
                │  • Phasensteuerung│
                │  • Peak/Off-Peak │
                └────────┬─────────┘
                         │
              Tick-Signal│an alle Agenten
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
  ┌────────────┐  ┌─────────────┐  ┌─────────┐
  │R1: Markt-  │  │A1: Airlines │  │K1/K2:   │
  │struktur    │  │A2: Plattform│  │Konsumen-│
  │            │  │             │  │ten      │
  │• n Airlines│  │             │  │         │
  │• HHI       │  │             │  │         │
  │• Ein-/     │  │             │  │         │
  │  Austritt  │  │             │  │         │
  └─────┬──────┘  └──────┬──────┘  └────┬────┘
        │                │              │
        │    Marktstruktur│  Transaktionen│
        │    daten        │  daten        │
        │                │              │
        └────────┐       │       ┌──────┘
                 │       │       │
                 ▼       ▼       ▼
           ┌─────────────────────────┐
           │  R2: Monitoring/Messung │
           │                         │
           │  • Preisdispersion      │
           │    (Gini, σ, CV)        │
           │  • Konzentration (HHI)  │
           │  • Hypothesenprüfung    │
           │  • Wohlfahrtsanalyse    │
           │  • Reporting            │
           └─────────────────────────┘
                      │
                      ▼
              Simulationsergebnisse
```

---

## Gesamtzusammenfassung aller Regulatorien

```
Agent    Funktion                    Kernaufgabe
──────────────────────────────────────────────────────────
R1       Marktstruktur               WAS wird simuliert?
         • Anzahl Airlines           (Marktrahmen)
         • Routen
         • Marktform
         • Konzentrationsmaße
         • Ein-/Austritte

R2       Monitoring/Messung          WAS wird gemessen?
         • Datenerfassung            (Ergebnisanalyse)
         • Preisdispersionsmaße
         • Hypothesenprüfung
         • Wohlfahrtsanalyse
         • Reporting

R3       Zeitsteuerung               WANN passiert was?
         • Phasensteuerung           (Orchestrierung)
         • Tick-Signale
         • Peak/Off-Peak
         • Synchronisation
         • Buchungszeitraum
```

---