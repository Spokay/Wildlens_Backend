from pydantic import BaseModel, Field
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
    image_file_name: str = Field(..., min_length=2, description="Image file name must be at least 2 characters")
    tmp_file_path: str = Field(..., min_length=2, description="Temporary file path must be at least 2 characters")


class CreateSpecieInfo(BaseModel):
    name: str = Field(..., min_length=2, description="Species name must be at least 2 characters")
    latin_name: str = Field(..., min_length=2, description="Latin name must be at least 2 characters")
    description: str = Field(..., min_length=2, description="Description must be at least 2 characters")
    size: str = Field(..., min_length=2, description="Size must be at least 2 characters")
    region: str = Field(..., min_length=2, description="Region must be at least 2 characters")
    fun_fact: str = Field(..., min_length=2, description="Fun fact must be at least 2 characters")
    specie_exemple_photo_url: str = Field(..., min_length=2, description="Species example photo URL must be at least 2 characters")
    footprint_exemple_photo_url: str = Field(..., min_length=2, description="Footprint example photo URL must be at least 2 characters")
    family_id: int
    habitats_ids: list[int]


class UpdateSpecieInfo(BaseModel):
    name: Optional[str] = Field(None, min_length=2, description="Species name must be at least 2 characters")
    latin_name: Optional[str] = Field(None, min_length=2, description="Latin name must be at least 2 characters")
    description: Optional[str] = Field(None, min_length=2, description="Description must be at least 2 characters")
    size: Optional[str] = Field(None, min_length=2, description="Size must be at least 2 characters")
    region: Optional[str] = Field(None, min_length=2, description="Region must be at least 2 characters")
    fun_fact: Optional[str] = Field(None, min_length=2, description="Fun fact must be at least 2 characters")
    specie_exemple_photo_url: Optional[str] = Field(None, min_length=2, description="Species example photo URL must be at least 2 characters")
    footprint_exemple_photo_url: Optional[str] = Field(None, min_length=2, description="Footprint example photo URL must be at least 2 characters")
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