from typing import Dict, Any

from sqlalchemy.sql.functions import count
from sqlmodel import Session, select

from app.config import get_settings
from app.dto.badge import BadgeResponse
from app.models import Badge, UserBadge, Identification, BadgeCriteria, Specie, SpecieHabitat

settings = get_settings()

async def get_user_badges(user_id: int, session : Session) -> list[BadgeResponse]:

    badges_response = []

    # get the badges already received by the user
    badges_already_received = await get_badges_already_received(user_id, session)

    # Extract the badge IDs of the badges already received
    awarded_badge_ids = {badge_response.id for badge_response in badges_already_received}

    # fill the badges list with the badges already received
    badges_response.extend(badges_already_received)

    # get the criteria for the badges not yet received
    unawarded_badge_criteria = await get_criteria_for_unawarded_badges(awarded_badge_ids, session)

    # check the criteria for each badge not yet received
    for badge_criteria in unawarded_badge_criteria:
        if await evaluate_criteria(user_id, badge_criteria.criteria, session):
            # award the badge to the user
            user_badge = await award_badge(user_id, badge_criteria.badge_id, session)

            # get the badge information
            badge = session.get(Badge, badge_criteria.badge_id)
            # add it to the response list
            badges_response.append(
                BadgeResponse(
                    id=badge.id,
                    name=badge.name,
                    description=badge.description,
                    badge_image=badge.badge_image or None,
                    date_awarded=user_badge.date_awarded
                )
            )

    return badges_response

async def get_badges_already_received(user_id: int, session: Session) -> list[BadgeResponse]:
    badges_statement = (select(Badge, UserBadge.date_awarded)
                        .join_from(Badge, UserBadge, Badge.id == UserBadge.badge_id)
                        .where(UserBadge.user_id == user_id))

    badges = session.exec(badges_statement).all()

    return [
        BadgeResponse(
            id=badge.id,
            name=badge.name,
            description=badge.description,
            badge_image=badge.badge_image or None,
            date_awarded=date_awarded
        )
        for badge, date_awarded in badges
    ]


async def get_criteria_for_unawarded_badges(awarded_badge_ids: set[int], session: Session) -> list[BadgeCriteria]:
    criterias_statement = (
        select(BadgeCriteria)
        .where(BadgeCriteria.badge_id.not_in(awarded_badge_ids))
    )

    return session.exec(criterias_statement).all()

async def award_badge(user_id: int, badge_id: int, session: Session) -> UserBadge:
    user_badge = UserBadge(user_id=user_id, badge_id=badge_id)
    session.add(user_badge)
    session.commit()
    session.refresh(user_badge)
    return user_badge


async def evaluate_identification_count_by_specie(user_id: int, criteria: Dict[str, Any], session: Session) -> bool:
    required = criteria.get("required", 0)

    required_specie = criteria.get("specie")

    statement = select(count()).where(Identification.user_id == user_id)

    if required_specie:
        statement = statement.where(Identification.specie_id == required_specie)

    identification_count = session.exec(statement).one()

    return identification_count >= required


async def evaluate_all_species_identified_by_habitat(user_id: int, criteria: Dict[str, Any], session: Session) -> bool:
    required_habitat = criteria.get("habitat")

    if not required_habitat:
        return False

    # Get all species in the specified habitat
    all_species_in_habitat_statement = (
        select(count())
        .select_from(Specie)
        .join(SpecieHabitat, Specie.id == SpecieHabitat.specie_id)
        .where(SpecieHabitat.habitat_id == required_habitat)
    )

    total_species_in_habitat = session.exec(all_species_in_habitat_statement).one()

    # Get count of species the user has identified in this habitat
    user_identified_species_statement = (
        select(count())
        .distinct(Identification.specie_id)
        .select_from(Identification)
        .join(SpecieHabitat, Identification.specie_id == SpecieHabitat.specie_id)
        .where(Identification.user_id == user_id)
        .where(SpecieHabitat.habitat_id == required_habitat)
    )

    user_identified_count = session.exec(user_identified_species_statement).one()

    return user_identified_count == total_species_in_habitat

async def evaluate_all_specied_identified(user_id: int, session: Session) -> bool:

    statement = select(count()).distinct(Identification.specie_id).where(Identification.user_id == user_id)
    amount_different_identified_species = session.exec(statement).one()

    return settings.number_of_classes == amount_different_identified_species

async def evaluate_criteria(user_id: int, criteria: Dict[str, Any], session: Session) -> bool:
    criteria_type = criteria.get("type")

    # criterias evaluation
    if criteria_type == "identification_count_by_specie":
        return await evaluate_identification_count_by_specie(user_id, criteria, session)

    if criteria_type == "all_species_identified_by_habitat":
        return await evaluate_all_species_identified_by_habitat(user_id, criteria, session)

    if criteria_type == "all_species_identified":
        return await evaluate_all_specied_identified(user_id, session)

    # TODO: Implement the other criteria types here

    # handle the "and" and "or" criteria types
    elif criteria_type == "and":
        conditions = criteria.get("conditions", [])
        return all([await evaluate_criteria(user_id, cond, session) for cond in conditions])

    elif criteria_type == "or":
        conditions = criteria.get("conditions", [])
        return any([await evaluate_criteria(user_id, cond, session) for cond in conditions])

    else:
        raise ValueError(f"Unknown criteria type: {criteria_type}")