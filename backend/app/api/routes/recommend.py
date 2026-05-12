from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.mysql import get_db
from app.models.user import User
from app.schemas.recommend import RecommendOverviewResponse
from app.services.recommend_service import RecommendationService, get_recommendation_service

router = APIRouter()


@router.get("/overview", response_model=RecommendOverviewResponse)
def get_recommendation_overview(
    target_concept_id: str | None = Query(default=None),
    current_user: User | dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendOverviewResponse:
    return recommendation_service.build_overview(
        user_id=current_user["id"] if isinstance(current_user, dict) else current_user.id,
        db=db,
        target_concept_id=target_concept_id,
    )
