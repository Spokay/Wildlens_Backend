from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import Session
from starlette import status
from starlette.responses import JSONResponse

from app.database import get_session
from app.mappers.family_mapper import get_family_mapper
from app.dto.family import CreateFamilyInfo, UpdateFamilyInfo, CreateFamilyResponse, DeleteFamilyResponse, \
    UpdateFamilyResponse, FamilyResponse
from app.services.authentication_service import role_required
from app.services.family_service import (
    create_family,
    delete_family,
    list_all_families,
    update_family,
    get_family,
)


router = APIRouter(prefix="/families", tags=["families"])


@role_required("ADMIN")
@router.post(
    "/create",
    description="Create a family",
    response_model=CreateFamilyResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_family_route(
    family_to_create: CreateFamilyInfo = Body(...),
    session: Session = Depends(get_session),
    family_mapper=Depends(get_family_mapper),
)-> CreateFamilyResponse:
    family = await create_family(session, family_mapper, family_to_create)

    return CreateFamilyResponse(message="family created successfully", family=family)


@role_required("ADMIN")
@router.delete(
    "/delete/{family_id}",
    description="Delete a family",
    response_model=DeleteFamilyResponse,
    status_code=status.HTTP_200_OK
)
async def delete_family_route(
    family_id: int,
    session: Session = Depends(get_session),
    family_mapper=Depends(get_family_mapper),
)-> DeleteFamilyResponse:
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

    return DeleteFamilyResponse(message="family deleted successfully", family=family)


@role_required("ADMIN")
@router.put(
    "/update/{family_id}",
    description="Update a family",
    response_model=UpdateFamilyResponse,
    status_code=status.HTTP_200_OK
)
async def update_family_route(
    family_id: int,
    session: Session = Depends(get_session),
    family_mapper=Depends(get_family_mapper),
    family_update: UpdateFamilyInfo = Body(...),
)-> UpdateFamilyResponse:
    family = await update_family(
        session,
        family_mapper,
        family_update,
        family_id,
    )

    return UpdateFamilyResponse(message="family updated successfully", family=family)


@router.get(
    "/list/all",
    description="List all families",
    response_model=list[FamilyResponse],
    status_code=status.HTTP_200_OK
)
async def list_all_familys_route(
    session: Session = Depends(get_session),
    family_mapper=Depends(get_family_mapper),
) -> list[FamilyResponse]:
    families = await list_all_families(session, family_mapper)

    return families


@router.get(
    "/list/{family_id}",
    description="List a family",
    response_model=FamilyResponse,
    status_code=status.HTTP_200_OK
)
async def get_family_route(
    family_id: int,
    session: Session = Depends(get_session),
    family_mapper=Depends(get_family_mapper),
) -> FamilyResponse:
    family = await get_family(session, family_id, family_mapper)

    return family