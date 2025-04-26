from typing import Annotated

from fastapi import UploadFile, APIRouter, HTTPException, Depends, Body
from sqlmodel import Session
from starlette import status
from starlette.responses import JSONResponse

from app.database import get_session
from app.dto.species import (
    SpecieResponse,
    SpecieBasicInfoResponse,
    UploadInfo,
    SpecieClassificationResponse,
    CreateSpecieInfo,
)
from app.mappers.specie_mapper import get_specie_mapper
from app.services.azure_blob_service import (
    AzureBlobService,
    get_azure_blob_service,
    add_base_path_to_file_name,
)
from app.services.specie_service import (
    get_specie_by_class_number,
    save_identification,
    get_identified_species_by_user,
    upload_blob_from_temp_file,
    save_temporary_file,
    create_specie,
)
from app.services.wildlens_api_service import (
    WildlensAPIService,
    get_wildlens_api_service,
)

router = APIRouter(prefix="/species", tags=["species"])


async def assert_content_type_is_valid(content_type: str):
    if content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a JPEG or PNG image.",
        )


@router.post(
    "/predict",
    description="Predicts the class of an image and saves the identification in the database",
    response_model=SpecieClassificationResponse,
    status_code=status.HTTP_200_OK,
)
async def predict_image_class(
    image: UploadFile,
    session: Session = Depends(get_session),
    wildlens_prediction_api_service: WildlensAPIService = Depends(
        get_wildlens_api_service
    ),
    specie_mapper=Depends(get_specie_mapper),
) -> SpecieClassificationResponse | JSONResponse:
    await assert_content_type_is_valid(image.content_type)

    # 1. check if the image is a footprint
    if await wildlens_prediction_api_service.check_image_for_footprint(image):
        # 2. if it is a footprint, predict the class of the image
        species_predictions = await wildlens_prediction_api_service.classify_image(
            image
        )

        tmp_file_path, image_file_name = await save_temporary_file(image)

        # 5. get the associated species data for each predicted class
        species = [
            await get_specie_by_class_number(prediction.class_number, session)
            for prediction in species_predictions
        ]

        # 6. prepare the response
        species_response = await specie_mapper.species_to_prediction_responses(
            species, species_predictions
        )

        return SpecieClassificationResponse(
            predictions_response=species_response,
            tmp_file_path=tmp_file_path,
            image_file_name=image_file_name,
        )
    else:
        return JSONResponse(
            {
                "message": "L'image n'est pas une empreinte",
            },
            422,
        )


@router.post(
    "/upload_identification",
    description="Upload an identification to the blob storage",
    status_code=status.HTTP_200_OK,
)
async def upload_identification(
    upload_info: UploadInfo,
    azure_blob_service: Annotated[AzureBlobService, Depends(get_azure_blob_service)],
    session: Session = Depends(get_session),
) -> JSONResponse:
    await upload_blob_from_temp_file(upload_info, azure_blob_service)

    file_storage_key = await add_base_path_to_file_name(upload_info.image_file_name)

    await save_identification(
        session, upload_info.user_id, upload_info.specie_id, file_storage_key
    )

    return JSONResponse({"message": "Identification enregistrée avec succès"})


@router.get(
    "/{class_number}",
    description="Get the species data associated with a class number",
    response_model=SpecieResponse,
    status_code=status.HTTP_200_OK,
)
async def get_specie_information(
    class_number: int,
    session: Session = Depends(get_session),
    specie_mapper=Depends(get_specie_mapper),
) -> JSONResponse:
    specie = await get_specie_by_class_number(class_number, session)

    specie_response = await specie_mapper.specie_to_response(specie)

    return specie_response


@router.get(
    "/identified/{user_id}",
    description="Get the species identified by a user",
    response_model=list[SpecieBasicInfoResponse],
    status_code=status.HTTP_200_OK,
)
async def get_identified_species(
    user_id: int,
    session: Session = Depends(get_session),
    specie_mapper=Depends(get_specie_mapper),
) -> list[SpecieBasicInfoResponse]:
    species_identified = await get_identified_species_by_user(
        user_id, session, specie_mapper
    )

    return species_identified


# CRUD


@router.post("/create")
async def create_specier_route(
    specie_to_create: CreateSpecieInfo = Body(...),
    session: Session = Depends(get_session),
    specie_mapper=Depends(get_specie_mapper),
):
    specie = await create_specie(session, specie_mapper, specie_to_create)
    return JSONResponse(
        {
            "message": "Species created successfully",
            "specie": specie.model_dump(mode="json"),
        },
        status_code=status.HTTP_201_CREATED,
    )


@router.delete("/delete/{specie_id}")
async def delete_specie_route(
    specie_id: int,
    session: Session = Depends(get_session),
    specie_mapper=Depends(get_specie_mapper),
):
    pass


@router.put("/update/{specie_id}")
async def update_specie_route(
    specie_id: int,
    session: Session = Depends(get_session),
    specie_mapper=Depends(get_specie_mapper),
):
    pass
