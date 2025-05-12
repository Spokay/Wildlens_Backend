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

class CreateHabitatResponse(BaseModel):
    message: str
    habitat: HabitatResponse

class UpdateHabitatResponse(BaseModel):
    message: str
    habitat: HabitatResponse

class DeleteHabitatResponse(BaseModel):
    message: str
    habitat: HabitatResponse