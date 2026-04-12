# Sequenzdiagramme

---

## Vollständiger Simulationsdurchlauf

```
┌────┐ ┌────┐ ┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌────┐ ┌────┐ ┌────┐
│ R3 │ │ R1 │ │  A1(i) │ │A1.4  │ │A1.3  │ │A1.1  │ │A1.2│ │ A2 │ │ R2 │
│Zeit│ │Mrkt│ │Airline │ │Plan  │ │Kapa  │ │Prog  │ │Pric│ │Plat│ │Mon │
└─┬──┘ └─┬──┘ └───┬────┘ └──┬───┘ └──┬───┘ └──┬───┘ └─┬──┘ └─┬──┘ └─┬──┘
  │      │        │         │        │        │       │      │      │
══╪══════╪════════╪═════════╪════════╪════════╪═══════╪══════╪══════╪═══
  │      │   PHASE 1: MARKTINITIALISIERUNG    │       │      │      │
══╪══════╪════════╪═════════╪════════╪════════╪═══════╪══════╪══════╪═══
  │      │        │         │        │        │       │      │      │
  │──────>        │         │        │        │       │      │      │
  │ start│        │         │        │        │       │      │      │
  │ Signal│       │         │        │        │       │      │      │
  │      │        │         │        │        │       │      │      │
  │      │──marktInitialisieren(config)       │       │      │      │
  │      │  │     │         │        │        │       │      │      │
  │      │  │ marktformFestlegen()   │        │       │      │      │
  │      │  │ routenDefinieren()     │        │       │      │      │
  │      │  │ nachfrageDefinieren()  │        │       │      │      │
  │      │  │ kostenstrukturFestlegen()       │       │      │      │
  │      │  │     │         │        │        │       │      │      │
  │      │<─┘     │         │        │        │       │      │      │
  │      │        │         │        │        │       │      │      │
  │      │──────────────────────────────────────────────────>│      │
  │      │   marktstrukturdatenErfassen(hhi, anteile)        │      │
  │      │        │         │        │        │       │      │      │
  │      │        │         │        │        │       │      │      │
  │      ├────────> (für jede Airline i = 1..n)       │      │      │
  │      │ erzeuge│         │        │        │       │      │      │
  │      │ Airline│         │        │        │       │      │      │
  │      │        │         │        │        │       │      │      │
  │      │        │──initialisieren(marktstruktur)    │      │      │
  │      │        │  │      │        │        │       │      │      │
  │      │        │<─┘      │        │        │       │      │      │
  │      │        │         │        │        │       │      │      │
  │      │        │─────────────────────────────────────>    │      │
  │      │        │    fluggesellschaftRegistrieren(airline) │      │
  │      │        │         │        │        │       │      │      │
  │<─────┤        │         │        │        │       │      │      │
  │ init │        │         │        │        │       │      │      │
  │ done │        │         │        │        │       │      │      │
  │      │        │         │        │        │       │      │      │
```

---
