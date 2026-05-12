from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_roles
from app.core.security import get_password_hash
from app.db import mysql as mysql_db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.admin import (
    AdminOverviewResponse,
    GraphStatsResponse,
    ManagedUserCreateRequest,
    ManagedUserItem,
    ManagedUserProfile,
    ManagedUserUpdateRequest,
    OperationLogItem,
    QuestionConceptStat,
    QuestionGovernanceStats,
    RecommendationSettingsResponse,
    RecommendationSettingsUpdateRequest,
)
from app.schemas.auth import UserResponse
from app.schemas.collaboration import QuestionCommentItemResponse, QuestionItemResponse
from app.schemas.coordination import CoordinationRequestItem, CoordinationRequestUpdateRequest
from app.schemas.graph_management import GraphChangeRequestItem, GraphChangeRequestReviewRequest
from app.services.graph_service import GraphService, get_graph_service
from app.services.json_store import (
    create_notification,
    create_operation_log,
    create_user,
    delete_question,
    delete_question_comment,
    delete_user,
    get_recommendation_settings,
    get_user_by_id,
    list_collaboration_requests,
    list_graph_change_requests,
    list_operation_logs,
    list_questions,
    list_users,
    update_collaboration_request,
    review_graph_change_request,
    update_recommendation_settings,
    update_user_account,
)
from app.services.recommend_service import RecommendationService, get_recommendation_service

router = APIRouter()


def _admin_actor(user: User | dict) -> tuple[int, str, str]:
    if isinstance(user, dict):
        profile = user.get("profile") or {}
        return user["id"], profile.get("real_name") or user["username"], user["role"]
    return user.id, (user.profile.real_name if user.profile and user.profile.real_name else user.username), user.role


def _serialize_user(
    user: User | dict,
    *,
    progress_rate: int = 0,
    mastered_count: int = 0,
    in_progress_count: int = 0,
    pending_question_count: int = 0,
) -> ManagedUserItem:
    if isinstance(user, dict):
        profile = user.get("profile") or {}
        return ManagedUserItem(
            id=user["id"],
            username=user["username"],
            role=user.get("role", "student"),
            class_id=user.get("class_id"),
            profile=ManagedUserProfile(
                real_name=profile.get("real_name"),
                school=profile.get("school"),
                major=profile.get("major"),
                grade=profile.get("grade"),
                class_name=profile.get("class_name"),
                gender=profile.get("gender"),
                age=profile.get("age"),
            )
            if profile
            else None,
            progress_rate=progress_rate,
            mastered_count=mastered_count,
            in_progress_count=in_progress_count,
            pending_question_count=pending_question_count,
        )

    profile = user.profile
    return ManagedUserItem(
        id=user.id,
        username=user.username,
        role=user.role,
        class_id=user.class_id,
        profile=ManagedUserProfile(
            real_name=profile.real_name if profile else None,
            school=profile.school if profile else None,
            major=profile.major if profile else None,
            grade=profile.grade if profile else None,
            class_name=profile.class_name if profile else None,
            gender=profile.gender if profile else None,
            age=profile.age if profile else None,
        )
        if profile
        else None,
        progress_rate=progress_rate,
        mastered_count=mastered_count,
        in_progress_count=in_progress_count,
        pending_question_count=pending_question_count,
    )


def _load_managed_users(db: Session) -> list[User | dict]:
    if mysql_db.database_mode == "json-fallback":
        return list_users()
    return db.query(User).options(selectinload(User.profile)).order_by(User.id.asc()).all()


def _resolve_user_summary(user_id: int | None, db: Session, cache: dict[int, dict]) -> dict:
    if not user_id:
        return {"name": "系统用户", "role": "system", "username": None}
    if user_id in cache:
        return cache[user_id]

    if mysql_db.database_mode == "json-fallback":
        user = get_user_by_id(user_id) or {}
        profile = user.get("profile") or {}
        summary = {
            "name": profile.get("real_name") or user.get("username") or f"用户{user_id}",
            "role": user.get("role", "student"),
            "username": user.get("username"),
        }
    else:
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
    cache[user_id] = summary
    return summary


def _serialize_question(question: dict, db: Session) -> QuestionItemResponse:
    user_cache: dict[int, dict] = {}
    student_summary = _resolve_user_summary(question["student_id"], db, user_cache)
    teacher_summary = _resolve_user_summary(question.get("teacher_id"), db, user_cache) if question.get("teacher_id") else None

    raw_comments = sorted(question.get("comments", []), key=lambda item: item["create_time"])
    comment_lookup: dict[int, QuestionCommentItemResponse] = {}
    top_level_comments: list[QuestionCommentItemResponse] = []
    for comment in raw_comments:
        author_summary = _resolve_user_summary(comment.get("author_id"), db, user_cache)
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
            like_count=len(comment.get("like_user_ids", [])),
            is_liked=False,
            is_excellent=comment.get("is_excellent", False),
            can_delete=False,
        )

    for comment in comment_lookup.values():
        if comment.parent_comment_id is not None and comment.parent_comment_id in comment_lookup:
            parent_comment = comment_lookup[comment.parent_comment_id]
            parent_comment.replies.append(comment)
            parent_comment.reply_count = len(parent_comment.replies)
        else:
            top_level_comments.append(comment)

    favorite_user_ids = question.get("favorite_user_ids", [])
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
        is_favorited=False,
        comment_count=len(raw_comments),
        comments=top_level_comments,
    )


def _serialize_coordination_request(item: dict, db: Session) -> CoordinationRequestItem:
    user_cache: dict[int, dict] = {}
    teacher_summary = _resolve_user_summary(item["teacher_id"], db, user_cache)
    handled_summary = _resolve_user_summary(item.get("handled_by"), db, user_cache) if item.get("handled_by") else None
    return CoordinationRequestItem(
        id=item["id"],
        teacher_id=item["teacher_id"],
        teacher_name=teacher_summary["name"],
        type=item["type"],
        title=item["title"],
        description=item["description"],
        status=item.get("status", "pending"),
        admin_reply=item.get("admin_reply"),
        create_time=item["create_time"],
        update_time=item.get("update_time", item["create_time"]),
        handled_by=item.get("handled_by"),
        handled_by_name=handled_summary["name"] if handled_summary else None,
    )


def _serialize_operation_log(item: dict) -> OperationLogItem:
    return OperationLogItem(
        id=item["id"],
        actor_name=item["actor_name"],
        actor_role=item["actor_role"],
        action=item["action"],
        target_type=item["target_type"],
        target_id=item.get("target_id"),
        description=item["description"],
        create_time=item["create_time"],
    )


def _serialize_graph_change_request(item: dict, db: Session) -> GraphChangeRequestItem:
    user_cache: dict[int, dict] = {}
    teacher_summary = _resolve_user_summary(item["teacher_id"], db, user_cache)
    reviewed_summary = _resolve_user_summary(item.get("reviewed_by"), db, user_cache) if item.get("reviewed_by") else None
    return GraphChangeRequestItem(
        id=item["id"],
        teacher_id=item["teacher_id"],
        teacher_name=teacher_summary["name"],
        action=item["action"],
        summary=item["summary"],
        target_concept_name=item.get("target_concept_name"),
        node=item["node"],
        prerequisite_names=item.get("prerequisite_names", []),
        next_names=item.get("next_names", []),
        related_names=item.get("related_names", []),
        status=item.get("status", "pending"),
        create_time=item["create_time"],
        review_time=item.get("review_time"),
        reviewed_by=item.get("reviewed_by"),
        reviewed_by_name=reviewed_summary["name"] if reviewed_summary else None,
        review_note=item.get("review_note"),
    )


@router.get("/overview", response_model=AdminOverviewResponse)
def get_admin_overview(
    current_user: User | dict = Depends(require_roles("admin")),
    db: Session = Depends(mysql_db.get_db),
    graph_service: GraphService = Depends(get_graph_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> AdminOverviewResponse:
    users = _load_managed_users(db)
    role_counts = Counter((user.get("role") if isinstance(user, dict) else user.role) for user in users)
    questions = list_questions()
    question_counts_by_student = Counter(item["student_id"] for item in questions if item["status"] == "pending")

    managed_users = []
    for user in users:
        role = user.get("role") if isinstance(user, dict) else user.role
        progress_rate = 0
        mastered_count = 0
        in_progress_count = 0
        if role == "student":
            user_id = user["id"] if isinstance(user, dict) else user.id
            overview = recommendation_service.build_overview(user_id=user_id, db=db)
            progress_rate = overview.progress_rate
            mastered_count = overview.mastered_count
            in_progress_count = overview.in_progress_count

        managed_users.append(
            _serialize_user(
                user,
                progress_rate=progress_rate,
                mastered_count=mastered_count,
                in_progress_count=in_progress_count,
                pending_question_count=question_counts_by_student.get(user["id"] if isinstance(user, dict) else user.id, 0),
            )
        )

    graph = graph_service.get_full_graph()
    coordination_requests = [_serialize_coordination_request(item, db) for item in list_collaboration_requests()[:12]]
    graph_change_requests = [_serialize_graph_change_request(item, db) for item in list_graph_change_requests()[:20]]
    category_breakdown = dict(Counter(node.category or "未分类" for node in graph.nodes))
    concept_counter = Counter(item.get("concept_name") or "综合问题" for item in questions)
    featured_question_count = sum(1 for item in questions if item.get("is_featured"))
    favorite_answer_count = sum(len(item.get("favorite_user_ids", [])) for item in questions)
    answered_question_count = sum(1 for item in questions if item["status"] == "answered")
    excellent_comment_count = sum(
        1
        for item in questions
        for comment in item.get("comments", [])
        if comment.get("is_excellent")
    )
    comment_like_count = sum(
        len(comment.get("like_user_ids", []))
        for item in questions
        for comment in item.get("comments", [])
    )

    return AdminOverviewResponse(
        total_users=len(users),
        role_counts=dict(role_counts),
        graph_stats=GraphStatsResponse(
            node_count=len(graph.nodes),
            relation_count=len(graph.links),
            category_breakdown=category_breakdown,
        ),
        pending_question_count=sum(1 for item in questions if item["status"] == "pending"),
        pending_coordination_count=sum(1 for item in coordination_requests if item.status != "resolved"),
        pending_graph_change_count=sum(1 for item in graph_change_requests if item.status == "pending"),
        question_governance=QuestionGovernanceStats(
            featured_question_count=featured_question_count,
            favorite_answer_count=favorite_answer_count,
            answered_question_count=answered_question_count,
            excellent_comment_count=excellent_comment_count,
            comment_like_count=comment_like_count,
            top_concepts=[
                QuestionConceptStat(concept_name=name, question_count=count)
                for name, count in concept_counter.most_common(6)
            ],
        ),
        recommendation_settings=RecommendationSettingsResponse(**get_recommendation_settings()),
        users=managed_users,
        recent_questions=[_serialize_question(item, db) for item in questions[:12]],
        coordination_requests=coordination_requests,
        graph_change_requests=graph_change_requests,
        operation_logs=[_serialize_operation_log(item) for item in list_operation_logs(limit=12)],
    )


@router.put("/users/{user_id}", response_model=UserResponse)
def manage_user(
    user_id: int,
    payload: ManagedUserUpdateRequest,
    current_user: User | dict = Depends(require_roles("admin")),
    db: Session = Depends(mysql_db.get_db),
) -> User | dict:
    actor_id, actor_name, actor_role = _admin_actor(current_user)
    profile_payload = {
        "real_name": payload.real_name,
        "school": payload.school,
        "major": payload.major,
        "grade": payload.grade,
        "class_name": payload.class_name,
        "gender": payload.gender,
        "age": payload.age,
    }

    if mysql_db.database_mode == "json-fallback":
        try:
            updated = update_user_account(
                user_id,
                {
                    "role": payload.role,
                    "class_id": payload.class_id,
                    "password": payload.password,
                    "profile": profile_payload,
                },
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        create_operation_log(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            action="update_user",
            target_type="user",
            target_id=str(user_id),
            description=f"修改账号 {updated['username']} 的角色或资料信息。",
        )
        return updated

    user = db.query(User).options(selectinload(User.profile)).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.role = payload.role
    user.class_id = payload.class_id
    if payload.password:
        user.password_hash = get_password_hash(payload.password)

    if any(value is not None and value != "" for value in profile_payload.values()):
        profile = user.profile
        if profile is None:
            profile = UserProfile(user_id=user.id)
            db.add(profile)
            db.flush()
        profile.real_name = payload.real_name
        profile.school = payload.school
        profile.major = payload.major
        profile.grade = payload.grade
        profile.class_name = payload.class_name
        profile.gender = payload.gender
        profile.age = payload.age

    db.add(user)
    db.commit()
    db.refresh(user)
    create_operation_log(
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action="update_user",
        target_type="user",
        target_id=str(user_id),
        description=f"修改账号 {user.username} 的角色或资料信息。",
    )
    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_managed_user(
    payload: ManagedUserCreateRequest,
    current_user: User | dict = Depends(require_roles("admin")),
    db: Session = Depends(mysql_db.get_db),
) -> User | dict:
    actor_id, actor_name, actor_role = _admin_actor(current_user)
    profile_payload = {
        "real_name": payload.real_name,
        "school": payload.school,
        "major": payload.major,
        "grade": payload.grade,
        "class_name": payload.class_name,
        "gender": payload.gender,
        "age": payload.age,
    }

    if mysql_db.database_mode == "json-fallback":
        try:
            created = create_user(
                {
                    "username": payload.username,
                    "password": payload.password,
                    "role": payload.role,
                    "class_id": payload.class_id,
                    "profile": profile_payload,
                }
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        create_operation_log(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            action="create_user",
            target_type="user",
            target_id=str(created["id"]),
            description=f"创建账号 {created['username']}。",
        )
        return created

    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists.")

    user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        class_id=payload.class_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if any(value for value in profile_payload.values()):
        db.add(UserProfile(user_id=user.id, **profile_payload))
        db.commit()

    create_operation_log(
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action="create_user",
        target_type="user",
        target_id=str(user.id),
        description=f"创建账号 {user.username}。",
    )
    return db.query(User).options(selectinload(User.profile)).filter(User.id == user.id).first()


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_managed_user(
    user_id: int,
    current_user: User | dict = Depends(require_roles("admin")),
    db: Session = Depends(mysql_db.get_db),
) -> None:
    actor_id, actor_name, actor_role = _admin_actor(current_user)
    if mysql_db.database_mode == "json-fallback":
        target = get_user_by_id(user_id)
        try:
            delete_user(user_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        create_operation_log(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            action="delete_user",
            target_type="user",
            target_id=str(user_id),
            description=f"删除账号 {(target or {}).get('username', user_id)}。",
        )
        return

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    username = user.username
    db.delete(user)
    db.commit()
    create_operation_log(
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action="delete_user",
        target_type="user",
        target_id=str(user_id),
        description=f"删除账号 {username}。",
    )


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_question(
    question_id: int,
    current_user: User | dict = Depends(require_roles("admin")),
) -> None:
    actor_id, actor_name, actor_role = _admin_actor(current_user)
    question = next((item for item in list_questions() if item["id"] == question_id), None)
    try:
        delete_question(question_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    create_operation_log(
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action="delete_question",
        target_type="question",
        target_id=str(question_id),
        description=f"删除讨论主题 {(question or {}).get('title', question_id)}。",
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_comment(
    comment_id: int,
    current_user: User | dict = Depends(require_roles("admin")),
) -> None:
    actor_id, actor_name, actor_role = _admin_actor(current_user)
    try:
        delete_question_comment(comment_id, force=True)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    create_operation_log(
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action="delete_comment",
        target_type="comment",
        target_id=str(comment_id),
        description=f"删除评论 {comment_id}。",
    )


@router.put("/coordination/{request_id}", response_model=CoordinationRequestItem)
def process_coordination_request(
    request_id: int,
    payload: CoordinationRequestUpdateRequest,
    current_user: User | dict = Depends(require_roles("admin")),
    db: Session = Depends(mysql_db.get_db),
) -> CoordinationRequestItem:
    admin_id, admin_name, admin_role = _admin_actor(current_user)
    try:
        item = update_collaboration_request(
            request_id,
            status=payload.status,
            admin_reply=payload.admin_reply,
            handled_by=admin_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    create_notification(
        item["teacher_id"],
        category="coordination",
        title="管理员已处理协同事项",
        content=f"{admin_name} 已将“{item['title']}”更新为“{item['status']}”，可前往教师工作台查看回复。",
        link="/teacher",
    )
    create_operation_log(
        actor_id=admin_id,
        actor_name=admin_name,
        actor_role=admin_role,
        action="update_coordination",
        target_type="coordination",
        target_id=str(request_id),
        description=f"更新教师协同事项《{item['title']}》状态为 {item['status']}。",
    )
    return _serialize_coordination_request(item, db)


@router.put("/graph-change-requests/{request_id}/review", response_model=GraphChangeRequestItem)
def review_teacher_graph_change_request(
    request_id: int,
    payload: GraphChangeRequestReviewRequest,
    current_user: User | dict = Depends(require_roles("admin")),
    db: Session = Depends(mysql_db.get_db),
) -> GraphChangeRequestItem:
    admin_id, admin_name, admin_role = _admin_actor(current_user)
    try:
        item = review_graph_change_request(
            request_id,
            status=payload.status,
            review_note=payload.review_note,
            reviewed_by=admin_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    action_text = "审核通过并发布" if payload.status == "approved" else "驳回"
    create_notification(
        item["teacher_id"],
        category="graph",
        title=f"图谱变更申请已{action_text}",
        content=f"{admin_name} 已{action_text}“{item['summary']}”。{payload.review_note or ''}",
        link="/teacher",
    )
    create_operation_log(
        actor_id=admin_id,
        actor_name=admin_name,
        actor_role=admin_role,
        action="review_graph_change",
        target_type="graph_change_request",
        target_id=str(request_id),
        description=f"{action_text}教师图谱变更申请《{item['summary']}》。",
    )
    return _serialize_graph_change_request(item, db)


@router.put("/settings/recommendation", response_model=RecommendationSettingsResponse)
def update_settings(
    payload: RecommendationSettingsUpdateRequest,
    current_user: User | dict = Depends(require_roles("admin")),
) -> RecommendationSettingsResponse:
    actor_id, actor_name, actor_role = _admin_actor(current_user)
    settings = update_recommendation_settings(payload.model_dump())
    create_operation_log(
        actor_id=actor_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action="update_recommendation_settings",
        target_type="settings",
        target_id="recommendation",
        description=(
            "修改推荐参数："
            f"推荐数 {settings['recommendation_limit']}，薄弱点 {settings['weak_point_limit']}，"
            f"路径上限 {settings['path_limit']}。"
        ),
    )
    return RecommendationSettingsResponse(**settings)
