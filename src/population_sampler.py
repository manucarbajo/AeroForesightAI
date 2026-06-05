import numpy as np
from pydantic import BaseModel

from src.models.population_models import PopulationConfig, DistributionConfig


class SegmentStats(BaseModel):
    segment_id: str
    share: float
    total_individuals: int
    booked_individuals: int
    booking_rate: float


class PopulationStats(BaseModel):
    total_population: int
    total_booked: int
    total_demand: float
    segments: dict[str, SegmentStats]


def _sample_distribution(config: DistributionConfig, size: int) -> np.ndarray:
    if config.type == "lognormal":
        # Approximation for lognormal mean/sigma from normal mean/std_dev
        # using the log of the mean for mu
        mu = np.log(max(0.01, config.mean))
        values = np.random.lognormal(mean=mu, sigma=max(0.01, config.std_dev), size=size)
    else:
        # Fallback for normal and beta (simplified to normal)
        values = np.random.normal(config.mean, config.std_dev, size)
        
    return np.clip(values, config.min_value, config.max_value)


def run_population_sampling(config: PopulationConfig, ticket_price: float, carbon_tax: float) -> PopulationStats:
    """
    Samples individuals based on PopulationConfig and calculates booking decisions
    using a Logit-based choice function.
    """
    total_pop = config.total_population
    
    segments_stats = {}
    total_booked = 0
    
    for segment in config.segments:
        n_individuals = int(np.round(total_pop * segment.share))
        if n_individuals <= 0:
            continue
            
        # Sample attributes for each individual
        # Note: income_level is generated but currently not used in the simplified utility function,
        # but could be used to adjust price elasticity.
        elasticity = _sample_distribution(segment.price_elasticity, n_individuals)
        awareness = _sample_distribution(segment.environmental_awareness, n_individuals)
        
        # Base utility to fly (represents the general desire to travel)
        base_utility = 2.0
        
        # Price penalty
        # normalized_price ~ 1.0 when ticket price is 100 EUR
        normalized_price = ticket_price / 100.0 
        price_penalty = elasticity * normalized_price
        
        # Environmental penalty
        # normalized_tax ~ 1.0 when carbon tax is 100 EUR/t
        normalized_tax = carbon_tax / 100.0
        eco_penalty = awareness * normalized_tax
        
        # Final Utility
        utility = base_utility - price_penalty - eco_penalty
        
        # Probability of booking (Logit function)
        prob = np.exp(utility) / (1.0 + np.exp(utility))
        
        # Draw random choices based on probability
        choices = np.random.rand(n_individuals) < prob
        
        booked = int(np.sum(choices))
        total_booked += booked
        
        segments_stats[segment.id] = SegmentStats(
            segment_id=segment.id,
            share=segment.share,
            total_individuals=n_individuals,
            booked_individuals=booked,
            booking_rate=booked / n_individuals if n_individuals > 0 else 0.0
        )
        
    return PopulationStats(
        total_population=total_pop,
        total_booked=total_booked,
        total_demand=total_booked / total_pop if total_pop > 0 else 0.0,
        segments=segments_stats
    )
