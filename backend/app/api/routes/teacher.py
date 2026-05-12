import csv
import io
from collections import Counter, defaultdict

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_roles
from app.db import mysql as mysql_db
from app.models.user import User
from app.models.user_knowledge_status import UserKnowledgeStatus
from app.schemas.collaboration import (
    CommentFeatureRequest,
    QuestionCommentItemResponse,
    QuestionFeatureRequest,
    QuestionItemResponse,
    QuestionReplyRequest,
)
from app.schemas.coordination import CoordinationRequestCreateRequest, CoordinationRequestItem
from app.schemas.graph_management import GraphChangeRequestCreateRequest, GraphChangeRequestItem
from app.schemas.teacher import (
    ClassOverviewMetrics,
    ClassLearningOverviewItem,
    ConceptClassAnalyticsItem,
    ConceptQuestionStat,
    ConceptStatusStat,
    QuickReplyTemplateCreateRequest,
    QuickReplyTemplateItem,
    LearningFactorAnalysisItem,
    LearningFactorGroupItem,
    NodeLearningAnalysisItem,
    StudentLearningStatusSnapshot,
    StudentProgressItem,
    StudentProgressProfile,
    StudentSnapshotResponse,
    TeacherOverviewResponse,
    TeacherConceptAnalyticsResponse,
    StatusDistributionItem,
)
from app.services.graph_service import GraphService, get_graph_service
from app.services.json_store import (
    create_collaboration_request,
    create_graph_change_request,
    create_notification,
    create_quick_reply_template,
    delete_quick_reply_template,
    get_user_by_id,
    list_all_learning_statuses,
    list_collaboration_requests,
    list_graph_change_requests,
    list_learning_statuses,
    list_node_visits,
    list_questions,
    list_quick_reply_templates,
    list_users,
    reply_question,
    set_comment_excellent,
    set_question_featured,
)
from app.services.recommend_service import RecommendationService, get_recommendation_service

router = APIRouter()


def _get_role_and_class(user: User | dict) -> tuple[int, int | None]:
    if isinstance(user, dict):
        return user["id"], user.get("class_id")
    return user.id, user.class_id


def _get_profile_value(user: User | dict, field_name: str) -> str | None:
    if isinstance(user, dict):
        return (user.get("profile") or {}).get(field_name)
    profile = user.profile
    return getattr(profile, field_name, None) if profile is not None else None


def _display_name(user: User | dict) -> str:
    return _get_profile_value(user, "real_name") or (user["username"] if isinstance(user, dict) else user.username)


def _list_student_users(db: Session, teacher_class_id: int | None) -> list[User | dict]:
    if mysql_db.database_mode == "json-fallback":
        users = [item for item in list_users() if item.get("role") == "student"]
        return users

    query = db.query(User).options(selectinload(User.profile)).filter(User.role == "student")
    return query.order_by(User.id.asc()).all()


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


def _build_progress_item(student: User | dict, overview) -> StudentProgressItem:
    user_id = student["id"] if isinstance(student, dict) else student.id
    return StudentProgressItem(
        user_id=user_id,
        username=student["username"] if isinstance(student, dict) else student.username,
        display_name=_display_name(student),
        class_id=student.get("class_id") if isinstance(student, dict) else student.class_id,
        profile=StudentProgressProfile(
            real_name=_get_profile_value(student, "real_name"),
            school=_get_profile_value(student, "school"),
            major=_get_profile_value(student, "major"),
            grade=_get_profile_value(student, "grade"),
            class_name=_get_profile_value(student, "class_name"),
            gender=_get_profile_value(student, "gender"),
            age=int(_get_profile_value(student, "age") or 0) or None,
        ),
        progress_rate=overview.progress_rate,
        mastered_count=overview.mastered_count,
        in_progress_count=overview.in_progress_count,
        unlearned_count=overview.unlearned_count,
        current_target=overview.default_target.name if overview.default_target else None,
        weak_point=overview.weak_points[0].concept.name if overview.weak_points else None,
    )


def _class_name_for_student(student: User | dict) -> str:
    profile_class_name = _get_profile_value(student, "class_name")
    class_id = student.get("class_id") if isinstance(student, dict) else student.class_id
    return profile_class_name or (f"{class_id}班" if class_id is not None else "未分班")


def _student_id(student: User | dict) -> int:
    return student["id"] if isinstance(student, dict) else student.id


def _student_class_id(student: User | dict) -> int | None:
    return student.get("class_id") if isinstance(student, dict) else student.class_id


def _status_percentage(count: int, total: int) -> int:
    return round((count / total) * 100) if total else 0


def _load_all_status_records(student_ids: set[int], db: Session) -> list[dict]:
    if not student_ids:
        return []
    if mysql_db.database_mode == "json-fallback":
        return [item for item in list_all_learning_statuses() if item["user_id"] in student_ids]
    records = db.query(UserKnowledgeStatus).filter(UserKnowledgeStatus.user_id.in_(student_ids)).all()
    return [
        {
            "user_id": item.user_id,
            "concept_id": item.concept_id,
            "status": item.status,
            "update_time": item.update_time.isoformat(),
        }
        for item in records
    ]


def _concept_status_stat(concept, counts: Counter) -> ConceptStatusStat:
    values = {
        0: counts.get(0, 0),
        1: counts.get(1, 0),
        2: counts.get(2, 0),
    }
    dominant_status, dominant_count = max(values.items(), key=lambda item: (item[1], -item[0]))
    return ConceptStatusStat(
        concept_id=concept.id,
        concept_name=concept.name,
        category=concept.category,
        unlearned_count=values[0],
        in_progress_count=values[1],
        mastered_count=values[2],
        dominant_status=dominant_status,
        dominant_count=dominant_count,
    )


def _build_class_overviews(
    *,
    students: list[User | dict],
    progress_items: list[StudentProgressItem],
    graph,
    status_records: list[dict],
    questions: list[dict],
) -> list[ClassLearningOverviewItem]:
    student_lookup = {_student_id(student): student for student in students}
    progress_lookup = {item.user_id: item for item in progress_items}
    status_map = {(item["user_id"], item["concept_id"]): item["status"] for item in status_records}
    questions_by_student = Counter(item["student_id"] for item in questions if item["status"] == "pending")
    featured_by_student = Counter(item["student_id"] for item in questions if item.get("is_featured"))

    class_buckets: dict[str, dict] = {}
    for student in students:
        class_name = _class_name_for_student(student)
        class_id = _student_class_id(student)
        class_buckets.setdefault(
            class_name,
            {
                "class_id": class_id,
                "students": [],
                "status_counter": Counter(),
                "concept_counters": {node.id: Counter() for node in graph.nodes},
            },
        )
        class_buckets[class_name]["students"].append(student)

    result: list[ClassLearningOverviewItem] = []
    for class_name, bucket in class_buckets.items():
        class_students = bucket["students"]
        class_student_ids = {_student_id(student) for student in class_students}
        class_progress_items = [progress_lookup[item] for item in class_student_ids if item in progress_lookup]
        student_count = len(class_students)
        for node in graph.nodes:
            for student_id in class_student_ids:
                status_value = status_map.get((student_id, node.id), 0)
                bucket["status_counter"][status_value] += 1
                bucket["concept_counters"][node.id][status_value] += 1

        concept_stats = [_concept_status_stat(node, bucket["concept_counters"][node.id]) for node in graph.nodes]
        result.append(
            ClassLearningOverviewItem(
                class_id=bucket["class_id"],
                class_name=class_name,
                student_count=student_count,
                average_progress_rate=round(sum(item.progress_rate for item in class_progress_items) / student_count) if student_count else 0,
                mastered_concepts_total=sum(item.mastered_count for item in class_progress_items),
                pending_question_count=sum(questions_by_student.get(item, 0) for item in class_student_ids),
                featured_question_count=sum(featured_by_student.get(item, 0) for item in class_student_ids),
                status_distribution=[
                    StatusDistributionItem(status=2, label="已掌握", count=bucket["status_counter"].get(2, 0), percentage=_status_percentage(bucket["status_counter"].get(2, 0), student_count * max(len(graph.nodes), 1))),
                    StatusDistributionItem(status=1, label="学习中", count=bucket["status_counter"].get(1, 0), percentage=_status_percentage(bucket["status_counter"].get(1, 0), student_count * max(len(graph.nodes), 1))),
                    StatusDistributionItem(status=0, label="未学", count=bucket["status_counter"].get(0, 0), percentage=_status_percentage(bucket["status_counter"].get(0, 0), student_count * max(len(graph.nodes), 1))),
                ],
                students=sorted(class_progress_items, key=lambda item: (-item.progress_rate, item.username)),
                top_unlearned_concepts=sorted(concept_stats, key=lambda item: (-item.unlearned_count, item.concept_name))[:6],
                top_in_progress_concepts=sorted(concept_stats, key=lambda item: (-item.in_progress_count, item.concept_name))[:6],
                top_mastered_concepts=sorted(concept_stats, key=lambda item: (-item.mastered_count, item.concept_name))[:6],
            )
        )
    return sorted(result, key=lambda item: item.class_name)


def _age_band(age: int | None) -> str:
    if age is None:
        return "未知年龄"
    if age <= 18:
        return "18岁及以下"
    if age <= 20:
        return "19-20岁"
    return "21岁及以上"


def _build_learning_factor_analysis(
    *,
    students: list[User | dict],
    graph,
    status_records: list[dict],
    visits: list[dict],
) -> list[LearningFactorAnalysisItem]:
    student_lookup = {_student_id(student): student for student in students}
    status_map = {(item["user_id"], item["concept_id"]): item["status"] for item in status_records}
    visit_minutes_by_student = Counter()
    for visit in visits:
        visit_minutes_by_student[visit["user_id"]] += round((visit.get("duration_seconds", 0) or 0) / 60)
    visit_seconds_by_concept: dict[str, list[int]] = defaultdict(list)
    for visit in visits:
        duration = int(visit.get("duration_seconds", 0) or 0)
        if duration > 0:
            visit_seconds_by_concept[visit["concept_id"]].append(duration)

    def status_concepts(concept_stats: list[ConceptStatusStat], status_value: int) -> list[ConceptStatusStat]:
        count_field = {0: "unlearned_count", 1: "in_progress_count", 2: "mastered_count"}[status_value]
        return sorted(
            [item for item in concept_stats if getattr(item, count_field) > 0],
            key=lambda item: (-getattr(item, count_field), item.concept_name),
        )

    def group_for_factor(student: User | dict, factor_key: str) -> tuple[str, str]:
        user_id = _student_id(student)
        if factor_key == "gender":
            value = _get_profile_value(student, "gender") or "未填写"
            return value, value
        if factor_key == "age":
            age = int(_get_profile_value(student, "age") or 0) or None
            label = _age_band(age)
            return label, label
        if factor_key == "duration":
            minutes = visit_minutes_by_student.get(user_id, 0)
            if minutes < 60:
                return "short", "累计学习60分钟以下"
            if minutes < 180:
                return "medium", "累计学习60-180分钟"
            return "long", "累计学习180分钟以上"
        class_name = _class_name_for_student(student)
        return class_name, class_name

    factor_specs = [
        ("gender", "性别分组", "比较不同性别学生在知识图谱中的掌握结构，用于发现是否存在学习支持差异。"),
        ("age", "年龄段分组", "按年龄段观察掌握率与薄弱节点，辅助教师调整案例难度和讲解节奏。"),
        ("duration", "学习时长分组", "按累计节点学习时间分组，观察学习投入与掌握状态之间的对应关系。"),
    ]
    result: list[LearningFactorAnalysisItem] = []
    total_nodes = max(len(graph.nodes), 1)
    for factor_key, factor_label, description in factor_specs:
        if factor_key == "duration":
            buckets: dict[str, dict] = {
                "short": {"label": "平均学习20分钟以下", "nodes": [], "status_counter": Counter(), "concept_counters": {}, "learning_minutes": 0},
                "medium": {"label": "平均学习20-40分钟", "nodes": [], "status_counter": Counter(), "concept_counters": {}, "learning_minutes": 0},
                "long": {"label": "平均学习40分钟以上", "nodes": [], "status_counter": Counter(), "concept_counters": {}, "learning_minutes": 0},
            }
            student_ids = {_student_id(student) for student in students}
            for node in graph.nodes:
                seconds_values = visit_seconds_by_concept.get(node.id, [])
                avg_minutes = round(sum(seconds_values) / len(seconds_values) / 60) if seconds_values else 0
                bucket_key = "short" if avg_minutes < 20 else "medium" if avg_minutes < 40 else "long"
                bucket = buckets[bucket_key]
                bucket["nodes"].append(node)
                bucket["concept_counters"][node.id] = Counter()
                bucket["learning_minutes"] += avg_minutes
                for student_id in student_ids:
                    status_value = status_map.get((student_id, node.id), 0)
                    bucket["status_counter"][status_value] += 1
                    bucket["concept_counters"][node.id][status_value] += 1

            groups = []
            for key, bucket in buckets.items():
                node_count = len(bucket["nodes"])
                denominator = len(students) * max(node_count, 1)
                concept_stats = [_concept_status_stat(node, bucket["concept_counters"][node.id]) for node in bucket["nodes"]]
                groups.append(
                    LearningFactorGroupItem(
                        group_key=key,
                        group_label=bucket["label"],
                        student_count=len(students),
                        mastered_count=bucket["status_counter"].get(2, 0),
                        in_progress_count=bucket["status_counter"].get(1, 0),
                        unlearned_count=bucket["status_counter"].get(0, 0),
                        mastered_percentage=_status_percentage(bucket["status_counter"].get(2, 0), denominator),
                        in_progress_percentage=_status_percentage(bucket["status_counter"].get(1, 0), denominator),
                        unlearned_percentage=_status_percentage(bucket["status_counter"].get(0, 0), denominator),
                        average_learning_minutes=round(bucket["learning_minutes"] / node_count) if node_count else 0,
                        weak_concepts=sorted(concept_stats, key=lambda item: (-item.unlearned_count, -item.in_progress_count, item.concept_name))[:5],
                        mastered_concepts=status_concepts(concept_stats, 2),
                        in_progress_concepts=status_concepts(concept_stats, 1),
                        unlearned_concepts=status_concepts(concept_stats, 0),
                    )
                )
            result.append(
                LearningFactorAnalysisItem(
                    factor_key=factor_key,
                    factor_label="节点平均学习时长分组",
                    description="按单个节点的平均学习时长分组，观察节点耗时与掌握状态之间的关系，用于判断节点难度。",
                    groups=groups,
                )
            )
            continue

        buckets: dict[str, dict] = {}
        for student in students:
            key, label = group_for_factor(student, factor_key)
            buckets.setdefault(
                key,
                {
                    "label": label,
                    "student_ids": [],
                    "status_counter": Counter(),
                    "concept_counters": {node.id: Counter() for node in graph.nodes},
                    "learning_minutes": 0,
                },
            )
            student_id = _student_id(student)
            buckets[key]["student_ids"].append(student_id)
            buckets[key]["learning_minutes"] += visit_minutes_by_student.get(student_id, 0)
            for node in graph.nodes:
                status_value = status_map.get((student_id, node.id), 0)
                buckets[key]["status_counter"][status_value] += 1
                buckets[key]["concept_counters"][node.id][status_value] += 1

        groups: list[LearningFactorGroupItem] = []
        for key, bucket in buckets.items():
            student_count = len(bucket["student_ids"])
            denominator = student_count * total_nodes
            concept_stats = [_concept_status_stat(node, bucket["concept_counters"][node.id]) for node in graph.nodes]
            groups.append(
                LearningFactorGroupItem(
                    group_key=key,
                    group_label=bucket["label"],
                    student_count=student_count,
                    mastered_count=bucket["status_counter"].get(2, 0),
                    in_progress_count=bucket["status_counter"].get(1, 0),
                    unlearned_count=bucket["status_counter"].get(0, 0),
                    mastered_percentage=_status_percentage(bucket["status_counter"].get(2, 0), denominator),
                    in_progress_percentage=_status_percentage(bucket["status_counter"].get(1, 0), denominator),
                    unlearned_percentage=_status_percentage(bucket["status_counter"].get(0, 0), denominator),
                    average_learning_minutes=round(bucket["learning_minutes"] / student_count) if student_count else 0,
                    weak_concepts=sorted(concept_stats, key=lambda item: (-item.unlearned_count, -item.in_progress_count, item.concept_name))[:5],
                    mastered_concepts=status_concepts(concept_stats, 2),
                    in_progress_concepts=status_concepts(concept_stats, 1),
                    unlearned_concepts=status_concepts(concept_stats, 0),
                )
            )
        result.append(
            LearningFactorAnalysisItem(
                factor_key=factor_key,
                factor_label=factor_label,
                description=description,
                groups=sorted(groups, key=lambda item: item.group_label),
            )
        )
    return result


def _build_node_learning_analysis(
    *,
    graph,
    student_ids: set[int],
    status_records: list[dict],
    questions: list[dict],
    visits: list[dict],
) -> list[NodeLearningAnalysisItem]:
    status_by_concept: dict[str, Counter] = {node.id: Counter() for node in graph.nodes}
    status_map = {(item["user_id"], item["concept_id"]): item["status"] for item in status_records}
    for node in graph.nodes:
        for student_id in student_ids:
            status_by_concept[node.id][status_map.get((student_id, node.id), 0)] += 1

    question_counter = Counter(item.get("concept_id") for item in questions if item.get("concept_id"))
    pending_counter = Counter(item.get("concept_id") for item in questions if item.get("concept_id") and item.get("status") == "pending")
    visit_counter = Counter(item.get("concept_id") for item in visits if item.get("concept_id"))
    visit_seconds_by_concept: dict[str, list[int]] = defaultdict(list)
    for visit in visits:
        duration = int(visit.get("duration_seconds", 0) or 0)
        if duration > 0 and visit.get("concept_id"):
            visit_seconds_by_concept[visit["concept_id"]].append(duration)

    total_students = len(student_ids)
    result: list[NodeLearningAnalysisItem] = []
    for node in graph.nodes:
        counts = status_by_concept[node.id]
        mastered = counts.get(2, 0)
        in_progress = counts.get(1, 0)
        unlearned = counts.get(0, 0)
        durations = visit_seconds_by_concept.get(node.id, [])
        average_minutes = round(sum(durations) / len(durations) / 60) if durations else 0
        question_count = question_counter.get(node.id, 0)
        pending_count = pending_counter.get(node.id, 0)
        unlearned_percentage = _status_percentage(unlearned, total_students)
        in_progress_percentage = _status_percentage(in_progress, total_students)
        mastered_percentage = _status_percentage(mastered, total_students)
        risk_score = min(
            100,
            round(
                unlearned_percentage * 0.45
                + in_progress_percentage * 0.2
                + min(question_count, 5) * 8
                + min(pending_count, 3) * 8
                + min(average_minutes, 60) * 0.25
            ),
        )
        reason_parts = []
        if unlearned_percentage >= 50:
            reason_parts.append(f"未学比例 {unlearned_percentage}%")
        if in_progress_percentage >= 30:
            reason_parts.append(f"学习中比例 {in_progress_percentage}%")
        if question_count:
            reason_parts.append(f"提问 {question_count} 次")
        if average_minutes:
            reason_parts.append(f"平均学习 {average_minutes} 分钟")
        result.append(
            NodeLearningAnalysisItem(
                concept_id=node.id,
                concept_name=node.name,
                category=node.category,
                question_count=question_count,
                pending_count=pending_count,
                click_count=visit_counter.get(node.id, 0),
                average_learning_minutes=average_minutes,
                mastered_count=mastered,
                in_progress_count=in_progress,
                unlearned_count=unlearned,
                mastered_percentage=mastered_percentage,
                in_progress_percentage=in_progress_percentage,
                unlearned_percentage=unlearned_percentage,
                risk_score=risk_score,
                risk_reason="；".join(reason_parts) or "当前学习数据较平稳",
            )
        )
    return sorted(result, key=lambda item: (-item.risk_score, -item.pending_count, -item.question_count, item.concept_name))


def _list_student_status_snapshot_records(student_id: int, db: Session, graph) -> list[StudentLearningStatusSnapshot]:
    if mysql_db.database_mode != "json-fallback":
        records = (
            db.query(UserKnowledgeStatus)
            .filter(UserKnowledgeStatus.user_id == student_id)
            .all()
        )
        status_map = {item.concept_id: item.status for item in records}
        time_map = {item.concept_id: item.update_time.isoformat() for item in records}
    else:
        records = list_learning_statuses(student_id)
        status_map = {item["concept_id"]: item["status"] for item in records}
        time_map = {item["concept_id"]: item["update_time"] for item in records}

    return [
        StudentLearningStatusSnapshot(
            concept_id=node.id,
            concept_name=node.name,
            status=status_map.get(node.id, 0),
            update_time=time_map.get(node.id, ""),
        )
        for node in graph.nodes
    ]


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


def _serialize_quick_reply_template(item: dict) -> QuickReplyTemplateItem:
    return QuickReplyTemplateItem(
        id=item["id"],
        title=item["title"],
        content=item["content"],
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


@router.get("/overview", response_model=TeacherOverviewResponse)
def get_teacher_overview(
    current_user: User | dict = Depends(require_roles("teacher")),
    db: Session = Depends(mysql_db.get_db),
    graph_service: GraphService = Depends(get_graph_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> TeacherOverviewResponse:
    teacher_id, teacher_class_id = _get_role_and_class(current_user)
    student_users = _list_student_users(db, teacher_class_id)
    progress_items: list[StudentProgressItem] = []
    graph = graph_service.get_full_graph()

    for student in student_users:
        user_id = student["id"] if isinstance(student, dict) else student.id
        overview = recommendation_service.build_overview(user_id=user_id, db=db)
        progress_items.append(_build_progress_item(student, overview))

    progress_items.sort(key=lambda item: (-item.progress_rate, item.username))
    tracked_student_ids = {item.user_id for item in progress_items}
    status_records = _load_all_status_records(tracked_student_ids, db)
    questions = [item for item in list_questions() if item["student_id"] in tracked_student_ids]
    question_count_by_student = Counter(item["student_id"] for item in questions)
    pending_question_count_by_student = Counter(item["student_id"] for item in questions if item["status"] == "pending")
    featured_question_count_by_student = Counter(item["student_id"] for item in questions if item.get("is_featured"))
    for item in progress_items:
        item.question_count = question_count_by_student.get(item.user_id, 0)
        item.pending_question_count = pending_question_count_by_student.get(item.user_id, 0)
        item.featured_question_count = featured_question_count_by_student.get(item.user_id, 0)

    concept_counter = Counter(item.get("concept_name") or "综合问题" for item in questions)
    concept_pending_counter = Counter((item.get("concept_name") or "综合问题") for item in questions if item["status"] == "pending")
    recent_questions = [_serialize_question(item, db, viewer_user_id=teacher_id) for item in questions[:30]]
    coordination_requests = [_serialize_coordination_request(item, db) for item in list_collaboration_requests(teacher_id=teacher_id)[:8]]
    quick_reply_templates = [_serialize_quick_reply_template(item) for item in list_quick_reply_templates(teacher_id)]
    graph_change_requests = [_serialize_graph_change_request(item, db) for item in list_graph_change_requests(teacher_id=teacher_id)[:12]]

    total_students = len(progress_items)
    average_progress_rate = round(sum(item.progress_rate for item in progress_items) / total_students) if total_students else 0
    mastered_concepts_total = sum(item.mastered_count for item in progress_items)
    pending_question_count = sum(1 for item in questions if item["status"] == "pending")
    answered_question_count = sum(1 for item in questions if item["status"] == "answered")
    featured_question_count = sum(1 for item in questions if item.get("is_featured"))

    class_overview = ClassOverviewMetrics(
        average_mastered_count=round(mastered_concepts_total / total_students, 1) if total_students else 0,
        top_asked_concepts=[
            ConceptQuestionStat(
                concept_name=concept_name,
                question_count=count,
                pending_count=concept_pending_counter.get(concept_name, 0),
            )
            for concept_name, count in concept_counter.most_common(5)
        ],
    )
    class_overviews = _build_class_overviews(
        students=student_users,
        progress_items=progress_items,
        graph=graph,
        status_records=status_records,
        questions=questions,
    )
    node_visits = [item for item in list_node_visits() if item["user_id"] in tracked_student_ids]
    learning_factor_analysis = _build_learning_factor_analysis(
        students=student_users,
        graph=graph,
        status_records=status_records,
        visits=node_visits,
    )
    node_learning_analysis = _build_node_learning_analysis(
        graph=graph,
        student_ids=tracked_student_ids,
        status_records=status_records,
        questions=questions,
        visits=node_visits,
    )

    return TeacherOverviewResponse(
        total_students=total_students,
        average_progress_rate=average_progress_rate,
        mastered_concepts_total=mastered_concepts_total,
        pending_question_count=pending_question_count,
        answered_question_count=answered_question_count,
        featured_question_count=featured_question_count,
        pending_coordination_count=sum(1 for item in coordination_requests if item.status != "resolved"),
        student_progress=progress_items,
        recent_questions=recent_questions,
        concept_question_stats=[
            ConceptQuestionStat(
                concept_name=concept_name,
                question_count=count,
                pending_count=concept_pending_counter.get(concept_name, 0),
            )
            for concept_name, count in concept_counter.most_common()
        ],
        coordination_requests=coordination_requests,
        class_overview=class_overview,
        class_overviews=class_overviews,
        learning_factor_analysis=learning_factor_analysis,
        node_learning_analysis=node_learning_analysis,
        quick_reply_templates=quick_reply_templates,
        graph_change_requests=graph_change_requests,
    )


@router.put("/questions/{question_id}/reply", response_model=QuestionItemResponse)
def answer_question(
    question_id: int,
    payload: QuestionReplyRequest,
    current_user: User | dict = Depends(require_roles("teacher")),
    db: Session = Depends(mysql_db.get_db),
) -> QuestionItemResponse:
    teacher_id, _ = _get_role_and_class(current_user)
    try:
        question = reply_question(question_id=question_id, teacher_id=teacher_id, reply=payload.teacher_reply)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _serialize_question(question, db, viewer_user_id=teacher_id)


@router.put("/questions/{question_id}/feature", response_model=QuestionItemResponse)
def feature_question(
    question_id: int,
    payload: QuestionFeatureRequest,
    current_user: User | dict = Depends(require_roles("teacher")),
    db: Session = Depends(mysql_db.get_db),
) -> QuestionItemResponse:
    teacher_id, _ = _get_role_and_class(current_user)
    questions = list_questions()
    question = next((item for item in questions if item["id"] == question_id), None)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    if payload.featured and not question.get("comments"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only answered questions can be featured.")

    try:
        updated_question = set_question_featured(question_id=question_id, teacher_id=teacher_id, featured=payload.featured)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if payload.featured:
        teacher_name = _display_name(current_user)
        create_notification(
            updated_question["student_id"],
            category="discussion",
            title="你的问题被教师置顶了",
            content=f"{teacher_name} 已将你在“{updated_question.get('concept_name') or '综合问题'}”下的讨论置顶，建议及时查看最新回复。",
            link=f"/graph?focus={updated_question.get('concept_id') or ''}",
        )
    return _serialize_question(updated_question, db, viewer_user_id=teacher_id)


@router.put("/comments/{comment_id}/feature", response_model=QuestionCommentItemResponse)
def feature_comment(
    comment_id: int,
    payload: CommentFeatureRequest,
    current_user: User | dict = Depends(require_roles("teacher")),
    db: Session = Depends(mysql_db.get_db),
) -> QuestionCommentItemResponse:
    try:
        comment = set_comment_excellent(comment_id=comment_id, is_excellent=payload.is_excellent)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    user_cache: dict[int, dict] = {}
    author_summary = _resolve_user_summary(comment.get("author_id"), db, user_cache)
    return QuestionCommentItemResponse(
        id=comment["id"],
        question_id=comment["question_id"],
        author_id=comment.get("author_id") or 0,
        author_name=author_summary["name"],
        author_role=comment.get("author_role") or author_summary["role"],
        content=comment["content"],
        create_time=comment["create_time"],
        like_count=len(comment.get("like_user_ids", [])),
        is_liked=False,
        is_excellent=comment.get("is_excellent", False),
        can_delete=False,
    )


@router.post("/coordination", response_model=CoordinationRequestItem, status_code=status.HTTP_201_CREATED)
def create_teacher_coordination_request(
    payload: CoordinationRequestCreateRequest,
    current_user: User | dict = Depends(require_roles("teacher")),
    db: Session = Depends(mysql_db.get_db),
) -> CoordinationRequestItem:
    teacher_id, _ = _get_role_and_class(current_user)
    item = create_collaboration_request(
        teacher_id=teacher_id,
        request_type=payload.type,
        title=payload.title,
        description=payload.description,
    )
    return _serialize_coordination_request(item, db)


@router.post("/graph-change-requests", response_model=GraphChangeRequestItem, status_code=status.HTTP_201_CREATED)
def create_teacher_graph_change_request(
    payload: GraphChangeRequestCreateRequest,
    current_user: User | dict = Depends(require_roles("teacher")),
    db: Session = Depends(mysql_db.get_db),
) -> GraphChangeRequestItem:
    teacher_id, _ = _get_role_and_class(current_user)
    item = create_graph_change_request(teacher_id, payload.model_dump())
    create_notification(
        teacher_id,
        category="graph",
        title="图谱变更申请已提交",
        content=f"你提交的“{item['summary']}”已进入图谱运维官审核队列。",
        link="/teacher",
    )
    return _serialize_graph_change_request(item, db)


@router.get("/concepts/{concept_id}/analytics", response_model=TeacherConceptAnalyticsResponse)
def get_teacher_concept_analytics(
    concept_id: str,
    current_user: User | dict = Depends(require_roles("teacher")),
    db: Session = Depends(mysql_db.get_db),
    graph_service: GraphService = Depends(get_graph_service),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> TeacherConceptAnalyticsResponse:
    teacher_id, teacher_class_id = _get_role_and_class(current_user)
    students = _list_student_users(db, teacher_class_id)
    student_ids = {_student_id(student) for student in students}
    graph = graph_service.get_full_graph()
    concept = next((node for node in graph.nodes if node.id == concept_id), None)
    if concept is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Concept not found.")

    progress_items: list[StudentProgressItem] = []
    progress_lookup: dict[int, StudentProgressItem] = {}
    for student in students:
        user_id = _student_id(student)
        overview = recommendation_service.build_overview(user_id=user_id, db=db)
        item = _build_progress_item(student, overview)
        progress_items.append(item)
        progress_lookup[user_id] = item

    status_records = _load_all_status_records(student_ids, db)
    status_map = {(item["user_id"], item["concept_id"]): item["status"] for item in status_records}
    class_buckets: dict[str, dict] = {}
    for student in students:
        class_name = _class_name_for_student(student)
        class_buckets.setdefault(
            class_name,
            {
                "class_id": _student_class_id(student),
                "student_ids": [],
                "students_by_status": {0: [], 1: [], 2: []},
            },
        )
        user_id = _student_id(student)
        class_buckets[class_name]["student_ids"].append(user_id)
        status_value = status_map.get((user_id, concept_id), 0)
        class_buckets[class_name]["students_by_status"][status_value].append(progress_lookup[user_id])

    class_stats: list[ConceptClassAnalyticsItem] = []
    for class_name, bucket in class_buckets.items():
        total = len(bucket["student_ids"])
        unlearned = len(bucket["students_by_status"][0])
        in_progress = len(bucket["students_by_status"][1])
        mastered = len(bucket["students_by_status"][2])
        class_stats.append(
            ConceptClassAnalyticsItem(
                class_id=bucket["class_id"],
                class_name=class_name,
                student_count=total,
                unlearned_count=unlearned,
                unlearned_percentage=_status_percentage(unlearned, total),
                in_progress_count=in_progress,
                in_progress_percentage=_status_percentage(in_progress, total),
                mastered_count=mastered,
                mastered_percentage=_status_percentage(mastered, total),
                students_unlearned=sorted(bucket["students_by_status"][0], key=lambda item: item.username),
                students_in_progress=sorted(bucket["students_by_status"][1], key=lambda item: item.username),
                students_mastered=sorted(bucket["students_by_status"][2], key=lambda item: item.username),
            )
        )

    visits = [item for item in list_node_visits(concept_id=concept_id) if item["user_id"] in student_ids]
    click_count = len(visits)
    duration_values = [item.get("duration_seconds", 0) for item in visits if item.get("duration_seconds", 0) > 0]
    average_learning_minutes = (
        round(sum(duration_values) / len(duration_values) / 60)
        if duration_values
        else 0
    )
    questions = [
        item
        for item in list_questions(concept_id=concept_id)
        if item["student_id"] in student_ids
    ]

    return TeacherConceptAnalyticsResponse(
        concept_id=concept.id,
        concept_name=concept.name,
        category=concept.category,
        click_count=click_count,
        average_learning_minutes=average_learning_minutes,
        question_count=len(questions),
        pending_question_count=sum(1 for item in questions if item["status"] == "pending"),
        featured_question_count=sum(1 for item in questions if item.get("is_featured")),
        class_stats=sorted(class_stats, key=lambda item: item.class_name),
        recent_questions=[_serialize_question(item, db, viewer_user_id=teacher_id) for item in questions[:8]],
    )


@router.get("/students/{student_id}/snapshot", response_model=StudentSnapshotResponse)
def get_student_snapshot(
    student_id: int,
    current_user: User | dict = Depends(require_roles("teacher")),
    db: Session = Depends(mysql_db.get_db),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    graph_service: GraphService = Depends(get_graph_service),
) -> StudentSnapshotResponse:
    _, teacher_class_id = _get_role_and_class(current_user)
    student_users = _list_student_users(db, teacher_class_id)
    student = next(
        (item for item in student_users if (item["id"] if isinstance(item, dict) else item.id) == student_id),
        None,
    )
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    overview = recommendation_service.build_overview(user_id=student_id, db=db)
    progress_item = _build_progress_item(student, overview)
    graph = graph_service.get_full_graph()
    concept_name_map = {node.id: node.name for node in graph.nodes}
    if mysql_db.database_mode != "json-fallback":
        status_records = (
            db.query(UserKnowledgeStatus)
            .filter(UserKnowledgeStatus.user_id == student_id)
            .order_by(UserKnowledgeStatus.update_time.desc())
            .all()
        )
        recent_statuses = [
            StudentLearningStatusSnapshot(
                concept_id=item.concept_id,
                concept_name=concept_name_map.get(item.concept_id, item.concept_id),
                status=item.status,
                update_time=item.update_time.isoformat(),
            )
            for item in status_records[:8]
        ]
    else:
        recent_statuses = [
            StudentLearningStatusSnapshot(
                concept_id=item["concept_id"],
                concept_name=concept_name_map.get(item["concept_id"], item["concept_id"]),
                status=item["status"],
                update_time=item["update_time"],
            )
            for item in sorted(list_learning_statuses(student_id), key=lambda record: record["update_time"], reverse=True)[:8]
        ]
    all_status_records = _list_student_status_snapshot_records(student_id, db, graph)
    weak_ids = {item.concept.id for item in overview.weak_points}
    student_questions = list_questions(student_id=student_id)
    pending_questions = [item for item in student_questions if item["status"] == "pending"]
    return StudentSnapshotResponse(
        student=progress_item,
        recent_statuses=recent_statuses,
        mastered_statuses=[item for item in all_status_records if item.status == 2],
        in_progress_statuses=[item for item in all_status_records if item.status == 1],
        unlearned_concepts=[item for item in all_status_records if item.status == 0],
        weak_statuses=[item for item in all_status_records if item.concept_id in weak_ids],
        recent_questions=[_serialize_question(item, db) for item in student_questions[:8]],
        pending_questions=[_serialize_question(item, db) for item in pending_questions[:8]],
        featured_answer_count=sum(1 for item in student_questions if item.get("is_featured")),
        total_question_count=len(student_questions),
        pending_question_count=sum(1 for item in student_questions if item["status"] == "pending"),
        answered_question_count=sum(1 for item in student_questions if item["status"] == "answered"),
    )


@router.post("/templates", response_model=QuickReplyTemplateItem, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: QuickReplyTemplateCreateRequest,
    current_user: User | dict = Depends(require_roles("teacher")),
) -> QuickReplyTemplateItem:
    teacher_id, _ = _get_role_and_class(current_user)
    item = create_quick_reply_template(teacher_id, payload.title, payload.content)
    return _serialize_quick_reply_template(item)


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    current_user: User | dict = Depends(require_roles("teacher")),
) -> None:
    teacher_id, _ = _get_role_and_class(current_user)
    try:
        delete_quick_reply_template(template_id, teacher_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/export/questions")
def export_teacher_questions_csv(
    current_user: User | dict = Depends(require_roles("teacher")),
    db: Session = Depends(mysql_db.get_db),
) -> Response:
    teacher_id, teacher_class_id = _get_role_and_class(current_user)
    student_users = _list_student_users(db, teacher_class_id)
    tracked_student_ids = {item["id"] if isinstance(item, dict) else item.id for item in student_users}
    questions = [item for item in list_questions() if item["student_id"] in tracked_student_ids]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "student_name",
            "concept_name",
            "title",
            "status",
            "comment_count",
            "is_featured",
            "create_time",
        ]
    )
    for item in questions:
        serialized = _serialize_question(item, db, viewer_user_id=teacher_id)
        writer.writerow(
            [
                serialized.student_name,
                serialized.concept_name or "",
                serialized.title,
                serialized.status,
                serialized.comment_count,
                "yes" if serialized.is_featured else "no",
                serialized.create_time,
            ]
        )

    filename = "teacher-class-question-stats.csv"
    csv_text = "\ufeff" + output.getvalue()
    return Response(
        content=csv_text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
