import datetime as dt
from typing import Optional

from app.models.photos import Identification
from app.models.specie import Specie

from sqlmodel import SQLModel, Field, Relationship


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    users: list["User"] = Relationship(back_populates="role")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    password: str
    disabled: Optional[bool] = False
    created_at: dt.datetime = Field(default=dt.datetime.now(dt.UTC))
    updated_at: dt.datetime = Field(default=dt.datetime.now(dt.UTC))
    last_login: Optional[dt.datetime] = Field(default=dt.datetime.now(dt.UTC))
    role_id: int = Field(foreign_key="role.id")
    role: Role = Relationship(back_populates="users")
    species: list["Specie"] = Relationship(back_populates="users", link_model=Identification)