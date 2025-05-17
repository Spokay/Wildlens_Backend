import datetime as dt
from typing import Dict

from pydantic import ConfigDict
from sqlalchemy import String, Column, JSON, TEXT
from sqlmodel import SQLModel, Field, Relationship, Session, select, insert




class Family(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True))
    species: list["Specie"] = Relationship(back_populates="family", cascade_delete=True)


class SpecieHabitat(SQLModel, table=True):
    specie_id: int = Field(foreign_key="specie.id", primary_key=True)
    habitat_id: int = Field(foreign_key="habitat.id", primary_key=True)


class Identification(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    specie_id: int = Field(foreign_key="specie.id", primary_key=True)
    file_storage_key: str = Field(sa_column=Column(String(255), primary_key=True))
    date_identified: dt.datetime = Field(default=dt.datetime.now(dt.UTC))


class Specie(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True))
    latin_name: str = Field(sa_column=Column(String(255)))
    description: str = Field(sa_column=Column(TEXT))
    size: str = Field(sa_column=Column(String(255)))
    region: str = Field(sa_column=Column(String(255)))
    fun_fact: str = Field(sa_column=Column(TEXT))
    specie_exemple_photo: str = Field(sa_column=Column(TEXT))
    footprint_exemple_photo: str = Field(sa_column=Column(TEXT))
    family_id: int = Field(foreign_key="family.id")
    family: "Family" = Relationship(back_populates="species")
    habitats: list["Habitat"] = Relationship(
        back_populates="species", link_model=SpecieHabitat
    )
    users: list["User"] = Relationship(
        back_populates="species", link_model=Identification
    )

    @property
    def identifications(self):
        from app.database import database_engine

        statement = (
            select(Identification)
            .where(Identification.specie_id == self.id)
            .order_by(Identification.date_identified)
        )

        with Session(database_engine) as session:
            try:
                response = session.exec(statement).all()
                if response:
                    return response
                else:
                    return []
            finally:
                session.close()

    def identifications_for_user(self, user_id):
        from app.database import database_engine

        statement = (
            select(Identification)
            .where(Identification.specie_id == self.id)
            .where(Identification.user_id == user_id)
            .order_by(Identification.date_identified)
        )

        with Session(database_engine) as session:
            try:
                response = session.exec(statement).all()
                if response:
                    return response
                else:
                    return []
            finally:
                session.close()

    def identifications_for_user(self, user_id):
        from app.database import database_engine
        statement = (
            select(Identification)
            .where(Identification.specie_id == self.id)
            .where(Identification.user_id == user_id)
            .order_by(Identification.date_identified)
        )

        with Session(database_engine) as session:
            try:
                response = session.exec(statement).all()
                if response:
                    return response
                else:
                    return []
            finally:
                session.close()

class Habitat(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True))
    species: list["Specie"] = Relationship(
        back_populates="habitats", link_model=SpecieHabitat
    )
    habitat_photo: str = Field(sa_column=Column(TEXT))


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
    username: str = Field(sa_column=Column(String(255), index=True, unique=True))
    email: str = Field(sa_column=Column(String(255), index=True, unique=True))
    password: str = Field(sa_column=Column(TEXT))
    disabled: bool = Field(default=False)
    created_at: dt.datetime = Field(default=dt.datetime.now(dt.UTC))
    updated_at: dt.datetime = Field(default=dt.datetime.now(dt.UTC))
    role_id: int = Field(foreign_key="role.id")
    role: "Role" = Relationship(back_populates="users")
    species: list["Specie"] = Relationship(
        back_populates="users", link_model=Identification
    )
    badges: list["Badge"] = Relationship(back_populates="users", link_model=UserBadge)
    profile_picture: str | None = Field(sa_column=Column(TEXT))


class Badge(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String(255), index=True))
    description: str = Field(sa_column=Column(TEXT))
    users: list["User"] = Relationship(back_populates="badges", link_model=UserBadge)


class BadgeCriteria(SQLModel, table=True):
    badge_id: int = Field(foreign_key="badge.id", primary_key=True)
    criteria: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    model_config = ConfigDict(
        frozen=False,
    )
