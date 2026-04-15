# UML Klassendiagramm – Konsumentenagenten

---

## Abstrakte Basisklasse: Konsument

```
┌─────────────────────────────────────────────────────────┐
│                      Konsument                          │
│                  <<Agent, abstract>>                    │
├─────────────────────────────────────────────────────────┤
│ # id: String                                            │
│ # typ: KonsumentTyp                                     │
│ # aktiv: Boolean                                        │
│ # hatGebucht: Boolean                                   │
│                                                         │
│ // Ökonomische Parameter                                │
│ # reservationspreis: Double                             │
│ # preiselastizitaet: Double                             │
│ # qualitaetspraeferenzParameter: Double                 │
│ # budget: Double                                        │
│                                                         │
│ // Präferenzparameter                                   │
│ # gewuenschteAbflugzeit: LocalTime                      │
│ # transportkostensatz: Double                           │
│ # markenpraeferenz: Double                              │
│ # praeferierteAirline: String                           │
│ # gewuenschteRoute: Route                               │
│                                                         │
│ // Qualitätspräferenz                                   │
│ # bevorzugteTicketKategorie: TicketKategorie            │
│ # mindestQualitaet: QualitaetsStufe                     │
│ # akzeptierteRestriktionen: List<Restriktion>           │
│                                                         │
│ // Buchungsverhalten                                    │
│ # buchungsZeitpunkt: Integer                            │
│ # suchkosten: Double                                    │
│ # informationsstand: List<Angebot>                      │
│                                                         │
│ // Entscheidungshistorie                                │
│ # betrachteteAngebote: List<Angebot>                    │
│ # gewaehltesBuchung: Buchung                            │
│ # realisierterNutzen: Double                            │
│ # konsumentenrente: Double                              │
├─────────────────────────────────────────────────────────┤
│ + initialisieren(parameter: KonsumentParameter): void   │
│                                                         │
│ // Informationsphase                                    │
│ + informationenEmpfangen(                               │
│     angebote: List<Angebot>                             │
│   ): void                                               │
│ + angeboteFiltern(                                      │
│     angebote: List<Angebot>                             │
│   ): List<Angebot>                                      │
│                                                         │
│ // Entscheidungsphase                                   │
│ + {abstract} vorauswahlTreffen(                         │
│     angebote: List<Angebot>                             │
│   ): List<Angebot>                                      │
│ + nutzenBerechnen(angebot: Angebot): Double             │
│ + {abstract} kaufentscheidungTreffen():                 │
│   KaufEntscheidung                                      │
│                                                         │
│ // Buchungsphase                                        │
│ + buchungDurchfuehren(                                  │
│     plattform: Vertriebsplattform                       │
│   ): BuchungsBestaetigung                               │
│                                                         │
│ // Berechnungen                                         │
│ + transportkostenBerechnen(                             │
│     abflugzeit: LocalTime                               │
│   ): Double                                             │
│ + markenwechselkostenBerechnen(                         │
│     airlineId: String                                   │
│   ): Double                                             │
│ + konsumentenrenteBerechnen(): Double                   │
│                                                         │
│ // Getter                                               │
│ + getTyp(): KonsumentTyp                                │
│ + getHatGebucht(): Boolean                              │
│ + getRealisierterNutzen(): Double                       │
│ + getKonsumentenrente(): Double                         │
│ + getGewaehltesBuchung(): Buchung                       │
│ + getTransaktionsdaten(): Transaktion                   │
└─────────────────────────────────────────────────────────┘
```

---

## Klasse K1: Geschaeftsreisender

```
┌─────────────────────────────────────────────────────────┐
│                  Geschaeftsreisender                    │
│                <<Agent>> extends Konsument              │
├─────────────────────────────────────────────────────────┤
│ // Spezifische ökonomische Parameter                    │
│ - reservationspreis: Double                             │
│   // Gezogen aus N(μ_r_hoch, σ²_r_hoch)                 │
│   // Typisch: oberes Quartil der Preisverteilung        │
│                                                         │
│ - preiselastizitaet: Double                             │
│   // Niedrig: |ε| < 1                                   │
│   // Typisch: -0.3 bis -0.7                             │
│                                                         │
│ - qualitaetspraeferenzParameter: Double                 │
│   // Hoch: θ_H                                          │
│   // Gezogen aus N(μ_θ_hoch, σ²_θ)                      │
│                                                         │
│ // Spezifische Präferenzparameter                       │
│ - gewuenschteAbflugzeit: LocalTime                      │
│   // Bimodal: morgens früh (06-09) oder                 │
│   //          abends spät (17-20)                       │
│                                                         │
│ - transportkostensatz: Double                           │
│   // Hoch: τ_H                                          │
│   // Gezogen aus N(μ_τ_hoch, σ²_τ)                      │
│                                                         │
│ - markenpraeferenz: Double                              │
│   // Stark: β ∈ [0.6, 1.0]                              │
│   // Gezogen aus U(0.6, 1.0)                            │
│                                                         │
│ - zeittoleranz: Double                                  │
│   // Gering: z.B. max. 1-2 Stunden Abweichung           │
│                                                         │
│ // Spezifische Qualitätsanforderungen                   │
│ - benoetigtFreieUmbuchung: Boolean = true               │
│ - benoetigtFreieStornierung: Boolean = true             │
│ - akzeptiertMindestaufenthalt: Boolean = false          │
│                                                         │
│ // Buchungsverhalten                                    │
│ - typischerBuchungsvorlauf: Integer                     │
│   // Kurz: 1-14 Tage vor Abflug                         │
│ - vergleichtPreiseIntensiv: Boolean = false             │
│ - zeitdruckBeiEntscheidung: Boolean = true              │
│                                                         │
│ // Vielfliegerstatus                                    │
│ - vielfliegerStatus: VielfliegerStatus                  │
│ - vielfliegerAirline: String                            │
│ - gesammelteMeilen: Integer                             │
├─────────────────────────────────────────────────────────┤
│ // Überschriebene Methoden                              │
│ + vorauswahlTreffen(                                    │
│     angebote: List<Angebot>                             │
│   ): List<Angebot>                                      │
│   // 1. Filtere nach Zeitfenster                        │
│   //    (|t_Flug - t*| ≤ zeittoleranz)                  │
│   // 2. Filtere nach Premium/Flex-Verfügbarkeit         │
│   // 3. Bevorzuge präferierte Airline                   │
│                                                         │
│ + kaufentscheidungTreffen(): KaufEntscheidung           │
│   // Nutzenfunktion:                                    │
│   // U = θ_H × q(f) - p(f) - τ_H × |Δt|                 │ 
│   //     - (1-β) × Markenwechselkosten                  │
│   // Wähle f* mit max U(f*)                             │
│   // Falls U(f*) ≥ 0 → BUCHEN                           │
│   // Falls U(f*) < 0 → NICHT_BUCHEN                     │
│                                                         │
│ // Spezifische Methoden                                 │
│ + zeitfensterPruefen(                                   │
│     abflugzeit: LocalTime                               │
│   ): Boolean                                            │
│ + premiumVerfuegbarkeitPruefen(                         │
│     angebot: Angebot                                    │
│   ): Boolean                                            │
│ + vielfliegerBonusBerechnen(): Double                   │
│ + markenwechselkostenBerechnen(                         │
│     airlineId: String                                   │
│   ): Double                                             │
│   // Hoch wenn airlineId ≠ vielfliegerAirline           │
│                                                         │
│ + nutzenBerechnen(angebot: Angebot): Double             │
│   // U = θ_H × q - p - τ_H × |Δt|                       │
│   //     - (1-β) × Wechselkosten                        │
│   //     + vielfliegerBonus                             │
└─────────────────────────────────────────────────────────┘
```

---

## Klasse K2: Freizeitreisender

```
┌─────────────────────────────────────────────────────────┐
│                   Freizeitreisender                     │
│                <<Agent>> extends Konsument              │
├─────────────────────────────────────────────────────────┤
│ // Spezifische ökonomische Parameter                    │
│ - reservationspreis: Double                             │
│   // Gezogen aus N(μ_r_niedrig, σ²_r_niedrig)           │
│   // Typisch: unteres Quartil der Preisverteilung       │
│                                                         │
│ - preiselastizitaet: Double                             │
│   // Hoch: |ε| > 1                                      │
│   // Typisch: -1.5 bis -3.0                             │
│                                                         │
│ - qualitaetspraeferenzParameter: Double                 │
│   // Niedrig: θ_L                                       │
│   // Gezogen aus N(μ_θ_niedrig, σ²_θ)                   │
│                                                         │
│ // Spezifische Präferenzparameter                       │
│ - gewuenschteAbflugzeit: LocalTime                      │
│   // Gleichverteilt über den Tag                        │
│   // U(06:00, 22:00)                                    │
│                                                         │
│ - transportkostensatz: Double                           │
│   // Niedrig: τ_L                                       │
│   // Gezogen aus N(μ_τ_niedrig, σ²_τ)                   │
│                                                         │
│ - markenpraeferenz: Double                              │
│   // Schwach: β ∈ [0.0, 0.3]                            │
│   // Gezogen aus U(0.0, 0.3)                            │
│                                                         │
│ - zeittoleranz: Double                                  │
│   // Hoch: z.B. 4-8 Stunden Abweichung akzeptabel       │
│                                                         │
│ // Spezifische Qualitätsanforderungen                   │
│ - benoetigtFreieUmbuchung: Boolean = false              │
│ - benoetigtFreieStornierung: Boolean = false            │
│ - akzeptiertMindestaufenthalt: Boolean = true           │
│                                                         │
│ // Buchungsverhalten                                    │
│ - typischerBuchungsvorlauf: Integer                     │
│   // Lang: 30-90 Tage vor Abflug                        │
│ - vergleichtPreiseIntensiv: Boolean = true              │
│ - zeitdruckBeiEntscheidung: Boolean = false             │
│                                                         │
│ // Preissensitivität                                    │
│ - maxPreisBereitschaft: Double                          │
│ - reagiertAufFruehbucher: Boolean = true                │
│ - nutztAlternativeVerkehrsmittel: Boolean               │
│ - alternativeKosten: Double                             │
│   // Kosten alternativer Verkehrsmittel                 │
│   // (Bahn, Auto, etc.) als Außenoption                 │
├─────────────────────────────────────────────────────────┤
│ // Überschriebene Methoden                              │
│ + vorauswahlTreffen(                                    │
│     angebote: List<Angebot>                             │
│   ): List<Angebot>                                      │
│   // 1. Filtere nach Preis                              │
│   //    (p ≤ reservationspreis)                         │
│   // 2. Breites Zeitfenster akzeptiert                  │
│   // 3. Keine Airline-Filterung                         │
│                                                         │
│ + kaufentscheidungTreffen(): KaufEntscheidung           │
│   // Nutzenfunktion:                                    │
│   // U = θ_L × q(f) - p(f) - τ_L × |Δt|                 │
│   // Markenwechselkosten ≈ 0                            │
│   // Wähle f* mit max U(f*)                             │
│   // Falls U(f*) ≥ 0 → BUCHEN                           │
│   // Falls U(f*) < 0 → NICHT_BUCHEN                     │
│   //   (Außenoption / alternatives Verkehrsmittel)      │
│                                                         │
│ // Spezifische Methoden                                 │
│ + preisfilterAnwenden(                                  │
│     angebote: List<Angebot>                             │
│   ): List<Angebot>                                      │
│   // Entfernt alle Angebote > reservationspreis         │
│                                                         │
│ + guenstigstesAngebotSuchen(                            │
│     angebote: List<Angebot>                             │
│   ): Angebot                                            │
│   // Sortiert nach Preis aufsteigend                    │
│                                                         │
│ + aussenoptionBewerten(): Double                        │
│   // Vergleich mit alternativem Verkehrsmittel          │
│   // Falls alternativeKosten < günstigstes Angebot      │
│   // → Nicht fliegen                                    │
│                                                         │
│ + nutzenBerechnen(angebot: Angebot): Double             │
│   // U = θ_L × q - p - τ_L × |Δt|                       │
│   // Kein Markenwechselkosten-Term                      │
│                                                         │
│ + aufFruehbucherReagieren(                              │
│     angebot: Angebot,                                   │
│     zeitBisAbflug: Integer                              │
│   ): Double                                             │
│   // Erhöht Buchungswahrscheinlichkeit                  │
│   // bei Frühbucherrabatt                               │
└─────────────────────────────────────────────────────────┘
```

---

## Hilfsklassen / Datenklassen der Konsumentenseite

```
┌─────────────────────────────────────────────────────────┐
│                  KonsumentParameter                     │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - typ: KonsumentTyp                                     │
│ - route: Route                                          │
│                                                         │
│ // Verteilungsparameter für Instanziierung              │
│ - mittelwertReservationspreis: Double                   │
│ - varianzReservationspreis: Double                      │
│ - mittelwertQualitaetspraeferenz: Double                │
│ - varianzQualitaetspraeferenz: Double                   │
│ - mittelwertTransportkostensatz: Double                 │
│ - varianzTransportkostensatz: Double                    │
│ - minMarkenpraeferenz: Double                           │
│ - maxMarkenpraeferenz: Double                           │
│ - abflugzeitVerteilung: Verteilung                      │
│ - buchungsvorlaufVerteilung: Verteilung                 │
├─────────────────────────────────────────────────────────┤
│ + erzeugeReservationspreis(): Double                    │
│ + erzeugeQualitaetspraeferenz(): Double                 │
│ + erzeugeTransportkostensatz(): Double                  │
│ + erzeugeMarkenpraeferenz(): Double                     │
│ + erzeugeAbflugzeit(): LocalTime                        │
│ + erzeugeBuchungsvorlauf(): Integer                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               KonsumentParameterK1                      │
│          <<DataClass>> extends KonsumentParameter       │
├─────────────────────────────────────────────────────────┤
│ // Vorkonfigurierte Werte für Geschäftsreisende         │
│ - mittelwertReservationspreis: Double = 800.0           │
│ - varianzReservationspreis: Double = 200.0              │
│ - mittelwertQualitaetspraeferenz: Double = 0.8          │
│ - varianzQualitaetspraeferenz: Double = 0.1             │
│ - mittelwertTransportkostensatz: Double = 50.0          │
│ - varianzTransportkostensatz: Double = 10.0             │
│ - minMarkenpraeferenz: Double = 0.6                     │
│ - maxMarkenpraeferenz: Double = 1.0                     │
│ - abflugzeitVerteilung: Verteilung = BIMODAL            │
│   // Peaks bei 07:00 und 18:00                          │
│ - buchungsvorlaufVerteilung: Verteilung =               │
│   RECHTSSCHIEF  // 1-14 Tage                            │
├─────────────────────────────────────────────────────────┤
│ + erzeugeAbflugzeit(): LocalTime                        │
│   // Bimodal: 50% morgens N(07:00, 1h)                  │
│   //          50% abends  N(18:00, 1h)                  │
│ + erzeugeBuchungsvorlauf(): Integer                     │
│   // Rechtssteil: Häufung 1-14 Tage                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               KonsumentParameterK2                      │
│          <<DataClass>> extends KonsumentParameter       │
├─────────────────────────────────────────────────────────┤
│ // Vorkonfigurierte Werte für Freizeitreisende          │
│ - mittelwertReservationspreis: Double = 300.0           │
│ - varianzReservationspreis: Double = 100.0              │
│ - mittelwertQualitaetspraeferenz: Double = 0.3          │
│ - varianzQualitaetspraeferenz: Double = 0.1             │
│ - mittelwertTransportkostensatz: Double = 10.0          │
│ - varianzTransportkostensatz: Double = 5.0              │
│ - minMarkenpraeferenz: Double = 0.0                     │
│ - maxMarkenpraeferenz: Double = 0.3                     │
│ - abflugzeitVerteilung: Verteilung = GLEICHVERTEILT     │
│   // U(06:00, 22:00)                                    │
│ - buchungsvorlaufVerteilung: Verteilung =               │
│   LINKSSCHIEF  // 30-90 Tage                            │
├─────────────────────────────────────────────────────────┤
│ + erzeugeAbflugzeit(): LocalTime                        │
│   // Gleichverteilt: U(06:00, 22:00)                    │
│ + erzeugeBuchungsvorlauf(): Integer                     │
│   // Linkssteil: Häufung 30-90 Tage                     │
└─────────────────────────────────────────────────────────┘
```

---

## Entscheidungsklassen

```
┌─────────────────────────────────────────────────────────┐
│                    KaufEntscheidung                     │
│                     <<DataClass>>                       │
├─────────────────────────────────────────────────────────┤
│ - konsumentId: String                                   │
│ - konsumentTyp: KonsumentTyp                            │
│ - entscheidung: EntscheidungsTyp                        │
│ - gewaehlterFlug: Angebot                               │
│ - gewaehlteKategorie: TicketKategorie                   │
│ - erwarteterNutzen: Double                              │
│ - zeitschritt: Integer                                  │
│                                                         │
│ // Entscheidungsgrundlage                               │
│ - anzahlBetrachteterAngebote: Integer                   │
│ - anzahlNachVorauswahl: Integer                         │
│ - nutzenAllernativen: Map<String, Double>               │
│ - nutzenAussenoption: Double                            │
│                                                         │
│ // Nutzenwerte des gewählten Angebots                   │
│ - qualitaetsnutzen: Double                              │
│ - preiskomponente: Double                               │
│ - transportkostenKomponente: Double                     │
│ - markenwechselKomponente: Double                       │
├─────────────────────────────────────────────────────────┤
│ + isBuchung(): Boolean                                  │
│ + isNichtBuchung(): Boolean                             │
│ + getNutzenDetails(): NutzenDetails                     │
│ + getEntscheidungsprotokoll(): String                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                     NutzenDetails                       │
│                     <<DataClass>>                       │
├─────────────────────────────────────────────────────────┤
│ - gesamtNutzen: Double                                  │
│ - qualitaetsNutzen: Double                              │
│   // θ × q                                              │
│ - preisKomponente: Double                               │
│   // -p                                                 │
│ - transportKosten: Double                               │
│   // -τ × |Δt|                                          │
│ - markenWechselKosten: Double                           │
│   // -(1-β) × Wechselkosten                             │
│ - vielfliegerBonus: Double                              │
│   // nur K1                                             │
├─────────────────────────────────────────────────────────┤
│ + getDominanterFaktor(): String                         │
│ + getAnteilQualitaet(): Double                          │
│ + getAnteilPreis(): Double                              │
│ + getAnteilTransport(): Double                          │
│ + getAnteilMarke(): Double                              │
└─────────────────────────────────────────────────────────┘
```

---

## Fabrikklasse für Konsumentenerzeugung

```
┌─────────────────────────────────────────────────────────┐
│                  KonsumentenFabrik                      │
│                    <<Factory>>                          │
├─────────────────────────────────────────────────────────┤
│ - zufallsGenerator: Random                              │
│ - parameterK1: KonsumentParameterK1                     │
│ - parameterK2: KonsumentParameterK2                     │
│ - erzeugteK1: Integer = 0                               │
│ - erzeugteK2: Integer = 0                               │
├─────────────────────────────────────────────────────────┤
│ + erzeugeGeschaeftsreisenden(                           │
│     route: Route                                        │
│   ): Geschaeftsreisender                                │
│   // Zieht Parameter aus Verteilungen:                  │
│   // r_j ~ N(800, 200²)                                 │
│   // t*_j ~ Bimodal(07:00, 18:00)                       │
│   // τ_j ~ N(50, 10²)                                   │
│   // θ_j ~ N(0.8, 0.1²)                                 │
│   // β_j ~ U(0.6, 1.0)                                  │
│                                                         │
│ + erzeugeFreizeitreisenden(                             │
│     route: Route                                        │
│   ): Freizeitreisender                                  │
│   // Zieht Parameter aus Verteilungen:                  │
│   // r_k ~ N(300, 100²)                                 │
│   // t*_k ~ U(06:00, 22:00)                             │
│   // τ_k ~ N(10, 5²)                                    │
│   // θ_k ~ N(0.3, 0.1²)                                 │
│   // β_k ~ U(0.0, 0.3)                                  │
│                                                         │
│ + erzeugeKonsumentenMix(                                │
│     anzahlK1: Integer,                                  │
│     anzahlK2: Integer,                                  │
│     route: Route                                        │
│   ): List<Konsument>                                    │
│                                                         │
│ + erzeugeKonsumentenNachVerhaeltnis(                    │
│     gesamtAnzahl: Integer,                              │
│     anteilK1: Double,                                   │
│     route: Route                                        │
│   ): List<Konsument>                                    │
│   // z.B. anteilK1 = 0.3 → 30% Geschäft                 │
│                                                         │
│ + getAnzahlErzeugteK1(): Integer                        │
│ + getAnzahlErzeugteK2(): Integer                        │
│ + resetZaehler(): void                                  │
└─────────────────────────────────────────────────────────┘
```

---

## Zusätzliche Enumerationen

```
┌──────────────────────────┐  ┌──────────────────────────┐
│    <<enumeration>>       │  │    <<enumeration>>       │
│    EntscheidungsTyp      │  │    VielfliegerStatus     │
├──────────────────────────┤  ├──────────────────────────┤
│ BUCHEN                   │  │ KEIN_STATUS              │
│ NICHT_BUCHEN             │  │ SILBER                   │
│ WARTEN                   │  │ GOLD                     │
│ ALTERNATIVE_WAEHLEN      │  │ PLATIN                   │
└──────────────────────────┘  └──────────────────────────┘

┌──────────────────────────┐
│    <<enumeration>>       │
│    Verteilung            │
├──────────────────────────┤
│ NORMALVERTEILT           │
│ GLEICHVERTEILT           │
│ BIMODAL                  │
│ RECHTSSCHIEF             │
│ LINKSSCHIEF              │
│ BIVARIATE_NORMAL         │
└──────────────────────────┘
```

---

## Beziehungsdiagramm Konsumentenseite

```
                    ┌─────────────────┐
                    │ KonsumentenFabrik│
                    │   <<Factory>>   │
                    └────────┬────────┘
                             │ erzeugt
                ┌────────────┼────────────┐
                │            │            │
                ▼            │            ▼
┌───────────────────┐        │  ┌───────────────────┐
│Geschaeftsreisender│        │  │Freizeitreisender  │
│      (K1)         │        │  │      (K2)         │
│   <<Agent>>       │        │  │   <<Agent>>       │
└────────┬──────────┘        │  └────────┬──────────┘
         │                   │           │
         │    ┌──────────────┴──┐        │
         └───►│    Konsument    │◄───────┘
              │  <<abstract>>   │
              └───────┬─────────┘
                      │ nutzt
         ┌────────────┼─────────────┐
         │            │             │
         ▼            ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│KaufEntschei- │ │ Nutzen-  │ │ Konsument-   │
│dung          │ │ Details  │ │ Parameter    │
│<<DataClass>> │ │<<Data>>  │ │<<DataClass>> │
└──────────────┘ └──────────┘ └──────┬───────┘
                                     │
                              ┌──────┴───────┐
                              │              │
                              ▼              ▼
                    ┌──────────────┐ ┌──────────────┐
                    │KonsumentPara-│ │KonsumentPara-│
                    │meterK1       │ │meterK2       │
                    └──────────────┘ └──────────────┘


Kardinalitäten:
─────────────────────────────────────────────
Konsument (abstrakt)    1 ──── 0..1  KaufEntscheidung
Konsument (abstrakt)    1 ──── 0..1  Buchung
Konsument (abstrakt)    1 ──── 0..1  NutzenDetails
Konsument (abstrakt)    1 ──── *     Angebot (betrachtet)
KonsumentenFabrik       1 ──── *     Geschaeftsreisender
KonsumentenFabrik       1 ──── *     Freizeitreisender
KonsumentenFabrik       1 ──── 1     KonsumentParameterK1
KonsumentenFabrik       1 ──── 1     KonsumentParameterK2
Geschaeftsreisender     * ──── 1     Vertriebsplattform
Freizeitreisender       * ──── 1     Vertriebsplattform
```

---

## Interaktion mit Anbieterseite

```
                Vertriebsplattform (A2)
                ┌──────────────────────┐
                │ aktuelleAngebote     │
                │ List<Angebot>        │
                └──────────┬───────────┘
                           │
            informationenEmpfangen()
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │K1: Geschäfts-   │       │K2: Freizeit-    │
    │reisender        │       │reisender        │
    │                 │       │                 │
    │vorauswahl:      │       │vorauswahl:      │
    │• Zeitfenster    │       │• Preisfilter    │
    │• Flex-Ticket    │       │• Breites        │
    │• Präf. Airline  │       │  Zeitfenster    │
    │                 │       │                 │
    │Nutzenfunktion:  │       │Nutzenfunktion:  │
    │U = θ_H×q - p    │       │U = θ_L×q - p    │
    │  - τ_H×|Δt|     │       │  - τ_L×|Δt|     │
    │  - Wechselk.    │       │                 │
    │                 │       │                 │
    │→ KaufEntschei-  │       │→ KaufEntschei-  │
    │  dung           │       │  dung           │
    └────────┬────────┘       └────────┬────────┘
             │                         │
             │  buchungDurchfuehren()   │
             │                         │
             └────────────┬────────────┘
                          │
                          ▼
                Vertriebsplattform (A2)
                ┌──────────────────────┐
                │buchungsAnfrageEnt-   │
                │gegennehmen()         │
                └──────────┬───────────┘
                           │
                buchungWeiterleiten()
                           │
                           ▼
                Fluggesellschaft (A1)
                ┌──────────────────────┐
                │A1.3: buchung-        │
                │Registrieren()        │
                └──────────────────────┘
```

---