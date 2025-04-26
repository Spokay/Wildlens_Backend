from pydantic import BaseModel
from sqlmodel import SQLModel
from typing import Optional


class FamilyResponse(SQLModel):
    id: int
    name: str


class CreateFamilyInfo(BaseModel):
    name: str


class UpdateFamilyInfo(BaseModel):
    name: Optional[str] = None
