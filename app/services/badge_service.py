from typing import Dict, Any

from sqlmodel import Session, select

from app.dto.badge import BadgeResponse
from app.models import Badge, User, UserBadge, Identification


def get_user_badges(user_id: int, session : Session) -> list[BadgeResponse]:
    statement = select(Badge, UserBadge.date_awarded).join_from(
        User, UserBadge, User.id == UserBadge.user_id
    ).join_from(
        UserBadge, Badge, UserBadge.badge_id == Badge.id
    )
    badges = session.exec(statement).all()

    badge_responses = [
        BadgeResponse(
            id=badge.id,
            name=badge.name,
            description=badge.description,
            date_awarded=badge.date_awarded
        ) for badge in badges
    ]
    return badge_responses

def evaluate_identification_count_by_specie(user_id: int, criteria: Dict[str, Any], session: Session) -> bool:
    required = criteria.get("required", 0)

    required_specie = criteria.get("specie")

    statement = select(Identification).where(Identification.user_id == user_id)

    if required_specie:
        statement = statement.where(Identification.specie_id == required_specie)

    identification_count = session.exec(statement).count()

    return len(identification_count) >= required

def evaluate_criteria(user_id: int, criteria: Dict[str, Any], session: Session) -> bool:
    criteria_type = criteria.get("type")

    if criteria_type == "identification_count_by_specie":
        return evaluate_identification_count_by_specie(user_id, criteria, session)

    # TODO: Implement the other criteria types here

    # handle the "and" and "or" criteria types
    elif criteria_type == "and":
        conditions = criteria.get("conditions", [])
        return all(evaluate_criteria(user_id, cond, session) for cond in conditions)

    elif criteria_type == "or":
        conditions = criteria.get("conditions", [])
        return any(evaluate_criteria(user_id, cond, session) for cond in conditions)

    else:
        raise ValueError(f"Unknown criteria type: {criteria_type}")