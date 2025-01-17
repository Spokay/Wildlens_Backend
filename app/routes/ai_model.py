from starlette.responses import JSONResponse
from starlette.routing import Route


async def predict_image_class(request):

    return JSONResponse({"message": "Predicting image class"})

routes = [
    Route("/predict", predict_image_class, methods=["POST"]),
]