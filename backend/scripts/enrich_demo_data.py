from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from app.core.security import get_password_hash, verify_password
from app.db import mysql as mysql_db
from app.db.mysql import SessionLocal, engine, init_db
from app.db.neo4j import driver as neo4j_driver
from app.models.user import User
from app.models.user_knowledge_status import UserKnowledgeStatus
from app.models.user_profile import UserProfile
from app.services.graph_catalog import get_graph_catalog
from app.services.graph_service import GraphService
from app.services.json_store import _default_state, _save_state


PASSWORD = "test"
SCHOOL_NAME = "数字素养实验大学"
NOW = datetime.now(UTC)

CLASS_SPECS = {
    101: "人工智能与数字素养一班",
    102: "人工智能与数字素养二班",
    103: "人工智能与数字素养三班",
}

STUDENTS = [
    ("stu1", "test_stu1", "林语知", 101, "人工智能教育", "基础概念掌握较好，正在进入机器学习模块。"),
    ("stu2", "test_stu2", "周晴岚", 101, "数字媒体技术", "擅长信息甄别和生成式 AI 案例分析。"),
    ("stu3", "test_stu3", "乔沐云", 101, "教育技术学", "关注大模型、自然语言处理和项目复盘。"),
    ("stu4", "test_stu4", "许知远", 102, "计算机科学与技术", "算法基础较稳，监督学习和模型评估需要继续推进。"),
    ("stu5", "test_stu5", "沈若溪", 102, "智能科学与技术", "提示词设计活跃，喜欢在论坛中补充案例。"),
    ("stu6", "test_stu6", "唐以宁", 102, "数据科学与大数据技术", "数据素养较好，但机器学习评价指标容易混淆。"),
    ("stu7", "test_stu7", "顾星野", 103, "软件工程", "项目实践积极，基础概念和数据清洗仍需补齐。"),
    ("stu8", "test_stu8", "叶南栀", 103, "网络空间安全", "数字安全与事实核验掌握较好，AI 模型部分较薄弱。"),
    ("stu9", "test_stu9", "陆景和", 103, "信息管理与信息系统", "刚开始系统学习，提问集中在学习路径和基础节点。"),
]

STUDENT_DEMOGRAPHICS = {
    "stu1": {"gender": "女", "age": "19"},
    "stu2": {"gender": "男", "age": "20"},
    "stu3": {"gender": "女", "age": "19"},
    "stu4": {"gender": "男", "age": "21"},
    "stu5": {"gender": "女", "age": "20"},
    "stu6": {"gender": "男", "age": "21"},
    "stu7": {"gender": "女", "age": "22"},
    "stu8": {"gender": "男", "age": "22"},
    "stu9": {"gender": "女", "age": "18"},
}

TEACHERS = [
    ("tea1", "test_tea1", "王清禾", 101, "人工智能课程教学", "负责基础概念、算法思维和机器学习模块。"),
    ("tea2", "test_tea2", "李明舟", 102, "生成式AI应用教学", "负责提示词设计、生成式 AI 和项目实践模块。"),
    ("tea3", "test_tea3", "孙睿安", 103, "AI伦理与治理", "负责伦理素养、数字安全和课程治理模块。"),
]

ADMINS = [
    ("adm1", "test_adm1", "陈曦", None, "平台治理", "负责账号治理、推荐参数和图谱审核发布。"),
    ("adm2", "test_adm2", "赵南一", None, "内容运维", "负责讨论治理、图谱内容审核和教师协同事项。"),
    ("adm3", "test_adm3", "何钧远", None, "系统支持", "负责系统日志、演示环境和问题排查。"),
]


def iso(*, days: int = 0, hours: int = 0, minutes: int = 0) -> str:
    return (NOW - timedelta(days=days, hours=hours, minutes=minutes)).isoformat()


def dt(*, days: int = 0, hours: int = 0, minutes: int = 0) -> datetime:
    return NOW - timedelta(days=days, hours=hours, minutes=minutes)


def build_concept_map() -> dict[str, str]:
    try:
        graph = GraphService(neo4j_driver).get_full_graph()
        concept_map = {node.name: node.id for node in graph.nodes}
        if concept_map:
            return concept_map
    except Exception as exc:
        print(f"Neo4j 图谱读取失败，改用课程目录 ID 生成演示数据: {exc}")

    concepts, _ = get_graph_catalog()
    return {item["name"]: f"catalog:{item['slug']}" for item in concepts}


def account_specs() -> list[dict]:
    specs = []
    for index, (key, username, real_name, class_id, major, bio) in enumerate(STUDENTS, start=1):
        demographic = STUDENT_DEMOGRAPHICS[key]
        specs.append(
            {
                "key": key,
                "username": username,
                "role": "student",
                "class_id": class_id,
                "profile": {
                    "real_name": real_name,
                    "email": f"{username}@example.com",
                    "school": SCHOOL_NAME,
                    "major": major,
                    "grade": "2023级" if class_id != 103 else "2022级",
                    "student_no": f"S2026{index:04d}",
                    "class_name": CLASS_SPECS[class_id],
                    "bio": bio,
                    "gender": demographic["gender"],
                    "age": demographic["age"],
                },
            }
        )
    for index, (key, username, real_name, class_id, major, bio) in enumerate(TEACHERS, start=1):
        specs.append(
            {
                "key": key,
                "username": username,
                "role": "teacher",
                "class_id": class_id,
                "profile": {
                    "real_name": real_name,
                    "email": f"{username}@example.com",
                    "school": SCHOOL_NAME,
                    "major": major,
                    "grade": "教师",
                    "student_no": f"T2026{index:03d}",
                    "class_name": CLASS_SPECS[class_id],
                    "bio": bio,
                },
            }
        )
    for index, (key, username, real_name, class_id, major, bio) in enumerate(ADMINS, start=1):
        specs.append(
            {
                "key": key,
                "username": username,
                "role": "admin",
                "class_id": class_id,
                "profile": {
                    "real_name": real_name,
                    "email": f"{username}@example.com",
                    "school": SCHOOL_NAME,
                    "major": major,
                    "grade": "图谱运维官",
                    "student_no": f"A2026{index:03d}",
                    "class_name": "图谱运维组",
                    "bio": bio,
                },
            }
        )
    return specs


def truncate_mysql_tables() -> None:
    if mysql_db.database_mode == "json-fallback":
        return
    try:
        with engine.begin() as conn:
            tables = [row[0] for row in conn.execute(text("SHOW TABLES")).fetchall()]
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            for table_name in tables:
                conn.execute(text(f"TRUNCATE TABLE `{table_name}`"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    except SQLAlchemyError as exc:
        print(f"MySQL 清表失败，将继续写入 JSON fallback 演示数据: {exc}")


def create_mysql_users(session: Session) -> dict[str, dict]:
    created = {}
    for spec in account_specs():
        password_hash = get_password_hash(PASSWORD)
        created[spec["key"]] = {
            "id": len(created) + 1,
            "username": spec["username"],
            "role": spec["role"],
            "class_id": spec["class_id"],
            "password_hash": password_hash,
            "profile": dict(spec["profile"]),
        }
        if mysql_db.database_mode == "json-fallback":
            continue

        user = User(
            username=spec["username"],
            password_hash=password_hash,
            role=spec["role"],
            class_id=spec["class_id"],
        )
        session.add(user)
        session.flush()
        mysql_profile_fields = {
            key: value
            for key, value in spec["profile"].items()
            if key in {"real_name", "email", "school", "major", "grade", "student_no", "class_name", "bio"}
        }
        session.add(UserProfile(user_id=user.id, **mysql_profile_fields))
        created[spec["key"]]["id"] = user.id
    if mysql_db.database_mode != "json-fallback":
        session.commit()
    return created


STATUS_PLAN = {
    "stu1": {"人工智能基础": 2, "算法思维": 2, "数据素养": 2, "数据采集与清洗": 2, "机器学习": 1, "监督学习": 1, "模型评估": 0, "提示词设计": 1},
    "stu2": {"人工智能基础": 2, "数据素养": 2, "信息甄别与数字安全": 2, "提示词设计": 1, "生成式AI应用": 1, "AI幻觉与事实核验": 0, "数字版权与学术规范": 0},
    "stu3": {"人工智能基础": 2, "算法思维": 2, "机器学习": 2, "神经网络基础": 1, "自然语言处理": 1, "大模型基础": 0, "AI项目式学习": 0, "AI伦理与治理": 1},
    "stu4": {"人工智能基础": 2, "算法思维": 2, "数据素养": 1, "机器学习": 1, "监督学习": 1, "模型评估": 0, "特征工程": 0},
    "stu5": {"人工智能基础": 2, "提示词设计": 2, "生成式AI应用": 2, "人机协同实践": 1, "AI幻觉与事实核验": 1, "数字版权与学术规范": 0},
    "stu6": {"人工智能基础": 2, "数据素养": 2, "开源数据集检索": 2, "数据采集与清洗": 1, "特征工程": 1, "机器学习": 0, "模型评估": 0},
    "stu7": {"人工智能基础": 1, "算法思维": 1, "提示词设计": 1, "生成式AI应用": 1, "AI项目式学习": 1, "机器学习": 0, "数据采集与清洗": 0},
    "stu8": {"人工智能基础": 2, "信息甄别与数字安全": 2, "AI幻觉与事实核验": 2, "AI伦理与治理": 1, "数字版权与学术规范": 1, "机器学习": 0, "神经网络基础": 0},
    "stu9": {"人工智能基础": 1, "算法思维": 0, "数据素养": 0, "提示词设计": 0, "机器学习": 0, "生成式AI应用": 0},
}


def seed_learning_statuses(session: Session, users: dict[str, dict], concept_map: dict[str, str]) -> list[dict]:
    statuses = []
    next_id = 1
    for user_key, concepts in STATUS_PLAN.items():
        for offset, (concept_name, status) in enumerate(concepts.items(), start=1):
            if concept_name not in concept_map:
                continue
            item = {
                "id": next_id,
                "user_id": users[user_key]["id"],
                "concept_id": concept_map[concept_name],
                "status": status,
                "update_time": iso(days=8 - min(offset, 7), hours=offset),
            }
            statuses.append(item)
            if mysql_db.database_mode != "json-fallback":
                session.add(
                    UserKnowledgeStatus(
                        user_id=item["user_id"],
                        concept_id=item["concept_id"],
                        status=status,
                        update_time=dt(days=8 - min(offset, 7), hours=offset),
                    )
                )
            next_id += 1
    if mysql_db.database_mode != "json-fallback":
        session.commit()
    return statuses


def make_quiz_attempts(users: dict[str, dict], concept_map: dict[str, str]) -> list[dict]:
    specs = [
        ("stu1", "机器学习", 72), ("stu1", "提示词设计", 84), ("stu1", "模型评估", 58),
        ("stu2", "生成式AI应用", 80), ("stu2", "AI幻觉与事实核验", 55),
        ("stu3", "神经网络基础", 66), ("stu3", "自然语言处理", 76), ("stu3", "大模型基础", 49),
        ("stu4", "监督学习", 70), ("stu4", "模型评估", 52),
        ("stu5", "生成式AI应用", 91), ("stu5", "人机协同实践", 78),
        ("stu6", "数据采集与清洗", 75), ("stu6", "机器学习", 48),
        ("stu7", "AI项目式学习", 69), ("stu7", "算法思维", 60),
        ("stu8", "AI幻觉与事实核验", 88), ("stu8", "AI伦理与治理", 74),
        ("stu9", "人工智能基础", 56), ("stu9", "算法思维", 42),
    ]
    attempts = []
    for index, (user_key, concept_name, score) in enumerate(specs, start=1):
        correct = max(0, min(10, round(score / 10)))
        attempts.append(
            {
                "id": index,
                "user_id": users[user_key]["id"],
                "concept_id": concept_map[concept_name],
                "concept_name": concept_name,
                "total_questions": 10,
                "correct_answers": correct,
                "wrong_answers": 10 - correct,
                "accuracy": round(correct / 10, 4),
                "score": score,
                "create_time": iso(days=(index % 5) + 1, hours=index),
            }
        )
    return attempts


def build_questions(users: dict[str, dict], concept_map: dict[str, str]) -> tuple[list[dict], int]:
    questions = []
    next_comment_id = 1

    def question(qid, student, concept, title, description, day, teacher=None, featured=False, favorites=None):
        nonlocal next_comment_id
        item = {
            "id": qid,
            "student_id": users[student]["id"],
            "concept_id": concept_map[concept],
            "concept_name": concept,
            "title": title,
            "description": description,
            "teacher_reply": None,
            "teacher_id": users[teacher]["id"] if teacher else None,
            "status": "answered" if teacher else "pending",
            "create_time": iso(days=day, hours=qid),
            "reply_time": iso(days=max(day - 1, 0), hours=qid) if teacher else None,
            "is_featured": featured,
            "featured_time": iso(days=max(day - 1, 0), hours=qid + 1) if featured else None,
            "featured_by": users[teacher]["id"] if featured and teacher else None,
            "favorite_user_ids": [users[key]["id"] for key in (favorites or [])],
            "comments": [],
            "legacy_reply_migrated": bool(teacher),
        }
        if teacher:
            reply = f"建议先回到“{concept}”节点的知识梳理和前置依赖，再结合自测错题定位具体薄弱点。"
            item["teacher_reply"] = reply
            item["comments"].append(
                {
                    "id": next_comment_id,
                    "question_id": qid,
                    "author_id": users[teacher]["id"],
                    "author_role": "teacher",
                    "content": reply,
                    "create_time": item["reply_time"],
                    "parent_comment_id": None,
                    "like_user_ids": [users[key]["id"] for key in (favorites or [])[:3]],
                    "is_excellent": featured,
                }
            )
            parent_id = next_comment_id
            next_comment_id += 1
            item["comments"].append(
                {
                    "id": next_comment_id,
                    "question_id": qid,
                    "author_id": users[student]["id"],
                    "author_role": "student",
                    "content": "收到，我会按这个思路补充笔记并重新完成自测。",
                    "create_time": iso(days=max(day - 1, 0), hours=qid + 2),
                    "parent_comment_id": parent_id,
                    "like_user_ids": [],
                    "is_excellent": False,
                }
            )
            next_comment_id += 1
        questions.append(item)

    question(1, "stu1", "机器学习", "监督学习和无监督学习该怎么区分？", "分类、回归、聚类和模型评估经常混在一起。", 4, "tea1", True, ["stu2", "stu3", "stu4"])
    question(2, "stu2", "AI幻觉与事实核验", "为什么生成式 AI 会编造看似真实的来源？", "做资料核验时不知道该优先检查哪些线索。", 3, "tea3", True, ["stu5", "stu8"])
    question(3, "stu3", "大模型基础", "上下文窗口和参数规模有什么区别？", "这两个概念都和能力有关，但解释时容易混淆。", 3, None)
    question(4, "stu4", "模型评估", "准确率和召回率什么时候看哪个？", "想结合教育场景理解漏判和误判的差异。", 2, "tea1", False)
    question(5, "stu5", "提示词设计", "链式提示在课程作业里怎么展示？", "希望把提示过程写进作业记录，但不知道粒度。", 2, "tea2", False)
    question(6, "stu6", "数据采集与清洗", "缺失值一定要删除吗？", "清洗数据时不知道删除、填充和保留怎么选。", 2, None)
    question(7, "stu7", "AI项目式学习", "项目复盘要写失败尝试吗？", "担心写失败过程会影响项目展示效果。", 1, "tea2", True, ["stu1", "stu5", "stu9"])
    question(8, "stu8", "数字版权与学术规范", "AI 生成图片能不能直接放进报告？", "不知道版权、标注和引用应该怎么处理。", 1, "tea3", False)
    question(9, "stu9", "人工智能基础", "我应该从哪个节点开始补基础？", "图谱节点很多，希望知道第一周如何安排学习。", 1, None)
    question(10, "stu6", "机器学习", "特征工程和模型训练哪个更重要？", "自测题里总把数据准备和模型选择分不开。", 1, "tea1", False)
    question(11, "stu4", "监督学习", "分类任务和回归任务能不能用同一套指标？", "教材里的指标很多，想知道最核心区别。", 0, None)
    question(12, "stu8", "信息甄别与数字安全", "如何判断一个 AI 工具是否安全？", "除了看隐私政策，还应该检查哪些方面？", 0, "tea3", True, ["stu2", "stu7"])
    return questions, next_comment_id


def make_node_visits(users: dict[str, dict], concept_map: dict[str, str]) -> list[dict]:
    hot_nodes = [
        ("人工智能基础", 18, 12), ("算法思维", 12, 18), ("机器学习", 26, 38),
        ("模型评估", 15, 42), ("提示词设计", 22, 25), ("生成式AI应用", 20, 32),
        ("AI幻觉与事实核验", 16, 28), ("AI项目式学习", 14, 36), ("数据采集与清洗", 13, 31),
    ]
    visits = []
    vid = 1
    student_keys = [f"stu{i}" for i in range(1, 10)]
    for concept_index, (concept, count, avg_minutes) in enumerate(hot_nodes, start=1):
        for n in range(count):
            user_key = student_keys[(n + concept_index) % len(student_keys)]
            duration = max(60, (avg_minutes + ((n % 5) - 2) * 4) * 60)
            visits.append(
                {
                    "id": vid,
                    "user_id": users[user_key]["id"],
                    "concept_id": concept_map[concept],
                    "concept_name": concept,
                    "duration_seconds": duration,
                    "create_time": iso(days=n % 7, hours=(n + concept_index) % 20),
                }
            )
            vid += 1
    return visits


def build_state(users: dict[str, dict], concept_map: dict[str, str], statuses: list[dict]) -> dict:
    state = _default_state()
    state["users"] = [
        {
            "id": item["id"],
            "username": item["username"],
            "password_hash": item["password_hash"],
            "role": item["role"],
            "class_id": item["class_id"],
            "profile": dict(item["profile"]),
        }
        for item in users.values()
    ]
    state["learning_statuses"] = statuses
    state["quiz_attempts"] = make_quiz_attempts(users, concept_map)
    state["questions"], next_comment_id = build_questions(users, concept_map)
    state["node_visit_records"] = make_node_visits(users, concept_map)
    state["collaboration_requests"] = [
        {"id": 1, "teacher_id": users["tea1"]["id"], "type": "图谱内容维护", "title": "补充模型评估案例", "description": "模型评估节点提问较多，希望补充准确率、召回率对比材料。", "status": "pending", "admin_reply": None, "create_time": iso(days=2), "update_time": iso(days=2), "handled_by": None},
        {"id": 2, "teacher_id": users["tea2"]["id"], "type": "教学资源补充", "title": "补充项目复盘模板", "description": "AI项目式学习节点适合增加复盘模板。", "status": "processing", "admin_reply": "已纳入图谱内容审核队列。", "create_time": iso(days=3), "update_time": iso(days=1), "handled_by": users["adm2"]["id"]},
        {"id": 3, "teacher_id": users["tea3"]["id"], "type": "图谱内容维护", "title": "完善数字版权材料", "description": "建议增加 AI 生成内容引用说明示例。", "status": "resolved", "admin_reply": "已补充到数字版权与学术规范节点。", "create_time": iso(days=4), "update_time": iso(days=1), "handled_by": users["adm1"]["id"]},
    ]
    state["quick_reply_templates"] = [
        {"id": 1, "teacher_id": users["tea1"]["id"], "title": "回看前置节点", "content": "建议先回看当前节点的前置依赖，再结合自测错题继续提问。", "create_time": iso(days=3)},
        {"id": 2, "teacher_id": users["tea1"]["id"], "title": "按任务类型梳理", "content": "请把任务类型、输入数据、输出结果和评价指标整理成表格。", "create_time": iso(days=2)},
        {"id": 3, "teacher_id": users["tea2"]["id"], "title": "记录提示词迭代", "content": "请记录每轮提示词修改点，并说明输出为什么变好或变差。", "create_time": iso(days=2)},
        {"id": 4, "teacher_id": users["tea3"]["id"], "title": "补充责任说明", "content": "如果使用 AI，请写清 AI 参与环节、人工核验方式和最终责任人。", "create_time": iso(days=2)},
    ]
    state["graph_change_requests"] = [
        {
            "id": 1,
            "teacher_id": users["tea1"]["id"],
            "action": "update_node",
            "summary": "补充模型评估节点的课堂案例和自测题",
            "target_concept_name": "模型评估",
            "node": {"name": "模型评估", "description": "通过准确率、召回率、泛化能力等指标评价模型效果。", "category": "算法模型", "difficulty": 3, "estimated_minutes": 35, "key_points": ["区分准确率与召回率", "理解过拟合与欠拟合"], "text_material": "结合教育场景比较漏判和误判成本。", "image_url": None, "video_title": "模型评估入门", "video_url": "", "resource_links": [], "study_tips": ["先看混淆矩阵，再理解指标。"], "common_mistakes": ["只看准确率，不看任务风险。"], "practice_task": "比较两个模型在不同指标下的取舍。", "quiz": []},
            "prerequisite_names": ["监督学习"],
            "next_names": ["AI产品体验评估"],
            "related_names": ["机器学习"],
            "status": "pending",
            "create_time": iso(days=1),
            "review_time": None,
            "reviewed_by": None,
            "review_note": None,
        }
    ]
    state["notifications"] = [
        {"id": i, "user_id": users[key]["id"], "category": "demo", "title": "演示数据已更新", "content": "系统已补充班级统计、节点访问、问答和自测数据。", "link": "/graph", "is_read": i % 2 == 0, "create_time": iso(hours=i)}
        for i, key in enumerate(["stu1", "stu2", "stu3", "stu4", "stu5", "stu6", "stu7", "stu8", "stu9", "tea1", "tea2", "tea3"], start=1)
    ]
    state["operation_logs"] = [
        {"id": 1, "actor_id": users["adm1"]["id"], "actor_name": "陈曦", "actor_role": "admin", "action": "seed_demo_data", "target_type": "system", "target_id": "demo", "description": "重建 9 名学生、3 名教师、3 名图谱运维官及班级统计演示数据。", "create_time": iso(hours=1)},
        {"id": 2, "actor_id": users["adm2"]["id"], "actor_name": "赵南一", "actor_role": "admin", "action": "review_graph_change", "target_type": "graph_change_request", "target_id": "1", "description": "收到教师提交的模型评估节点优化申请，等待审核发布。", "create_time": iso(hours=2)},
    ]
    state["recommendation_settings"] = {"recommendation_limit": 6, "weak_point_limit": 4, "path_limit": 7, "mastery_weight": 1.0, "in_progress_weight": 0.65}
    state["next_user_id"] = max(item["id"] for item in state["users"]) + 1
    state["next_status_id"] = max(item["id"] for item in state["learning_statuses"]) + 1
    state["next_question_id"] = max(item["id"] for item in state["questions"]) + 1
    state["next_comment_id"] = next_comment_id
    state["next_collaboration_request_id"] = max(item["id"] for item in state["collaboration_requests"]) + 1
    state["next_quiz_attempt_id"] = max(item["id"] for item in state["quiz_attempts"]) + 1
    state["next_node_visit_id"] = max(item["id"] for item in state["node_visit_records"]) + 1
    state["next_notification_id"] = max(item["id"] for item in state["notifications"]) + 1
    state["next_template_id"] = max(item["id"] for item in state["quick_reply_templates"]) + 1
    state["next_graph_change_request_id"] = max(item["id"] for item in state["graph_change_requests"]) + 1
    state["next_operation_log_id"] = max(item["id"] for item in state["operation_logs"]) + 1
    return state


def verify(session: Session, users: dict[str, dict], state: dict) -> None:
    if len([item for item in state["users"] if item["role"] == "student"]) != 9:
        raise RuntimeError("学生账号数量不是 9。")
    sample = next(item for item in state["users"] if item["username"] == "test_stu9")
    if not verify_password(PASSWORD, sample["password_hash"]):
        raise RuntimeError("演示账号密码校验失败。")
    if mysql_db.database_mode != "json-fallback":
        if session.query(User).count() != 15:
            raise RuntimeError("MySQL 用户数量异常。")
        if session.query(UserKnowledgeStatus).count() < 45:
            raise RuntimeError("MySQL 学习状态数量不足。")


def print_summary(state: dict) -> None:
    print("\n=== 演示账号（统一密码 test） ===")
    for role_name, role in [("学生", "student"), ("教师", "teacher"), ("图谱运维官", "admin")]:
        print(f"\n{role_name}账号:")
        for item in state["users"]:
            if item["role"] == role:
                print(f"- {item['username']} / test / {item['profile']['real_name']} / {item['profile']['class_name']}")
    print("\n=== 数据规模 ===")
    print(f"用户数: {len(state['users'])}")
    print(f"学习状态: {len(state['learning_statuses'])}")
    print(f"自测记录: {len(state['quiz_attempts'])}")
    print(f"节点访问记录: {len(state['node_visit_records'])}")
    print(f"节点问题: {len(state['questions'])}")
    print(f"评论数: {sum(len(item['comments']) for item in state['questions'])}")
    print(f"图谱变更申请: {len(state['graph_change_requests'])}")
    print(f"数据库模式: {mysql_db.database_mode}")


def main() -> None:
    init_db()
    concept_map = build_concept_map()
    missing = [name for name in ["人工智能基础", "机器学习", "模型评估", "提示词设计", "AI项目式学习"] if name not in concept_map]
    if missing:
        raise RuntimeError(f"图谱节点缺失，无法生成演示数据: {missing}")

    truncate_mysql_tables()
    session = SessionLocal()
    try:
        users = create_mysql_users(session)
        statuses = seed_learning_statuses(session, users, concept_map)
        state = build_state(users, concept_map, statuses)
        _save_state(state)
        verify(session, users, state)
        print_summary(state)
    finally:
        session.close()


if __name__ == "__main__":
    main()
