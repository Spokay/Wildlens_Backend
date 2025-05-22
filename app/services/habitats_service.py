from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.dto.habitat import (
    CreateHabitatInfo,
    UpdateHabitatInfo,
    HabitatResponse,
)
from app.mappers.habitat_mapper import HabitatMapper
from app.models import Habitat


async def create_habitat(
    session: Session,
    habitat_mapper: HabitatMapper,
    habitat_to_create: CreateHabitatInfo,
) -> HabitatResponse:
    already_exists_statement = select(Habitat).where(
        habitat_to_create.name == Habitat.name
    )

    already_exists = session.exec(already_exists_statement).all()
    if len(already_exists) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"habitat with name {habitat_to_create.name} already exists",
        )
    else:
        new_habitat = Habitat(
            name=habitat_to_create.name, habitat_photo=habitat_to_create.habitat_photo
        )

        session.add(new_habitat)
        session.commit()

        return await habitat_mapper.habitat_to_response(new_habitat)


async def update_habitat(
    session: Session,
    habitat_mapper: HabitatMapper,
    habitat: UpdateHabitatInfo,
    habitat_id,
) -> HabitatResponse:
    habitat_to_update = session.get(Habitat, habitat_id)

    if not habitat_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"habitat with id {habitat_id} not found",
        )

    for key, value in habitat.model_dump(mode="json", exclude_unset=True).items():
        if hasattr(habitat_to_update, key):
            setattr(habitat_to_update, key, value)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"habitat does not have property {key}",
            )

    session.commit()

    return await habitat_mapper.habitat_to_response(habitat_to_update)


async def delete_habitat(
    session: Session, habitat_id: int, habitat_mapper: HabitatMapper
) -> HabitatResponse:
    habitat_to_delete = session.get(Habitat, habitat_id)

    if not habitat_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"habitat with id {habitat_id} not found",
        )

    response = await habitat_mapper.habitat_to_response(habitat_to_delete)

    session.delete(habitat_to_delete)
    session.commit()
    return response


async def list_all_habitats(
    session: Session, habitat_mapper: HabitatMapper
) -> list[HabitatResponse]:
    statement = select(Habitat)
    habitats = session.exec(statement).all()

    if not habitats:
        return []

    habitat_list = [habitat for habitat in habitats]

    familes_response = await habitat_mapper.habitat_list_to_response(habitat_list)

    return familes_response


async def get_habitat_by_id(
    session: Session, habitat_id: int, habitat_mapper: HabitatMapper
) -> HabitatResponse:
    statement = select(Habitat).where(Habitat.id == habitat_id)
    habitat = session.exec(statement).first()

    if not habitat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"habitat with id {habitat_id} not found",
        )

    return await habitat_mapper.habitat_to_response(habitat)
