from typing import List

from pydantic import BaseModel

from app.schemas.budget import BudgetUtilization


class CategoryAmount(BaseModel):
    category: str
    amount: float


class MonthAmount(BaseModel):
    month: str  # YYYY-MM
    amount: float


class DashboardMetrics(BaseModel):
    total_expenses: float
    monthly_expenses: float
    category_breakdown: List[CategoryAmount]
    monthly_trend: List[MonthAmount]
    savings_estimate: float
    total_budget: float
    budget_utilization: List[BudgetUtilization]


class HealthScore(BaseModel):
    score: int
    rating: str
    savings_ratio: float
    budget_adherence: float
    spending_consistency: float
    breakdown: dict
