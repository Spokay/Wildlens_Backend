from dotenv import load_dotenv

from app.database import get_session

load_dotenv()

from app.config import get_settings, logger

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
from app.routes import users, species, families, habitats

SessionDep = Annotated[Session, Depends(get_session)]

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info(f"Starting application in {settings.environment} mode")

    # Validating required configurations
    if settings.is_production:
        if not settings.wildlens_prediction_api_key:
            raise ValueError("WILDLENS_PREDICTION_API_KEY missing in production")
        if not settings.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY missing in production")

    if settings.is_development:
        pass

    elif settings.is_production:
        pass

    try:
        from app.database import startup_database, get_database_info
        await startup_database()

        db_info = get_database_info()
        del db_info['database_url']
        logger.info(f"Database connection established: {db_info}")

    except Exception as e:
        logger.error(f"Database startup failed: {e}")
        raise

    # Application is ready to serve requests
    yield

    # Shutdown logic
    logger.info("Shutting down application")
    try:
        from app.database import shutdown_database
        await shutdown_database()
    except Exception as e:
        logger.error(f"Database shutdown error: {e}")


def create_app():
    wildlens_app = FastAPI(root_path=settings.api_prefix, lifespan=lifespan)

    # Exposing Prometheus metrics endpoints
    Instrumentator().instrument(wildlens_app).expose(wildlens_app)

    # Middlewares
    wildlens_app.add_middleware(AuthMiddleware)
    wildlens_app.add_middleware(ExceptionHandlerLoggingMiddleware)

    # Routers
    wildlens_app.include_router(users.router)
    wildlens_app.include_router(species.router)
    wildlens_app.include_router(families.router)
    wildlens_app.include_router(habitats.router)

    return wildlens_app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.app_port)
