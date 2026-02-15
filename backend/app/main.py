from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, groups, movies, recommend, users
from app.core.config import settings
from app.core.exceptions import FilmMatchError
from app.core.logging import get_logger, setup_logging
from app.core.redis import close_redis
from app.services.tmdb_service import tmdb_service

logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("starting", environment=settings.environment)
    yield
    await tmdb_service.close()
    await close_redis()
    logger.info("shutdown_complete")


app = FastAPI(
    title="FilmMatch AI",
    description="AI-powered movie recommendation engine — solo or with friends",
    version="0.3.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# Global error handler
@app.exception_handler(FilmMatchError)
async def filmmatch_error_handler(request: Request, exc: FilmMatchError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.error("unhandled_error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


# Routes
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(recommend.router, prefix="/api/v1")
app.include_router(movies.router, prefix="/api/v1")
app.include_router(groups.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {
        "status": "ok",
        "version": "0.2.0",
        "environment": settings.environment,
    }
