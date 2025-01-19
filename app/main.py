from fastapi import FastAPI

from .routes import users, ai_model

app = FastAPI(
    root_path="/api"
)

app.include_router(users.router)
app.include_router(ai_model.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)