from fastapi import UploadFile, APIRouter
from starlette.responses import JSONResponse

from app.services.azure_blob_service import azure_blob_service
from app.services.prediction_service import prediction_service
from app.services.specie_service import get_specie_by_class_number, get_species_responses

router = APIRouter(
    prefix="/ai_model"
)


@router.post(
    "/predict",
    description="predict the class of an image",
)
def predict_image_class(image: UploadFile) -> JSONResponse:
    # 1. check if the image is a footprint
    if prediction_service.check_image_for_footprint(image):

        # 2. if it is a footprint, predict the class of the image
        species_predictions = prediction_service.classify_image(image)

        # 3. save the image in the blob storage if it is a footprint
        azure_blob_service.upload_file(image)

        # 4. get the associated species data for each predicted class
        species = [get_specie_by_class_number(prediction.class_number) for prediction in species_predictions]

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
