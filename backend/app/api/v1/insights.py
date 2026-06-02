from fastapi import APIRouter

from app.core.deps import CurrentUser, DbSession
from app.schemas.insight import InsightResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/insights", tags=["AI Insights"])


@router.get("", response_model=InsightResponse)
def get_insights(db: DbSession, current_user: CurrentUser) -> InsightResponse:
    """Generate AI-powered financial insights from an aggregated, privacy-safe
    summary of the user's data (raw records are never sent to the model)."""
    return AIService(db).generate_insights(current_user.id)
