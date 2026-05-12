from pydantic import BaseModel, Field


class QuestionCreateRequest(BaseModel):
    concept_id: str | None = None
    concept_name: str | None = None
    title: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=5, max_length=1000)


class QuestionReplyRequest(BaseModel):
    teacher_reply: str = Field(min_length=2, max_length=1000)


class QuestionCommentCreateRequest(BaseModel):
    content: str = Field(min_length=2, max_length=1000)
    parent_comment_id: int | None = None


class QuestionFeatureRequest(BaseModel):
    featured: bool = True


class CommentFeatureRequest(BaseModel):
    is_excellent: bool = True


class QuestionFavoriteToggleResponse(BaseModel):
    question_id: int
    is_favorited: bool
    favorite_count: int


class QuestionCommentLikeToggleResponse(BaseModel):
    comment_id: int
    is_liked: bool
    like_count: int


class QuestionCommentItemResponse(BaseModel):
    id: int
    question_id: int
    author_id: int
    author_name: str
    author_role: str
    content: str
    create_time: str
    parent_comment_id: int | None = None
    reply_to_author_name: str | None = None
    like_count: int = 0
    is_liked: bool = False
    is_excellent: bool = False
    can_delete: bool = False
    reply_count: int = 0
    replies: list["QuestionCommentItemResponse"] = Field(default_factory=list)


class QuestionItemResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    concept_id: str | None = None
    concept_name: str | None = None
    title: str
    description: str
    teacher_reply: str | None = None
    teacher_id: int | None = None
    teacher_name: str | None = None
    status: str
    create_time: str
    reply_time: str | None = None
    is_featured: bool = False
    featured_time: str | None = None
    favorite_count: int = 0
    is_favorited: bool = False
    comment_count: int = 0
    comments: list[QuestionCommentItemResponse] = Field(default_factory=list)


class QuestionCollectionResponse(BaseModel):
    items: list[QuestionItemResponse]


QuestionCommentItemResponse.model_rebuild()
