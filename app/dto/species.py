from pydantic import BaseModel
from sqlmodel import SQLModel

from app.dto.family import FamilyResponse
from app.dto.habitat import HabitatResponse


class SpeciePrediction(BaseModel):
    class_number: int
    probability: float

class SpecieBasicInfoResponse(BaseModel):
    id: int
    name: str
    latin_name: str
    region: str
    family: "FamilyResponse"
    habitats: list["HabitatResponse"]

class SpecieResponse(SQLModel):
    id: int
    name: str
    latin_name: str
    description: str
    size: str
    region: str
    fun_fact: str
    specie_exemple_photo_url: str
    footprint_exemple_photo_url: str
    family: "FamilyResponse"
    habitats: list["HabitatResponse"]

class SpeciePredictionResponse(SQLModel):
    id: int
    name: str
    latin_name: str
    description: str
    size: str
    region: str
    fun_fact: str
    family: "FamilyResponse"
    habitats: list["HabitatResponse"]
    probability: float


