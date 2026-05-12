from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeStatusUpdateRequest(BaseModel):
    status: int = Field(ge=0, le=2)


class KnowledgeStatusItemResponse(BaseModel):
    id: int
    concept_id: str
    status: int
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeStatusCollectionResponse(BaseModel):
    items: list[KnowledgeStatusItemResponse]
    status_map: dict[str, int]


class QuizAttemptCreateRequest(BaseModel):
    concept_name: str = Field(min_length=1, max_length=120)
    total_questions: int = Field(ge=1, le=50)
    correct_answers: int = Field(ge=0, le=50)
    score: int = Field(ge=0, le=100)


class NodeVisitCreateRequest(BaseModel):
    concept_name: str | None = Field(default=None, max_length=120)
    duration_seconds: int | None = Field(default=None, ge=0, le=7200)


class QuizAttemptItemResponse(BaseModel):
    id: int
    concept_id: str
    concept_name: str
    total_questions: int
    correct_answers: int
    wrong_answers: int
    accuracy: float
    score: int
    create_time: str


class LearningStatusProgressItem(BaseModel):
    label: str
    status: int
    count: int
    ratio: int


class ModuleProgressItem(BaseModel):
    module_name: str
    total_count: int
    mastered_count: int
    in_progress_count: int
    unlearned_count: int
    progress_rate: int


class WeakReviewItemResponse(BaseModel):
    concept_id: str
    concept_name: str
    module_name: str | None = None
    question_count: int = 0
    incorrect_count: int = 0
    error_rate: int = 0
    review_score: int = 0
    latest_score: int | None = None
    reason: str


class NodeLearningTimeItemResponse(BaseModel):
    concept_id: str
    concept_name: str
    total_minutes: int = 0
    visit_count: int = 0
    average_minutes: int = 0
    latest_time: str | None = None


class LearningAnalyticsResponse(BaseModel):
    progress_rate: int
    total_concepts: int
    mastered_count: int
    in_progress_count: int
    unlearned_count: int
    status_progress: list[LearningStatusProgressItem]
    module_progress: list[ModuleProgressItem]
    weak_review_items: list[WeakReviewItemResponse]
    recent_quiz_attempts: list[QuizAttemptItemResponse]
    node_learning_times: list[NodeLearningTimeItemResponse] = Field(default_factory=list)
