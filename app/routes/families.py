from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import Session
from starlette import status
from starlette.responses import JSONResponse

from app.database import get_session
from app.mappers.family_mapper import get_family_mapper
from app.dto.family import CreateFamilyInfo, UpdateFamilyInfo
from app.services.family_service import (
    create_family,
    delete_family,
    list_all_families,
    update_family,
)


router = APIRouter(prefix="/families", tags=["families"])


@router.post("/create")
async def create_family_route(
    family_to_create: CreateFamilyInfo = Body(...),
    session: Session = Depends(get_session),
    family_mapper=Depends(get_family_mapper),
):
    family = await create_family(session, family_mapper, family_to_create)
    return JSONResponse(
        {
            "message": "familys created successfully",
            "family": family.model_dump(mode="json"),
        },
        status_code=status.HTTP_201_CREATED,
    )


@router.delete("/delete/{family_id}")
async def delete_family_route(
    family_id: int,
    session: Session = Depends(get_session),
    family_mapper=Depends(get_family_mapper),
):
    family = await delete_family(
        session,
        family_id,
        family_mapper,
    )
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"family with id {family_id} not found",
        )
    return JSONResponse(
        {
            "message": "families deleted successfully",
            "family": family.model_dump(mode="json"),
        }
    )


@router.put("/update/{family_id}")
async def update_family_route(
    family_id: int,
    session: Session = Depends(get_session),
    family_mapper=Depends(get_family_mapper),
    family_update: UpdateFamilyInfo = Body(...),
):
    family = await update_family(
        session,
        family_mapper,
        family_update,
        family_id,
    )

    return JSONResponse(
        {
            "message": "family updated successfully",
            "family": family.model_dump(mode="json"),
        }
    )


@router.get("/list/all")
async def list_all_familys_route(
    session: Session = Depends(get_session),
    family_mapper=Depends(get_family_mapper),
) -> JSONResponse:
    families = await list_all_families(session, family_mapper)

    return JSONResponse(
        {
            "message": "families retrieved successfully",
            "families": [family.model_dump(mode="json") for family in families],
        }
    )
