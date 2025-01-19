from pydantic import BaseModel

from app.models.specie import Specie


class SpecieResponse(BaseModel):
    specie: Specie
    probability: float