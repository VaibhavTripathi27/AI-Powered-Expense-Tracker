from typing import List

from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.repositories.budget_repo import BudgetRepository
from app.schemas.budget import BudgetCreate, BudgetOut, BudgetUpdate, BudgetUtilization
from app.utils.exceptions import ConflictError, NotFoundError
from app.utils.dates import current_month_range


class BudgetService:
    def __init__(self, db: Session):
        self.repo = BudgetRepository(db)

    def create(self, user_id: int, payload: BudgetCreate) -> BudgetOut:
        if self.repo.get_by_category(user_id, payload.category):
            raise ConflictError(f"A budget for {payload.category.value} already exists")
        budget = Budget(
            category=payload.category.value,
            monthly_limit=payload.monthly_limit,
            user_id=user_id,
        )
        budget = self.repo.create(budget)
        return BudgetOut.model_validate(budget)

    def update(self, user_id: int, budget_id: int, payload: BudgetUpdate) -> BudgetOut:
        budget = self.repo.get_for_user(user_id, budget_id)
        if not budget:
            raise NotFoundError("Budget not found")
        budget.monthly_limit = payload.monthly_limit
        budget = self.repo.update(budget)
        return BudgetOut.model_validate(budget)

    def delete(self, user_id: int, budget_id: int) -> None:
        budget = self.repo.get_for_user(user_id, budget_id)
        if not budget:
            raise NotFoundError("Budget not found")
        self.repo.delete(budget)

    def list(self, user_id: int) -> List[BudgetOut]:
        return [BudgetOut.model_validate(b) for b in self.repo.list_for_user(user_id)]

    def utilization(self, user_id: int) -> List[BudgetUtilization]:
        from app.repositories.expense_repo import ExpenseRepository

        start, end = current_month_range()
        spent_map = ExpenseRepository(self.repo.db).sum_by_category_in_period(
            user_id, start, end
        )
        result: List[BudgetUtilization] = []
        for budget in self.repo.list_for_user(user_id):
            limit = float(budget.monthly_limit)
            spent = spent_map.get(budget.category, 0.0)
            pct = round((spent / limit) * 100, 1) if limit else 0.0
            result.append(
                BudgetUtilization(
                    category=budget.category,
                    monthly_limit=limit,
                    spent=round(spent, 2),
                    remaining=round(limit - spent, 2),
                    utilization_pct=pct,
                )
            )
        return result
