from sqlmodel import SQLModel
import datetime as dt


class BadgeResponse(SQLModel):
    id: int
    name: str
    description: str | None
    date_awarded: dt.datetime
    badge_image: str | None