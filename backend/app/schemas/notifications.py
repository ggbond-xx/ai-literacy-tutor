from pydantic import BaseModel, Field


class NotificationItemResponse(BaseModel):
    id: int
    category: str
    title: str
    content: str
    link: str | None = None
    is_read: bool = False
    create_time: str


class NotificationCollectionResponse(BaseModel):
    unread_count: int = 0
    items: list[NotificationItemResponse] = Field(default_factory=list)
