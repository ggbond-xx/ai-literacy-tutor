from pydantic import BaseModel, Field

from app.schemas.collaboration import QuestionItemResponse
from app.schemas.coordination import CoordinationRequestItem
from app.schemas.graph_management import GraphChangeRequestItem


class RecommendationSettingsResponse(BaseModel):
    recommendation_limit: int
    weak_point_limit: int
    path_limit: int
    mastery_weight: float
    in_progress_weight: float


class RecommendationSettingsUpdateRequest(BaseModel):
    recommendation_limit: int = Field(ge=1, le=12)
    weak_point_limit: int = Field(ge=1, le=10)
    path_limit: int = Field(ge=1, le=12)
    mastery_weight: float = Field(ge=0.5, le=2.0)
    in_progress_weight: float = Field(ge=0.1, le=1.0)


class ManagedUserProfile(BaseModel):
    real_name: str | None = None
    school: str | None = None
    major: str | None = None
    grade: str | None = None
    class_name: str | None = None
    gender: str | None = None
    age: str | None = None


class ManagedUserItem(BaseModel):
    id: int
    username: str
    role: str
    class_id: int | None = None
    profile: ManagedUserProfile | None = None
    progress_rate: int = 0
    mastered_count: int = 0
    in_progress_count: int = 0
    pending_question_count: int = 0


class ManagedUserUpdateRequest(BaseModel):
    role: str
    class_id: int | None = None
    password: str | None = Field(default=None, min_length=4, max_length=50)
    real_name: str | None = Field(default=None, max_length=50)
    school: str | None = Field(default=None, max_length=120)
    major: str | None = Field(default=None, max_length=120)
    grade: str | None = Field(default=None, max_length=50)
    class_name: str | None = Field(default=None, max_length=80)
    gender: str | None = Field(default=None, max_length=20)
    age: str | None = Field(default=None, max_length=10)


class ManagedUserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=50)
    role: str = Field(default="student")
    class_id: int | None = None
    real_name: str | None = Field(default=None, max_length=50)
    school: str | None = Field(default=None, max_length=120)
    major: str | None = Field(default=None, max_length=120)
    grade: str | None = Field(default=None, max_length=50)
    class_name: str | None = Field(default=None, max_length=80)
    gender: str | None = Field(default=None, max_length=20)
    age: str | None = Field(default=None, max_length=10)


class GraphStatsResponse(BaseModel):
    node_count: int
    relation_count: int
    category_breakdown: dict[str, int]


class QuestionConceptStat(BaseModel):
    concept_name: str
    question_count: int


class QuestionGovernanceStats(BaseModel):
    featured_question_count: int
    favorite_answer_count: int
    answered_question_count: int
    excellent_comment_count: int = 0
    comment_like_count: int = 0
    top_concepts: list[QuestionConceptStat]


class OperationLogItem(BaseModel):
    id: int
    actor_name: str
    actor_role: str
    action: str
    target_type: str
    target_id: str | None = None
    description: str
    create_time: str


class AdminOverviewResponse(BaseModel):
    total_users: int
    role_counts: dict[str, int]
    graph_stats: GraphStatsResponse
    pending_question_count: int
    pending_coordination_count: int = 0
    pending_graph_change_count: int = 0
    question_governance: QuestionGovernanceStats
    recommendation_settings: RecommendationSettingsResponse
    users: list[ManagedUserItem]
    recent_questions: list[QuestionItemResponse] = Field(default_factory=list)
    coordination_requests: list[CoordinationRequestItem] = Field(default_factory=list)
    graph_change_requests: list[GraphChangeRequestItem] = Field(default_factory=list)
    operation_logs: list[OperationLogItem] = Field(default_factory=list)
