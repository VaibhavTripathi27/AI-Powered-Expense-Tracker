from statistics import pstdev

from sqlalchemy.orm import Session

from app.repositories.budget_repo import BudgetRepository
from app.repositories.expense_repo import ExpenseRepository
from app.schemas.analytics import HealthScore
from app.services.budget_service import BudgetService
from app.utils.dates import last_n_months, month_range


def _rating(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 65:
        return "Good"
    if score >= 50:
        return "Fair"
    if score >= 35:
        return "Needs Attention"
    return "Critical"


class HealthScoreService:
    """Financial health score (0-100) from savings ratio, budget adherence and
    spending consistency. Each pillar is scored 0-1 then weighted."""

    WEIGHTS = {"savings": 0.4, "adherence": 0.35, "consistency": 0.25}

    def __init__(self, db: Session):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.budget_repo = BudgetRepository(db)
        self.budget_service = BudgetService(db)

    def compute(self, user_id: int) -> HealthScore:
        savings_ratio = self._savings_ratio(user_id)
        adherence = self._budget_adherence(user_id)
        consistency = self._spending_consistency(user_id)

        score = (
            savings_ratio * self.WEIGHTS["savings"]
            + adherence * self.WEIGHTS["adherence"]
            + consistency * self.WEIGHTS["consistency"]
        ) * 100
        score_int = max(0, min(100, round(score)))

        return HealthScore(
            score=score_int,
            rating=_rating(score_int),
            savings_ratio=round(savings_ratio, 3),
            budget_adherence=round(adherence, 3),
            spending_consistency=round(consistency, 3),
            breakdown={
                "savings_points": round(savings_ratio * self.WEIGHTS["savings"] * 100, 1),
                "adherence_points": round(adherence * self.WEIGHTS["adherence"] * 100, 1),
                "consistency_points": round(
                    consistency * self.WEIGHTS["consistency"] * 100, 1
                ),
            },
        )

    def _savings_ratio(self, user_id: int) -> float:
        utilization = self.budget_service.utilization(user_id)
        total_budget = sum(u.monthly_limit for u in utilization)
        total_spent = sum(u.spent for u in utilization)
        if total_budget <= 0:
            return 0.5  # neutral when no budgets are configured
        ratio = (total_budget - total_spent) / total_budget
        return max(0.0, min(1.0, ratio))

    def _budget_adherence(self, user_id: int) -> float:
        utilization = self.budget_service.utilization(user_id)
        if not utilization:
            return 0.5
        scores = []
        for u in utilization:
            if u.utilization_pct <= 100:
                scores.append(1.0)
            else:
                # Penalise overspend linearly, floor at 0.
                scores.append(max(0.0, 1.0 - (u.utilization_pct - 100) / 100))
        return sum(scores) / len(scores)

    def _spending_consistency(self, user_id: int) -> float:
        totals = []
        for year, month in last_n_months(6):
            start, end = month_range(year, month)
            totals.append(
                sum(
                    self.expense_repo.sum_by_category_in_period(
                        user_id, start, end
                    ).values()
                )
            )
        totals = [t for t in totals if t > 0]
        if len(totals) < 2:
            return 0.5
        mean = sum(totals) / len(totals)
        if mean == 0:
            return 0.5
        cv = pstdev(totals) / mean  # coefficient of variation
        return max(0.0, min(1.0, 1.0 - cv))
