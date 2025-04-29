from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import Session
from starlette import status
from starlette.responses import JSONResponse

from app.database import get_session
from app.mappers.habitat_mapper import get_habitat_mapper
from app.dto.habitat import CreateHabitatInfo, UpdateHabitatInfo
from app.services.habitats_service import (
    create_habitat,
    delete_habitat,
    list_all_habitats,
    update_habitat,
    get_habitat_by_id,
)


router = APIRouter(prefix="/habitats", tags=["habtitats"])


@router.post("/create")
async def create_habitat_route(
    habitat_to_create: CreateHabitatInfo = Body(...),
    session: Session = Depends(get_session),
    habitat_mapper=Depends(get_habitat_mapper),
):
    habitat = await create_habitat(session, habitat_mapper, habitat_to_create)
    return JSONResponse(
        {
            "message": "habitats created successfully",
            "habitat": habitat.model_dump(mode="json"),
        },
        status_code=status.HTTP_201_CREATED,
    )


@router.delete("/delete/{habitat_id}")
async def delete_habitat_route(
    habitat_id: int,
    session: Session = Depends(get_session),
    habitat_mapper=Depends(get_habitat_mapper),
):
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
    return JSONResponse(
        {
            "message": "habitats deleted successfully",
            "habitat": habitat.model_dump(mode="json"),
        }
    )


@router.put("/update/{habitat_id}")
async def update_habitat_route(
    habitat_id: int,
    session: Session = Depends(get_session),
    habitat_mapper=Depends(get_habitat_mapper),
    habitat_update: UpdateHabitatInfo = Body(...),
):
    habitat = await update_habitat(
        session,
        habitat_mapper,
        habitat_update,
        habitat_id,
    )

    return JSONResponse(
        {
            "message": "habitat updated successfully",
            "habitat": habitat.model_dump(mode="json"),
        }
    )


@router.get("/list/all")
async def list_all_habitats_route(
    session: Session = Depends(get_session),
    habitat_mapper=Depends(get_habitat_mapper),
) -> JSONResponse:
    habitats = await list_all_habitats(session, habitat_mapper)

    return JSONResponse(
        {
            "message": "habitats retrieved successfully",
            "habitats": [habitat.model_dump(mode="json") for habitat in habitats],
        }
    )


@router.get("/list/{habitat_id}")
async def list_habitat_by_id_route(
    habitat_id: int,
    session: Session = Depends(get_session),
    habitat_mapper=Depends(get_habitat_mapper),
) -> JSONResponse:
    habitat = await get_habitat_by_id(
        session,
        habitat_id,
        habitat_mapper,
    )

    return JSONResponse(
        {
            "message": "habitats retrieved successfully",
            "habitat": habitat.model_dump(mode="json"),
        }
    )
