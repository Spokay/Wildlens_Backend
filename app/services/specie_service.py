from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session, select
from starlette import status

from app.dto.species import SpecieResponse, SpecieBasicInfoResponse
from app.dto.users import AuthenticatedUser
from app.mappers.specie_mapper import SpecieMapper
from app.models import Specie, Identification, Family


async def get_specie_by_class_number(class_number: int, session: Session) -> Specie:
    specie: Optional[Specie] = session.get(Specie, class_number)
    if specie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Specie with id {class_number} not found"
        )

    return specie


async def save_identification(
        session: Session,
        authenticated_user: AuthenticatedUser,
        class_number: int,
        blob_key: str
) -> Identification:

    identification = Identification(
        user_id=authenticated_user.user_id,
        specie_id=class_number,
        file_storage_key=blob_key
    )
    session.add(identification)
    session.commit()
    session.refresh(identification)

    return identification


async def get_identified_species_by_user(user_id: int, session: Session, specie_mapper : SpecieMapper) -> list[SpecieBasicInfoResponse]:
    statement = select(Specie).join(Identification).where(Identification.user_id == user_id)

    identified_species = session.exec(statement).all()

    species_response = await specie_mapper.species_to_basic_info_responses(identified_species)

    return species_response