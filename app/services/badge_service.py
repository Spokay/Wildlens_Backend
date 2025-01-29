from typing import Dict, Any

from sqlalchemy.sql.functions import count
from sqlmodel import Session, select

from app.config import NUMBER_OF_CLASSES
from app.dto.badge import BadgeResponse
from app.models import Badge, UserBadge, Identification, BadgeCriteria


def get_user_badges(user_id: int, session : Session) -> list[BadgeResponse]:

    badges_response = []

    # get the badges already received by the user
    badges_already_received = get_badges_already_received(user_id, session)

    # Extract the badge IDs of the badges already received
    awarded_badge_ids = {badge_response.id for badge_response in badges_already_received}

    # fill the badges list with the badges already received
    badges_response.extend(badges_already_received)

    # get the criteria for the badges not yet received
    unawarded_badge_criteria = get_criteria_for_unawarded_badges(awarded_badge_ids, session)

    # check the criteria for each badge not yet received
    for badge_criteria in unawarded_badge_criteria:
        if evaluate_criteria(user_id, badge_criteria.criteria, session):
            # award the badge to the user
            user_badge = award_badge(user_id, badge_criteria.badge_id, session)

            # get the badge information
            badge = session.get(Badge, badge_criteria.badge_id)
            # add it to the response list
            badges_response.append(
                BadgeResponse(
                    id=badge.id,
                    name=badge.name,
                    description=badge.description,
                    date_awarded=user_badge.date_awarded
                )
            )

    return badges_response

def get_badges_already_received(user_id: int, session: Session) -> list[BadgeResponse]:
    badges_statement = (select(Badge, UserBadge.date_awarded)
                        .join_from(Badge, UserBadge, Badge.id == UserBadge.badge_id)
                        .where(UserBadge.user_id == user_id))

    badges = session.exec(badges_statement).all()

    return [
        BadgeResponse(id=badge.id, name=badge.name, description=badge.description, date_awarded=date_awarded)
        for badge, date_awarded in badges
    ]


def get_criteria_for_unawarded_badges(awarded_badge_ids: set[int], session: Session) -> list[BadgeCriteria]:
    criterias_statement = (
        select(BadgeCriteria)
        .where(BadgeCriteria.badge_id.not_in(awarded_badge_ids))
    )

    return session.exec(criterias_statement).all()

def award_badge(user_id: int, badge_id: int, session: Session) -> UserBadge:
    user_badge = UserBadge(user_id=user_id, badge_id=badge_id)
    session.add(user_badge)
    session.commit()
    session.refresh(user_badge)
    return user_badge


def evaluate_identification_count_by_specie(user_id: int, criteria: Dict[str, Any], session: Session) -> bool:
    required = criteria.get("required", 0)

    required_specie = criteria.get("specie")

    statement = select(count()).where(Identification.user_id == user_id)

    if required_specie:
        statement = statement.where(Identification.specie_id == required_specie)

    identification_count = session.exec(statement).one()

    return identification_count >= required

def evaluate_all_specied_identified(user_id: int, session: Session) -> bool:

    statement = select(count()).distinct(Identification.specie_id).where(Identification.user_id == user_id)
    amount_different_identified_species = session.exec(statement).one()

    return NUMBER_OF_CLASSES == amount_different_identified_species

def evaluate_criteria(user_id: int, criteria: Dict[str, Any], session: Session) -> bool:
    criteria_type = criteria.get("type")

    # criterias evaluation
    if criteria_type == "identification_count_by_specie":
        return evaluate_identification_count_by_specie(user_id, criteria, session)

    if criteria_type == "all_species_identified":
        return evaluate_all_specied_identified(user_id, session)

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