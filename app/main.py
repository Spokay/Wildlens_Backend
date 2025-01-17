from fastapi import FastAPI
from starlette.routing import Router, Mount
from app.routes.users import routes as users_router
from app.routes.ai_model import routes as ai_model_router
app = FastAPI()

router = Router(
    routes=[
        Mount("/users", users_router),
        Mount("/ai_model", ai_model_router),
    ]
)

app.mount(
    "/api",
    router,
    name="api",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)