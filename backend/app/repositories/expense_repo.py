from __future__ import annotations

from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import Category
from app.models.expense import Expense
from app.repositories.base import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    def __init__(self, db: Session):
        super().__init__(Expense, db)

    def _base_query(
        self,
        user_id: int,
        category: Optional[Category] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
    ):
        stmt = select(Expense).where(Expense.user_id == user_id)
        if category:
            stmt = stmt.where(Expense.category == category.value)
        if start_date:
            stmt = stmt.where(Expense.transaction_date >= start_date)
        if end_date:
            stmt = stmt.where(Expense.transaction_date <= end_date)
        if search:
            pattern = f"%{search.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Expense.description).like(pattern),
                    func.lower(cast(Expense.category, String)).like(pattern),
                )
            )
        return stmt

    def get_for_user(self, user_id: int, expense_id: int) -> Expense | None:
        stmt = select(Expense).where(
            Expense.id == expense_id, Expense.user_id == user_id
        )
        return self.db.scalar(stmt)

    def list_paginated(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        category: Optional[Category] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Expense], int]:
        base = self._base_query(user_id, category, start_date, end_date, search)
        count_stmt = select(func.count()).select_from(base.subquery())
        total = self.db.scalar(count_stmt) or 0

        stmt = (
            base.order_by(Expense.transaction_date.desc(), Expense.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.scalars(stmt).all())
        return items, total

    def list_all(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Expense]:
        stmt = self._base_query(user_id, start_date=start_date, end_date=end_date)
        return list(self.db.scalars(stmt).all())

    def sum_by_category_in_period(
        self, user_id: int, start_date: date, end_date: date
    ) -> dict[str, float]:
        stmt = (
            select(Expense.category, func.coalesce(func.sum(Expense.amount), 0))
            .where(
                Expense.user_id == user_id,
                Expense.transaction_date >= start_date,
                Expense.transaction_date <= end_date,
            )
            .group_by(Expense.category)
        )
        return {row[0]: float(row[1]) for row in self.db.execute(stmt).all()}