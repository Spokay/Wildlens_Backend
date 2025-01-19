from fastapi import UploadFile, APIRouter
from starlette.responses import JSONResponse

from app.services.wildlens_model_service import wildlens_model_service

router = APIRouter(
    prefix="/ai_model"
)

@router.post(
    "/predict",
    description="predict the class of an image",
 )
def predict_image_class(image: UploadFile):
    # 1. check if the image is a footprint
    wildlens_model_service.predict_class(image)
    # 2. if it is a footprint, predict the class of the image

    # 3. save the image in the blob storage if it is a footprint

    # 4. return the data associated with the class
    return JSONResponse({"message": "Predicting image class"})
