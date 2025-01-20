from typing import Optional

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship


class SpeciePrediction(BaseModel):
    class_number: int
    probability: float


class Family(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    species: list["Specie"] = Relationship(back_populates="family")

class SpecieHabitat(SQLModel, table=True):
    specie_id: int = Field(foreign_key="specie.id", primary_key=True)
    habitat_id: int = Field(foreign_key="habitat.id", primary_key=True)

class Specie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    latin_name: Optional[str] = None
    description: Optional[str] = None
    size: Optional[str] = None
    region: Optional[str] = None
    fun_fact: Optional[str] = None
    family_id: int = Field(foreign_key="family.id")
    family: Family = Relationship(back_populates="species")
    habitats: list["Habitat"] = Relationship(back_populates="species", link_model=SpecieHabitat)

class Habitat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    species: list[Specie] = Relationship(back_populates="habitats", link_model=SpecieHabitat)