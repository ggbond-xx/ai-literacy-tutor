import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock

from app.core.security import get_password_hash

_store_lock = Lock()
_store_path = Path(__file__).resolve().parents[2] / "storage" / "app_state.json"


def _default_state() -> dict:
    return {
        "users": [],
        "learning_statuses": [],
        "questions": [],
        "collaboration_requests": [],
        "quiz_attempts": [],
        "node_visit_records": [],
        "notifications": [],
        "quick_reply_templates": [],
        "graph_change_requests": [],
        "graph_overrides": {
            "concepts": [],
            "relations": [],
            "relation_replacements": [],
        },
        "operation_logs": [],
        "recommendation_settings": {
            "recommendation_limit": 6,
            "weak_point_limit": 5,
            "path_limit": 6,
            "mastery_weight": 1.0,
            "in_progress_weight": 0.5,
        },
        "next_user_id": 1,
        "next_status_id": 1,
        "next_question_id": 1,
        "next_comment_id": 1,
        "next_collaboration_request_id": 1,
        "next_quiz_attempt_id": 1,
        "next_node_visit_id": 1,
        "next_notification_id": 1,
        "next_template_id": 1,
        "next_graph_change_request_id": 1,
        "next_operation_log_id": 1,
    }


def _normalize_profile_data(profile_data: dict | None, *, drop_empty: bool = True) -> dict | None:
    if not profile_data:
        return None

    normalized = {}
    for key, value in profile_data.items():
        if isinstance(value, str):
            value = value.strip()
            value = value or None
        normalized[key] = value

    if drop_empty and not any(value is not None for value in normalized.values()):
        return None
    return normalized


def _ensure_store() -> None:
    _store_path.parent.mkdir(parents=True, exist_ok=True)
    if not _store_path.exists():
        _store_path.write_text(json.dumps(_default_state(), ensure_ascii=False, indent=2), encoding="utf-8")


def _hydrate_state(state: dict) -> dict:
    defaults = _default_state()
    for key, value in defaults.items():
        if key not in state:
            state[key] = deepcopy(value)

    settings = state.get("recommendation_settings") or {}
    for key, value in defaults["recommendation_settings"].items():
        settings.setdefault(key, value)
    state["recommendation_settings"] = settings

    for question in state.get("questions", []):
        question.setdefault("is_featured", False)
        question.setdefault("featured_time", None)
        question.setdefault("featured_by", None)
        question.setdefault("favorite_user_ids", [])
        question.setdefault("comments", [])
        question.setdefault("legacy_reply_migrated", False)

        for comment in question["comments"]:
            comment.setdefault("like_user_ids", [])
            comment.setdefault("is_excellent", False)
            comment.setdefault("parent_comment_id", None)

        if question.get("teacher_reply") and not question["comments"] and not question.get("legacy_reply_migrated"):
            question["comments"].append(
                {
                    "id": state.get("next_comment_id", 1),
                    "question_id": question["id"],
                    "author_id": question.get("teacher_id"),
                    "author_role": "teacher",
                    "content": question["teacher_reply"],
                    "create_time": question.get("reply_time") or _now_iso(),
                    "parent_comment_id": None,
                    "like_user_ids": [],
                    "is_excellent": question.get("is_featured", False),
                }
            )
            state["next_comment_id"] = state.get("next_comment_id", 1) + 1
            question["legacy_reply_migrated"] = True

    for request in state.get("collaboration_requests", []):
        request.setdefault("status", "pending")
        request.setdefault("admin_reply", None)
        request.setdefault("handled_by", None)
        request.setdefault("update_time", request.get("create_time") or _now_iso())

    graph_overrides = state.setdefault("graph_overrides", {})
    graph_overrides.setdefault("concepts", [])
    graph_overrides.setdefault("relations", [])
    graph_overrides.setdefault("relation_replacements", [])

    for request in state.get("graph_change_requests", []):
        request.setdefault("status", "pending")
        request.setdefault("review_time", None)
        request.setdefault("reviewed_by", None)
        request.setdefault("review_note", None)
        request.setdefault("prerequisite_names", [])
        request.setdefault("next_names", [])
        request.setdefault("related_names", [])

    max_comment_id = 0
    for question in state.get("questions", []):
        for comment in question.get("comments", []):
            max_comment_id = max(max_comment_id, comment.get("id", 0))
    state["next_comment_id"] = max(state.get("next_comment_id", 1), max_comment_id + 1)
    max_request_id = max((item.get("id", 0) for item in state.get("collaboration_requests", [])), default=0)
    state["next_collaboration_request_id"] = max(state.get("next_collaboration_request_id", 1), max_request_id + 1)
    max_quiz_attempt_id = max((item.get("id", 0) for item in state.get("quiz_attempts", [])), default=0)
    state["next_quiz_attempt_id"] = max(state.get("next_quiz_attempt_id", 1), max_quiz_attempt_id + 1)
    for visit in state.get("node_visit_records", []):
        visit.setdefault("duration_seconds", 0)
        visit.setdefault("concept_name", None)
    max_node_visit_id = max((item.get("id", 0) for item in state.get("node_visit_records", [])), default=0)
    state["next_node_visit_id"] = max(state.get("next_node_visit_id", 1), max_node_visit_id + 1)
    max_notification_id = max((item.get("id", 0) for item in state.get("notifications", [])), default=0)
    state["next_notification_id"] = max(state.get("next_notification_id", 1), max_notification_id + 1)
    max_template_id = max((item.get("id", 0) for item in state.get("quick_reply_templates", [])), default=0)
    state["next_template_id"] = max(state.get("next_template_id", 1), max_template_id + 1)
    max_graph_change_request_id = max((item.get("id", 0) for item in state.get("graph_change_requests", [])), default=0)
    state["next_graph_change_request_id"] = max(
        state.get("next_graph_change_request_id", 1),
        max_graph_change_request_id + 1,
    )
    max_log_id = max((item.get("id", 0) for item in state.get("operation_logs", [])), default=0)
    state["next_operation_log_id"] = max(state.get("next_operation_log_id", 1), max_log_id + 1)
    return state


def _default_template_payloads() -> list[dict]:
    return [
        {
            "title": "先看学习材料",
            "content": "建议先查看当前节点学习材料中的核心要点和图示，再回来继续讨论你的疑问。",
        },
        {
            "title": "先完成自测题",
            "content": "建议先完成当前节点的自测题，看看具体卡在了哪一类题目，再带着结果继续提问。",
        },
        {
            "title": "回顾前置知识点",
            "content": "这个问题通常和前置知识点有关，建议先回顾当前节点的前置依赖，再继续推进学习。",
        },
    ]


def _ensure_default_quick_reply_templates(state: dict, teacher_id: int) -> None:
    existing = [item for item in state["quick_reply_templates"] if item["teacher_id"] == teacher_id]
    if existing:
        return

    now = _now_iso()
    for payload in _default_template_payloads():
        state["quick_reply_templates"].append(
            {
                "id": state["next_template_id"],
                "teacher_id": teacher_id,
                "title": payload["title"],
                "content": payload["content"],
                "create_time": now,
            }
        )
        state["next_template_id"] += 1


def _load_state() -> dict:
    _ensure_store()
    state = json.loads(_store_path.read_text(encoding="utf-8"))
    return _hydrate_state(state)


def _save_state(state: dict) -> None:
    _ensure_store()
    _store_path.write_text(json.dumps(_hydrate_state(state), ensure_ascii=False, indent=2), encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def get_user_by_username(username: str) -> dict | None:
    with _store_lock:
        state = _load_state()
        return next((user for user in state["users"] if user["username"] == username), None)


def get_user_by_id(user_id: int) -> dict | None:
    with _store_lock:
        state = _load_state()
        return next((user for user in state["users"] if user["id"] == user_id), None)


def list_users() -> list[dict]:
    with _store_lock:
        state = _load_state()
        return sorted(state["users"], key=lambda item: item["id"])


def create_user(payload: dict) -> dict:
    with _store_lock:
        state = _load_state()
        if any(user["username"] == payload["username"] for user in state["users"]):
            raise ValueError("Username already exists.")

        user = {
            "id": state["next_user_id"],
            "username": payload["username"],
            "password_hash": get_password_hash(payload["password"]),
            "role": payload.get("role", "student"),
            "class_id": payload.get("class_id"),
            "profile": _normalize_profile_data(payload.get("profile")),
        }
        state["users"].append(user)
        state["next_user_id"] += 1
        _save_state(state)
        return user


def update_user_profile(user_id: int, profile_data: dict) -> dict:
    with _store_lock:
        state = _load_state()
        user = next((item for item in state["users"] if item["id"] == user_id), None)
        if user is None:
            raise ValueError("User not found.")

        existing_profile = user.get("profile") or {}
        normalized_profile = _normalize_profile_data(profile_data, drop_empty=False) or {}
        merged_profile = {
            **existing_profile,
            **normalized_profile,
        }
        user["profile"] = _normalize_profile_data(merged_profile)
        _save_state(state)
        return user


def update_user_account(user_id: int, payload: dict) -> dict:
    with _store_lock:
        state = _load_state()
        user = next((item for item in state["users"] if item["id"] == user_id), None)
        if user is None:
            raise ValueError("User not found.")

        if "role" in payload and payload["role"]:
            user["role"] = payload["role"]
        if "class_id" in payload:
            user["class_id"] = payload["class_id"]
        if "password" in payload and payload["password"]:
            user["password_hash"] = get_password_hash(payload["password"])

        profile_payload = payload.get("profile")
        if profile_payload is not None:
            existing_profile = user.get("profile") or {}
            normalized_profile = _normalize_profile_data(profile_payload, drop_empty=False) or {}
            user["profile"] = _normalize_profile_data({**existing_profile, **normalized_profile})

        _save_state(state)
        return user


def list_learning_statuses(user_id: int) -> list[dict]:
    with _store_lock:
        state = _load_state()
        return [item for item in state["learning_statuses"] if item["user_id"] == user_id]


def list_all_learning_statuses() -> list[dict]:
    with _store_lock:
        state = _load_state()
        return list(state["learning_statuses"])


def upsert_learning_status(user_id: int, concept_id: str, status: int) -> dict:
    with _store_lock:
        state = _load_state()
        record = next(
            (
                item
                for item in state["learning_statuses"]
                if item["user_id"] == user_id and item["concept_id"] == concept_id
            ),
            None,
        )
        now = _now_iso()
        if record is None:
            record = {
                "id": state["next_status_id"],
                "user_id": user_id,
                "concept_id": concept_id,
                "status": status,
                "update_time": now,
            }
            state["learning_statuses"].append(record)
            state["next_status_id"] += 1
        else:
            record["status"] = status
            record["update_time"] = now

        _save_state(state)
        return record


def create_question(
    student_id: int,
    concept_id: str | None,
    concept_name: str | None,
    title: str,
    description: str,
) -> dict:
    with _store_lock:
        state = _load_state()
        question = {
            "id": state["next_question_id"],
            "student_id": student_id,
            "concept_id": concept_id,
            "concept_name": concept_name,
            "title": title.strip(),
            "description": description.strip(),
            "teacher_reply": None,
            "teacher_id": None,
            "status": "pending",
            "create_time": _now_iso(),
            "reply_time": None,
            "is_featured": False,
            "featured_time": None,
            "featured_by": None,
            "favorite_user_ids": [],
        }
        state["questions"].append(question)
        state["next_question_id"] += 1
        _save_state(state)
        return question


def _get_question_mutable(state: dict, question_id: int) -> dict | None:
    return next((item for item in state["questions"] if item["id"] == question_id), None)


def _get_comment_mutable(state: dict, comment_id: int) -> tuple[dict | None, dict | None]:
    for question in state["questions"]:
        comment = next((item for item in question.get("comments", []) if item["id"] == comment_id), None)
        if comment is not None:
            return question, comment
    return None, None


def list_questions(
    *,
    student_id: int | None = None,
    concept_id: str | None = None,
    status: str | None = None,
    featured_only: bool = False,
    favorite_user_id: int | None = None,
) -> list[dict]:
    with _store_lock:
        state = _load_state()
        questions = list(state["questions"])
        if student_id is not None:
            questions = [item for item in questions if item["student_id"] == student_id]
        if concept_id is not None:
            questions = [item for item in questions if item.get("concept_id") == concept_id]
        if status is not None:
            questions = [item for item in questions if item["status"] == status]
        if featured_only:
            questions = [item for item in questions if item.get("is_featured")]
        if favorite_user_id is not None:
            questions = [item for item in questions if favorite_user_id in item.get("favorite_user_ids", [])]
        return sorted(questions, key=lambda item: item["create_time"], reverse=True)


def get_question_by_id(question_id: int) -> dict | None:
    with _store_lock:
        state = _load_state()
        return next((item for item in state["questions"] if item["id"] == question_id), None)


def reply_question(question_id: int, teacher_id: int, reply: str) -> dict:
    with _store_lock:
        state = _load_state()
        question = _get_question_mutable(state, question_id)
        if question is None:
            raise ValueError("Question not found.")

        question["teacher_reply"] = reply.strip()
        question["teacher_id"] = teacher_id
        question["status"] = "answered"
        question["reply_time"] = _now_iso()

        if not question.get("legacy_reply_migrated"):
            question.setdefault("comments", []).append(
                {
                    "id": state["next_comment_id"],
                    "question_id": question_id,
                    "author_id": teacher_id,
                    "author_role": "teacher",
                    "content": reply.strip(),
                    "create_time": question["reply_time"],
                    "parent_comment_id": None,
                    "like_user_ids": [],
                    "is_excellent": question.get("is_featured", False),
                }
            )
            state["next_comment_id"] += 1
            question["legacy_reply_migrated"] = True
        _save_state(state)
        return question


def set_question_featured(question_id: int, teacher_id: int, featured: bool) -> dict:
    with _store_lock:
        state = _load_state()
        question = _get_question_mutable(state, question_id)
        if question is None:
            raise ValueError("Question not found.")

        question["is_featured"] = featured
        question["featured_by"] = teacher_id if featured else None
        question["featured_time"] = _now_iso() if featured else None
        _save_state(state)
        return question


def toggle_question_favorite(question_id: int, user_id: int) -> dict:
    with _store_lock:
        state = _load_state()
        question = _get_question_mutable(state, question_id)
        if question is None:
            raise ValueError("Question not found.")

        favorite_user_ids = question.setdefault("favorite_user_ids", [])
        if user_id in favorite_user_ids:
            favorite_user_ids.remove(user_id)
        else:
            favorite_user_ids.append(user_id)

        _save_state(state)
        return {
            "question_id": question_id,
            "is_favorited": user_id in favorite_user_ids,
            "favorite_count": len(favorite_user_ids),
        }


def create_question_comment(
    question_id: int,
    author_id: int,
    author_role: str,
    content: str,
    parent_comment_id: int | None = None,
) -> dict:
    with _store_lock:
        state = _load_state()
        question = _get_question_mutable(state, question_id)
        if question is None:
            raise ValueError("Question not found.")
        if parent_comment_id is not None:
            parent_comment = next(
                (item for item in question.get("comments", []) if item["id"] == parent_comment_id),
                None,
            )
            if parent_comment is None:
                raise ValueError("Parent comment not found.")

        comment = {
            "id": state["next_comment_id"],
            "question_id": question_id,
            "author_id": author_id,
            "author_role": author_role,
            "content": content.strip(),
            "create_time": _now_iso(),
            "parent_comment_id": parent_comment_id,
            "like_user_ids": [],
            "is_excellent": False,
        }
        question.setdefault("comments", []).append(comment)
        if author_role == "teacher":
            question["status"] = "answered"
            question["reply_time"] = comment["create_time"]
            question["teacher_id"] = author_id
            question["teacher_reply"] = content.strip()
        state["next_comment_id"] += 1
        _save_state(state)
        return deepcopy(comment)


def _collect_descendant_comment_ids(question: dict, comment_id: int) -> set[int]:
    descendants = {comment_id}
    changed = True
    while changed:
        changed = False
        for item in question.get("comments", []):
            if item.get("parent_comment_id") in descendants and item["id"] not in descendants:
                descendants.add(item["id"])
                changed = True
    return descendants


def delete_question_comment(comment_id: int, user_id: int | None = None, *, force: bool = False) -> None:
    with _store_lock:
        state = _load_state()
        question, comment = _get_comment_mutable(state, comment_id)
        if question is None or comment is None:
            raise ValueError("Comment not found.")
        if not force and comment.get("author_id") != user_id:
            raise PermissionError("Only the author can delete this comment.")

        remove_ids = _collect_descendant_comment_ids(question, comment_id)
        question["comments"] = [item for item in question.get("comments", []) if item["id"] not in remove_ids]
        _save_state(state)


def toggle_comment_like(comment_id: int, user_id: int) -> dict:
    with _store_lock:
        state = _load_state()
        _, comment = _get_comment_mutable(state, comment_id)
        if comment is None:
            raise ValueError("Comment not found.")
        if comment.get("author_id") == user_id:
            raise PermissionError("Authors cannot like their own comments.")

        like_user_ids = comment.setdefault("like_user_ids", [])
        if user_id in like_user_ids:
            like_user_ids.remove(user_id)
        else:
            like_user_ids.append(user_id)

        _save_state(state)
        return {
            "comment_id": comment_id,
            "is_liked": user_id in like_user_ids,
            "like_count": len(like_user_ids),
        }


def set_comment_excellent(comment_id: int, is_excellent: bool) -> dict:
    with _store_lock:
        state = _load_state()
        _, comment = _get_comment_mutable(state, comment_id)
        if comment is None:
            raise ValueError("Comment not found.")

        comment["is_excellent"] = is_excellent
        _save_state(state)
        return deepcopy(comment)


def delete_question(question_id: int) -> None:
    with _store_lock:
        state = _load_state()
        existing_count = len(state["questions"])
        state["questions"] = [item for item in state["questions"] if item["id"] != question_id]
        if len(state["questions"]) == existing_count:
            raise ValueError("Question not found.")
        _save_state(state)


def delete_user(user_id: int) -> None:
    with _store_lock:
        state = _load_state()
        if not any(user["id"] == user_id for user in state["users"]):
            raise ValueError("User not found.")

        state["users"] = [user for user in state["users"] if user["id"] != user_id]
        state["learning_statuses"] = [item for item in state["learning_statuses"] if item["user_id"] != user_id]
        state["questions"] = [item for item in state["questions"] if item["student_id"] != user_id]
        state["collaboration_requests"] = [item for item in state["collaboration_requests"] if item["teacher_id"] != user_id]
        state["quiz_attempts"] = [item for item in state["quiz_attempts"] if item["user_id"] != user_id]
        state["node_visit_records"] = [item for item in state["node_visit_records"] if item["user_id"] != user_id]
        state["notifications"] = [item for item in state["notifications"] if item["user_id"] != user_id]
        state["quick_reply_templates"] = [item for item in state["quick_reply_templates"] if item["teacher_id"] != user_id]
        state["graph_change_requests"] = [item for item in state["graph_change_requests"] if item["teacher_id"] != user_id]
        state["operation_logs"] = [item for item in state["operation_logs"] if item.get("actor_id") != user_id]

        for question in state["questions"]:
            question["favorite_user_ids"] = [item for item in question.get("favorite_user_ids", []) if item != user_id]
            question["comments"] = [item for item in question.get("comments", []) if item.get("author_id") != user_id]
            valid_comment_ids = {item["id"] for item in question.get("comments", [])}
            question["comments"] = [
                {
                    **item,
                    "like_user_ids": [like_user_id for like_user_id in item.get("like_user_ids", []) if like_user_id != user_id],
                    "parent_comment_id": item.get("parent_comment_id") if item.get("parent_comment_id") in valid_comment_ids else None,
                }
                for item in question.get("comments", [])
            ]

        _save_state(state)


def list_collaboration_requests(*, teacher_id: int | None = None, status: str | None = None) -> list[dict]:
    with _store_lock:
        state = _load_state()
        items = list(state["collaboration_requests"])
        if teacher_id is not None:
            items = [item for item in items if item["teacher_id"] == teacher_id]
        if status is not None:
            items = [item for item in items if item["status"] == status]
        return sorted(items, key=lambda item: item["create_time"], reverse=True)


def create_collaboration_request(teacher_id: int, request_type: str, title: str, description: str) -> dict:
    with _store_lock:
        state = _load_state()
        now = _now_iso()
        item = {
            "id": state["next_collaboration_request_id"],
            "teacher_id": teacher_id,
            "type": request_type.strip(),
            "title": title.strip(),
            "description": description.strip(),
            "status": "pending",
            "admin_reply": None,
            "create_time": now,
            "update_time": now,
            "handled_by": None,
        }
        state["collaboration_requests"].append(item)
        state["next_collaboration_request_id"] += 1
        _save_state(state)
        return deepcopy(item)


def update_collaboration_request(request_id: int, *, status: str, admin_reply: str | None, handled_by: int) -> dict:
    with _store_lock:
        state = _load_state()
        item = next((entry for entry in state["collaboration_requests"] if entry["id"] == request_id), None)
        if item is None:
            raise ValueError("Coordination request not found.")

        item["status"] = status
        item["admin_reply"] = admin_reply.strip() if isinstance(admin_reply, str) and admin_reply.strip() else None
        item["handled_by"] = handled_by
        item["update_time"] = _now_iso()
        _save_state(state)
        return deepcopy(item)


def get_recommendation_settings() -> dict:
    with _store_lock:
        state = _load_state()
        return dict(state["recommendation_settings"])


def update_recommendation_settings(payload: dict) -> dict:
    with _store_lock:
        state = _load_state()
        settings = state["recommendation_settings"]
        for key, value in payload.items():
            if value is not None:
                settings[key] = value
        state["recommendation_settings"] = settings
        _save_state(state)
        return dict(settings)


def create_notification(
    user_id: int,
    *,
    category: str,
    title: str,
    content: str,
    link: str | None = None,
) -> dict:
    with _store_lock:
        state = _load_state()
        notification = {
            "id": state["next_notification_id"],
            "user_id": user_id,
            "category": category,
            "title": title.strip(),
            "content": content.strip(),
            "link": link,
            "is_read": False,
            "create_time": _now_iso(),
        }
        state["notifications"].append(notification)
        state["next_notification_id"] += 1
        _save_state(state)
        return deepcopy(notification)


def list_notifications(user_id: int, *, unread_only: bool = False) -> list[dict]:
    with _store_lock:
        state = _load_state()
        items = [item for item in state["notifications"] if item["user_id"] == user_id]
        if unread_only:
            items = [item for item in items if not item.get("is_read")]
        return sorted(items, key=lambda item: item["create_time"], reverse=True)


def mark_notification_read(notification_id: int, user_id: int) -> dict:
    with _store_lock:
        state = _load_state()
        item = next(
            (entry for entry in state["notifications"] if entry["id"] == notification_id and entry["user_id"] == user_id),
            None,
        )
        if item is None:
            raise ValueError("Notification not found.")
        item["is_read"] = True
        _save_state(state)
        return deepcopy(item)


def mark_all_notifications_read(user_id: int) -> int:
    with _store_lock:
        state = _load_state()
        count = 0
        for item in state["notifications"]:
            if item["user_id"] == user_id and not item.get("is_read"):
                item["is_read"] = True
                count += 1
        _save_state(state)
        return count


def list_quick_reply_templates(teacher_id: int) -> list[dict]:
    with _store_lock:
        state = _load_state()
        _ensure_default_quick_reply_templates(state, teacher_id)
        _save_state(state)
        items = [item for item in state["quick_reply_templates"] if item["teacher_id"] == teacher_id]
        return sorted(items, key=lambda item: item["create_time"])


def create_quick_reply_template(teacher_id: int, title: str, content: str) -> dict:
    with _store_lock:
        state = _load_state()
        template = {
            "id": state["next_template_id"],
            "teacher_id": teacher_id,
            "title": title.strip(),
            "content": content.strip(),
            "create_time": _now_iso(),
        }
        state["quick_reply_templates"].append(template)
        state["next_template_id"] += 1
        _save_state(state)
        return deepcopy(template)


def delete_quick_reply_template(template_id: int, teacher_id: int) -> None:
    with _store_lock:
        state = _load_state()
        existing_count = len(state["quick_reply_templates"])
        state["quick_reply_templates"] = [
            item
            for item in state["quick_reply_templates"]
            if not (item["id"] == template_id and item["teacher_id"] == teacher_id)
        ]
        if len(state["quick_reply_templates"]) == existing_count:
            raise ValueError("Quick reply template not found.")
        _save_state(state)


def _clean_string_list(items: list[str] | None, *, limit: int = 12) -> list[str]:
    cleaned: list[str] = []
    for item in items or []:
        if not isinstance(item, str):
            continue
        value = item.strip()
        if value and value not in cleaned:
            cleaned.append(value)
        if len(cleaned) >= limit:
            break
    return cleaned


def _normalize_graph_node_payload(payload: dict) -> dict:
    node = deepcopy(payload)
    for key in ("name", "description", "category", "text_material", "image_url", "video_title", "video_url", "practice_task"):
        if key in node and isinstance(node[key], str):
            node[key] = node[key].strip() or None

    node["name"] = node.get("name") or "未命名知识点"
    for key in ("key_points", "study_tips", "common_mistakes"):
        node[key] = _clean_string_list(node.get(key), limit=8)

    resource_links = []
    for item in node.get("resource_links") or []:
        label = (item.get("label") or "").strip()
        url = (item.get("url") or "").strip()
        if label and url:
            resource_links.append({"label": label, "url": url})
    node["resource_links"] = resource_links[:8]

    quiz = []
    for item in node.get("quiz") or []:
        question = (item.get("question") or "").strip()
        options = _clean_string_list(item.get("options"), limit=6)
        explanation = (item.get("explanation") or "").strip()
        answer_index = item.get("answer_index", 0)
        if question and len(options) >= 2 and isinstance(answer_index, int) and 0 <= answer_index < len(options):
            quiz.append(
                {
                    "question": question,
                    "options": options,
                    "answer_index": answer_index,
                    "explanation": explanation or "请结合知识梳理与学习材料复盘本题。",
                }
            )
    node["quiz"] = quiz[:12]
    return node


def _build_graph_change_relations(item: dict) -> list[dict]:
    node_name = item["node"]["name"]
    relations = []
    for name in _clean_string_list(item.get("prerequisite_names"), limit=12):
        if name != node_name:
            relations.append({"source_name": name, "target_name": node_name, "type": "PREREQUISITE_OF"})
    for name in _clean_string_list(item.get("next_names"), limit=12):
        if name != node_name:
            relations.append({"source_name": node_name, "target_name": name, "type": "PREREQUISITE_OF"})
    for name in _clean_string_list(item.get("related_names"), limit=12):
        if name != node_name:
            relations.append({"source_name": node_name, "target_name": name, "type": "RELATED_TO"})
    return relations


def _apply_graph_change_request(state: dict, item: dict) -> None:
    overrides = state.setdefault("graph_overrides", {"concepts": [], "relations": []})
    concepts = overrides.setdefault("concepts", [])
    relations = overrides.setdefault("relations", [])
    relation_replacements = overrides.setdefault("relation_replacements", [])
    node = {
        **_normalize_graph_node_payload(item["node"]),
        "origin": "approved",
        "approved_request_id": item["id"],
        "approved_time": _now_iso(),
    }
    node_name = node["name"]
    if node_name not in relation_replacements:
        relation_replacements.append(node_name)

    existing_node = next((entry for entry in concepts if entry.get("name") == node_name), None)
    if existing_node is None:
        concepts.append(node)
    else:
        existing_node.update(node)

    relation_keys_to_replace = {
        (entry.get("source_name"), entry.get("target_name"), entry.get("type"))
        for entry in relations
        if entry.get("source_name") == node_name or entry.get("target_name") == node_name
    }
    new_relations = _build_graph_change_relations(item)
    new_relation_keys = {
        (entry["source_name"], entry["target_name"], entry["type"])
        for entry in new_relations
    }
    relations[:] = [
        entry
        for entry in relations
        if (entry.get("source_name"), entry.get("target_name"), entry.get("type")) not in relation_keys_to_replace
        and (entry.get("source_name"), entry.get("target_name"), entry.get("type")) not in new_relation_keys
    ]
    relations.extend(new_relations)


def get_graph_overrides() -> dict:
    with _store_lock:
        state = _load_state()
        return deepcopy(state.get("graph_overrides", {"concepts": [], "relations": []}))


def list_graph_change_requests(*, teacher_id: int | None = None, status: str | None = None) -> list[dict]:
    with _store_lock:
        state = _load_state()
        items = list(state["graph_change_requests"])
        if teacher_id is not None:
            items = [item for item in items if item["teacher_id"] == teacher_id]
        if status is not None:
            items = [item for item in items if item["status"] == status]
        return sorted(items, key=lambda item: item["create_time"], reverse=True)


def create_graph_change_request(teacher_id: int, payload: dict) -> dict:
    with _store_lock:
        state = _load_state()
        node = _normalize_graph_node_payload(payload["node"])
        item = {
            "id": state["next_graph_change_request_id"],
            "teacher_id": teacher_id,
            "action": payload.get("action", "update_node"),
            "summary": payload["summary"].strip(),
            "target_concept_name": (payload.get("target_concept_name") or node["name"]).strip(),
            "node": node,
            "prerequisite_names": _clean_string_list(payload.get("prerequisite_names"), limit=12),
            "next_names": _clean_string_list(payload.get("next_names"), limit=12),
            "related_names": _clean_string_list(payload.get("related_names"), limit=12),
            "status": "pending",
            "create_time": _now_iso(),
            "review_time": None,
            "reviewed_by": None,
            "review_note": None,
        }
        state["graph_change_requests"].append(item)
        state["next_graph_change_request_id"] += 1
        _save_state(state)
        return deepcopy(item)


def review_graph_change_request(request_id: int, *, status: str, review_note: str | None, reviewed_by: int) -> dict:
    with _store_lock:
        state = _load_state()
        item = next((entry for entry in state["graph_change_requests"] if entry["id"] == request_id), None)
        if item is None:
            raise ValueError("Graph change request not found.")
        if item["status"] != "pending":
            raise ValueError("Graph change request has already been reviewed.")
        if status not in {"approved", "rejected"}:
            raise ValueError("Invalid review status.")

        item["status"] = status
        item["review_time"] = _now_iso()
        item["reviewed_by"] = reviewed_by
        item["review_note"] = review_note.strip() if isinstance(review_note, str) and review_note.strip() else None
        if status == "approved":
            _apply_graph_change_request(state, item)

        _save_state(state)
        return deepcopy(item)


def create_quiz_attempt(
    user_id: int,
    *,
    concept_id: str,
    concept_name: str,
    total_questions: int,
    correct_answers: int,
    score: int,
) -> dict:
    with _store_lock:
        state = _load_state()
        wrong_answers = max(total_questions - correct_answers, 0)
        attempt = {
            "id": state["next_quiz_attempt_id"],
            "user_id": user_id,
            "concept_id": concept_id,
            "concept_name": concept_name.strip(),
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers,
            "accuracy": round(correct_answers / total_questions, 4) if total_questions else 0.0,
            "score": score,
            "create_time": _now_iso(),
        }
        state["quiz_attempts"].append(attempt)
        state["next_quiz_attempt_id"] += 1
        _save_state(state)
        return deepcopy(attempt)


def list_quiz_attempts(user_id: int, *, concept_id: str | None = None) -> list[dict]:
    with _store_lock:
        state = _load_state()
        items = [item for item in state["quiz_attempts"] if item["user_id"] == user_id]
        if concept_id is not None:
            items = [item for item in items if item["concept_id"] == concept_id]
        return sorted(items, key=lambda item: item["create_time"], reverse=True)


def record_node_visit(
    user_id: int,
    *,
    concept_id: str,
    concept_name: str | None = None,
    duration_seconds: int | None = None,
) -> dict:
    with _store_lock:
        state = _load_state()
        duration = max(int(duration_seconds or 0), 0)
        item = {
            "id": state["next_node_visit_id"],
            "user_id": user_id,
            "concept_id": concept_id,
            "concept_name": concept_name,
            "duration_seconds": duration,
            "create_time": _now_iso(),
        }
        state["node_visit_records"].append(item)
        state["next_node_visit_id"] += 1
        _save_state(state)
        return deepcopy(item)


def list_node_visits(*, concept_id: str | None = None, user_id: int | None = None) -> list[dict]:
    with _store_lock:
        state = _load_state()
        items = list(state["node_visit_records"])
        if concept_id is not None:
            items = [item for item in items if item["concept_id"] == concept_id]
        if user_id is not None:
            items = [item for item in items if item["user_id"] == user_id]
        return sorted(items, key=lambda item: item["create_time"], reverse=True)


def create_operation_log(
    *,
    actor_id: int,
    actor_name: str,
    actor_role: str,
    action: str,
    target_type: str,
    target_id: str | None,
    description: str,
) -> dict:
    with _store_lock:
        state = _load_state()
        item = {
            "id": state["next_operation_log_id"],
            "actor_id": actor_id,
            "actor_name": actor_name,
            "actor_role": actor_role,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "description": description,
            "create_time": _now_iso(),
        }
        state["operation_logs"].append(item)
        state["next_operation_log_id"] += 1
        _save_state(state)
        return deepcopy(item)


def list_operation_logs(limit: int | None = None) -> list[dict]:
    with _store_lock:
        state = _load_state()
        items = sorted(state["operation_logs"], key=lambda item: item["create_time"], reverse=True)
        if limit is not None:
            return items[:limit]
        return items
