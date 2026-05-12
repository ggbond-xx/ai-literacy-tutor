from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.graph import GraphQuizQuestion, GraphResourceLink


class GraphNodeDraft(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=600)
    category: str | None = Field(default=None, max_length=60)
    difficulty: int | None = Field(default=None, ge=1, le=5)
    estimated_minutes: int | None = Field(default=None, ge=5, le=240)
    key_points: list[str] = Field(default_factory=list, max_length=8)
    text_material: str | None = Field(default=None, max_length=4000)
    image_url: str | None = Field(default=None, max_length=300)
    video_title: str | None = Field(default=None, max_length=120)
    video_url: str | None = Field(default=None, max_length=300)
    resource_links: list[GraphResourceLink] = Field(default_factory=list, max_length=8)
    study_tips: list[str] = Field(default_factory=list, max_length=8)
    common_mistakes: list[str] = Field(default_factory=list, max_length=8)
    practice_task: str | None = Field(default=None, max_length=1200)
    quiz: list[GraphQuizQuestion] = Field(default_factory=list, max_length=12)


class GraphChangeRequestCreateRequest(BaseModel):
    action: Literal["create_node", "update_node"] = "update_node"
    summary: str = Field(min_length=4, max_length=160)
    target_concept_name: str | None = Field(default=None, max_length=80)
    node: GraphNodeDraft
    prerequisite_names: list[str] = Field(default_factory=list, max_length=12)
    next_names: list[str] = Field(default_factory=list, max_length=12)
    related_names: list[str] = Field(default_factory=list, max_length=12)


class GraphChangeRequestReviewRequest(BaseModel):
    status: Literal["approved", "rejected"]
    review_note: str | None = Field(default=None, max_length=500)


class GraphChangeRequestItem(BaseModel):
    id: int
    teacher_id: int
    teacher_name: str
    action: str
    summary: str
    target_concept_name: str | None = None
    node: GraphNodeDraft
    prerequisite_names: list[str] = Field(default_factory=list)
    next_names: list[str] = Field(default_factory=list)
    related_names: list[str] = Field(default_factory=list)
    status: str
    create_time: str
    review_time: str | None = None
    reviewed_by: int | None = None
    reviewed_by_name: str | None = None
    review_note: str | None = None
