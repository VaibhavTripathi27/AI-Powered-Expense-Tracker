from datetime import date
from typing import Optional

from fastapi import APIRouter, Query, status

from app.core.deps import CurrentUser, DbSession
from app.models.enums import Category
from app.schemas.common import PaginatedResponse
from app.schemas.expense import ExpenseCreate, ExpenseOut, ExpenseUpdate
from app.services.expense_service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", response_model=PaginatedResponse[ExpenseOut])
def list_expenses(
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[Category] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = Query(None, max_length=120),
) -> PaginatedResponse[ExpenseOut]:
    return ExpenseService(db).list(
        current_user.id, page, page_size, category, start_date, end_date, search
    )


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate, db: DbSession, current_user: CurrentUser
) -> ExpenseOut:
    return ExpenseService(db).create(current_user.id, payload)


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(
    expense_id: int, db: DbSession, current_user: CurrentUser
) -> ExpenseOut:
    return ExpenseService(db).get(current_user.id, expense_id)


@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ExpenseOut:
    return ExpenseService(db).update(current_user.id, expense_id, payload)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int, db: DbSession, current_user: CurrentUser
) -> None:
    ExpenseService(db).delete(current_user.id, expense_id)
