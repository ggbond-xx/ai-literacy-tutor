from pydantic import BaseModel, Field

from app.schemas.collaboration import QuestionItemResponse
from app.schemas.coordination import CoordinationRequestItem
from app.schemas.graph_management import GraphChangeRequestItem


class StudentProgressProfile(BaseModel):
    real_name: str | None = None
    school: str | None = None
    major: str | None = None
    grade: str | None = None
    class_name: str | None = None
    gender: str | None = None
    age: int | None = None


class StudentProgressItem(BaseModel):
    user_id: int
    username: str
    display_name: str
    class_id: int | None = None
    profile: StudentProgressProfile | None = None
    progress_rate: int
    mastered_count: int
    in_progress_count: int
    unlearned_count: int
    question_count: int = 0
    pending_question_count: int = 0
    featured_question_count: int = 0
    current_target: str | None = None
    weak_point: str | None = None


class ConceptQuestionStat(BaseModel):
    concept_name: str
    question_count: int
    pending_count: int


class StatusDistributionItem(BaseModel):
    status: int
    label: str
    count: int
    percentage: int


class ConceptStatusStat(BaseModel):
    concept_id: str
    concept_name: str
    category: str | None = None
    unlearned_count: int = 0
    in_progress_count: int = 0
    mastered_count: int = 0
    dominant_status: int = 0
    dominant_count: int = 0


class ClassLearningOverviewItem(BaseModel):
    class_id: int | None = None
    class_name: str
    student_count: int
    average_progress_rate: int
    mastered_concepts_total: int
    pending_question_count: int = 0
    featured_question_count: int = 0
    status_distribution: list[StatusDistributionItem] = Field(default_factory=list)
    students: list[StudentProgressItem] = Field(default_factory=list)
    top_unlearned_concepts: list[ConceptStatusStat] = Field(default_factory=list)
    top_in_progress_concepts: list[ConceptStatusStat] = Field(default_factory=list)
    top_mastered_concepts: list[ConceptStatusStat] = Field(default_factory=list)


class ClassOverviewMetrics(BaseModel):
    average_mastered_count: float = 0
    top_asked_concepts: list[ConceptQuestionStat] = Field(default_factory=list)


class LearningFactorGroupItem(BaseModel):
    group_key: str
    group_label: str
    student_count: int
    mastered_count: int
    in_progress_count: int
    unlearned_count: int
    mastered_percentage: int
    in_progress_percentage: int
    unlearned_percentage: int
    average_learning_minutes: int = 0
    weak_concepts: list[ConceptStatusStat] = Field(default_factory=list)
    mastered_concepts: list[ConceptStatusStat] = Field(default_factory=list)
    in_progress_concepts: list[ConceptStatusStat] = Field(default_factory=list)
    unlearned_concepts: list[ConceptStatusStat] = Field(default_factory=list)


class LearningFactorAnalysisItem(BaseModel):
    factor_key: str
    factor_label: str
    description: str
    groups: list[LearningFactorGroupItem] = Field(default_factory=list)


class NodeLearningAnalysisItem(BaseModel):
    concept_id: str
    concept_name: str
    category: str | None = None
    question_count: int = 0
    pending_count: int = 0
    click_count: int = 0
    average_learning_minutes: int = 0
    mastered_count: int = 0
    in_progress_count: int = 0
    unlearned_count: int = 0
    mastered_percentage: int = 0
    in_progress_percentage: int = 0
    unlearned_percentage: int = 0
    risk_score: int = 0
    risk_reason: str = ""


class QuickReplyTemplateItem(BaseModel):
    id: int
    title: str
    content: str
    create_time: str


class QuickReplyTemplateCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=50)
    content: str = Field(min_length=4, max_length=300)


class TeacherOverviewResponse(BaseModel):
    total_students: int
    average_progress_rate: int
    mastered_concepts_total: int
    pending_question_count: int
    answered_question_count: int
    featured_question_count: int
    pending_coordination_count: int = 0
    student_progress: list[StudentProgressItem]
    recent_questions: list[QuestionItemResponse]
    concept_question_stats: list[ConceptQuestionStat]
    coordination_requests: list[CoordinationRequestItem] = Field(default_factory=list)
    class_overview: ClassOverviewMetrics = Field(default_factory=ClassOverviewMetrics)
    class_overviews: list[ClassLearningOverviewItem] = Field(default_factory=list)
    learning_factor_analysis: list[LearningFactorAnalysisItem] = Field(default_factory=list)
    node_learning_analysis: list[NodeLearningAnalysisItem] = Field(default_factory=list)
    quick_reply_templates: list[QuickReplyTemplateItem] = Field(default_factory=list)
    graph_change_requests: list[GraphChangeRequestItem] = Field(default_factory=list)


class StudentLearningStatusSnapshot(BaseModel):
    concept_id: str
    concept_name: str
    status: int
    update_time: str


class StudentSnapshotResponse(BaseModel):
    student: StudentProgressItem
    recent_statuses: list[StudentLearningStatusSnapshot]
    mastered_statuses: list[StudentLearningStatusSnapshot] = Field(default_factory=list)
    in_progress_statuses: list[StudentLearningStatusSnapshot] = Field(default_factory=list)
    unlearned_concepts: list[StudentLearningStatusSnapshot] = Field(default_factory=list)
    weak_statuses: list[StudentLearningStatusSnapshot] = Field(default_factory=list)
    recent_questions: list[QuestionItemResponse]
    pending_questions: list[QuestionItemResponse] = Field(default_factory=list)
    featured_answer_count: int
    total_question_count: int = 0
    pending_question_count: int = 0
    answered_question_count: int = 0


class ConceptClassAnalyticsItem(BaseModel):
    class_id: int | None = None
    class_name: str
    student_count: int
    unlearned_count: int
    unlearned_percentage: int
    in_progress_count: int
    in_progress_percentage: int
    mastered_count: int
    mastered_percentage: int
    students_unlearned: list[StudentProgressItem] = Field(default_factory=list)
    students_in_progress: list[StudentProgressItem] = Field(default_factory=list)
    students_mastered: list[StudentProgressItem] = Field(default_factory=list)


class TeacherConceptAnalyticsResponse(BaseModel):
    concept_id: str
    concept_name: str
    category: str | None = None
    click_count: int = 0
    average_learning_minutes: int = 0
    question_count: int = 0
    pending_question_count: int = 0
    featured_question_count: int = 0
    class_stats: list[ConceptClassAnalyticsItem] = Field(default_factory=list)
    recent_questions: list[QuestionItemResponse] = Field(default_factory=list)
