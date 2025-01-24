from sqlmodel import Session, select

from app.dto.badge import BadgeResponse
from app.models import Badge, User, UserBadge


def get_user_badges(user_id: int, session : Session) -> list[BadgeResponse]:
    statement = select(Badge, UserBadge.date_awarded).join_from(
        User, UserBadge, User.id == UserBadge.user_id
    ).join_from(
        UserBadge, Badge, UserBadge.badge_id == Badge.id
    )
    badges = session.exec(statement).all()
    print(badges)

    badge_responses = [
        BadgeResponse(
            id=badge.id,
            name=badge.name,
            description=badge.description,
            date_awarded=badge.date_awarded
        ) for badge in badges
    ]
    return badge_responses