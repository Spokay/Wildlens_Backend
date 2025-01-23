from pydantic import BaseModel
from app.models import Specie


class SpeciePrediction(BaseModel):
    class_number: int
    probability: float


class SpeciePredictionResponse(BaseModel):
    specie: Specie
    probability: float

class SpecieInformationResponse(BaseModel):
    specie: Specie