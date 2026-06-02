from __future__ import annotations

from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.enums import Category
from app.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, db: Session):
        super().__init__(Budget, db)

    def get_for_user(self, user_id: int, budget_id: int) -> Budget | None:
        stmt = select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
        return self.db.scalar(stmt)

    def get_by_category(self, user_id: int, category: Category | str) -> Budget | None:
        value = category.value if isinstance(category, Category) else category
        stmt = select(Budget).where(
            Budget.user_id == user_id, Budget.category == value
        )
        return self.db.scalar(stmt)

    def list_for_user(self, user_id: int) -> List[Budget]:
        stmt = select(Budget).where(Budget.user_id == user_id).order_by(Budget.category)
        return list(self.db.scalars(stmt).all())