from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Depends
from typing import Annotated
from sqlmodel import SQLModel, Session
from app.config import database_engine
from app.models.photos import Identification
from app.models.specie import Family, Habitat, Specie, SpecieHabitat
from app.models.user import Role, User
from app.routes import users, ai_model


def create_db_and_tables():
    SQLModel.metadata.create_all(database_engine)


def get_session():
    with Session(database_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executed before startup (setup):
    SQLModel.metadata.create_all(database_engine, tables=[
        Role.__table__,
        Family.__table__,
        Habitat.__table__,
        Specie.__table__,
        User.__table__,
        SpecieHabitat.__table__,
        Identification.__table__,
    ])
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)