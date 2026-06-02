from typing import List

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.enums import AlertType
from app.models.expense import Expense
from app.repositories.alert_repo import AlertRepository
from app.repositories.budget_repo import BudgetRepository
from app.repositories.expense_repo import ExpenseRepository
from app.schemas.alert import AlertOut
from app.utils.dates import current_month_range, previous_month_range
from app.utils.exceptions import NotFoundError

UNUSUAL_MULTIPLIER = 3.0  # transaction > 3x the user's average is "unusual"
SPENDING_INCREASE_PCT = 25.0  # month-over-month increase threshold


class AlertService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AlertRepository(db)
        self.budget_repo = BudgetRepository(db)
        self.expense_repo = ExpenseRepository(db)

    def list(self, user_id: int, unread_only: bool = False) -> List[AlertOut]:
        return [
            AlertOut.model_validate(a)
            for a in self.repo.list_for_user(user_id, unread_only)
        ]

    def mark_read(self, user_id: int, alert_id: int) -> AlertOut:
        alert = self.repo.get_for_user(user_id, alert_id)
        if not alert:
            raise NotFoundError("Alert not found")
        alert.is_read = True
        alert = self.repo.update(alert)
        return AlertOut.model_validate(alert)

    def mark_all_read(self, user_id: int) -> None:
        self.repo.mark_all_read(user_id)

    def delete(self, user_id: int, alert_id: int) -> None:
        alert = self.repo.get_for_user(user_id, alert_id)
        if not alert:
            raise NotFoundError("Alert not found")
        self.repo.delete(alert)

    def _emit(self, user_id: int, type_: AlertType, message: str) -> None:
        if self.repo.exists_recent(user_id, type_.value, message):
            return
        self.repo.create(
            Alert(user_id=user_id, type=type_.value, message=message)
        )

    def evaluate_for_expense(self, user_id: int, expense: Expense) -> None:
        """Run all alert rules after a new expense is recorded."""
        self._check_budget(user_id, expense)
        self._check_unusual_transaction(user_id, expense)
        self._check_spending_increase(user_id)

    def _check_budget(self, user_id: int, expense: Expense) -> None:
        budget = self.budget_repo.get_by_category(user_id, expense.category)
        if not budget:
            return
        start, end = current_month_range()
        spent_map = self.expense_repo.sum_by_category_in_period(user_id, start, end)
        spent = spent_map.get(expense.category, 0.0)
        limit = float(budget.monthly_limit)
        if limit <= 0:
            return
        pct = (spent / limit) * 100
        if pct >= 100:
            self._emit(
                user_id,
                AlertType.BUDGET_EXCEEDED,
                f"You have exceeded your {expense.category} budget "
                f"(spent {spent:.2f} of {limit:.2f}).",
            )
        elif pct >= 90:
            self._emit(
                user_id,
                AlertType.BUDGET_THRESHOLD,
                f"You have used {pct:.0f}% of your {expense.category} budget "
                f"({spent:.2f} of {limit:.2f}).",
            )

    def _check_unusual_transaction(self, user_id: int, expense: Expense) -> None:
        expenses = self.expense_repo.list_all(user_id)
        if len(expenses) < 5:
            return
        amounts = [float(e.amount) for e in expenses if e.id != expense.id]
        if not amounts:
            return
        avg = sum(amounts) / len(amounts)
        if avg > 0 and float(expense.amount) >= avg * UNUSUAL_MULTIPLIER:
            self._emit(
                user_id,
                AlertType.UNUSUAL_TRANSACTION,
                f"Unusual transaction detected: {expense.category} expense of "
                f"{float(expense.amount):.2f} is well above your average of {avg:.2f}.",
            )

    def _check_spending_increase(self, user_id: int) -> None:
        cur_start, cur_end = current_month_range()
        prev_start, prev_end = previous_month_range()
        current = sum(
            self.expense_repo.sum_by_category_in_period(user_id, cur_start, cur_end).values()
        )
        previous = sum(
            self.expense_repo.sum_by_category_in_period(user_id, prev_start, prev_end).values()
        )
        if previous <= 0:
            return
        increase = ((current - previous) / previous) * 100
        if increase >= SPENDING_INCREASE_PCT:
            self._emit(
                user_id,
                AlertType.SPENDING_INCREASE,
                f"Your spending is up {increase:.0f}% compared to last month "
                f"({current:.2f} vs {previous:.2f}).",
            )
