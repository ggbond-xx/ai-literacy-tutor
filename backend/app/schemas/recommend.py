from pydantic import BaseModel


class RecommendedConcept(BaseModel):
    id: str
    name: str
    category: str | None = None
    description: str | None = None
    difficulty: int | None = None
    status: int
    readiness: float
    prerequisite_count: int
    blocked_count: int


class WeakPointItem(BaseModel):
    concept: RecommendedConcept
    impact_count: int


class LearningPathStep(BaseModel):
    step: int
    concept: RecommendedConcept
    reason: str


class RecommendOverviewResponse(BaseModel):
    progress_rate: int
    total_concepts: int
    mastered_count: int
    in_progress_count: int
    unlearned_count: int
    recommended_concepts: list[RecommendedConcept]
    weak_points: list[WeakPointItem]
    default_target: RecommendedConcept | None = None
    learning_path: list[LearningPathStep]
