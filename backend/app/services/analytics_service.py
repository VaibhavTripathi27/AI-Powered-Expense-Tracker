from datetime import date

from sqlalchemy.orm import Session

from app.repositories.expense_repo import ExpenseRepository
from app.schemas.analytics import (
    CategoryAmount,
    DashboardMetrics,
    HealthScore,
    MonthAmount,
)
from app.services.budget_service import BudgetService
from app.services.health_score_service import HealthScoreService
from app.utils.dates import current_month_range, last_n_months, month_range


class AnalyticsService:
    def __init__(self, db: Session):
        self.expense_repo = ExpenseRepository(db)
        self.budget_service = BudgetService(db)
        self.health_service = HealthScoreService(db)

    def dashboard(self, user_id: int) -> DashboardMetrics:
        all_expenses = self.expense_repo.list_all(user_id)
        total = sum(float(e.amount) for e in all_expenses)

        cur_start, cur_end = current_month_range()
        monthly_map = self.expense_repo.sum_by_category_in_period(
            user_id, cur_start, cur_end
        )
        monthly_total = sum(monthly_map.values())

        category_breakdown = [
            CategoryAmount(category=cat, amount=round(amt, 2))
            for cat, amt in sorted(monthly_map.items(), key=lambda x: -x[1])
        ]

        trend: list[MonthAmount] = []
        for year, month in last_n_months(6):
            start, end = month_range(year, month)
            amt = sum(
                self.expense_repo.sum_by_category_in_period(user_id, start, end).values()
            )
            trend.append(MonthAmount(month=f"{year}-{month:02d}", amount=round(amt, 2)))

        utilization = self.budget_service.utilization(user_id)
        total_budget = sum(u.monthly_limit for u in utilization)
        savings_estimate = round(total_budget - monthly_total, 2) if total_budget else 0.0

        return DashboardMetrics(
            total_expenses=round(total, 2),
            monthly_expenses=round(monthly_total, 2),
            category_breakdown=category_breakdown,
            monthly_trend=trend,
            savings_estimate=savings_estimate,
            total_budget=round(total_budget, 2),
            budget_utilization=utilization,
        )

    def health_score(self, user_id: int) -> HealthScore:
        return self.health_service.compute(user_id)
