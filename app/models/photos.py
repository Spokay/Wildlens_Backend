from sqlmodel import SQLModel, Field
import datetime as dt


class Identification(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    specie_id: int = Field(foreign_key="specie.id", primary_key=True)
    date_identified: dt.datetime = Field(default=dt.datetime.now(dt.UTC))