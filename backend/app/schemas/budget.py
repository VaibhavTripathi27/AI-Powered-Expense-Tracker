from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Category


class BudgetBase(BaseModel):
    category: Category
    monthly_limit: float = Field(..., gt=0, le=10_000_000)


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    monthly_limit: float = Field(..., gt=0, le=10_000_000)


class BudgetOut(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int


class BudgetUtilization(BaseModel):
    category: Category
    monthly_limit: float
    spent: float
    remaining: float
    utilization_pct: float
