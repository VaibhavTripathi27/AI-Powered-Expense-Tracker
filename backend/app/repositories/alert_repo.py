from __future__ import annotations

from typing import List

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.repositories.base import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    def __init__(self, db: Session):
        super().__init__(Alert, db)

    def get_for_user(self, user_id: int, alert_id: int) -> Alert | None:
        stmt = select(Alert).where(Alert.id == alert_id, Alert.user_id == user_id)
        return self.db.scalar(stmt)

    def list_for_user(self, user_id: int, unread_only: bool = False) -> List[Alert]:
        stmt = select(Alert).where(Alert.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Alert.is_read.is_(False))
        stmt = stmt.order_by(Alert.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def exists_recent(self, user_id: int, type_: str, message: str) -> bool:
        """Avoid duplicate alerts with identical type+message."""
        stmt = select(Alert.id).where(
            Alert.user_id == user_id,
            Alert.type == type_,
            Alert.message == message,
            Alert.is_read.is_(False),
        )
        return self.db.scalar(stmt) is not None

    def mark_all_read(self, user_id: int) -> None:
        self.db.execute(
            update(Alert).where(Alert.user_id == user_id).values(is_read=True)
        )
        self.db.commit()