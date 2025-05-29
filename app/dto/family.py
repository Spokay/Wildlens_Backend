from pydantic import BaseModel, Field
from sqlmodel import SQLModel
from typing import Optional


class FamilyResponse(SQLModel):
    id: int
    name: str


class CreateFamilyInfo(BaseModel):
    name: str = Field(..., min_length=2, description="Family name must be at least 2 characters")


class UpdateFamilyInfo(BaseModel):
    name: Optional[str] = Field(None, min_length=2, description="Family name must be at least 2 characters")

class CreateFamilyResponse(BaseModel):
    message: str
    family: FamilyResponse

class UpdateFamilyResponse(BaseModel):
    message: str
    family: FamilyResponse

class DeleteFamilyResponse(BaseModel):
    message: str
    family: FamilyResponse