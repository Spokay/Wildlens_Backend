from sqlmodel import SQLModel


class HabitatResponse(SQLModel):
    id: int
    name: str
    description: str | None