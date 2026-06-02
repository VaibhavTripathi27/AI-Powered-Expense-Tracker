from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Category


class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0, le=10_000_000)
    category: Category
    description: str = Field("", max_length=255)
    transaction_date: date


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: float | None = Field(None, gt=0, le=10_000_000)
    category: Category | None = None
    description: str | None = Field(None, max_length=255)
    transaction_date: date | None = None


class ExpenseOut(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime