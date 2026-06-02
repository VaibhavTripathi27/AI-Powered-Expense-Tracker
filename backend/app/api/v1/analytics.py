from fastapi import APIRouter

from app.core.deps import CurrentUser, DbSession
from app.schemas.analytics import DashboardMetrics, HealthScore
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardMetrics)
def dashboard(db: DbSession, current_user: CurrentUser) -> DashboardMetrics:
    return AnalyticsService(db).dashboard(current_user.id)


@router.get("/health-score", response_model=HealthScore)
def health_score(db: DbSession, current_user: CurrentUser) -> HealthScore:
    return AnalyticsService(db).health_score(current_user.id)
