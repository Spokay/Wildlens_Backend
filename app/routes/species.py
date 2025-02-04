import os
from typing import Annotated

from fastapi import UploadFile, APIRouter, HTTPException, Depends
from sqlmodel import Session
from starlette import status
from starlette.responses import JSONResponse

from app.database import get_session
from app.dto.species import SpecieResponse, SpeciePredictionResponse, SpecieBasicInfoResponse
from app.dto.users import AuthenticatedUser
from app.mappers.specie_mapper import get_specie_mapper
from app.services.authentication_service import get_current_user
from app.services.azure_blob_service import AzureBlobService, get_azure_blob_service
from app.services.specie_service import get_specie_by_class_number, save_identification, get_identified_species_by_user
from app.services.wildlens_api_service import WildlensAPIService, get_wildlens_api_service

router = APIRouter(
    prefix="/species",
    tags=["species"]
)


def assert_content_type_is_valid(content_type: str):
    if content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JPEG or PNG image.")

@router.post(
    "/predict",
    description="Predicts the class of an image and saves the identification in the database",
    response_model=list[SpeciePredictionResponse],
    status_code=status.HTTP_200_OK
)
async def predict_image_class(
        image: UploadFile,
        authenticated_user : Annotated[AuthenticatedUser, Depends(get_current_user)],
        session: Session = Depends(get_session),
        azure_blob_service: AzureBlobService = Depends(get_azure_blob_service),
        wildlens_prediction_api_service: WildlensAPIService = Depends(get_wildlens_api_service),
        specie_mapper = Depends(get_specie_mapper)
) -> list[SpeciePredictionResponse] | JSONResponse:
    assert_content_type_is_valid(image.content_type)

    # 1. check if the image is a footprint
    if await wildlens_prediction_api_service.check_image_for_footprint(image):

        # 2. if it is a footprint, predict the class of the image
        species_predictions = await wildlens_prediction_api_service.classify_image(image)

        # 3. save the image in the blob storage if it is a footprint
        blob_key = await azure_blob_service.upload_file(image)

        # 4. save the Identification in the database for the maximum probability class
        await save_identification(session, authenticated_user, species_predictions[0].class_number, blob_key)

        # 5. get the associated species data for each predicted class
        species = [await get_specie_by_class_number(prediction.class_number, session) for prediction in species_predictions]

        # 6. prepare the response
        species_response = await specie_mapper.species_to_prediction_responses(species, species_predictions)

        return species_response
    else:
        return JSONResponse({
            "message": "L'image n'est pas une empreinte",
        },422)


@router.get(
    "/{class_number}",
    description="Get the species data associated with a class number",
    response_model=SpecieResponse,
    status_code=status.HTTP_200_OK
)
async def get_specie_information(
        class_number: int,
        session: Session = Depends(get_session),
        specie_mapper = Depends(get_specie_mapper)
) -> JSONResponse:
    specie = await get_specie_by_class_number(class_number, session)

    specie_response = await specie_mapper.specie_to_response(specie)

    return JSONResponse(
        {"specie": specie_response.dict()},
        200
    )


@router.get(
    "/identified/{user_id}",
    description="Get the species identified by a user",
    response_model=list[SpecieBasicInfoResponse],
    status_code=status.HTTP_200_OK
)
async def get_identified_species(
        user_id: int,
        session: Session = Depends(get_session),
        specie_mapper = Depends(get_specie_mapper)
) -> list[SpecieBasicInfoResponse]:
    species_identified = await get_identified_species_by_user(user_id, session, specie_mapper)

    return species_identified
