import datetime as dt

from sqlalchemy import String, Column
from sqlmodel import SQLModel, Field, Relationship


class Family(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True))
    species: list["Specie"] = Relationship(back_populates="family")

class SpecieHabitat(SQLModel, table=True):
    specie_id: int = Field(foreign_key="specie.id", primary_key=True)
    habitat_id: int = Field(foreign_key="habitat.id", primary_key=True)

class Identification(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    specie_id: int = Field(foreign_key="specie.id", primary_key=True)
    date_identified: dt.datetime = Field(default=dt.datetime.now(dt.UTC))
    file_storage_key: str = Field(sa_column=Column(String(255), unique=True))

class Specie(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True))
    latin_name: str = Field(default=None)
    description: str = Field(default=None)
    size: str = Field(default=None)
    region: str = Field(default=None)
    fun_fact: str = Field(default=None)
    family_id: int = Field(foreign_key="family.id")
    family: "Family" = Relationship(back_populates="species")
    habitats: list["Habitat"] = Relationship(back_populates="species", link_model=SpecieHabitat)
    users: list["User"] = Relationship(back_populates="species", link_model=Identification)

class Habitat(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True))
    description: str = None
    species: list["Specie"] = Relationship(back_populates="habitats", link_model=SpecieHabitat)


class Role(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True))
    users: list["User"] = Relationship(back_populates="role")


class UserBadge(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    badge_id: int = Field(foreign_key="badge.id", primary_key=True)
    date_awarded: dt.datetime = Field(default=dt.datetime.now(dt.UTC))

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(sa_column=Column(String(255), index=True))
    password: str
    disabled: bool = Field(default=False)
    created_at: dt.datetime = Field(default=dt.datetime.now(dt.UTC))
    updated_at: dt.datetime = Field(default=dt.datetime.now(dt.UTC))
    role_id: int = Field(foreign_key="role.id")
    role: "Role" = Relationship(back_populates="users")
    species: list["Specie"] = Relationship(back_populates="users", link_model=Identification)
    badges: list["Badge"] = Relationship(back_populates="users", link_model=UserBadge)


class Badge(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True))
    description: str = Field(default=None)
    users: list["User"] = Relationship(back_populates="badges", link_model=UserBadge)