# Challenge 1

## Softwareentwicklungsmodell 

*XP (Extreme Programming):*

XP-Primärtechniken
- Pair Programming: Zwei Entwickler arbeiten gemeinsam an einem Rechner (Pilot/Copilot) – erhöht die Codequalität und den Wissenstransfer.
- Continuous Integration: Code wird mehrmals täglich integriert und automatisiert getestet, um Integrationsprobleme frühzeitig zu lösen.
- Whole Team: Alle Rollen arbeiten eng zusammen, um Abhängigkeiten zu minimieren.
- Informative Workspace: Projektstatus und Fortschritt sind für alle Teammitglieder jederzeit visuell im Arbeitsraum sichtbar. -> eventuell aufsetzen von Kanban-Board?
- User Stories: Anforderungen werden als kurze Geschichten aus Nutzersicht formuliert, um den Fokus auf den echten Mehrwert zu legen. -> ist genau unsere Anforderung
- Continuous Feedback: Regelmäßige Rückkopplungsschleifen durch Tests, Kundenfeedback und Team-Reviews zur Kurskorrektur. -> wir müssen die ganze Zeit testen und behalten/merken was gut ist
- Test-driven Development (TDD): Automatisierte Tests werden vor dem eigentlichen Code geschrieben, was Design und Stabilität verbessert. -> wir haben bestimmte anforderungen die wir erfüllen sollen
- Wöchentliche Iterationen: Kurze Entwicklungszyklen mit wöchentlicher Planung und Review ermöglichen maximale Flexibilität. -> wir machen tägliche commits für thies und kunz, also macht es sinn kurze entwicklungszyklen zu haben
- Incremental Design: Die Systemarchitektur entwickelt sich schrittweise durch ständiges Refactoring weiter, statt sie vorab starr festzulegen. -> wir wissen nicht wie das ende aussieht, können es immer nur ausbauen 
- Sit Together: Das Team arbeitet in einem gemeinsamen Raum, um Kommunikationswege kurz zu halten und die Dynamik zu fördern. -> sind eh im austausch
- Energized Work: Ein nachhaltiges Arbeitstempo ohne Überstunden sichert langfristige Produktivität und Konzentration -> wir wollen schnell vorankommen
(Kopiert aus: https://www.it-agile.de/agiles-wissen/agile-entwicklung/was-ist-extreme-programming/, als Bulletpoints von KI erstellt)

*Warum XP für das Projekt?*
- Starre Modelle wie Wasserfall oder V-Modell ist für so Prototypen nicht geeignet, da keine Iteration erlaub ist. Wir sind immer am testen und haben kein richtiges Ziel. Dazu müssen wir tägliche Commits machen. 
- Alternative wäre womöglich wie bspw. Scrum. Es muss jedoch schnelle Iterationen erlauben.

## UML-Klassendiagramme

- Bevor Architekturüberlegung Recherche bzgl. der heutigen Situation und Abschätzung was passieren kann
- Benötigt, um realistische/branchenspezifische Vorhersagen zu können -> ohne Hintergrundwissen bringt uns die Modellierung nichts
- Strategic Foresight a la Börjeson et al.  (gefunden im Moodle Kurs) 
- Developing qualitative scenario storylines for environmental change assessment. auch interessant für das Projekt (auch aus Moodle)
- Da verschiedene äußere Faktoren eine Rolle spielen, kann PESTEL-Analyse eventuell -> evtl. einbauen im Prozess, damit auch diese Faktoren immer wieder generiert werden? -> Aktualität im Monat / Jahr, und alle Akteure wissen, welche äußerlichen Faktoren entstehen -> Interessant wäre es, wenn die KI diese Faktoren analysiert und anwendet -> wenn wir starre Angaben machen, verzerrt das die Möglichkeiten die entstehen könnten
-> Folgefrage: wie stellen wir innere Faktoren nach? wie bspw. innerhalb einer Airline
- Branchenspezifische Parameter, wie Größe der Flotte und SAF-Verfügbarkeit (sustainable aviation fuel) -> Ableitung durch IATA Net Zero Roadmap für den Anfang, dann weitere Simulation im späteren Verlauf mit LLM

### Abkürzungen fürs Verständnis:
- SAF = Sustainable Aviation Fule = Nachhaltiger Luftfahrttreibstoff aus nichtfossilen Rohstoffen
 
```mermaid
classDiagram
    class Agent {
        +str role
        +float budget
        +list goals
        +dict memory
    }

    class Traveler {
        +float environmental_awareness
        +float price_sensitivity
        +int travel_frequency
        +str preferred_transport_mode
        +str character
    }

    class Airline {
        +int total_fleet_size
        +dict fleet_composition 
        +float operational_efficiency
        +float carbon_footprint
        +float reputation
        +float profit
    }

    class Regulator {
        +float co2_tax_rate
        +dict subsidies_allocation 
        +float rd_funding_pool
        +int restriction_level
    }

    class AirportManagement {
        +int capacity
        +dict possible_routes
        +int budget
        +str investment
    }

    class Environment {
        +int current_year
        +float global_carbon_emissions
        +dict energy_prices
        +dict infrastructure_readiness 
        +dict tech_maturity_index 
        +advance_year()
        +get_global_context() dict
    }

    class SimulationEngine {
        +list agents
        +Environment env
        +MessageLog log
        +run_simulation()
    }

    Agent <|-- Traveler
    Agent <|-- Airline
    Agent <|-- Regulator
    Agent <|-- AirportManagement
```
### Info des Diagramms:
- fleet_composition: z.B. {"kerosene": 80, "saf": 20, "hydrogen": 0}
- subsidies_allocation: z.B. {"saf": 500M, "hydrogen_tech": 200M}
- energy_prices: z.B. {"kerosene": 1.2, "saf": 3.5, "hydrogen": 8.0}
- infrastructure_readiness: z.B. {"saf_refineries": 0.4, "h2_airports": 0.1}
- tech_maturity_index: Wie marktreif sind neue Antriebe?
- Agent: budget -> evtl. unnötig da Regulator kein Geld hat


### Erklärungen zu den ersten Überlegungen
- Agent hat mehrere Unterklassen Traveler, Airline, Regulator und erben von Agent -> Damit werden die Hauptmechanismen mitgegeben und spezifiziert in einzelnen Agenten
- Environment isoliert den Markt von der Ausführungslogik. Man hätte es auch theoretisch zusammen machen können, aber ich denke, dass wir damit besser voran kommen
- SimulationEngine brauchen wir für jeden Iterationsschritt (Ausführung je Monat x 20 Monate, Jahre oder etc.)
- SimulationEngine steuert Workflow von langgraph. Da wir genau spezifizieren, können wir wie in der gezeigten Demo leicht den Ablauf steuern
- MessageLog für uns, damit wir pro Iteration nachvollziehen können was passiert und Parameter etc. anpassen können. -> direktes Logging von dem was wir ausarbeiten

#### Agent Traveler mit Parameter character
- Agent Traveler hat den Parameter character -> damit ist gemeint, wie der Kunde drauf ist, was ihm wichtig ist. Evtl. auch als dict, jedoch ist es wichtig verschiedene Kundentypen zu haben. Hier könnte man auch noch tiefer einstiegen, und verschiedene Personas überlegen oder der KI generieren lassen im Prozess. Ein Kundentyp ist jedoch nicht zielführend, da die Welt mehr als einen Typ hat.
- Quelle: Bonabeu 2002 -> In Agenten-basierten Umgebungen brauchen Agenten unterschiedliche Präferenzen. Das ist bereits gegebenen für die verschiedenen
- SFO (San Francisco International Airport) Leitaden (Quelle SFO-prinicples-of-reach) die zeigt, wie ein Airport Passagiere unterteilt.
- Folgende Typologies gibt es: Leisure Passengers, Business Passengers, Family Passengers, Assisted Passengers, Unique Passengers -> genauere Beschreibung im Doc

## UML-Aktivitätsdiagramm
Bessere Nachvollziehbarkeit meiner Iterationsschleife.
Wahrscheinlich vereinfacht, jedoch schwer komplett zu modellieren. Wird immer weiter ausgebaut

```mermaid
flowchart TD
    %% Start
    Start(("Start der Simulation")) --> Init["Initialisierung Environment & Agenten"]
    
    %% Condition
    Init --> CheckYear{"Zieljahr/Zielmonat erreicht?"}
    
    %% Regulator
    CheckYear -- Nein --> RegulatorNode["<b>Node: Regulator</b><br>Analysiert vorige Iteration und setzt neue Regulatoriken"]
    
    %% Airport Management
    RegulatorNode --> AirportNode["<b>Node: AirportManagement</b><br>Analysiert vorige Iteration und setzt neue Routen/Kappas"]
    
    %% Environment
    AirportNode --> EnvUpdate1["<b>Node: Environment</b><br>Gibt neue Politik vor und stellt diese in Zahlen zur Verfügung<br>(evtl. auch als dict mit Fließtext)"]
    
    %% Wahrnehmung für Agenten
    EnvUpdate1 --> AgentSync["<b>Node: Wahrnehmung der Agenten</b><br>Alle Agenten lesen das neue Environment aus<br>und updaten ihr Memory"]
    
    %% Airline 
    AgentSync --> AirlineNode["<b>Node: Airline</b><br>Passt Flotte & Preise an, basierend auf<br>neuen Airport-Kapazitäten & SAF-Preisen, etc."]
    
    %% Traveler
    AirlineNode --> TravelerNode["<b>Node: Traveler</b><br>Bewertet sein Umfeld (ihm steht frei, was ihm wichtig ist),<br>trifft dann finale Reiseentscheidung"]
    
    %% Environment Zusammenfassung
    TravelerNode --> EnvUpdate2["<b>Node: Environment-Zusammenfassung</b><br>Berechnet bspw. resultierende global_carbon_emissions<br>& führt dann advance_year() aus"]
    
    %% Logging
    EnvUpdate2 --> Log["<b>Node: MessageLog</b><br>Speichert alle Entscheidungen als Jahres/Monats-Protokoll"]
    
    %% Loop
    Log --> CheckYear
    
    %% Ende
    CheckYear -- Ja --> End(("Ende / Datenexport<br>(SPÄTER CROSS-MATRIX READY MACHEN)"))
```

### Erklärungen zum Diagramm
- Erst muss der äußere Umstand analysiert werden, wie bspw. Regulatorik und AirportManagement
- Danach muss Environment angepasst werden
- Wahrnehmung der Agenten wird getriggert, damit alle die Infos haben
- Airline passt sich dementsprechend an
- Traveler prüft, ob es sich lohnt zu kaufen.

***ERM***

tbd

***User Stories***

Systemnutzer
Traveler
Airline
Regulator
AirportManagement