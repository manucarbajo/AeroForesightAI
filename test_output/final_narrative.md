# Simulationsbericht: Flugverkehr Szenarioplanung MVP

Prototypische Multi-Agenten-Simulation fuer Szenarioplanung im Flugverkehr (2025-2035)

## Überblick
- **Simulierte Runden:** 3
- **Simulierte Jahre:** 2026 – 2029
- **Gesamte Events:** 16
- **Preis Start:** 108.00 €
- **Preis Ende:** 125.97 €

## Rundenübersicht

### Runde 1 – Jahr 2027
- **regulator:** Um die Klimaziele zu erreichen und gleichzeitig die Wettbewerbsfähigkeit der Luftfahrt zu erhalten, wird entschieden, die CO2-Steuer weiterhin auf 55.0 Euro pro Tonne anzustigen, um den Treibstoffverbrauch zu reduzieren. Gleichzeitig wird eine Foerderung für die Entwicklung und den Einsatz von alternativen Antriebstechnologien wie SAF/E-Fuels/H2 gestartet, um die wirtschaftliche Auswirkungen zu minimieren.
- **provider:** Um die Nachfrage nach günstigen Flügen zu decken und gleichzeitig die Kosten minimieren, entscheide ich, die Preise um 8% zu senken.
- **consumer:** Die Nachfrage wird durch die steigende Nachfrageschwelle und die zunehmenden CO2-Steuern beeinflusst. Viele Privatreisende werden zu umweltbewussteren Entscheidungen führen, was zu einem Rückgang der Nachfrage nach günstigen Flügen führt. Die Geschäftsreisenden sind jedoch nur zum Teil von diesen Faktoren beeinflusst und bleiben eher bei ihren ursprünglichen Entscheidungen, die auf Preis und Zeitpunkt abzielen.

**Events (5):**
- consumer: Die Nachfrage nach günstigen Flügen nimmt ab, da Reisende umweltbewussterer Entscheidungen treffen
- provider: Preise um 8% gesenkt, Begruendung: Investition in SAF/E-Fuels/H2 reduziert Treibstoffkosten und senkt Preise.
- regulator: Die CO2-Steuer wird auf 55.0 Euro pro Tonne angehoben.
- regulator: Eine Initiative zur Foerderung der alternativen Antriebstechnologien wird gestartet.
- market: Market update: price=108.00, demand_level=1.00

### Runde 2 – Jahr 2028
- **regulator:** Die regulatorische Entscheidung soll die Klimaziele erreichen und gleichzeitig die Wettbewerbsfähigkeit der Luftfahrt erhalten. Die CO2-Steuer wird weiterhin auf 55.0 Euro pro Tonne angehoben, um den Treibstoffverbrauch zu reduzieren. Gleichzeitig wird eine Foerderung für die Entwicklung und den Einsatz von alternativen Antriebstechnologien wie SAF/E-Fuels/H2 gestartet, um die wirtschaftliche Auswirkungen zu minimieren.
- **provider:** Um die Nachfrage nach günstigen Flügen zu decken und gleichzeitig die Kosten minimieren, entscheide ich, die Preise um 8% zu senken. Dieser Schritt wird durch die steigende Nachfrageschwelle und die zunehmenden CO2-Steuern beeinflusst.
- **consumer:** Die Nachfrage nach günstigen Flügen nimmt ab, da Reisende umweltbewussterer Entscheidungen treffen. Dies führt zu einer Abnahme der Zahlungsbereitschaft, insbesondere bei den Privatreisenden, die sich für alternative Reiseziele oder -möglichkeiten entscheiden. In der gleichen Runde wird ein Preisverlust von 8% bei Flügen angeboten, was für Geschäftsreisende nur zum Teil beeinflusst ist und sie eher bei ihren ursprünglichen Entscheidungen bleibt. Daher ist es für mich als Konsument entscheidend, auf Alternativangebote wie Bussen oder Züge zurückzugreifen, um die Umweltbelastung zu minimieren.

**Events (6):**
- consumer: Die Nachfrage nach günstigen Flügen nimmt ab, da Reisende umweltbewussterer Entscheidungen treffen
- consumer: Preise um 8% gesenkt, Begruendung: Investition in SAF/E-Fuels/H2 reduziert Treibstoffkosten und senkt Preise
- provider: Preise um 8% gesenkt, Begruendung: Investition in SAF/E-Fuels/H2 reduziert Treibstoffkosten und senkt Preise.
- regulator: Die CO2-Steuer wird auf 55.0 Euro pro Tonne angehoben.
- regulator: Der Preis für Flüge sinkt um 8%.
- market: Market update: price=116.64, demand_level=1.00

### Runde 3 – Jahr 2029
- **regulator:** um den Treibstoffverbrauch zu reduzieren und die Klimaziele zu erreichen
- **provider:** Die steigende Nachfrage nach günstigen Flügen und die CO2-Steuererhöhung führen dazu, dass Investitionen in Alternativen wie SAF/E-Fuels/H2 sinnvoll sind. Dies reduziert Treibstoffkosten und senkt Preise.
- **consumer:** Die Nachfrage nach günstigen Flügen nimmt ab, da Reisende umweltbewussterer Entscheidungen treffen. Dies führt zu einer Abnahme der Zahlungsbereitschaft, insbesondere bei den Privatreisenden, die sich für alternative Reiseziele oder -möglichkeiten entscheiden. Als Konsument möchte ich daher auf Alternativangebote wie Bussen oder Züge zurückgreifen, um die Umweltbelastung zu minimieren.

**Events (5):**
- consumer: Die Nachfrage nach günstigen Flügen nimmt ab, da Reisende umweltbewussterer Entscheidungen treffen
- provider: Preise um 8% gesenkt, Begruendung: Investition in SAF/E-Fuels/H2 reduziert Treibstoffkosten und senkt Preise
- provider: CO2-Steuer auf 55.0 Euro pro Tonne angehoben, um den Treibstoffverbrauch zu reduzieren und die Klimaziele zu erreichen
- regulator: Fallback event generated from parsed actions.
- market: Market update: price=125.97, demand_level=1.00

## Finaler Umweltzustand
- **Mobilitaetsbeduerfnis / Nachfrage:** F1.2 – Stagnation und Verzicht, Substitution
- **Regulatorische Strenge:** F2.2 – Radikale Dekarbonisierung, Verbote
- **Technologische Reife:** F3.2 – Durchbruch bei SAF/E-Fuels/H2
- **Wirtschaftliche Entwicklung:** F4.1 – Stabiles Wachstum, moderate Inflation
- **Verfuegbarkeit von Alternativen:** F5.1 – Schiene stagniert, Fliegen alternativlos
- **Gesellschaftlicher Wertewandel:** F6.1 – Fliegen bleibt akzeptiert
- **Geopolitische Stabilitaet:** F7.1 – Offene Maerkte, Kooperation