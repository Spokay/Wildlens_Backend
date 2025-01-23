from fastapi import UploadFile, APIRouter, HTTPException
from sqlmodel import Session
from starlette.responses import JSONResponse

from app.services.azure_blob_service import azure_blob_service
from app.services.prediction_service import prediction_service
from app.services.specie_service import get_specie_by_class_number, get_species_responses, get_specie_response

router = APIRouter(
    prefix="/species"
)

def assert_content_type_is_valid(content_type: str):
    if content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JPEG or PNG image.")

@router.post(
    "/predict",
    description="predicts the class of an image",
)
async def predict_image_class(image: UploadFile, session : Session) -> JSONResponse:

    assert_content_type_is_valid(image.content_type)

    # 1. check if the image is a footprint
    if prediction_service.check_image_for_footprint(image):

        # 2. if it is a footprint, predict the class of the image
        species_predictions = prediction_service.classify_image(image)

        # 3. save the image in the blob storage if it is a footprint
        azure_blob_service.upload_file(image)

        # 4. get the associated species data for each predicted class
        species = [get_specie_by_class_number(prediction.class_number, session) for prediction in species_predictions]

        # 5. prepare the response
        species_response = get_species_responses(species, species_predictions)

        return JSONResponse(
            {"species": species_response},
            200
        )
    else:
        return JSONResponse({
            "message": "L'image n'est pas une empreinte",
        },422)


@router.get(
    "/{class_number}",
    description="get the species data associated with a class number",
)
async def get_specie_by_class_number(class_number: int, session: Session) -> JSONResponse:
    specie = get_specie_by_class_number(class_number, session)

    specie_response = get_specie_response(specie)

    return JSONResponse(
        {"specie": specie_response},
        200
    )
