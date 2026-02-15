from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import recommend
from app.core.config import settings

app = FastAPI(
    title="FilmMatch AI",
    description="Movie recommendation engine — solo or with friends",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
