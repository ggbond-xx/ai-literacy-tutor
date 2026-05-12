from pydantic import BaseModel, Field


class CoordinationRequestItem(BaseModel):
    id: int
    teacher_id: int
    teacher_name: str
    type: str
    title: str
    description: str
    status: str
    admin_reply: str | None = None
    create_time: str
    update_time: str
    handled_by: int | None = None
    handled_by_name: str | None = None


class CoordinationRequestCreateRequest(BaseModel):
    type: str = Field(min_length=2, max_length=40)
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=5, max_length=1000)


class CoordinationRequestUpdateRequest(BaseModel):
    status: str = Field(min_length=2, max_length=20)
    admin_reply: str | None = Field(default=None, max_length=1000)
