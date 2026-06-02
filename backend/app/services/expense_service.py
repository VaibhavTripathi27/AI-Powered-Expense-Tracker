from datetime import date
from math import ceil
from typing import Optional

from sqlalchemy.orm import Session

from app.models.enums import Category
from app.models.expense import Expense
from app.repositories.expense_repo import ExpenseRepository
from app.schemas.common import PaginatedResponse
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseUpdate
from app.services.alert_service import AlertService
from app.utils.exceptions import NotFoundError


class ExpenseService:
    def __init__(self, db: Session):
        self.repo = ExpenseRepository(db)
        self.alert_service = AlertService(db)

    def create(self, user_id: int, payload: ExpenseCreate) -> ExpenseOut:
        expense = Expense(
            amount=payload.amount,
            category=payload.category.value,
            description=payload.description.strip(),
            transaction_date=payload.transaction_date,
            user_id=user_id,
        )
        expense = self.repo.create(expense)
        # Evaluate alerts triggered by the new expense.
        self.alert_service.evaluate_for_expense(user_id, expense)
        return ExpenseOut.model_validate(expense)

    def update(self, user_id: int, expense_id: int, payload: ExpenseUpdate) -> ExpenseOut:
        expense = self.repo.get_for_user(user_id, expense_id)
        if not expense:
            raise NotFoundError("Expense not found")

        data = payload.model_dump(exclude_unset=True)
        if "category" in data and data["category"] is not None:
            data["category"] = data["category"].value
        if "description" in data and data["description"] is not None:
            data["description"] = data["description"].strip()
        for key, value in data.items():
            setattr(expense, key, value)

        expense = self.repo.update(expense)
        return ExpenseOut.model_validate(expense)

    def delete(self, user_id: int, expense_id: int) -> None:
        expense = self.repo.get_for_user(user_id, expense_id)
        if not expense:
            raise NotFoundError("Expense not found")
        self.repo.delete(expense)

    def get(self, user_id: int, expense_id: int) -> ExpenseOut:
        expense = self.repo.get_for_user(user_id, expense_id)
        if not expense:
            raise NotFoundError("Expense not found")
        return ExpenseOut.model_validate(expense)

    def list(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        category: Optional[Category] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[ExpenseOut]:
        items, total = self.repo.list_paginated(
            user_id, page, page_size, category, start_date, end_date, search
        )
        return PaginatedResponse[ExpenseOut](
            items=[ExpenseOut.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
            pages=ceil(total / page_size) if page_size else 1,
        )
