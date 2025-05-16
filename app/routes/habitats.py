from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import Session
from starlette import status
from starlette.responses import JSONResponse

from app.database import get_session
from app.mappers.habitat_mapper import get_habitat_mapper
from app.dto.habitat import (
    CreateHabitatInfo,
    UpdateHabitatInfo,
    CreateHabitatResponse,
    DeleteHabitatResponse,
    UpdateHabitatResponse,
    HabitatResponse,
)
from app.services.authentication_service import role_required
from app.services.habitats_service import (
    create_habitat,
    delete_habitat,
    list_all_habitats,
    update_habitat,
    get_habitat_by_id,
)


router = APIRouter(prefix="/habitats", tags=["habtitats"])


@role_required("ADMIN")
@router.post(
    "/create",
    description="Create a habitat",
    response_model=CreateHabitatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_habitat_route(
    habitat_to_create: CreateHabitatInfo = Body(...),
    session: Session = Depends(get_session),
    habitat_mapper=Depends(get_habitat_mapper),
) -> CreateHabitatResponse:
    habitat = await create_habitat(session, habitat_mapper, habitat_to_create)
    return CreateHabitatResponse(
        message="habitats created successfully", habitat=habitat
    )


@role_required("ADMIN")
@router.delete(
    "/delete/{habitat_id}",
    description="Delete a habitat",
    response_model=DeleteHabitatResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_habitat_route(
    habitat_id: int,
    session: Session = Depends(get_session),
    habitat_mapper=Depends(get_habitat_mapper),
) -> DeleteHabitatResponse:
    habitat = await delete_habitat(
        session,
        habitat_id,
        habitat_mapper,
    )
    if not habitat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"habitat with id {habitat_id} not found",
        )

    return DeleteHabitatResponse(
        message="habitats deleted successfully", habitat=habitat
    )


@role_required("ADMIN")
@router.put(
    "/update/{habitat_id}",
    description="Update a habitat",
    response_model=UpdateHabitatResponse,
    status_code=status.HTTP_200_OK,
)
async def update_habitat_route(
    habitat_id: int,
    session: Session = Depends(get_session),
    habitat_mapper=Depends(get_habitat_mapper),
    habitat_update: UpdateHabitatInfo = Body(...),
) -> UpdateHabitatResponse:
    habitat = await update_habitat(
        session,
        habitat_mapper,
        habitat_update,
        habitat_id,
    )

    return UpdateHabitatResponse(
        message="habitat updated successfully", habitat=habitat
    )


@router.get(
    "/list/all",
    description="List all habitats",
    response_model=list[HabitatResponse],
    status_code=status.HTTP_200_OK,
)
async def list_all_habitats_route(
    session: Session = Depends(get_session),
    habitat_mapper=Depends(get_habitat_mapper),
) -> list[HabitatResponse]:
    habitats = await list_all_habitats(session, habitat_mapper)

    return habitats


@router.get(
    "/{habitat_id}",
    description="List a habitat",
    response_model=HabitatResponse,
    status_code=status.HTTP_200_OK,
)
async def list_habitat_by_id_route(
    habitat_id: int,
    session: Session = Depends(get_session),
    habitat_mapper=Depends(get_habitat_mapper),
) -> HabitatResponse:
    habitat = await get_habitat_by_id(
        session,
        habitat_id,
        habitat_mapper,
    )

    return habitat
