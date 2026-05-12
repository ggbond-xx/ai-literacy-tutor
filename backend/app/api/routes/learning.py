import csv
import io
from collections import Counter, defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db import mysql as mysql_db
from app.models.user import User
from app.models.user_knowledge_status import UserKnowledgeStatus
from app.schemas.collaboration import (
    QuestionCommentCreateRequest,
    QuestionCommentItemResponse,
    QuestionCommentLikeToggleResponse,
    QuestionCollectionResponse,
    QuestionCreateRequest,
    QuestionFavoriteToggleResponse,
    QuestionItemResponse,
)
from app.schemas.learning import (
    KnowledgeStatusCollectionResponse,
    KnowledgeStatusItemResponse,
    KnowledgeStatusUpdateRequest,
    LearningAnalyticsResponse,
    LearningStatusProgressItem,
    ModuleProgressItem,
    NodeLearningTimeItemResponse,
    NodeVisitCreateRequest,
    QuizAttemptCreateRequest,
    QuizAttemptItemResponse,
    WeakReviewItemResponse,
)
from app.services.graph_service import GraphService, get_graph_service
from app.services.json_store import (
    create_question as create_json_question,
    create_question_comment,
    create_quiz_attempt,
    delete_question_comment,
    get_user_by_id,
    list_learning_statuses,
    list_node_visits,
    list_questions,
    list_quiz_attempts,
    record_node_visit,
    toggle_comment_like,
    toggle_question_favorite,
    upsert_learning_status as upsert_json_status,
)
from app.services.recommend_service import RecommendationService, get_recommendation_service

router = APIRouter()


def _user_identity(user: User | dict) -> tuple[int, str, str, str]:
    if isinstance(user, dict):
        profile = user.get("profile") or {}
        return user["id"], user["username"], profile.get("real_name") or user["username"], user["role"]

    profile = user.profile
    return user.id, user.username, (profile.real_name if profile and profile.real_name else user.username), user.role


def _resolve_user_summary(user_id: int | None, db: Session, cache: dict[int, dict]) -> dict:
    if not user_id:
        return {"name": "系统用户", "role": "system"}
    if user_id in cache:
        return cache[user_id]

    if mysql_db.database_mode != "json-fallback":
        user = db.query(User).options(selectinload(User.profile)).filter(User.id == user_id).first()
        summary = {
            "name": (
                (user.profile.real_name if user and user.profile and user.profile.real_name else None)
                or (user.username if user else None)
                or f"用户{user_id}"
            ),
            "role": user.role if user else "student",
            "username": user.username if user else None,
        }
    else:
        user = get_user_by_id(user_id) or {}
        profile = user.get("profile") or {}
        summary = {
            "name": profile.get("real_name") or user.get("username") or f"用户{user_id}",
            "role": user.get("role", "student"),
            "username": user.get("username"),
        }
    cache[user_id] = summary
    return summary


def _serialize_question(question: dict, db: Session, *, viewer_user_id: int | None = None) -> QuestionItemResponse:
    user_cache: dict[int, dict] = {}
    student_summary = _resolve_user_summary(question["student_id"], db, user_cache)
    teacher_summary = _resolve_user_summary(question.get("teacher_id"), db, user_cache) if question.get("teacher_id") else None

    favorite_user_ids = question.get("favorite_user_ids", [])
    raw_comments = sorted(question.get("comments", []), key=lambda item: item["create_time"])
    comment_lookup: dict[int, QuestionCommentItemResponse] = {}
    comments = []
    for comment in raw_comments:
        author_summary = _resolve_user_summary(comment.get("author_id"), db, user_cache)
        like_user_ids = comment.get("like_user_ids", [])
        parent_comment_id = comment.get("parent_comment_id")
        reply_to_author_name = None
        if parent_comment_id is not None:
            parent_comment = next((item for item in raw_comments if item["id"] == parent_comment_id), None)
            if parent_comment is not None:
                reply_to_author_name = _resolve_user_summary(parent_comment.get("author_id"), db, user_cache)["name"]

        comment_lookup[comment["id"]] = QuestionCommentItemResponse(
            id=comment["id"],
            question_id=question["id"],
            author_id=comment.get("author_id") or 0,
            author_name=author_summary["name"],
            author_role=comment.get("author_role") or author_summary["role"],
            content=comment["content"],
            create_time=comment["create_time"],
            parent_comment_id=parent_comment_id,
            reply_to_author_name=reply_to_author_name,
            like_count=len(like_user_ids),
            is_liked=viewer_user_id in like_user_ids if viewer_user_id is not None else False,
            is_excellent=comment.get("is_excellent", False),
            can_delete=viewer_user_id == comment.get("author_id"),
        )

    for comment in comment_lookup.values():
        if comment.parent_comment_id is not None and comment.parent_comment_id in comment_lookup:
            parent_comment = comment_lookup[comment.parent_comment_id]
            parent_comment.replies.append(comment)
            parent_comment.reply_count = len(parent_comment.replies)
        else:
            comments.append(comment)

    return QuestionItemResponse(
        id=question["id"],
        student_id=question["student_id"],
        student_name=student_summary["name"],
        concept_id=question.get("concept_id"),
        concept_name=question.get("concept_name"),
        title=question["title"],
        description=question["description"],
        teacher_reply=question.get("teacher_reply"),
        teacher_id=question.get("teacher_id"),
        teacher_name=teacher_summary["name"] if teacher_summary else None,
        status=question["status"],
        create_time=question["create_time"],
        reply_time=question.get("reply_time"),
        is_featured=question.get("is_featured", False),
        featured_time=question.get("featured_time"),
        favorite_count=len(favorite_user_ids),
        is_favorited=viewer_user_id in favorite_user_ids if viewer_user_id is not None else False,
        comment_count=len(raw_comments),
        comments=comments,
    )


def _list_status_records(user_id: int, db: Session) -> list[dict]:
    if mysql_db.database_mode != "json-fallback":
        records = (
            db.query(UserKnowledgeStatus)
            .filter(UserKnowledgeStatus.user_id == user_id)
            .order_by(UserKnowledgeStatus.update_time.desc())
            .all()
        )
        return [
            {
                "id": record.id,
                "concept_id": record.concept_id,
                "status": record.status,
                "update_time": record.update_time.isoformat(),
            }
            for record in records
        ]

    records = list_learning_statuses(user_id)
    return sorted(records, key=lambda item: item["update_time"], reverse=True)


def _build_learning_analytics(
    *,
    user_id: int,
    db: Session,
    graph_service: GraphService,
    recommendation_service: RecommendationService,
) -> LearningAnalyticsResponse:
    graph = graph_service.get_full_graph()
    status_records = _list_status_records(user_id, db)
    status_map = {item["concept_id"]: item["status"] for item in status_records}
    quiz_attempts = list_quiz_attempts(user_id)
    student_questions = list_questions(student_id=user_id)
    recommendation_overview = recommendation_service.build_overview(user_id=user_id, db=db)

    total_concepts = len(graph.nodes)
    mastered_count = sum(1 for node in graph.nodes if status_map.get(node.id, 0) == 2)
    in_progress_count = sum(1 for node in graph.nodes if status_map.get(node.id, 0) == 1)
    unlearned_count = max(total_concepts - mastered_count - in_progress_count, 0)

    def ratio(count: int) -> int:
        return round((count / total_concepts) * 100) if total_concepts else 0

    status_progress = [
        LearningStatusProgressItem(label="已掌握", status=2, count=mastered_count, ratio=ratio(mastered_count)),
        LearningStatusProgressItem(label="学习中", status=1, count=in_progress_count, ratio=ratio(in_progress_count)),
        LearningStatusProgressItem(label="未学", status=0, count=unlearned_count, ratio=ratio(unlearned_count)),
    ]

    module_buckets: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "total_count": 0,
            "mastered_count": 0,
            "in_progress_count": 0,
            "unlearned_count": 0,
        }
    )
    for node in graph.nodes:
        module_name = node.category or "未分类模块"
        bucket = module_buckets[module_name]
        bucket["total_count"] += 1
        node_status = status_map.get(node.id, 0)
        if node_status == 2:
            bucket["mastered_count"] += 1
        elif node_status == 1:
            bucket["in_progress_count"] += 1
        else:
            bucket["unlearned_count"] += 1

    module_progress = [
        ModuleProgressItem(
            module_name=module_name,
            total_count=bucket["total_count"],
            mastered_count=bucket["mastered_count"],
            in_progress_count=bucket["in_progress_count"],
            unlearned_count=bucket["unlearned_count"],
            progress_rate=round(
                (
                    (bucket["mastered_count"] + bucket["in_progress_count"] * 0.5)
                    / max(bucket["total_count"], 1)
                )
                * 100
            ),
        )
        for module_name, bucket in module_buckets.items()
    ]
    module_progress.sort(key=lambda item: (item.progress_rate, item.module_name))

    question_count_by_concept = Counter(item.get("concept_id") for item in student_questions if item.get("concept_id"))
    quiz_stat_map: dict[str, dict[str, int | float | None]] = defaultdict(
        lambda: {
            "wrong_answers": 0,
            "total_questions": 0,
            "latest_score": None,
        }
    )
    for attempt in quiz_attempts:
        bucket = quiz_stat_map[attempt["concept_id"]]
        bucket["wrong_answers"] += attempt.get("wrong_answers", 0)
        bucket["total_questions"] += attempt.get("total_questions", 0)
        if bucket["latest_score"] is None:
            bucket["latest_score"] = attempt.get("score")

    node_lookup = {node.id: node for node in graph.nodes}
    weak_review_items: list[WeakReviewItemResponse] = []
    for concept_id, node in node_lookup.items():
        question_count = question_count_by_concept.get(concept_id, 0)
        quiz_stats = quiz_stat_map.get(concept_id, {})
        wrong_answers = int(quiz_stats.get("wrong_answers", 0) or 0)
        total_questions_for_quiz = int(quiz_stats.get("total_questions", 0) or 0)
        if question_count <= 0 and wrong_answers <= 0:
            continue

        error_rate = round((wrong_answers / total_questions_for_quiz) * 100) if total_questions_for_quiz else 0
        review_score = round(error_rate * 0.7 + min(question_count, 3) / 3 * 30)
        reason_parts = []
        if error_rate > 0:
            reason_parts.append(f"自测错误率 {error_rate}%")
        if question_count > 0:
            reason_parts.append(f"围绕该节点提问 {question_count} 次")
        weak_review_items.append(
            WeakReviewItemResponse(
                concept_id=concept_id,
                concept_name=node.name,
                module_name=node.category,
                question_count=question_count,
                incorrect_count=wrong_answers,
                error_rate=error_rate,
                review_score=review_score,
                latest_score=quiz_stats.get("latest_score"),
                reason="，".join(reason_parts) or "建议回看当前节点。",
            )
        )

    weak_review_items.sort(key=lambda item: (-item.review_score, -item.question_count, -item.error_rate, item.concept_name))

    if len(weak_review_items) < 3:
        existing_ids = {item.concept_id for item in weak_review_items}
        for weak_point in recommendation_overview.weak_points:
            if weak_point.concept.id in existing_ids:
                continue
            weak_review_items.append(
                WeakReviewItemResponse(
                    concept_id=weak_point.concept.id,
                    concept_name=weak_point.concept.name,
                    module_name=weak_point.concept.category,
                    question_count=0,
                    incorrect_count=0,
                    error_rate=0,
                    review_score=weak_point.impact_count * 10,
                    latest_score=None,
                    reason=f"该节点会影响 {weak_point.impact_count} 个后续知识点，建议优先回顾。",
                )
            )
            if len(weak_review_items) >= 3:
                break

    recent_quiz_attempts = [
        QuizAttemptItemResponse(
            id=item["id"],
            concept_id=item["concept_id"],
            concept_name=item["concept_name"],
            total_questions=item["total_questions"],
            correct_answers=item["correct_answers"],
            wrong_answers=item["wrong_answers"],
            accuracy=round(float(item.get("accuracy", 0)) * 100, 1),
            score=item["score"],
            create_time=item["create_time"],
        )
        for item in quiz_attempts[:6]
    ]

    visit_buckets: dict[str, dict[str, int | str | None]] = defaultdict(
        lambda: {
            "total_seconds": 0,
            "visit_count": 0,
            "latest_time": None,
        }
    )
    for visit in list_node_visits(user_id=user_id):
        concept_id = visit["concept_id"]
        bucket = visit_buckets[concept_id]
        bucket["total_seconds"] = int(bucket["total_seconds"] or 0) + int(visit.get("duration_seconds", 0) or 0)
        bucket["visit_count"] = int(bucket["visit_count"] or 0) + 1
        if bucket["latest_time"] is None:
            bucket["latest_time"] = visit.get("create_time")

    node_learning_times = [
        NodeLearningTimeItemResponse(
            concept_id=concept_id,
            concept_name=node_lookup.get(concept_id).name if concept_id in node_lookup else concept_id,
            total_minutes=round(int(bucket["total_seconds"] or 0) / 60),
            visit_count=int(bucket["visit_count"] or 0),
            average_minutes=round((int(bucket["total_seconds"] or 0) / max(int(bucket["visit_count"] or 0), 1)) / 60),
            latest_time=bucket["latest_time"] if isinstance(bucket["latest_time"], str) else None,
        )
        for concept_id, bucket in visit_buckets.items()
    ]
    node_learning_times.sort(key=lambda item: (-item.total_minutes, item.concept_name))

    return LearningAnalyticsResponse(
        progress_rate=recommendation_overview.progress_rate,
        total_concepts=total_concepts,
        mastered_count=mastered_count,
        in_progress_count=in_progress_count,
        unlearned_count=unlearned_count,
        status_progress=status_progress,
        module_progress=module_progress,
        weak_review_items=weak_review_items[:3],
        recent_quiz_attempts=recent_quiz_attempts,
        node_learning_times=node_learning_times,
    )


@router.get("/status", response_model=KnowledgeStatusCollectionResponse)
def get_learning_statuses(
    current_user: User | dict = Depends(get_current_user),
    db: Session = Depends(mysql_db.get_db),
) -> KnowledgeStatusCollectionResponse:
    user_id = current_user["id"] if isinstance(current_user, dict) else current_user.id
    records = _list_status_records(user_id, db)
    items = [KnowledgeStatusItemResponse.model_validate(record) for record in records]
    return KnowledgeStatusCollectionResponse(
        items=items,
        status_map={item.concept_id: item.status for item in items},
    )


@router.put("/status/{concept_id}", response_model=KnowledgeStatusItemResponse)
def upsert_learning_status(
    concept_id: str,
    payload: KnowledgeStatusUpdateRequest,
    current_user: User | dict = Depends(get_current_user),
    db: Session = Depends(mysql_db.get_db),
) -> UserKnowledgeStatus | dict:
    user_id = current_user["id"] if isinstance(current_user, dict) else current_user.id
    if mysql_db.database_mode == "json-fallback":
        return upsert_json_status(user_id, concept_id, payload.status)

    record = (
        db.query(UserKnowledgeStatus)
        .filter(
            UserKnowledgeStatus.user_id == user_id,
            UserKnowledgeStatus.concept_id == concept_id,
        )
        .first()
    )

    if record is None:
        record = UserKnowledgeStatus(
            user_id=user_id,
            concept_id=concept_id,
            status=payload.status,
        )
        db.add(record)
    else:
        record.status = payload.status

    db.commit()
    db.refresh(record)
    return record


@router.get("/questions", response_model=QuestionCollectionResponse)
def get_visible_questions(
    concept_id: str | None = Query(default=None),
    featured_only: bool = Query(default=False),
    favorites_only: bool = Query(default=False),
    current_user: User | dict = Depends(get_current_user),
    db: Session = Depends(mysql_db.get_db),
) -> QuestionCollectionResponse:
    user_id, _, _, _ = _user_identity(current_user)
    questions = list_questions(
        concept_id=concept_id,
        featured_only=featured_only,
        favorite_user_id=user_id if favorites_only else None,
    )

    items = [_serialize_question(item, db, viewer_user_id=user_id) for item in questions]
    return QuestionCollectionResponse(items=items)


@router.post("/questions", response_model=QuestionItemResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    payload: QuestionCreateRequest,
    current_user: User | dict = Depends(get_current_user),
    db: Session = Depends(mysql_db.get_db),
) -> QuestionItemResponse:
    user_id, _, _, role = _user_identity(current_user)
    if role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can create questions.")

    question = create_json_question(
        student_id=user_id,
        concept_id=payload.concept_id,
        concept_name=payload.concept_name,
        title=payload.title,
        description=payload.description,
    )
    return _serialize_question(question, db, viewer_user_id=user_id)


@router.post("/questions/{question_id}/favorite", response_model=QuestionFavoriteToggleResponse)
def toggle_favorite_question(
    question_id: int,
    current_user: User | dict = Depends(get_current_user),
) -> QuestionFavoriteToggleResponse:
    user_id, _, _, role = _user_identity(current_user)
    if role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can favorite answers.")

    questions = list_questions()
    question = next((item for item in questions if item["id"] == question_id), None)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    has_excellent_comment = any(comment.get("is_excellent") for comment in question.get("comments", []))
    has_teacher_comment = any(comment.get("author_role") == "teacher" for comment in question.get("comments", []))
    if not question.get("is_featured") or not (question.get("teacher_reply") or has_excellent_comment or has_teacher_comment):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only featured answered questions can be favorited.")

    result = toggle_question_favorite(question_id=question_id, user_id=user_id)
    return QuestionFavoriteToggleResponse(**result)


@router.post("/questions/{question_id}/comments", response_model=QuestionCommentItemResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    question_id: int,
    payload: QuestionCommentCreateRequest,
    current_user: User | dict = Depends(get_current_user),
) -> QuestionCommentItemResponse:
    user_id, username, display_name, role = _user_identity(current_user)
    try:
        comment = create_question_comment(
            question_id=question_id,
            author_id=user_id,
            author_role=role,
            content=payload.content,
            parent_comment_id=payload.parent_comment_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return QuestionCommentItemResponse(
        id=comment["id"],
        question_id=question_id,
        author_id=user_id,
        author_name=display_name or username,
        author_role=role,
        content=comment["content"],
        create_time=comment["create_time"],
        parent_comment_id=comment.get("parent_comment_id"),
        like_count=0,
        is_liked=False,
        is_excellent=False,
        can_delete=True,
        reply_count=0,
        replies=[],
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_comment(
    comment_id: int,
    current_user: User | dict = Depends(get_current_user),
) -> None:
    user_id, _, _, _ = _user_identity(current_user)
    try:
        delete_question_comment(comment_id=comment_id, user_id=user_id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/comments/{comment_id}/like", response_model=QuestionCommentLikeToggleResponse)
def like_comment(
    comment_id: int,
    current_user: User | dict = Depends(get_current_user),
) -> QuestionCommentLikeToggleResponse:
    user_id, _, _, _ = _user_identity(current_user)
    try:
        result = toggle_comment_like(comment_id=comment_id, user_id=user_id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return QuestionCommentLikeToggleResponse(**result)


@router.post("/quiz/{concept_id}/attempts", response_model=QuizAttemptItemResponse, status_code=status.HTTP_201_CREATED)
def submit_quiz_attempt(
    concept_id: str,
    payload: QuizAttemptCreateRequest,
    current_user: User | dict = Depends(get_current_user),
) -> QuizAttemptItemResponse:
    user_id, _, _, role = _user_identity(current_user)
    if role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can submit quiz attempts.")

    attempt = create_quiz_attempt(
        user_id,
        concept_id=concept_id,
        concept_name=payload.concept_name,
        total_questions=payload.total_questions,
        correct_answers=payload.correct_answers,
        score=payload.score,
    )
    return QuizAttemptItemResponse(
        id=attempt["id"],
        concept_id=attempt["concept_id"],
        concept_name=attempt["concept_name"],
        total_questions=attempt["total_questions"],
        correct_answers=attempt["correct_answers"],
        wrong_answers=attempt["wrong_answers"],
        accuracy=round(float(attempt["accuracy"]) * 100, 1),
        score=attempt["score"],
        create_time=attempt["create_time"],
    )


@router.post("/node-visits/{concept_id}", status_code=status.HTTP_201_CREATED)
def create_node_visit_record(
    concept_id: str,
    payload: NodeVisitCreateRequest,
    current_user: User | dict = Depends(get_current_user),
) -> dict:
    user_id, _, _, _ = _user_identity(current_user)
    return record_node_visit(
        user_id,
        concept_id=concept_id,
        concept_name=payload.concept_name,
        duration_seconds=payload.duration_seconds,
    )


@router.get("/analytics", response_model=LearningAnalyticsResponse)
def get_learning_analytics(
    current_user: User | dict = Depends(get_current_user),
    db: Session = Depends(mysql_db.get_db),
    graph_service: GraphService = Depends(get_graph_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> LearningAnalyticsResponse:
    user_id, _, _, role = _user_identity(current_user)
    if role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can view learning analytics.")
    return _build_learning_analytics(
        user_id=user_id,
        db=db,
        graph_service=graph_service,
        recommendation_service=recommendation_service,
    )


@router.get("/export/csv")
def export_learning_records_csv(
    current_user: User | dict = Depends(get_current_user),
    db: Session = Depends(mysql_db.get_db),
) -> Response:
    user_id, username, display_name, role = _user_identity(current_user)
    if role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can export learning records.")

    status_records = _list_status_records(user_id, db)
    quiz_attempts = list_quiz_attempts(user_id)
    questions = list_questions(student_id=user_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "record_type",
            "username",
            "display_name",
            "concept_id",
            "concept_name",
            "status",
            "quiz_score",
            "question_title",
            "question_status",
            "create_time",
        ]
    )

    for item in status_records:
        writer.writerow(
            [
                "learning_status",
                username,
                display_name,
                item["concept_id"],
                "",
                item["status"],
                "",
                "",
                "",
                item["update_time"],
            ]
        )

    for item in quiz_attempts:
        writer.writerow(
            [
                "quiz_attempt",
                username,
                display_name,
                item["concept_id"],
                item["concept_name"],
                "",
                item["score"],
                "",
                "",
                item["create_time"],
            ]
        )

    for item in questions:
        writer.writerow(
            [
                "question",
                username,
                display_name,
                item.get("concept_id") or "",
                item.get("concept_name") or "",
                "",
                "",
                item["title"],
                item["status"],
                item["create_time"],
            ]
        )

    filename = f"student-learning-records-{username}.csv"
    csv_text = "\ufeff" + output.getvalue()
    return Response(
        content=csv_text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
