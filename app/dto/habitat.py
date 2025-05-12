from sqlmodel import SQLModel
from pydantic import BaseModel


class HabitatResponse(SQLModel):
    id: int
    name: str
    description: str | None


class CreateHabitatInfo(BaseModel):
    name: str
    description: str


class UpdateHabitatInfo(BaseModel):
    name: str
    description: str
