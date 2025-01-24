from sqlmodel import SQLModel


class FamilyResponse(SQLModel):
    id: int
    name: str