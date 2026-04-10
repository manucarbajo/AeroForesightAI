# UML Klassendiagramm – Regulatorien / Marktumgebungsagenten

---

## Klasse R1: MarktstrukturAgent

```
┌─────────────────────────────────────────────────────────┐
│                   MarktstrukturAgent                    │
│                      <<Agent>>                          │
├─────────────────────────────────────────────────────────┤
│ - id: String                                            │
│ - aktuelleMarktform: Marktform                          │
│ - aktiv: Boolean                                        │
│                                                         │
│ // Marktstruktur                                        │
│ - anzahlFluggesellschaften: Integer                     │
│ - registrierteFluggesellschaften: List<String>          │
│ - aktiveFluggesellschaften: List<String>                │
│ - marktanteile: Map<String, Double>                     │
│                                                         │
│ // Routenstruktur                                       │
│ - verfuegbareRouten: List<Route>                        │
│ - routenZuweisungen: Map<String, List<Route>>           │
│ - routenCharakteristiken:                               │
│   Map<Route, RoutenCharakteristik>                      │
│                                                         │
│ // Marktgröße                                           │
│ - gesamtNachfrageProRoute: Map<Route, Integer>          │
│ - k1K2Verhaeltnis: Map<Route, Double>                   │
│ - saisonaleNachfragefaktoren:                           │
│   Map<Saison, Double>                                   │
│                                                         │
│ // Wettbewerbsparameter                                 │
│ - eintrittsbarrierenHoehe: Double                       │
│ - austrittsbarrierenHoehe: Double                       │
│ - wettbewerberSymmetrie: Boolean                        │
│ - mindestProfitabilitaet: Double                        │
│ - mindestAuslastung: Double                             │
│ - periodenBisAustritt: Integer                          │
│                                                         │
│ // Kostenstruktur                                       │
│ - fixkostenProFlug: Double                              │
│ - variableKostenProPassagier: Double                    │
│ - grenzkostenKapazitaetserweiterung: Double             │
│ - kostenAsymmetrien: Map<String, Double>                │
│                                                         │
│ // Produktdifferenzierung                               │
│ - horizontaleDifferenzierung: Double                    │
│ - vertikaleDifferenzierung: Double                      │
│ - hotellingKreisUmfang: Double                          │
│                                                         │
│ // Konzentrationsmaße                                   │
│ - aktuellerHHI: Double                                  │
│ - konzentrationsCR1: Double                             │
│ - konzentrationsCR4: Double                             │
│ - anzahlEffektiverWettbewerber: Double                  │
│ - hhistorie: List<HHIEintrag>                           │
│                                                         │
│ // Marktdynamik                                         │
│ - eintrittsereignisse: List<MarktEreignis>              │
│ - austrittsereignisse: List<MarktEreignis>              │
│ - dynamischerMarkt: Boolean                             │
├─────────────────────────────────────────────────────────┤
│ // Initialisierung                                      │
│ + marktInitialisieren(                                  │
│     config: MarktKonfiguration                          │
│   ): void                                               │
│ + marktformFestlegen(                                   │
│     form: Marktform                                     │
│   ): void                                               │
│ + routenDefinieren(                                     │
│     routen: List<Route>                                 │
│   ): void                                               │
│ + routenZuweisen(                                       │
│     airlineId: String,                                  │
│     routen: List<Route>                                 │
│   ): void                                               │
│ + nachfrageDefinieren(                                  │
│     route: Route,                                       │
│     nachfrage: Integer,                                 │
│     k1Anteil: Double                                    │
│   ): void                                               │
│ + kostenstrukturFestlegen(                              │
│     fixkosten: Double,                                  │
│     variableKosten: Double                              │
│   ): void                                               │
│                                                         │
│ // Marktdynamik                                         │
│ + markteintrittPruefen(                                 │
│     profitabilitaet: Map<Route, Double>                 │
│   ): Boolean                                            │
│ + markteintrittDurchfuehren(                            │
│     neueAirline: Fluggesellschaft                       │
│   ): MarktEreignis                                      │
│ + marktaustrittPruefen(                                 │
│     airlineId: String,                                  │
│     verlustPerioden: Integer,                           │
│     auslastung: Double                                  │
│   ): Boolean                                            │
│ + marktaustrittDurchfuehren(                            │
│     airlineId: String                                   │
│   ): MarktEreignis                                      │
│                                                         │
│ // Konzentrationsberechnung                             │
│ + hhiBerechnen(): Double                                │
│   // HHI = Σ (s_i)² × 10.000                            │
│ + konzentrationCR(k: Integer): Double                   │
│   // CR_k = Σ_{i=1}^{k} s_i                             │
│ + effektiveWettbewerberBerechnen(): Double              │
│   // n_eff = 10.000 / HHI                               │
│ + marktanteileAktualisieren(                            │
│     buchungsdaten: Map<String, Integer>                 │
│   ): void                                               │
│ + konzentrationsmasseAktualisieren(): void              │
│                                                         │
│ // Szenariensteuerung                                   │
│ + szenarioLaden(szenario: Szenario): void               │
│ + naechstesSzenario(): Szenario                         │
│                                                         │
│ // Getter                                               │
│ + getMarktform(): Marktform                             │
│ + getAnzahlAirlines(): Integer                          │
│ + getHHI(): Double                                      │
│ + getCR(k: Integer): Double                             │
│ + getMarktanteile(): Map<String, Double>                │
│ + getRouten(): List<Route>                              │
│ + getKostenstruktur(): Kostenstruktur                   │
│ + getMarktEreignisse(): List<MarktEreignis>             │
│ + getHHIHistorie(): List<HHIEintrag>                    │
│ + getNachfrageProRoute(route: Route): Integer           │
│ + getK1Anteil(route: Route): Double                     │
└─────────────────────────────────────────────────────────┘
```

---

## Klasse R2: MonitoringAgent

```
┌─────────────────────────────────────────────────────────┐
│                    MonitoringAgent                      │
│                      <<Agent>>                          │
├─────────────────────────────────────────────────────────┤
│ - id: String                                            │
│ - aktiv: Boolean                                        │
│                                                         │
│ // Transaktionsdaten                                    │
│ - alleTransaktionen: List<Transaktion>                  │
│ - transaktionenProZeitschritt:                          │
│   Map<Integer, List<Transaktion>>                       │
│ - transaktionenProAirline:                              │
│   Map<String, List<Transaktion>>                        │
│ - transaktionenProRoute:                                │
│   Map<Route, List<Transaktion>>                         │
│ - transaktionenProKonsumentTyp:                         │
│   Map<KonsumentTyp, List<Transaktion>>                  │
│                                                         │
│ // Angebotsdaten                                        │
│ - preisHistorieProAirline:                              │
│   Map<String, List<PreisAenderung>>                     │
│ - auslastungProAirline:                                 │
│   Map<String, List<Double>>                             │
│ - umsatzProAirline: Map<String, Double>                 │
│ - gewinnProAirline: Map<String, Double>                 │
│                                                         │
│ // Marktstrukturdaten                                   │
│ - hhiVerlauf: List<HHIEintrag>                          │
│ - marktanteilsVerlauf:                                  │
│   Map<Integer, Map<String, Double>>                     │
│ - marktEreignisse: List<MarktEreignis>                  │
│                                                         │
│ // Preisdispersionsmaße                                 │
│ - giniKoeffizient: Double                               │
│ - standardabweichung: Double                            │
│ - variationskoeffizient: Double                         │
│ - preisRange: Double                                    │
│ - interquartilsabstand: Double                          │
│ - intraAirlineDispersion: Double                        │
│ - interAirlineDispersion: Double                        │
│                                                         │
│ // Wohlfahrtsmaße                                       │
│ - konsumentenrenteK1: Double                            │
│ - konsumentenrenteK2: Double                            │
│ - konsumentenrenteGesamt: Double                        │
│ - produzentenrenteGesamt: Double                        │
│ - gesamtwohlfahrt: Double                               │
│ - deadweightLoss: Double                                │
│                                                         │
│ // Hypothesentests                                      │
│ - hypothesenErgebnisse:                                 │
│   List<HypothesenErgebnis>                              │
│ - szenarienVergleiche:                                  │
│   List<SzenarienVergleich>                              │
│                                                         │
│ // Konfiguration                                        │
│ - messIntervall: Integer                                │
│ - signifikanzNiveau: Double                             │
│ - anzahlWiederholungen: Integer                         │
├─────────────────────────────────────────────────────────┤
│ // Datenerfassung                                       │
│ + transaktionErfassen(                                  │
│     transaktion: Transaktion                            │
│   ): void                                               │
│ + transaktionenSammeln(                                 │
│     plattform: Vertriebsplattform                       │
│   ): void                                               │
│ + preishistorieSammeln(                                 │
│     airlineId: String,                                  │
│     historie: List<PreisAenderung>                      │
│   ): void                                               │
│ + auslastungsdatenSammeln(                              │
│     airlineId: String,                                  │
│     auslastung: Double                                  │
│   ): void                                               │
│ + umsatzUndGewinnErfassen(                              │
│     airlineId: String,                                  │
│     umsatz: Double,                                     │
│     gewinn: Double                                      │
│   ): void                                               │
│ + marktstrukturdatenErfassen(                           │
│     hhi: Double,                                        │
│     marktanteile: Map<String, Double>,                  │
│     ereignisse: List<MarktEreignis>                     │
│   ): void                                               │
│                                                         │
│ // Preisdispersionsberechnung                           │
│ + giniKoeffizientBerechnen(                             │
│     preise: List<Double>                                │
│   ): Double                                             │
│   // G = (Σ_i Σ_j |p_i−p_j|) / (2n²×p̄)                  │
│ + standardabweichungBerechnen(                          │
│     preise: List<Double>                                │
│   ): Double                                             │
│   // σ = √(Σ(p_i−p̄)²/n)                                 │
│ + variationskoeffizientBerechnen(                       │
│     preise: List<Double>                                │
│   ): Double                                             │
│   // CV = σ / p̄                                         │
│ + preisRangeBerechnen(                                  │
│     preise: List<Double>                                │
│   ): Double                                             │
│   // Range = p_max − p_min                              │
│ + interquartilsabstandBerechnen(                        │
│     preise: List<Double>                                │
│   ): Double                                             │
│   // IQR = Q_75 − Q_25                                  │
│ + alleDispersionsmasseBerechnen(                        │
│     preise: List<Double>                                │
│   ): DispersionsMasse                                   │
│                                                         │
│ // Dispersions-Zerlegung                                │
│ + intraAirlineDispersionBerechnen(                      │
│     transaktionen: List<Transaktion>                    │
│   ): Double                                             │
│ + interAirlineDispersionBerechnen(                      │
│     transaktionen: List<Transaktion>                    │
│   ): Double                                             │
│ + dispersionZerlegen(                                   │
│     transaktionen: List<Transaktion>                    │
│   ): DispersionsZerlegung                               │
│                                                         │
│ // Wohlfahrtsberechnung                                 │
│ + konsumentenrenteBerechnen(                            │
│     typ: KonsumentTyp                                   │
│   ): Double                                             │
│ + produzentenrenteBerechnen(): Double                   │
│ + gesamtwohlfahrtBerechnen(): Double                    │
│ + deadweightLossBerechnen(): Double                     │
│                                                         │
│ // Hypothesenprüfung                                    │
│ + hypotheseApruefen(                                    │
│     hhiWerte: List<Double>,                             │
│     giniWerte: List<Double>                             │
│   ): HypothesenErgebnis                                 │
│   // Negativer Zusammenhang:                            │
│   // Korrelation HHI↔Gini positiv?                      │
│                                                         │
│ + hypotheseBpruefen(                                    │
│     hhiWerte: List<Double>,                             │
│     giniWerte: List<Double>                             │
│   ): HypothesenErgebnis                                 │
│   // Positiver Zusammenhang:                            │
│   // Korrelation HHI↔Gini negativ?                      │
│                                                         │
│ + hypotheseCpruefen(                                    │
│     hhiWerte: List<Double>,                             │
│     giniWerte: List<Double>                             │
│   ): HypothesenErgebnis                                 │
│   // Umgekehrt U-förmig:                           ,    │
│   // Quadratische Regression                            │
│                                                         │
│ + korrelationBerechnen(                                 │
│     x: List<Double>,                                    │
│     y: List<Double>                                     │
│   ): Double                                             │
│ + quadratischeRegressionDurchfuehren(                   │
│     x: List<Double>,                                    │
│     y: List<Double>                                     │
│   ): RegressionsErgebnis                                │
│                                                         │
│ // Szenarienvergleich                                   │
│ + szenarienVergleichen(                                 │
│     ergebnis1: SzenarioErgebnis,                        │
│     ergebnis2: SzenarioErgebnis                         │
│   ): SzenarienVergleich                                 │
│ + signifikanztestDurchfuehren(                          │
│     stichprobe1: List<Double>,                          │
│     stichprobe2: List<Double>                           │
│   ): SignifikanzTestErgebnis                            │
│                                                         │
│ // Reporting                                            │
│ + zyklusReportErstellen(                                │
│     zyklus: Integer                                     │
│   ): ZyklusReport                                       │
│ + szenarioReportErstellen(                              │
│     szenario: Szenario                                  │
│   ): SzenarioReport                                     │
│ + gesamtReportErstellen(): GesamtReport                 │
│ + visualisierungErstellen(                              │
│     typ: VisualisierungsTyp                             │
│   ): Visualisierung                                     │
│                                                         │
│ // Getter                                               │
│ + getGiniKoeffizient(): Double                          │
│ + getStandardabweichung(): Double                       │
│ + getDispersionsMasse(): DispersionsMasse               │
│ + getWohlfahrtsMasse(): WohlfahrtsMasse                 │
│ + getHypothesenErgebnisse():                            │
│   List<HypothesenErgebnis>                              │
│ + getAlleTransaktionen(): List<Transaktion>             │
└─────────────────────────────────────────────────────────┘
```

---

## Klasse R3: ZeitsteuerungsAgent

```
┌─────────────────────────────────────────────────────────┐
│                  ZeitsteuerungsAgent                    │
│                      <<Agent>>                          │
├─────────────────────────────────────────────────────────┤
│ - id: String                                            │
│ - aktiv: Boolean                                        │
│                                                         │
│ // Simulationshorizont                                  │
│ - gesamtDauer: Integer                                  │
│ - anzahlBuchungsZyklen: Integer                         │
│ - wiederholungenProSzenario: Integer                    │
│ - aktuelleWiederholung: Integer                         │
│                                                         │
│ // Buchungszeitraum                                     │
│ - buchungsZeitraumLaenge: Integer                       │
│ - zeitschrittGranularitaet: ZeitGranularitaet           │
│ - anzahlZeitschritte: Integer                           │
│ - aktuellerZeitschritt: Integer                         │
│ - buchungsOeffnung: Integer                             │
│ - abflugZeitpunkt: Integer                              │
│ - verbleibendeZeitBisAbflug: Integer                    │
│                                                         │
│ // Phasensteuerung                                      │
│ - aktuellePhase: SimulationsPhase                       │
│ - aktuellerSubSchritt: BuchungsSubSchritt               │
│ - phasenReihenfolge: List<SimulationsPhase>             │
│                                                         │
│ // Peak/Off-Peak                                        │
│ - peakZeiten: List<ZeitFenster>                         │
│ - offPeakZeiten: List<ZeitFenster>                      │
│ - saisonalePeaks: List<SaisonalerPeak>                  │
│ - aktuellesPeakStatus: Boolean                          │
│ - aktuellerWochentag: Wochentag                         │
│ - aktuelleSaison: Saison                                │
│                                                         │
│ // Buchungszeitpunkt-Steuerung                          │
│ - k1BuchungsVerteilung: Verteilung                      │
│ - k2BuchungsVerteilung: Verteilung                      │
│ - konsumentenProZeitschritt:                            │
│   Map<Integer, List<String>>                            │
│                                                         │
│ // Preisanpassungsfrequenz                              │
│ - preisanpassungsIntervall: Integer                     │
│ - naechstePreisanpassung: Integer                       │
│ - eventGesteuerteAnpassung: Boolean                     │
│ - anpassungsSchwelle: Double                            │
│                                                         │
│ // Synchronisation                                      │
│ - synchronisationsModell: SynchronisationsModell        │
│ - agentenReihenfolge: List<String>                      │
│                                                         │
│ // Registrierte Agenten                                 │
│ - registrierteAgenten: Map<String, Agent>               │
├─────────────────────────────────────────────────────────┤
│ // Initialisierung                                      │
│ + simulationInitialisieren(                             │
│     config: ZeitKonfiguration                           │
│   ): void                                               │
│ + buchungszeitraumDefinieren(                           │
│     laenge: Integer,                                    │
│     granularitaet: ZeitGranularitaet                    │
│   ): void                                               │
│ + peakZeitenDefinieren(                                 │
│     peaks: List<ZeitFenster>                            │
│   ): void                                               │
│ + saisonalePeaksDefinieren(                             │
│     peaks: List<SaisonalerPeak>                         │
│   ): void                                               │
│ + buchungsverteilungenDefinieren(                       │
│     k1Verteilung: Verteilung,                           │
│     k2Verteilung: Verteilung                            │
│   ): void                                               │
│ + agentenRegistrieren(                                  │
│     agenten: Map<String, Agent>                         │
│   ): void                                               │
│                                                         │
│ // Simulationssteuerung                                 │
│ + simulationStarten(): void                             │
│ + simulationPausieren(): void                           │
│ + simulationBeenden(): void                             │
│ + naechsterZeitschritt(): void                          │
│ + naechstePhase(): void                                 │
│                                                         │
│ // Phasensteuerung                                      │
│ + phase1Initialisierung(): void                         │
│   // R3 → R1: Startsignal                               │
│   // R1 konfiguriert Markt                              │
│   // A1-Instanzen werden erzeugt                        │
│                                                         │
│ + phase2Angebotsplanung(): void                         │
│   // R3 → A1.4: Planungssignal                          │
│   // Interne Kette A1.4→A1.3→A1.1→A1.2                  │
│                                                         │
│ + phase3Preisveroeffentlichung(): void                  │
│   // R3 → A1.2: Veröffentlichungssignal                 │
│   // A1.2 → A2: Preise publiziert                       │
│                                                         │
│ + phase4BuchungszyklusDurchfuehren(): void              │
│   // Iteriert über alle Zeitschritte                    │
│   // Ruft Subschritte 4a-4f auf                         │
│                                                         │
│ + phase4aInformation(): void                            │
│   // A2 → K1/K2: Marktübersicht                         │
│                                                         │
│ + phase4bKaufentscheidung(): void                       │
│   // K1/K2 → A2 → A1: Buchungen                         │
│                                                         │
│ + phase4cKapazitaetsUpdate(): void                      │
│   // A1.3 → A1.1: Aktualisierung                        │
│                                                         │
│ + phase4dDynamischePreisanpassung(): void               │
│   // A1.1 → A1.2: Preisänderung                         │
│                                                         │
│ + phase4eWettbewerbsreaktion(): void                    │
│   // A2 → A1.2: Wettbewerberpreise                      │
│                                                         │
│ + phase4fNeuePreisveroeffentlichung(): void             │
│   // A1.2 → A2: Aktualisierte Preise                    │
│                                                         │
│ + phase5MessungUndAuswertung(): void                    │
│   // R3 → R2: Auswertungssignal                         │
│   // R2 sammelt und analysiert                          │
│                                                         │
│ // Tick-/Signal-Steuerung                               │
│ + tickSignalSenden(): void                              │
│ + phasenWechselSignalSenden(                            │
│     neuePhase: SimulationsPhase                         │
│   ): void                                               │
│ + auswertungsSignalSenden(): void                       │
│ + simulationsEndeSignalSenden(): void                   │
│                                                         │
│ // Peak/Off-Peak Bestimmung                             │
│ + isPeakPeriode(): Boolean                              │
│ + isPeakTageszeit(                                      │
│     zeit: LocalTime                                     │
│   ): Boolean                                            │
│ + isPeakSaison(): Boolean                               │
│ + isPeakWochentag(): Boolean                            │
│                                                         │
│ // Konsumenten-Timing                                   │
│ + konsumentenFuerZeitschrittBestimmen(                  │
│     zeitschritt: Integer                                │
│   ): List<Konsument>                                    │
│ + buchungswahrscheinlichkeitK1(                         │
│     zeitschritt: Integer                                │
│   ): Double                                             │
│   // Rechtssteil: steigt gegen Abflug                   │
│ + buchungswahrscheinlichkeitK2(                         │
│     zeitschritt: Integer                                │
│   ): Double                                             │
│   // Linkssteil: hoch am Anfang                         │
│                                                         │
│ // Preisanpassungssteuerung                             │
│ + istPreisanpassungErlaubt(): Boolean                   │
│ + naechstePreisanpassungIn(): Integer                   │
│                                                         │
│ // Getter                                               │
│ + getAktuellerZeitschritt(): Integer                    │
│ + getAktuellePhase(): SimulationsPhase                  │
│ + getVerbleibendeZeit(): Integer                        │
│ + isPeak(): Boolean                                     │
│ + getAktuelleSaison(): Saison                           │
│ + getAktuellerWochentag(): Wochentag                    │
│ + getSimulationsFortschritt(): Double                   │
│ + getAktuelleWiederholung(): Integer                    │
└─────────────────────────────────────────────────────────┘
```

---

## Hilfsklassen / Datenklassen der Regulatorien

### Marktstruktur-Datenklassen

```
┌─────────────────────────────────────────────────────────┐
│                  MarktKonfiguration                     │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - marktform: Marktform                                  │
│ - anzahlAirlines: Integer                               │
│ - routen: List<Route>                                   │
│ - gesamtNachfrage: Integer                              │
│ - k1Anteil: Double                                      │
│ - symmetrisch: Boolean                                  │
│ - fixkosten: Double                                     │
│ - variableKosten: Double                                │
│ - eintrittsbarrieren: Double                            │
│ - austrittsbarrieren: Double                            │
│ - dynamischerMarkt: Boolean                             │
│ - hotellingKreisUmfang: Double                          │
├─────────────────────────────────────────────────────────┤
│ + validate(): Boolean                                   │
│ + toSzenario(): Szenario                                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                RoutenCharakteristik                     │
│                  <<DataClass>>                          │
├─────────────────────────────────────────────────────────┤
│ - route: Route                                          │
│ - routentyp: Routentyp                                  │
│ - streckenlaenge: Double                                │
│ - dominanterKonsumentTyp: KonsumentTyp                  │
│ - durchschnittlicheNachfrage: Integer                   │
│ - saisonalitaetsFaktor: Double                          │
│ - wettbewerbsIntensitaet: Double                        │
├─────────────────────────────────────────────────────────┤
│ + isGeschaeftsRoute(): Boolean                          │
│ + isTouristikRoute(): Boolean                           │
│ + getNachfrageFaktor(saison: Saison): Double            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Kostenstruktur                        │
│                   <<DataClass>>                         │
├─────────────────────────────────────────────────────────┤
│ - fixkostenProFlug: Double                              │
│ - variableKostenProPassagier: Double                    │
│ - grenzkostenKapazitaet: Double                         │
│ - kostenAsymmetrie: Double                              │
├─────────────────────────────────────────────────────────┤
│ + gesamtkostenBerechnen(                                │
│     anzahlFluege: Integer,                              │
│     anzahlPassagiere: Integer                           │
│   ): Double                                             │
│ + stueckkostenBerechnen(                                │
│     anzahlPassagiere: Integer                           │
│   ): Double                                             │
│ + breakEvenBerechnen(): Integer                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    MarktEreignis                        │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - zeitschritt: Integer                                  │
│ - typ: MarktEreignisTyp                                 │
│ - airlineId: String                                     │
│ - route: Route                                          │
│ - grund: String                                         │
│ - hhi_vorher: Double                                    │
│ - hhi_nachher: Double                                   │
├─────────────────────────────────────────────────────────┤
│ + getHHIAenderung(): Double                             │
│ + getBeschreibung(): String                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                     HHIEintrag                          │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - zeitschritt: Integer                                  │
│ - hhi: Double                                           │
│ - anzahlAirlines: Integer                               │
│ - marktanteile: Map<String, Double>                     │
│ - konzentrationsKlasse: KonzentrationsKlasse            │
├─────────────────────────────────────────────────────────┤
│ + isHochKonzentriert(): Boolean                         │
│ + isMaessigKonzentriert(): Boolean                      │
│ + isGeringKonzentriert(): Boolean                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                      Szenario                           │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - szenarioId: String                                    │
│ - name: String                                          │
│ - beschreibung: String                                  │
│ - marktKonfiguration: MarktKonfiguration                │
│ - zeitKonfiguration: ZeitKonfiguration                  │
│ - konsumentenKonfiguration: KonsumentenKonfiguration    │
├─────────────────────────────────────────────────────────┤
│ + validate(): Boolean                                   │
│ + getZusammenfassung(): String                          │
└─────────────────────────────────────────────────────────┘
```

---

### Monitoring-Datenklassen

```
┌─────────────────────────────────────────────────────────┐
│                   DispersionsMasse                      │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - giniKoeffizient: Double                               │
│ - standardabweichung: Double                            │
│ - variationskoeffizient: Double                         │
│ - preisRange: Double                                    │
│ - interquartilsabstand: Double                          │
│ - median: Double                                        │
│ - mittelwert: Double                                    │
│ - anzahlBeobachtungen: Integer                          │
│ - zeitschritt: Integer                                  │
├─────────────────────────────────────────────────────────┤
│ + toArray(): Double[]                                   │
│ + getZusammenfassung(): String                          │
│ + vergleicheMit(                                        │
│     andere: DispersionsMasse                            │
│   ): DispersionsVergleich                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 DispersionsZerlegung                    │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - gesamtDispersion: Double                              │
│ - intraAirlineDispersion: Double                        │
│ - interAirlineDispersion: Double                        │
│ - anteilIntra: Double                                   │
│ - anteilInter: Double                                   │
│                                                         │
│ // Ursachenzerlegung Intra-Airline                      │
│ - anteilPreisdifferenzierung: Double                    │
│   // Verschiedene Ticketkategorien                      │
│ - anteilDynamischPreissetzung: Double                   │
│   // Preisänderungen über Buchungszeitraum              │
│ - anteilPeakLoadPricing: Double                         │
│   // Verschiedene Tageszeiten                           │
│                                                         │
│ // Ursachenzerlegung Inter-Airline                      │
│ - anteilWettbewerb: Double                              │
│ - anteilProduktdifferenzierung: Double                  │
├─────────────────────────────────────────────────────────┤
│ + getIntraAnteilProzent(): Double                       │
│ + getInterAnteilProzent(): Double                       │
│ + getDominanteUrsache(): String                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  WohlfahrtsMasse                        │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - konsumentenrenteK1: Double                            │
│ - konsumentenrenteK2: Double                            │
│ - konsumentenrenteGesamt: Double                        │
│ - produzentenrenteGesamt: Double                        │
│ - produzentenrenteProAirline:                           │
│   Map<String, Double>                                   │
│ - gesamtwohlfahrt: Double                               │
│ - deadweightLoss: Double                                │
│ - zeitschritt: Integer                                  │
├─────────────────────────────────────────────────────────┤
│ + getEffizienzgrad(): Double                            │
│   // Gesamtwohlfahrt / Maximalwohlfahrt                 │
│ + getVerteilungsgerechtigkeit(): Double                 │
│   // KR_gesamt / (KR_gesamt + PR_gesamt)                │
│ + getZusammenfassung(): String                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 HypothesenErgebnis                      │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - hypothese: HypothesenTyp                              │
│ - beschreibung: String                                  │
│ - korrelation: Double                                   │
│ - pWert: Double                                         │
│ - signifikant: Boolean                                  │
│ - signifikanzNiveau: Double                             │
│ - stichprobenGroesse: Integer                           │
│ - konfidenzIntervallUnten: Double                       │
│ - konfidenzIntervallOben: Double                        │
│                                                         │
│ // Nur für Hypothese C                                  │
│ - regressionsKoeffizienten: Double[]                    │
│ - bestimmtheitsmass: Double                             │
│ - wendepunkt: Double                                    │
├─────────────────────────────────────────────────────────┤
│ + isBestaetigt(): Boolean                               │
│ + getInterpretation(): String                           │
│ + getDetailBericht(): String                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 RegressionsErgebnis                     │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - koeffizienten: Double[]                               │
│   // [a, b, c] für y = ax² + bx + c                     │
│ - bestimmtheitsmass: Double                             │
│   // R²                                                 │
│ - standardfehler: Double[]                              │
│ - tWerte: Double[]                                      │
│ - pWerte: Double[]                                      │
│ - fStatistik: Double                                    │
│ - fPWert: Double                                        │
├─────────────────────────────────────────────────────────┤
│ + getWendepunkt(): Double                               │
│   // -b / (2a) für quadratische Regression              │
│ + isSignifikant(): Boolean                              │
│ + getGleichung(): String                                │
│ + vorhersagen(x: Double): Double                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               SignifikanzTestErgebnis                   │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - testTyp: String                                       │
│ - testStatistik: Double                                 │
│ - pWert: Double                                         │
│ - signifikant: Boolean                                  │
│ - freiheitsgrade: Integer                               │
│ - effektGroesse: Double                                 │
├─────────────────────────────────────────────────────────┤
│ + isSignifikant(niveau: Double): Boolean                │
│ + getInterpretation(): String                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 SzenarienVergleich                      │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - szenario1: Szenario                                   │
│ - szenario2: Szenario                                   │
│ - dispersion1: DispersionsMasse                         │
│ - dispersion2: DispersionsMasse                         │
│ - wohlfahrt1: WohlfahrtsMasse                           │
│ - wohlfahrt2: WohlfahrtsMasse                           │
│ - signifikanzTest: SignifikanzTestErgebnis              │
│ - differenzen: Map<String, Double>                      │
├─────────────────────────────────────────────────────────┤
│ + getVergleichsTabelle(): String                        │
│ + isDifferenzSignifikant(): Boolean                     │
│ + getGewinner(metrik: String): Szenario                 │
└─────────────────────────────────────────────────────────┘
```

---

### Reporting-Datenklassen

```
┌─────────────────────────────────────────────────────────┐
│                    ZyklusReport                         │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - zyklusNummer: Integer                                 │
│ - anzahlTransaktionen: Integer                          │
│ - durchschnittsPreis: Double                            │
│ - dispersionsMasse: DispersionsMasse                    │
│ - dispersionsZerlegung: DispersionsZerlegung            │
│ - wohlfahrtsMasse: WohlfahrtsMasse                      │
│ - hhi: Double                                           │
│ - marktanteile: Map<String, Double>                     │
│ - auslastungenProAirline: Map<String, Double>           │
│ - buchungsverteilung: Map<String, Integer>              │
├─────────────────────────────────────────────────────────┤
│ + getZusammenfassung(): String                          │
│ + toCSV(): String                                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   SzenarioReport                        │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - szenario: Szenario                                    │
│ - zyklusReports: List<ZyklusReport>                     │
│ - durchschnittDispersion: DispersionsMasse              │
│ - durchschnittWohlfahrt: WohlfahrtsMasse                │
│ - konfidenzIntervalle:                                  │
│   Map<String, KonfidenzIntervall>                       │
│ - zeitreihen: Map<String, List<Double>>                 │
├─────────────────────────────────────────────────────────┤
│ + getDurchschnitt(metrik: String): Double               │
│ + getKonfidenzIntervall(                                │
│     metrik: String                                      │
│   ): KonfidenzIntervall                                 │
│ + getZeitreihe(metrik: String): List<Double>            │
│ + toCSV(): String                                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   GesamtReport                          │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - szenarioReports: List<SzenarioReport>                 │
│ - szenarienVergleiche: List<SzenarienVergleich>         │
│ - hypothesenErgebnisse: List<HypothesenErgebnis>        │
│ - visualisierungen: List<Visualisierung>                │
│ - erstellungsZeitpunkt: LocalDateTime                   │
├─────────────────────────────────────────────────────────┤
│ + getHauptErgebnis(): String                            │
│ + exportAlsCSV(pfad: String): void                      │
│ + exportAlsPDF(pfad: String): void                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Visualisierung                        │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - typ: VisualisierungsTyp                               │
│ - titel: String                                         │
│ - xAchse: String                                        │
│ - yAchse: String                                        │
│ - datenPunkte: List<DatenPunkt>                         │
│ - datenReihen: Map<String, List<DatenPunkt>>            │
├─────────────────────────────────────────────────────────┤
│ + rendern(): void                                       │
│ + exportieren(pfad: String): void                       │
└─────────────────────────────────────────────────────────┘
```

---

### Zeitsteuerungs-Datenklassen

```
┌─────────────────────────────────────────────────────────┐
│                  ZeitKonfiguration                      │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - gesamtDauer: Integer                                  │
│ - buchungsZeitraumLaenge: Integer                       │
│ - granularitaet: ZeitGranularitaet                      │
│ - anzahlBuchungsZyklen: Integer                         │
│ - wiederholungen: Integer                               │
│ - peakZeiten: List<ZeitFenster>                         │
│ - saisonalePeaks: List<SaisonalerPeak>                  │
│ - preisanpassungsIntervall: Integer                     │
│ - synchronisationsModell: SynchronisationsModell        │
├─────────────────────────────────────────────────────────┤
│ + validate(): Boolean                                   │
│ + getAnzahlZeitschritte(): Integer                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    ZeitFenster                          │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - beginn: LocalTime                                     │
│ - ende: LocalTime                                       │
│ - bezeichnung: String                                   │
│ - typ: PeakTyp                                          │
├─────────────────────────────────────────────────────────┤
│ + enthaelt(zeit: LocalTime): Boolean                    │
│ + getDauer(): Duration                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   SaisonalerPeak                        │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - saison: Saison                                        │
│ - nachfrageFaktor: Double                               │
│ - k1AnteilAnpassung: Double                             │
│ - bezeichnung: String                                   │
├─────────────────────────────────────────────────────────┤
│ + isAktiv(aktuelleSaison: Saison): Boolean              │
│ + getNachfrageMultiplikator(): Double                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              KonsumentenKonfiguration                   │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - gesamtAnzahl: Integer                                 │
│ - anteilK1: Double                                      │
│ - parameterK1: KonsumentParameterK1                     │
│ - parameterK2: KonsumentParameterK2                     │
├─────────────────────────────────────────────────────────┤
│ + getAnzahlK1(): Integer                                │
│ + getAnzahlK2(): Integer                                │
│ + validate(): Boolean                                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                KonfidenzIntervall                       │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - untergrenze: Double                                   │
│ - obergrenze: Double                                    │
│ - niveau: Double                                        │
│ - mittelwert: Double                                    │
│ - standardfehler: Double                                │
├─────────────────────────────────────────────────────────┤
│ + getBreite(): Double                                   │
│ + enthaelt(wert: Double): Boolean                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    DatenPunkt                           │
│                    <<DataClass>>                        │
├─────────────────────────────────────────────────────────┤
│ - x: Double                                             │
│ - y: Double                                             │
│ - label: String                                         │
│ - kategorie: String                                     │
├─────────────────────────────────────────────────────────┤
│ + getKoordinaten(): Double[]                            │
└─────────────────────────────────────────────────────────┘
```

---

## Zusätzliche Enumerationen

```
┌──────────────────────────┐  ┌──────────────────────────┐
│    <<enumeration>>       │  │    <<enumeration>>       │
│    Marktform             │  │    SimulationsPhase      │
├──────────────────────────┤  ├──────────────────────────┤
│ MONOPOL                  │  │ INITIALISIERUNG          │
│ DUOPOL                   │  │ ANGEBOTSPLANUNG          │
│ OLIGOPOL                 │  │ PREISVEROEFFENTLICHUNG   │
│ POLYOPOL                 │  │ BUCHUNGSZYKLUS           │
└──────────────────────────┘  │ MESSUNG_AUSWERTUNG       │
                              └──────────────────────────┘

┌──────────────────────────┐  ┌──────────────────────────┐
│    <<enumeration>>       │  │    <<enumeration>>       │
│    BuchungsSubSchritt    │  │    ZeitGranularitaet.    │
├──────────────────────────┤  ├──────────────────────────┤
│ INFORMATION              │  │ STUNDE                   │
│ KAUFENTSCHEIDUNG         │  │ TAG                      │
│ KAPAZITAETS_UPDATE       │  │ WOCHE                    │
│ DYNAMISCHE_PREISANPASSUNG│  └──────────────────────────┘
│ WETTBEWERBSREAKTION      │
│ NEUE_PREISVEROEFFENTL    │  ┌──────────────────────────┐
└──────────────────────────┘  │    <<enumeration>>       │
                              │  SynchronisationsModell  │
┌──────────────────────────┐  ├──────────────────────────┤
│    <<enumeration>>       │  │ SEQUENTIELL              │
│    MarktEreignisTyp      │  │ PARALLEL                 │
├──────────────────────────┤  │ EVENT_BASIERT            │
│ EINTRITT                 │  └──────────────────────────┘
│ AUSTRITT                 │
│ FUSION                   │  ┌──────────────────────────┐
│ KAPAZITAETSERWEITERUNG   │  │    <<enumeration>>       │
│ KAPAZITAETSREDUKTION     │  │    KonzentrationsKlasse  │
└──────────────────────────┘  ├──────────────────────────┤
                              │ HOCH_KONZENTRIERT        │
┌──────────────────────────┐  │   // HHI > 2.500         │
│    <<enumeration>>       │  │ MAESSIG_KONZENTRIERT     │
│    HypothesenTyp         │  │   // HHI 1.500–2.500     │
├──────────────────────────┤  │ GERING_KONZENTRIERT      │
│ HYPOTHESE_A_NEGATIV      │  │   // HHI < 1.500         │
│ HYPOTHESE_B_POSITIV      │  └──────────────────────────┘
│ HYPOTHESE_C_U_FOERMIG    │
└──────────────────────────┘  ┌──────────────────────────┐
                              │    <<enumeration>>       │
┌──────────────────────────┐  │    VisualisierungsTyp    │
│    <<enumeration>>       │  ├──────────────────────────┤
│    PeakTyp               │  │ SCATTER_HHI_GINI         │
├──────────────────────────┤  │ PREISPFADE_ZEITVERLAUF   │
│ MORGEN_GESCHAEFT         │  │ BUCHUNGSVERTEILUNG       │
│ ABEND_RUECKREISE         │  │ KONSUMENTENRENTE_TYP     │
│ SAISONAL_FERIEN          │  │ GINI_UEBER_SZENARIEN     │
│ WOCHENTAG                │  │ WOHLFAHRT_VERGLEICH      │
└──────────────────────────┘  │ DISPERSIONS_ZERLEGUNG    │
                              └──────────────────────────┘
```

---

## Beziehungsdiagramm Regulatorien

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   ┌─────────────────┐     steuert      ┌─────────────────┐   │
│   │R3: Zeitsteuerung│─────────────────►│R1: Marktstruktur│   │
│   │                 │                  │                 │   │
│   │• Phasen         │     steuert      │• n Airlines     │   │
│   │• Zeitschritte   │─────────────────►│• HHI            │   │
│   │• Peak/Off-Peak  │                   │• Ein-/Austritt │   │
│   │• Synchronisation│                   │• Kosten        │   │
│   └────────┬────────┘                   └───────┬────────┘   │
│            │                                    │            │
│            │ Tick-Signal                        │ Markt-     │
│            │ an alle                            │ struktur-  │
│            │ Agenten                            │ daten      │
│            │                                    │            │
│   ┌────────┼────────────────────────────────────┼────────┐   │
│   │        ▼                                    ▼        │   │
│   │   ┌─────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│   │   │A1:      │  │A2:           │  │K1/K2:        │    │   │
│   │   │Airlines │  │Vertriebsplatt│  │Konsumenten   │    │   │
│   │   │         │  │form          │  │              │    │   │
│   │   └────┬────┘  └──────┬───────┘  └──────┬───────┘    │   │
│   │        │              │                 │            │   │
│   │        │  Transaktions-│   Transaktions- │           │   │
│   │        │  daten        │   daten         │           │   │
│   └────────┼──────────────┼─────────────────┼────────────┘   │
│            │              │                 │                │
│            └──────────────┼─────────────────┘                │
│                           │                                  │
│                           ▼                                  │
│                  ┌────────────────┐                          │
│                  │R2: Monitoring  │                          │
│                  │                │                          │
│                  │• Dispersion    │──► ZyklusReport          │
│                  │  - Gini        │──► SzenarioReport        │
│                  │  - σ, CV       │──► GesamtReport          │
│                  │  - Zerlegung   │──► Visualisierung        │
│                  │• Wohlfahrt     │                          │
│                  │  - KR, PR      │                          │
│                  │  - DWL         │                          │
│                  │• Hypothesen    │                          │
│                  │  - A (negativ) │                          │
│                  │  - B (positiv) │                          │
│                  │  - C (U-Form)  │                          │
│                  │• Szenarien-    │                          │
│                  │  vergleich     │                          │
│                  └────────────────┘                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘


Kardinalitäten:
──────────────────────────────────────────────────────
MarktstrukturAgent    1 ──── *  Fluggesellschaft
MarktstrukturAgent    1 ──── *  Route
MarktstrukturAgent    1 ──── *  MarktEreignis
MarktstrukturAgent    1 ──── *  HHIEintrag
MarktstrukturAgent    1 ──── 1  MarktKonfiguration
MarktstrukturAgent    1 ──── 1  Kostenstruktur

MonitoringAgent       1 ──── *  Transaktion
MonitoringAgent       1 ──── *  DispersionsMasse
MonitoringAgent       1 ──── *  WohlfahrtsMasse
MonitoringAgent       1 ──── *  HypothesenErgebnis
MonitoringAgent       1 ──── *  SzenarienVergleich
MonitoringAgent       1 ──── *  ZyklusReport
MonitoringAgent       1 ──── *  SzenarioReport
MonitoringAgent       1 ──── 1  GesamtReport

ZeitsteuerungsAgent   1 ──── 1  ZeitKonfiguration
ZeitsteuerungsAgent   1 ──── *  ZeitFenster
ZeitsteuerungsAgent   1 ──── *  SaisonalerPeak
ZeitsteuerungsAgent   1 ──── *  Agent (registriert)

Szenario              1 ──── 1  MarktKonfiguration
Szenario              1 ──── 1  ZeitKonfiguration
Szenario              1 ──── 1  KonsumentenKonfiguration
```

---
