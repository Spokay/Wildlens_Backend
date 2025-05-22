from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.dto.family import (
    CreateFamilyInfo,
    UpdateFamilyInfo,
    FamilyResponse,
)
from app.mappers.family_mapper import FamilyMapper
from app.models import Family


async def create_family(
    session: Session, family_mapper: FamilyMapper, family_to_create: CreateFamilyInfo
) -> FamilyResponse:
    already_exists_statement = select(Family).where(
        family_to_create.name == Family.name
    )

    already_exists = session.exec(already_exists_statement).all()
    if len(already_exists) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"family with name {family_to_create.name} already exists",
        )
    else:
        new_family = Family(
            name=family_to_create.name,
        )

        session.add(new_family)
        session.commit()

        return await family_mapper.family_to_response(new_family)


async def update_family(
    session: Session, family_mapper: FamilyMapper, family: UpdateFamilyInfo, family_id
) -> FamilyResponse:
    family_to_update = session.get(Family, family_id)

    if not family_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"family with id {family_id} not found",
        )

    for key, value in family.model_dump(mode="json", exclude_unset=True).items():
        if hasattr(family_to_update, key):
            setattr(family_to_update, key, value)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"family does not have property {key}",
            )

    session.commit()

    return await family_mapper.family_to_response(family_to_update)


async def delete_family(
    session: Session, family_id: int, family_mapper: FamilyMapper
) -> FamilyResponse:
    family_to_delete = session.get(Family, family_id)

    if not family_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"family with id {family_id} not found",
        )

    response = await family_mapper.family_to_response(family_to_delete)

    session.delete(family_to_delete)
    session.commit()
    return response


async def list_all_families(
    session: Session, family_mapper: FamilyMapper
) -> list[FamilyResponse]:
    statement = select(Family)
    families = session.exec(statement).all()

    if not families:
        return []

    family_list = [family for family in families]

    familes_response = await family_mapper.families_to_response(family_list)

    return familes_response


async def get_family(
    session: Session, family_id: int, family_mapper: FamilyMapper
) -> FamilyResponse:
    statement = select(Family).where(Family.id == family_id)
    family = session.exec(statement).first()

    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="family not found",
        )

    return await family_mapper.family_to_response(family)
