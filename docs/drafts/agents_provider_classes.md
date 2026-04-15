# UML Klassendiagramm – Anbieteragenten

---

## Klasse A1: Fluggesellschaft

```
┌─────────────────────────────────────────────────────────┐
│                    Fluggesellschaft                     │
│                      <<Agent>>                          │
├─────────────────────────────────────────────────────────┤
│ - id: String                                            │
│ - name: String                                          │
│ - marktanteil: Double                                   │
│ - markenIdentitaet: String                              │
│ - gesamtkapazitaet: Integer                             │
│ - gesamtgewinn: Double                                  │
│ - gesamtumsatz: Double                                  │
│ - fixkosten: Double                                     │
│ - variableKostenProPassagier: Double                    │
│ - aktiv: Boolean                                        │
│ - marktposition: Integer                                │
│ - symmetrisch: Boolean                                  │
│                                                         │
│ - prognoseModul: PrognoseModul                          │
│ - pricingModul: PricingModul                            │
│ - kapazitaetsModul: KapazitaetsModul                    │
│ - angebotsplanung: Angebotsplanung                      │
├─────────────────────────────────────────────────────────┤
│ + initialisieren(marktstruktur: Marktstruktur): void    │
│ + buchungVerarbeiten(buchung: Buchung): Boolean         │
│ + zyklusDurchfuehren(zeitschritt: Integer): void        │
│ + preiseVeroeffentlichen(): List<Angebot>               │
│ + wettbewerbspreiseEmpfangen(preise: List<Angebot>):    │
│   void                                                  │
│ + gewinnBerechnen(): Double                             │
│ + umsatzBerechnen(): Double                             │
│ + marktanteilAktualisieren(anteil: Double): void        │
│ + deaktivieren(): void                                  │
│ + getAktuelleAngebote(): List<Angebot>                  │
│ + getTransaktionsdaten(): List<Transaktion>             │
│ + getAuslastung(): Double                               │
└─────────────────────────────────────────────────────────┘
```

---

## Klasse A1.1: PrognoseModul

```
┌─────────────────────────────────────────────────────────┐
│                     PrognoseModul                       │
│                     <<SubAgent>>                        │
├─────────────────────────────────────────────────────────┤
│ - fluggesellschaftId: String                            │
│ - prognostizierteGesamtnachfrage: Integer               │
│ - prognostizierterNachfragemix: NachfrageMix            │
│ - tatsaechlicheNachfrage: Integer                       │
│ - sollIstAbweichung: Double                             │
│ - nachfrageelastizitaet: Double                         │
│ - historischeBuchungsverlaeufe: List<Buchungsverlauf>   │
│ - historischeAuslastungsraten: List<Double>             │
│ - vergangeneK1K2Verhaeltnisse: List<Double>             │
│ - buchungsgeschwindigkeit: Double                       │
│ - aktuelleSaison: Saison                                │
│ - aktuellerWochentag: Wochentag                         │
│ - istPeakPeriode: Boolean                               │
│ - istFerienzeit: Boolean                                │
├─────────────────────────────────────────────────────────┤
│ + prognoseErstellen(                                    │
│     kapazitaetsdaten: Kapazitaetsdaten,                 │
│     marktdaten: Marktdaten,                             │
│     zeitdaten: Zeitdaten                                │
│   ): Prognose                                           │
│ + sollIstVergleichDurchfuehren(                         │
│     aktuelleNachfrage: Integer                          │
│   ): Double                                             │
│ + nachfrageelastizitaetSchaetzen(): Double              │
│ + buchungsgeschwindigkeitBerechnen(                     │
│     buchungenProZeiteinheit: Integer                    │
│   ): Double                                             │
│ + nachfragemixPrognostizieren(): NachfrageMix           │
│ + historieDatenAktualisieren(                           │
│     verlauf: Buchungsverlauf                            │
│   ): void                                               │
│ + saisonalitaetBewerten(                                │
│     saison: Saison,                                     │
│     wochentag: Wochentag                                │
│   ): Double                                             │
│ + getPrognose(): Prognose                               │
│ + getAbweichung(): Double                               │
└─────────────────────────────────────────────────────────┘
```

---

## Klasse A1.2: PricingModul

```
┌─────────────────────────────────────────────────────────┐
│                      PricingModul                       │
│                      <<SubAgent>>                       │
├─────────────────────────────────────────────────────────┤
│ - fluggesellschaftId: String                            │
│ - aktuellePreise: Map<TicketKategorie, Double>          │
│ - preisHistorie: List<PreisAenderung>                   │
│ - ticketKategorien: List<TicketKategorie>               │
│ - wettbewerberPreise: List<Angebot>                     │
│ - preisstrategie: Preisstrategie                        │
│                                                         │
│ // Preisdifferenzierung 2. Ordnung                      │
│ - qualitaetsstufen: List<QualitaetsStufe>               │
│ - anreizkompatibilitaetsRestriktionen:                  │
│   List<Restriktion>                                     │
│                                                         │
│ // Preisdifferenzierung 3. Ordnung                      │
│ - segmentRabatte: Map<Kundensegment, Double>            │
│                                                         │
│ // Dynamische Preisanpassung                            │
│ - preisanpassungsFaktor: Double                         │
│ - mindestpreis: Double                                  │
│ - hoechstpreis: Double                                  │
│ - fruehbucherRabatt: Double                             │
│ - lastMinuteAufschlag: Double                           │
│                                                         │
│ // Peak-Load Pricing                                    │
│ - peakAufschlag: Double                                 │
│ - offPeakRabatt: Double                                 │
│                                                         │
│ // Modellparameter                                      │
│ - geschaetzteReservationspreiseK1: Double               │
│ - geschaetzteReservationspreiseK2: Double               │
│ - qualitaetspraeferenzParameterHoch: Double             │
│ - qualitaetspraeferenzParameterNiedrig: Double          │
│ - transportkostensatz: Double                           │
├─────────────────────────────────────────────────────────┤
│ + initialePreiseSetzten(                                │
│     prognose: Prognose,                                 │
│     kapazitaet: Kapazitaetsdaten                        │
│   ): Map<TicketKategorie, Double>                       │
│ + preiseDynamischAnpassen(                              │
│     prognoseAbweichung: Double,                         │
│     restkapazitaet: Kapazitaetsdaten,                   │
│     zeitschritt: Integer                                │
│   ): Map<TicketKategorie, Double>                       │
│ + aufWettbewerbReagieren(                               │
│     wettbewerberAngebote: List<Angebot>                 │
│   ): Map<TicketKategorie, Double>                       │
│ + peakLoadPricingAnwenden(                              │
│     istPeak: Boolean                                    │
│   ): Map<TicketKategorie, Double>                       │
│ + preisdifferenzierung2OrdnungAnwenden():               │
│   List<PreisQualitaetsKombination>                      │
│ + preisdifferenzierung3OrdnungAnwenden(                 │
│     segment: Kundensegment                              │
│   ): Double                                             │
│ + anreizkompatibilitaetPruefen(                         │
│     kombination: PreisQualitaetsKombination             │
│   ): Boolean                                            │
│ + ticketKategorieVerfuegbarkeitAnpassen(                │
│     kategorie: TicketKategorie,                         │
│     verfuegbar: Boolean                                 │
│   ): void                                               │
│ + getAktuellePreise(): Map<TicketKategorie, Double>     │
│ + getPreisHistorie(): List<PreisAenderung>              │
└─────────────────────────────────────────────────────────┘
```

---

## Klasse A1.3: KapazitaetsModul

```
┌─────────────────────────────────────────────────────────┐
│                   KapazitaetsModul                      │
│                    <<SubAgent>>                         │
├─────────────────────────────────────────────────────────┤
│ - fluggesellschaftId: String                            │
│ - fluege: List<Flug>                                    │
│                                                         │
│ // Physische Kapazität                                  │
│ - gesamtSitzplaetzeProFlug: Integer                     │
│ - flugzeugtyp: String                                   │
│ - anzahlFluege: Integer                                 │
│                                                         │
│ // Kommerzielle Kontingentierung                        │
│ - kontingentPremium: Integer                            │
│ - kontingentRestriktiv: Integer                         │
│ - ueberbuchungsRate: Double                             │
│                                                         │
│ // Buchungsstatus                                       │
│ - gebuchtePlaetzeGesamt: Integer                        │
│ - gebuchtePlaetzePremium: Integer                       │
│ - gebuchtePlaetzeRestriktiv: Integer                    │
│ - stornierungen: Integer                                │
│ - noShowRate: Double                                    │
│                                                         │
│ // Abgeleitete Werte                                    │
│ - verbleibendePlaetzeGesamt: Integer                    │
│ - verbleibendePlaetzePremium: Integer                   │
│ - verbleibendePlaetzeRestriktiv: Integer                │
│ - auslastungsRate: Double                               │
│ - istAusverkauft: Boolean                               │
├─────────────────────────────────────────────────────────┤
│ + kapazitaetInitialisieren(                             │
│     fluege: List<Flug>,                                 │
│     sitzplaetze: Integer,                               │
│     premiumAnteil: Double                               │
│   ): void                                               │
│ + buchungRegistrieren(                                  │
│     buchung: Buchung                                    │
│   ): Boolean                                            │
│ + stornierungVerarbeiten(                               │
│     buchungsId: String                                  │
│   ): void                                               │
│ + kontingentAnpassen(                                   │
│     kategorie: TicketKategorie,                         │
│     neuesKontingent: Integer                            │
│   ): void                                               │
│ + verfuegbarkeitPruefen(                                │
│     kategorie: TicketKategorie,                         │
│     flugId: String                                      │
│   ): Boolean                                            │
│ + auslastungBerechnen(): Double                         │
│ + auslastungProKategorie(                               │
│     kategorie: TicketKategorie                          │
│   ): Double                                             │
│ + getRestkapazitaet(): Kapazitaetsdaten                 │
│ + getGebuchtePlaetzeProKategorie():                     │
│   Map<TicketKategorie, Integer>                         │
│ + getVerfuegbarkeit():                                  │
│   Map<TicketKategorie, Integer>                         │
│ + isAusverkauft(): Boolean                              │
└─────────────────────────────────────────────────────────┘
```

---

## Klasse A1.4: Angebotsplanung

```
┌─────────────────────────────────────────────────────────┐
│                    Angebotsplanung                      │
│                     <<SubAgent>>                        │
├─────────────────────────────────────────────────────────┤
│ - fluggesellschaftId: String                            │
│                                                         │
│ // Strategische Planung                                 │
│ - bedienteRouten: List<Route>                           │
│ - flugfrequenzProRoute: Map<Route, Integer>             │
│ - abflugzeiten: List<LocalTime>                         │
│ - saisonaleAnpassungen: Map<Saison, Double>             │
│                                                         │
│ // Wettbewerbspositionierung                            │
│ - positionAufZeitkreis: Double                          │
│ - anzahlMarkenProdukte: Integer                         │
│ - netzwerktyp: Netzwerktyp                              │
│ - differenzierungsgrad: Double                          │
│                                                         │
│ // Modellparameter (Hotelling)                          │
│ - hotellingPosition: Double                             │
│ - symmetrischePositionierung: Boolean                   │
│                                                         │
│ // Slot-Verwaltung                                      │
│ - verfuegbareSlots: List<Slot>                          │
│ - zugewieseneSlots: List<Slot>                          │
├─────────────────────────────────────────────────────────┤
│ + routenPlanen(                                         │
│     marktstruktur: Marktstruktur,                       │
│     nachfrageprognose: Prognose                         │
│   ): List<Route>                                        │
│ + abflugzeitenFestlegen(                                │
│     route: Route,                                       │
│     wettbewerberZeiten: List<LocalTime>                 │
│   ): List<LocalTime>                                    │
│ + flugfrequenzBestimmen(                                │
│     route: Route,                                       │
│     nachfrage: Integer                                  │
│   ): Integer                                            │
│ + hotellingPositionBerechnen(                           │
│     anzahlWettbewerber: Integer,                        │
│     symmetrisch: Boolean                                │
│   ): Double                                             │
│ + saisonaleAnpassungVornehmen(                          │
│     saison: Saison                                      │
│   ): void                                               │
│ + getRouten(): List<Route>                              │
│ + getAbflugzeiten(): List<LocalTime>                    │
│ + getHotellingPosition(): Double                        │
│ + getAnzahlMarkenProdukte(): Integer                    │
└─────────────────────────────────────────────────────────┘
```

---

## Klasse A2: Vertriebsplattform

```
┌─────────────────────────────────────────────────────────┐
│                   Vertriebsplattform                    │
│                      <<Agent>>                          │
├─────────────────────────────────────────────────────────┤
│ - id: String                                            │
│ - name: String                                          │
│ - registrierteFluggesellschaften: List<String>          │
│ - aktuelleAngebote: List<Angebot>                       │
│ - transaktionsLog: List<Transaktion>                    │
│ - buchungsAnfragen: Queue<BuchungsAnfrage>              │
├─────────────────────────────────────────────────────────┤
│ + fluggesellschaftRegistrieren(                         │
│     airline: Fluggesellschaft                           │
│   ): void                                               │
│ + fluggesellschaftAbmelden(                             │
│     airlineId: String                                   │
│   ): void                                               │
│ + angeboteAktualisieren(                                │
│     airlineId: String,                                  │
│     angebote: List<Angebot>                             │
│   ): void                                               │
│ + angeboteAnzeigen(                                     │
│     route: Route,                                       │
│     filterKriterien: FilterKriterien                    │
│   ): List<Angebot>                                      │
│ + angeboteSortieren(                                    │
│     angebote: List<Angebot>,                            │
│     sortierung: Sortierkriterium                        │
│   ): List<Angebot>                                      │
│ + buchungsAnfrageEntgegennehmen(                        │
│     anfrage: BuchungsAnfrage                            │
│   ): BuchungsBestaetigung                               │
│ + buchungWeiterleiten(                                  │
│     anfrage: BuchungsAnfrage                            │
│   ): Boolean                                            │
│ + stornierungWeiterleiten(                              │
│     buchungsId: String                                  │
│   ): Boolean                                            │
│ + wettbewerberPreiseBereitstellen(                      │
│     airlineId: String                                   │
│   ): List<Angebot>                                      │
│ + getTransaktionsdaten(): List<Transaktion>             │
│ + getAlleAngebote(): List<Angebot>                      │
│ + getAngeboteNachRoute(                                 │
│     route: Route                                        │
│   ): List<Angebot>                                      │
│ + getAngeboteNachAirline(                               │
│     airlineId: String                                   │
│   ): List<Angebot>                                      │
└─────────────────────────────────────────────────────────┘
```

---

## Hilfsklassen / Datenklassen

```
┌──────────────────────────┐  ┌──────────────────────────┐
│         Angebot          │  │        Buchung           │
│       <<DataClass>>      │  │      <<DataClass>>       │
├──────────────────────────┤  ├──────────────────────────┤
│ - angebotId: String      │  │ - buchungId: String      │
│ - fluggesellschaftId:    │  │ - angebotId: String      │
│   String                 │  │ - konsumentId: String    │
│ - flugId: String         │  │ - konsumentTyp:          │
│ - route: Route           │  │   KonsumentTyp           │
│ - abflugzeit: LocalTime  │  │ - gezahlterPreis: Double │
│ - ticketKategorie:       │  │ - ticketKategorie:       │
│   TicketKategorie        │  │   TicketKategorie        │
│ - preis: Double          │  │ - buchungsZeitpunkt:     │
│ - qualitaet:             │  │   Integer                │
│   QualitaetsStufe        │  │ - abflugzeit: LocalTime  │
│ - verfuegbarePlaetze:    │  │ - route: Route           │
│   Integer                │  │ - storniert: Boolean     │
├──────────────────────────┤  ├──────────────────────────┤
│ + isVerfuegbar(): Boolean│  │ + stornieren(): void     │
└──────────────────────────┘  └──────────────────────────┘

┌──────────────────────────┐  ┌──────────────────────────┐
│       Prognose           │  │    Kapazitaetsdaten      │
│     <<DataClass>>        │  │      <<DataClass>>       │
├──────────────────────────┤  ├──────────────────────────┤
│ - gesamtNachfrage:       │  │ - gesamtKapazitaet:      │
│   Integer                │  │   Integer                │
│ - nachfrageMix:          │  │ - verbleibendGesamt:     │
│   NachfrageMix           │  │   Integer                │
│ - elastizitaet: Double   │  │ - verbleibendPremium:    │
│ - sollIstAbweichung:     │  │   Integer                │
│   Double                 │  │ - verbleibendRestriktiv: │
│ - konfidenz: Double      │  │   Integer                │
├──────────────────────────┤  │ - auslastungsRate:       │
│ + isUebertroffen():      │  │   Double                 │
│   Boolean                │  ├──────────────────────────┤
│ + isUnterschritten():    │  │ + isEngpass(): Boolean   │
│   Boolean                │  │ + isAusverkauft():       │
└──────────────────────────┘  │   Boolean                │
                              └──────────────────────────┘

┌──────────────────────────┐  ┌──────────────────────────┐
│    PreisAenderung        │  │PreisQualitaetsKombination│
│     <<DataClass>>        │  │      <<DataClass>>       │
├──────────────────────────┤  ├──────────────────────────┤
│ - zeitschritt: Integer   │  │ - ticketKategorie:       │
│ - ticketKategorie:       │  │   TicketKategorie        │
│   TicketKategorie        │  │ - qualitaet:             │
│ - alterPreis: Double     │  │   QualitaetsStufe        │
│ - neuerPreis: Double     │  │ - preis: Double          │
│ - grund:                 │  │ - restriktionen:         │
│   PreisAenderungsGrund   │  │   List<Restriktion>      │
├──────────────────────────┤  ├──────────────────────────┤
│ + getDifferenz(): Double │  │ + getNettoutzenK1(       │
│ + getProzentual(): Double│  │     theta: Double        │
└──────────────────────────┘  │   ): Double              │
                              │ + getNettoutzenK2(       │
                              │     theta: Double        │
                              │   ): Double              │
                              └──────────────────────────┘

┌──────────────────────────┐  ┌──────────────────────────┐
│         Route            │  │          Flug            │
│      <<DataClass>>       │  │       <<DataClass>>      │
├──────────────────────────┤  ├──────────────────────────┤
│ - routeId: String        │  │ - flugId: String         │
│ - herkunft: String       │  │ - route: Route           │
│ - ziel: String           │  │ - abflugzeit: LocalTime  │
│ - distanz: Double        │  │ - fluggesellschaftId:    │
│ - routentyp: Routentyp   │  │   String                 │
├──────────────────────────┤  │ - flugzeugtyp: String    │
│ + equals(other): Boolean │  │ - sitzplaetze: Integer   │
└──────────────────────────┘  ├──────────────────────────┤
                              │ + getKapazitaet():       │
                              │   Integer                │
                              └──────────────────────────┘

┌──────────────────────────┐  ┌──────────────────────────┐
│     NachfrageMix         │  │    BuchungsAnfrage       │
│      <<DataClass>>       │  │      <<DataClass>>       │
├──────────────────────────┤  ├──────────────────────────┤
│ - anteilK1: Double       │  │ - konsumentId: String    │
│ - anteilK2: Double       │  │ - konsumentTyp:          │
│ - absolutK1: Integer     │  │   KonsumentTyp           │
│ - absolutK2: Integer     │  │ - gewuenschteRoute:      │
├──────────────────────────┤  │   Route                  │
│ + getGesamt(): Integer   │  │ - gewuenschterFlug:      │
│ + getVerhaeltnis():      │  │   String                 │
│   Double                 │  │ - gewuenschteKategorie:  │
└──────────────────────────┘  │   TicketKategorie        │
                              │ - maxPreis: Double       │
                              ├──────────────────────────┤
                              │ + isGueltig(): Boolean   │
                              └──────────────────────────┘

┌──────────────────────────┐  ┌──────────────────────────┐
│   BuchungsBestaetigung   │  │     FilterKriterien      │
│      <<DataClass>>       │  │      <<DataClass>>       │
├──────────────────────────┤  ├──────────────────────────┤
│ - erfolgreich: Boolean   │  │ - route: Route           │
│ - buchungId: String      │  │ - minAbflugzeit:         │
│ - grund: String          │  │   LocalTime              │
├──────────────────────────┤  │ - maxAbflugzeit:         │
│ + isErfolgreich():       │  │   LocalTime              │
│   Boolean                │  │ - maxPreis: Double       │
└──────────────────────────┘  │ - ticketKategorie:       │
                              │   TicketKategorie        │
                              │ - airline: String        │
                              ├──────────────────────────┤
                              │ + matches(angebot:       │
                              │   Angebot): Boolean      │
                              └──────────────────────────┘

┌──────────────────────────┐
│      Transaktion         │
│      <<DataClass>>       │
├──────────────────────────┤
│ - transaktionId: String  │
│ - buchung: Buchung       │
│ - zeitstempel: Integer   │
│ - fluggesellschaftId:    │
│   String                 │
│ - route: Route           │
│ - preis: Double          │
│ - ticketKategorie:       │
│   TicketKategorie        │
│ - konsumentTyp:          │
│   KonsumentTyp           │
├──────────────────────────┤
│ + getDetails(): String   │
└──────────────────────────┘
```

---

## Enumerationen

```
┌──────────────────────────┐  ┌──────────────────────────┐
│    <<enumeration>>       │  │    <<enumeration>>       │
│    TicketKategorie       │  │    QualitaetsStufe       │
├──────────────────────────┤  ├──────────────────────────┤
│ PREMIUM_FLEX             │  │ HOCH                     │
│ RESTRIKTIV               │  │ NIEDRIG                  │
└──────────────────────────┘  └──────────────────────────┘

┌──────────────────────────┐  ┌──────────────────────────┐
│    <<enumeration>>        │  │    <<enumeration>>      │
│    KonsumentTyp           │  │    Saison               │
├──────────────────────────┤  ├──────────────────────────┤
│ GESCHAEFTSREISENDER      │  │ HAUPTSAISON              │
│ FREIZEITREISENDER        │  │ NEBENSAISON              │
└──────────────────────────┘  │ UEBERGANG                │
                              └──────────────────────────┘

┌──────────────────────────┐  ┌──────────────────────────┐
│    <<enumeration>>       │  │    <<enumeration>>       │
│    Netzwerktyp           │  │  PreisAenderungsGrund    │
├──────────────────────────┤  ├──────────────────────────┤
│ HUB_AND_SPOKE            │  │ NACHFRAGE_HOEHER         │
│ PUNKT_ZU_PUNKT           │  │ NACHFRAGE_NIEDRIGER      │
└──────────────────────────┘  │ KAPAZITAET_KNAPP         │
                              │ WETTBEWERB_REAKTION      │
┌──────────────────────────┐  │ PEAK_LOAD                │
│    <<enumeration>>       │  │ FRUEHBUCHER              │
│    Sortierkriterium      │  │ LAST_MINUTE              │
├──────────────────────────┤  └──────────────────────────┘
│ PREIS_AUFSTEIGEND        │
│ PREIS_ABSTEIGEND         │  ┌──────────────────────────┐
│ ABFLUGZEIT               │  │    <<enumeration>>       │
│ AIRLINE                  │  │    Routentyp             │
│ VERFUEGBARKEIT           │  ├──────────────────────────┤
└──────────────────────────┘  │ KURZSTRECKE              │
                              │ LANGSTRECKE              │
┌──────────────────────────┐  │ TOURISTISCH              │
│    <<enumeration>>       │  │ GESCHAEFTLICH            │
│    Wochentag             │  └──────────────────────────┘
├──────────────────────────┤
│ MONTAG                   │  ┌──────────────────────────┐
│ DIENSTAG                 │  │    <<enumeration>>       │
│ MITTWOCH                 │  │    Restriktion           │
│ DONNERSTAG               │  ├──────────────────────────┤
│ FREITAG                  │  │ KEINE_UMBUCHUNG          │
│ SAMSTAG                  │  │ KEINE_STORNIERUNG        │
│ SONNTAG                  │  │ MINDESTAUFENTHALT        │
└──────────────────────────┘  │ VORAUSBUCHUNGSFRIST      │
                              └──────────────────────────┘
```

---

## Beziehungsdiagramm

```
┌─────────────────────────────────────────────────────┐
│              Fluggesellschaft <<Agent>>             │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────┐│
│  │Angebots- │  │Kapazitäts│  │Prognose- │  │Pricing││
│  │planung   │──│Modul     │──│Modul     │──│Modul  ││
│  │(A1.4)    │  │(A1.3)    │  │(A1.1)    │  │(A1.2) ││
│  └──────────┘  └────┬─────┘  └──────────┘  └───┬───┘│
│                     │                           │   │
└─────────────────────┼───────────────────────────┼───┘
                      │                           │
           1..*  ◄────┘                           │
        ┌──────┐                                  │
        │ Flug │                           1..* ◄─┘
        └──────┘                      ┌──────────────┐
                                      │   Angebot    │
                                      └──────┬───────┘
                                             │
                                    ┌────────┴────────┐
                                    │                 │
                                    ▼                 ▼
                         ┌───────────────┐  ┌───────────────┐
                         │Vertriebsplatt │  │   Buchung     │
                         │form <<Agent>> │  └───────────────┘
                         └──────┬────────┘        │
                                │                 │
                                │            1..* │
                                ▼                 ▼
                         ┌──────────────┐  ┌──────────────┐
                         │ Transaktion  │  │ PreisÄnderung│
                         └──────────────┘  └──────────────┘


Kardinalitäten:
─────────────────────────────────────────────
Fluggesellschaft  1 ──── 1  PrognoseModul
Fluggesellschaft  1 ──── 1  PricingModul
Fluggesellschaft  1 ──── 1  KapazitaetsModul
Fluggesellschaft  1 ──── 1  Angebotsplanung
Fluggesellschaft  1 ──── *  Flug
Fluggesellschaft  1 ──── *  Angebot
Vertriebsplattform 1 ──── *  Fluggesellschaft
Vertriebsplattform 1 ──── *  Angebot
Vertriebsplattform 1 ──── *  Transaktion
PricingModul      1 ──── *  PreisAenderung
PricingModul      1 ──── *  PreisQualitaetsKombination
KapazitaetsModul  1 ──── *  Flug
Angebot           1 ──── *  Buchung
```

---

