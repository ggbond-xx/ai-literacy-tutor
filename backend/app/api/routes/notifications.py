from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.notifications import NotificationCollectionResponse, NotificationItemResponse
from app.services.json_store import (
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
)

router = APIRouter()


def _user_id(user: User | dict) -> int:
    return user["id"] if isinstance(user, dict) else user.id


@router.get("", response_model=NotificationCollectionResponse)
def get_notifications(
    current_user: User | dict = Depends(get_current_user),
) -> NotificationCollectionResponse:
    user_id = _user_id(current_user)
    items = [NotificationItemResponse(**item) for item in list_notifications(user_id)]
    unread_count = sum(1 for item in items if not item.is_read)
    return NotificationCollectionResponse(unread_count=unread_count, items=items)


@router.put("/{notification_id}/read", response_model=NotificationItemResponse)
def read_notification(
    notification_id: int,
    current_user: User | dict = Depends(get_current_user),
) -> NotificationItemResponse:
    user_id = _user_id(current_user)
    try:
        item = mark_notification_read(notification_id, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return NotificationItemResponse(**item)


@router.put("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def read_all_notifications(
    current_user: User | dict = Depends(get_current_user),
) -> None:
    user_id = _user_id(current_user)
    mark_all_notifications_read(user_id)
