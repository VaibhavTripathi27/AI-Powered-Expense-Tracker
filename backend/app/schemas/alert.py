from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import AlertType


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: AlertType
    message: str
    is_read: bool
    user_id: int
    created_at: datetime
