from src.models.cib_models import CIBEntry, CIBMatrix
from src.models.state_models import SimulationState


class CIBExtractorNode:
    """
    Extrahiert CIB-Matrix aus dem Event-Log und den Faktoränderungen.
    MVP-Regel: Wenn ein Event einen Faktor beeinflusst und ein anderer Faktor
    ebenfalls betroffen ist, wird eine Einflussbewertung abgeleitet.
    """

    # Einflussstärke je nach Agenten-Typ
    AGENT_WEIGHT = {
        "regulator": 1.0,
        "provider": 0.75,
        "consumer": 0.5,
        "market": 0.25,
    }

    def invoke(self, state: SimulationState) -> SimulationState:
        entries = self._extract_entries(state)

        state.cib_matrix = CIBMatrix(
            entries=entries,
            round_generated=state.clock.current_round,
            metadata={
                "total_events": len(state.event_log),
                "total_entries": len(entries),
                "rounds": state.clock.current_round,
            },
        )
        return state

    def _extract_entries(self, state: SimulationState) -> list[CIBEntry]:
        # Sammle alle Faktor-Paare die in Events gemeinsam vorkommen
        pair_scores: dict[tuple[str, str], list[float]] = {}
        pair_reasoning: dict[tuple[str, str], str] = {}

        for event in state.event_log:
            if len(event.affected_factors) < 2:
                continue

            weight = self.AGENT_WEIGHT.get(event.source_agent, 0.5)

            # Alle Paare aus affected_factors bilden
            factors = event.affected_factors
            for i in range(len(factors)):
                for j in range(len(factors)):
                    if i == j:
                        continue
                    source = factors[i]
                    target = factors[j]

                    # Nur bekannte Faktoren
                    if source not in state.environment.factors:
                        continue
                    if target not in state.environment.factors:
                        continue

                    pair = (source, target)
                    if pair not in pair_scores:
                        pair_scores[pair] = []
                        pair_reasoning[pair] = event.description
                    pair_scores[pair].append(weight)

        # CIBEntry pro Paar erstellen
        entries: list[CIBEntry] = []
        for (source, target), scores in pair_scores.items():
            avg_score = sum(scores) / len(scores)
            entries.append(
                CIBEntry(
                    source_factor=source,
                    target_factor=target,
                    influence_score=round(avg_score, 3),
                    reasoning=pair_reasoning[(source, target)],
                )
            )

        # Sortiert nach Einflussstärke
        entries.sort(key=lambda e: e.influence_score, reverse=True)
        return entries