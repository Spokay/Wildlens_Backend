from pydantic import BaseModel
from sqlmodel import SQLModel
from typing import Optional, Union

from app.dto.family import FamilyResponse
from app.dto.habitat import HabitatResponse
from app.models import Identification


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

class SpecieIdentifiedResponse(SpecieResponse):
    identifications: list["Identification"]
    is_identified: Optional[bool] = None

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


class SpecieClassificationResponse(BaseModel):
    predictions_response: list[SpeciePredictionResponse]
    tmp_file_path: str
    image_file_name: str


class UploadInfo(BaseModel):
    specie_id: int
    user_id: int
    image_file_name: str
    tmp_file_path: str


class CreateSpecieInfo(BaseModel):
    name: str
    latin_name: str
    description: str
    size: str
    region: str
    fun_fact: str
    specie_exemple_photo_url: str
    footprint_exemple_photo_url: str
    family_id: int
    habitats_ids: list[int]


class UpdateSpecieInfo(BaseModel):
    name: Optional[str] = None
    latin_name: Optional[str] = None
    description: Optional[str] = None
    size: Optional[str] = None
    region: Optional[str] = None
    fun_fact: Optional[str] = None
    specie_exemple_photo_url: Optional[str] = None
    footprint_exemple_photo_url: Optional[str] = None
    family_id: Optional[int] = None
    habitats_ids: Optional[list[int]] = None

class CreateSpecieResponse(BaseModel):
    message: str
    specie: SpecieBasicInfoResponse | SpecieResponse

class UpdateSpecieResponse(BaseModel):
    message: str
    specie: SpecieBasicInfoResponse | SpecieResponse

class DeleteSpecieResponse(BaseModel):
    message: str
    specie:SpecieBasicInfoResponse | SpecieResponse