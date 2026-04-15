## Nachfragerseite
## Agent K1: Geschäftsreisender

### Grundcharakterisierung

```
Geschäftsreisender (Instanz j)
├── Hohe Zahlungsbereitschaft (hoher Reservationspreis)
├── Niedrige Preiselastizität
├── Starke Markenpräferenz
├── Hohe Zeitsensitivität
├── Hoher Qualitätspräferenzparameter θ
└── Gewünschte Abflugzeit (individuell)
```

---

### Individuelle Parameter

```
PARAMETER-PROFIL K1
│
├── Ökonomische Parameter
│   ├── Reservationspreis r_j
│   │   ├── Gezogen aus oberer Hälfte einer
│   │   │   bivariaten Normalverteilung
│   │   │   (Borenstein/Rose 1994)
│   │   ├── Deutlich über Durchschnittspreis
│   │   └── Hohe Varianz zwischen Instanzen möglich
│   │
│   ├── Preiselastizität ε_j
│   │   ├── Niedrig (betragsmäßig < 1)
│   │   └── Reagiert schwach auf Preisänderungen
│   │
│   └── Qualitätspräferenzparameter θ_j
│       ├── Hoch (θ_H)
│       ├── Bestimmt Zahlungsbereitschaft für
│       │   Qualitätsmerkmale (Flexibilität etc.)
│       └── Nutzen = θ_j × Qualität − Preis
│
├── Präferenzparameter
│   ├── Gewünschte Abflugzeit t*_j
│   │   ├── Meist zu geschäftsüblichen Zeiten
│   │   │   (Morgen früh, Abend spät)
│   │   └── Geringe Abweichungstoleranz
│   │
│   ├── Transportkostensatz τ_j
│   │   ├── Hoch
│   │   ├── Misst Nutzenverlust pro Zeiteinheit
│   │   │   Abweichung vom Wunschflug
│   │   └── Transportkosten = τ_j × |t_Flug − t*_j|
│   │
│   ├── Markenpräferenz β_j
│   │   ├── Stark ausgeprägt
│   │   ├── Bevorzugt bestimmte Airline
│   │   │   (Vielfliegerprogramm, Gewohnheit)
│   │   └── Wechselkosten hoch
│   │
│   └── Qualitätspräferenz
│       ├── Bevorzugt Premium/Flex-Tickets
│       ├── Freie Umbuchung wichtig
│       ├── Stornierbarkeit wichtig
│       └── Mindestaufenthalt inakzeptabel
│
└── Buchungsverhalten
    ├── Buchungszeitpunkt eher kurzfristig
    ├── Geringe Vorlaufzeit
    └── Zeitdruck bei Entscheidung
```

---

### Entscheidungslogik

```
KAUFENTSCHEIDUNG K1 (pro Zeitschritt)
│
├── Schritt 1: Informationsbeschaffung
│   ├── Erhält Marktübersicht von A2
│   ├── Filtert nach gewünschter Route
│   └── Beachtet vor allem Abflugzeiten
│       und Airline-Marke
│
├── Schritt 2: Vorauswahl
│   ├── Eliminiert Flüge mit zu großer
│   │   zeitlicher Abweichung
│   │   (|t_Flug − t*_j| > Toleranzschwelle)
│   ├── Eliminiert Flüge ohne verfügbare
│   │   Premium/Flex-Tickets
│   └── Bevorzugt präferierte Airline
│
├── Schritt 3: Nutzenkalkulation
│   │
│   │  Für jeden verbleibenden Flug f:
│   │
│   │  U_j(f) = θ_j × q(f)
│   │           − p(f)
│   │           − τ_j × |t_f − t*_j|
│   │           − (1 − β_j) × Markenwechselkosten
│   │
│   ├── θ_j × q(f)     = Qualitätsnutzen
│   ├── p(f)            = Ticketpreis
│   ├── τ_j × |Δt|     = Transportkosten (zeitlich)
│   └── Markenwechsel   = Zusatzkosten bei
│                         Nicht-Präferenz-Airline
│
├── Schritt 4: Kaufentscheidung
│   ├── Wähle Flug f* mit maximalem U_j(f*)
│   ├── FALLS U_j(f*) ≥ 0 → Buchung
│   ├── FALLS U_j(f*) < 0 → Keine Buchung
│   │   (Außenoption/Nicht-Reisen)
│   └── Wählt nahezu immer Premium/Flex-Ticket
│
└── Schritt 5: Buchung
    ├── Buchungsanfrage an A2
    ├── A2 leitet an entsprechende A1 weiter
    ├── A1.3 bestätigt Verfügbarkeit
    └── Transaktion wird registriert
```

---

### Einflussfaktoren auf Kaufentscheidung

| Faktor | Einfluss | Gewichtung |
|---|---|---|
| Abflugzeit | Starker Einfluss (hohe Transportkosten) | **Sehr hoch** |
| Airline-Marke | Starke Präferenz für bestimmte Airline | **Hoch** |
| Ticketqualität | Flex/Premium wird stark bevorzugt | **Hoch** |
| Preis | Geringer Einfluss wegen niedriger Elastizität | **Niedrig** |
| Verfügbarkeit | Relevant bei kurzfristiger Buchung | **Mittel** |
| Wettbewerberpreise | Kaum relevant (geringe Wechselbereitschaft) | **Niedrig** |

---

## Agent K2: Freizeitreisender (mehrfach instanziierbar)

### Grundcharakterisierung

```
Freizeitreisender (Instanz k)
├── Niedrige Zahlungsbereitschaft (niedriger Reservationspreis)
├── Hohe Preiselastizität
├── Geringe Markenpräferenz
├── Niedrige Zeitsensitivität
├── Niedriger Qualitätspräferenzparameter θ
└── Gewünschte Abflugzeit (flexibel)
```

---

### Individuelle Parameter

```
PARAMETER-PROFIL K2
│
├── Ökonomische Parameter
│   ├── Reservationspreis r_k
│   │   ├── Gezogen aus unterer Hälfte einer
│   │   │   bivariaten Normalverteilung
│   │   │   (Borenstein/Rose 1994)
│   │   ├── Näher am oder unter Durchschnittspreis
│   │   └── Moderatere Varianz als K1
│   │
│   ├── Preiselastizität ε_k
│   │   ├── Hoch (betragsmäßig > 1)
│   │   └── Reagiert stark auf Preisänderungen
│   │
│   └── Qualitätspräferenzparameter θ_k
│       ├── Niedrig (θ_L)
│       ├── Geringe Zahlungsbereitschaft für
│       │   Zusatzqualität
│       └── Nutzen = θ_k × Qualität − Preis
│
├── Präferenzparameter
│   ├── Gewünschte Abflugzeit t*_k
│   │   ├── Flexibel über den Tag verteilt
│   │   └── Hohe Abweichungstoleranz
│   │
│   ├── Transportkostensatz τ_k
│   │   ├── Niedrig
│   │   ├── Geringe Kosten bei zeitlicher
│   │   │   Abweichung vom Wunschflug
│   │   └── Transportkosten = τ_k × |t_Flug − t*_k|
│   │
│   ├── Markenpräferenz β_k
│   │   ├── Schwach ausgeprägt
│   │   ├── Keine starke Airline-Bindung
│   │   └── Wechselkosten gering
│   │
│   └── Qualitätspräferenz
│       ├── Akzeptiert restriktive Tickets
│       ├── Mindestaufenthalt akzeptabel
│       ├── Eingeschränkte Umbuchung akzeptabel
│       └── Stornierungseinschränkungen akzeptabel
│
└── Buchungsverhalten
    ├── Buchungszeitpunkt eher frühzeitig
    ├── Längere Vorlaufzeit
    ├── Mehr Zeit für Preisvergleiche
    └── Reagiert auf Frühbucherangebote
```

---

### Entscheidungslogik

```
KAUFENTSCHEIDUNG K2 (pro Zeitschritt)
│
├── Schritt 1: Informationsbeschaffung
│   ├── Erhält Marktübersicht von A2
│   ├── Filtert nach gewünschter Route
│   └── Sortiert primär nach Preis
│
├── Schritt 2: Vorauswahl
│   ├── Eliminiert Flüge über Reservationspreis
│   │   (p(f) > r_k → ausgeschlossen)
│   ├── Breite Zeitfenster-Toleranz
│   │   (|t_Flug − t*_k| > Toleranz → nur bei
│   │    sehr großer Abweichung eliminiert)
│   └── Keine Airline-basierte Filterung
│
├── Schritt 3: Nutzenkalkulation
│   │
│   │  Für jeden verbleibenden Flug f:
│   │
│   │  U_k(f) = θ_k × q(f)
│   │           − p(f)
│   │           − τ_k × |t_f − t*_k|
│   │
│   ├── θ_k × q(f)     = Qualitätsnutzen
│   │                     (niedrig, da θ_k klein)
│   ├── p(f)            = Ticketpreis
│   │                     (dominanter Faktor)
│   └── τ_k × |Δt|     = Transportkosten
│                         (gering, da τ_k klein)
│
│   HINWEIS: Markenwechselkosten entfallen
│            weitgehend (β_k ≈ 0)
│
├── Schritt 4: Kaufentscheidung
│   ├── Wähle Flug f* mit maximalem U_k(f*)
│   ├── FALLS U_k(f*) ≥ 0 → Buchung
│   ├── FALLS U_k(f*) < 0 → Keine Buchung
│   │   (Außenoption/alternatives Verkehrsmittel)
│   └── Wählt nahezu immer restriktives Ticket
│       (Preis dominiert Qualität)
│
└── Schritt 5: Buchung
    ├── Buchungsanfrage an A2
    ├── A2 leitet an entsprechende A1 weiter
    ├── A1.3 bestätigt Verfügbarkeit
    └── Transaktion wird registriert
```

---

### Einflussfaktoren auf Kaufentscheidung

| Faktor | Einfluss | Gewichtung |
|---|---|---|
| Preis | Dominanter Entscheidungsfaktor | **Sehr hoch** |
| Verfügbarkeit günstiger Tickets | Entscheidend für Buchung | **Sehr hoch** |
| Wettbewerberpreise | Hoher Einfluss (aktiver Vergleich) | **Hoch** |
| Abflugzeit | Geringer Einfluss (flexible Zeitplanung) | **Niedrig** |
| Airline-Marke | Kaum relevant | **Sehr niedrig** |
| Ticketqualität | Niedrige Qualität wird akzeptiert | **Niedrig** |

---

## Vergleichsmatrix K1 vs. K2

```
Parameter                    K1 Geschäft        K2 Freizeit
─────────────────────────────────────────────────────────────
Reservationspreis r          Hoch               Niedrig
Preiselastizität ε           Niedrig (|ε|<1)    Hoch (|ε|>1)
Qualitätspräferenz θ         Hoch (θ_H)         Niedrig (θ_L)
Transportkosten τ            Hoch               Niedrig
Markenpräferenz β            Stark              Schwach
Bevorzugte Ticketkategorie   Premium/Flex       Restriktiv
Buchungszeitpunkt            Kurzfristig        Frühzeitig
Zeitsensitivität             Hoch               Niedrig
Preissensitivität            Niedrig            Hoch
Wechselbereitschaft          Gering             Hoch
```

---

## Interaktionsdiagramm der Nachfragerseite

```
         A2: Vertriebsplattform
         (Preise, Verfügbarkeiten,
          Ticketkategorien)
              │              │
              ▼              ▼
    ┌──────────────┐  ┌──────────────┐
    │ K1: Geschäft │  │ K2: Freizeit │
    │              │  │              │
    │ Filtert nach │  │ Filtert nach │
    │ • Abflugzeit │  │ • Preis      │
    │ • Airline    │  │ • Verfügbar- │
    │ • Qualität   │  │   keit       │
    │              │  │              │
    │ Nutzen-      │  │ Nutzen-      │
    │ kalkulation: │  │ kalkulation: │
    │ θ_H×q − p    │  │ θ_L×q − p    │
    │ − τ_H×|Δt|   │  │ − τ_L×|Δt|   │
    │ − Wechsel-   │  │              │
    │   kosten     │  │              │
    │              │  │              │
    │ → Flex-      │  │ → Restrik-   │
    │   Ticket     │  │   tives      │
    │              │  │   Ticket     │
    └──────┬───────┘  └──────┬───────┘
           │                 │
           ▼                 ▼
         A2: Vertriebsplattform
         (Buchungsanfragen)
              │
              ▼
    A1: Fluggesellschaft
    (A1.3 Kapazitäts-Update)
```

---

## Instanziierung und Parameterverteilung
```
BEI ERZEUGUNG EINER INSTANZ
│
├── K1: Geschäftsreisender
│   ├── r_j ~ N(μ_r_hoch, σ²_r_hoch)    [oberer Bereich]
│   ├── t*_j ~ Geschäftszeiten-Verteilung
│   │         (bimodal: morgens früh, abends)
│   ├── τ_j ~ N(μ_τ_hoch, σ²_τ)          [hoher Bereich]
│   ├── θ_j ~ N(μ_θ_hoch, σ²_θ)          [hoher Bereich]
│   └── β_j ~ U(0.6, 1.0)                [starke Präferenz]
│
└── K2: Freizeitreisender
    ├── r_k ~ N(μ_r_niedrig, σ²_r_niedrig) [unterer Bereich]
    ├── t*_k ~ Gleichverteilung über den Tag
    ├── τ_k ~ N(μ_τ_niedrig, σ²_τ)         [niedriger Bereich]
    ├── θ_k ~ N(μ_θ_niedrig, σ²_θ)         [niedriger Bereich]
    └── β_k ~ U(0.0, 0.3)                  [schwache Präferenz]
```

---