from sqlmodel import SQLModel


class BadgeResponse(SQLModel):
    id: int
    name: str
    description: str | None