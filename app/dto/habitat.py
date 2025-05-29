from sqlmodel import SQLModel
from pydantic import BaseModel, Field
from typing import Optional

class HabitatResponse(SQLModel):
    id: int
    name: str
    habitat_photo: str | None


class CreateHabitatInfo(BaseModel):
    name: str = Field(..., min_length=2, description="Habitat name must be at least 2 characters")
    habitat_photo: str = Field(..., min_length=2, description="Habitat photo URL must be at least 2 characters")


class UpdateHabitatInfo(BaseModel):
    name: Optional[str] = Field(None, min_length=2, description="Habitat name must be at least 2 characters")
    habitat_photo: Optional[str] = Field(None, min_length=2, description="Habitat photo URL must be at least 2 characters")

class CreateHabitatResponse(BaseModel):
    message: str
    habitat: HabitatResponse

class UpdateHabitatResponse(BaseModel):
    message: str
    habitat: HabitatResponse

class DeleteHabitatResponse(BaseModel):
    message: str
    habitat: HabitatResponse