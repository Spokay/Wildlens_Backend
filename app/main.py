from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Depends
from sqlmodel import Session

from app.database import create_db_and_tables, get_session
from app.routes import users, ai_model



SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app_object: FastAPI):
    # Executed before startup (setup):
    create_db_and_tables()
    # ------------------------------
    yield  # <--- This is where the context manager pauses and the application starts
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
