import os

from dotenv import load_dotenv

load_dotenv()

from app.config import API_PREFIX

from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Depends
from sqlmodel import Session

from app.services.authentication_service import (
    AuthMiddleware,
    ExceptionHandlerLoggingMiddleware,
)
from app.database import create_db_and_tables, get_session, database_engine
from app.routes import users, species, families

SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app_object: FastAPI):
    # Executed before startup (setup):
    create_db_and_tables(database_engine)
    # ------------------------------
    yield  # <--- This is where the context manager pauses and the application starts
    # ------------------------------
    # Executed after shutdown (cleanup):
    #
    #


app = FastAPI(root_path=API_PREFIX, lifespan=lifespan)

Instrumentator().instrument(app).expose(app)

app.add_middleware(AuthMiddleware)
app.add_middleware(ExceptionHandlerLoggingMiddleware)

app.include_router(users.router)
app.include_router(species.router)
app.include_router(families.router)

if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
