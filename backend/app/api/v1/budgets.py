from typing import List

from fastapi import APIRouter, status

from app.core.deps import CurrentUser, DbSession
from app.schemas.budget import BudgetCreate, BudgetOut, BudgetUpdate, BudgetUtilization
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", response_model=List[BudgetOut])
def list_budgets(db: DbSession, current_user: CurrentUser) -> List[BudgetOut]:
    return BudgetService(db).list(current_user.id)


@router.get("/utilization", response_model=List[BudgetUtilization])
def budget_utilization(
    db: DbSession, current_user: CurrentUser
) -> List[BudgetUtilization]:
    return BudgetService(db).utilization(current_user.id)


@router.post("", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate, db: DbSession, current_user: CurrentUser
) -> BudgetOut:
    return BudgetService(db).create(current_user.id, payload)


@router.put("/{budget_id}", response_model=BudgetOut)
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> BudgetOut:
    return BudgetService(db).update(current_user.id, budget_id, payload)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, db: DbSession, current_user: CurrentUser) -> None:
    BudgetService(db).delete(current_user.id, budget_id)
