from fastapi import APIRouter, HTTPException

from app.schemas.recommendation import RecommendationRequest
from app.services.ai_service import get_recommendation

router = APIRouter()


@router.post("/recommend")
async def recommend(request: RecommendationRequest):
    try:
        result = await get_recommendation(request)
        return {"recommendation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
