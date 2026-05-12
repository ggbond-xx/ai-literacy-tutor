from pydantic import BaseModel, Field


class GraphResourceLink(BaseModel):
    label: str
    url: str


class GraphQuizQuestion(BaseModel):
    question: str
    options: list[str]
    answer_index: int
    explanation: str


class GraphNode(BaseModel):
    id: str
    name: str
    description: str | None = None
    category: str | None = None
    difficulty: int | None = None
    estimated_minutes: int | None = None
    key_points: list[str] = Field(default_factory=list)
    text_material: str | None = None
    image_url: str | None = None
    video_title: str | None = None
    video_url: str | None = None
    resource_links: list[GraphResourceLink] = Field(default_factory=list)
    study_tips: list[str] = Field(default_factory=list)
    common_mistakes: list[str] = Field(default_factory=list)
    practice_task: str | None = None
    quiz: list[GraphQuizQuestion] = Field(default_factory=list)
    origin: str = "neo4j"


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    links: list[GraphEdge]
