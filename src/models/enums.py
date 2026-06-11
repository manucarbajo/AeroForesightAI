from enum import Enum


class AgentType(str, Enum):
    CONSUMER = "consumer"
    PROVIDER = "provider"
    REGULATOR = "regulator"


class EventType(str, Enum):
    PRICE_CHANGE = "price_change"
    REGULATION = "regulation"
    DEMAND_SHIFT = "demand_shift"
    INVESTMENT = "investment"
    POLICY_CHANGE = "policy_change"
    MARKET_EVENT = "market_event"
    TECHNOLOGY_SHIFT = "technology_shift"


class DistributionType(str, Enum):
    NORMAL = "normal"
    UNIFORM = "uniform"
    TRIANGULAR = "triangular"
    LOGNORMAL = "lognormal"
    BETA = "beta"
