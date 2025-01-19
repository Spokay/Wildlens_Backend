from fastapi import UploadFile, APIRouter
from starlette.responses import JSONResponse

from app.models.response import SpecieResponse
from app.services.prediction_service import prediction_service
from app.services.azure_blob_service import azure_blob_service
from app.services.specie_service import get_specie_by_class

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
        prediction = prediction_service.classify_image(image)

        # 3. save the image in the blob storage if it is a footprint
        azure_blob_service.upload_file(image)

        # 4. get the associated species data from the prediction class
        specie = get_specie_by_class(prediction["class"])

        return JSONResponse(
            SpecieResponse(
                specie=specie,
                probability=prediction["probability"]
            ),
            200
        )
    else:
        return JSONResponse({
            "message": "L'image n'est pas une empreinte",
        },422)
