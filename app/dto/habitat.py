from sqlmodel import SQLModel
from pydantic import BaseModel


class HabitatResponse(SQLModel):
    id: int
    name: str
    habitat_photo: str | None


class CreateHabitatInfo(BaseModel):
    name: str
    habitat_photo: str


class UpdateHabitatInfo(BaseModel):
    name: str
    habitat_photo: str

class CreateHabitatResponse(BaseModel):
    message: str
    habitat: HabitatResponse

class UpdateHabitatResponse(BaseModel):
    message: str
    habitat: HabitatResponse

class DeleteHabitatResponse(BaseModel):
    message: str
    habitat: HabitatResponse