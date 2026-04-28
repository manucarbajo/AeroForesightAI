from pydantic import BaseModel


class CIBEntry(BaseModel):
    source_factor: str
    target_factor: str
    influence_score: float
    reasoning: str = ""


class CIBMatrix(BaseModel):
    entries: list[CIBEntry]
    round_generated: int
    metadata: dict = {}
