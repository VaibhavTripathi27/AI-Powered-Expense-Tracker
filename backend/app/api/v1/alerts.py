from typing import List

from fastapi import APIRouter, Query, status

from app.core.deps import CurrentUser, DbSession
from app.schemas.alert import AlertOut
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertOut])
def list_alerts(
    db: DbSession,
    current_user: CurrentUser,
    unread_only: bool = Query(False),
) -> List[AlertOut]:
    return AlertService(db).list(current_user.id, unread_only)


@router.patch("/{alert_id}/read", response_model=AlertOut)
def mark_read(alert_id: int, db: DbSession, current_user: CurrentUser) -> AlertOut:
    return AlertService(db).mark_read(current_user.id, alert_id)


@router.patch("/read-all", status_code=status.HTTP_200_OK)
def mark_all_read(db: DbSession, current_user: CurrentUser) -> dict[str, str]:
    AlertService(db).mark_all_read(current_user.id)
    return {"detail": "All alerts marked as read"}


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: int, db: DbSession, current_user: CurrentUser) -> None:
    AlertService(db).delete(current_user.id, alert_id)
