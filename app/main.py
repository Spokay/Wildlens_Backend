from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy.sql.annotation import Annotated
from sqlmodel import SQLModel, Session

from app.classifier_models import load_models
from app.config import database_engine
from .routes import users, ai_model


def create_db_and_tables():
    SQLModel.metadata.create_all(database_engine)


def get_session():
    with Session(database_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executed before startup (setup):
    load_models()
    create_db_and_tables()
    # ------------------------------
    yield # <--- This is where the context manager pauses and the application starts
    # ------------------------------
    # Executed after shutdown (cleanup):
    #
    #

app = FastAPI(
    root_path="/api",
    lifespan=lifespan
)

app.include_router(users.router)
app.include_router(ai_model.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)