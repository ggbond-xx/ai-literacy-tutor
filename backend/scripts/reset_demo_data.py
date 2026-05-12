from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys

from sqlalchemy import text
from sqlalchemy.orm import Session

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from app.core.security import get_password_hash, verify_password
from app.db.mysql import SessionLocal, engine, init_db
from app.db.neo4j import driver as neo4j_driver
from app.models.user import User
from app.models.user_knowledge_status import UserKnowledgeStatus
from app.models.user_profile import UserProfile
from app.services.graph_service import GraphService
from app.services.json_store import _default_state, _save_state


PASSWORD = "test"
CLASS_ID = 101
CLASS_NAME = "人工智能与数字素养一班"
SCHOOL_NAME = "数字素养实验大学"

NOW_UTC = datetime.now(UTC)
NOW_LOCAL = datetime.now()

ACCOUNT_SPECS = [
    {
        "key": "stu_linyu",
        "username": "test_stu1",
        "role": "student",
        "class_id": CLASS_ID,
        "profile": {
            "real_name": "林语知",
            "email": "linyuzi@example.com",
            "school": SCHOOL_NAME,
            "major": "人工智能教育",
            "grade": "2023级",
            "student_no": "S20231001",
            "class_name": CLASS_NAME,
            "bio": "关注学习路径推荐与课程项目实践，希望把图谱学习和课堂任务结合起来。",
        },
    },
    {
        "key": "stu_zhouqing",
        "username": "test_stu2",
        "role": "student",
        "class_id": CLASS_ID,
        "profile": {
            "real_name": "周晴岚",
            "email": "zhouqinglan@example.com",
            "school": SCHOOL_NAME,
            "major": "数字媒体技术",
            "grade": "2023级",
            "student_no": "S20231002",
            "class_name": CLASS_NAME,
            "bio": "对生成式 AI 和数字版权很感兴趣，喜欢从案例里理解知识点。",
        },
    },
    {
        "key": "stu_qiaomu",
        "username": "test_stu3",
        "role": "student",
        "class_id": CLASS_ID,
        "profile": {
            "real_name": "乔沐云",
            "email": "qiaomuyun@example.com",
            "school": SCHOOL_NAME,
            "major": "教育技术学",
            "grade": "2022级",
            "student_no": "S20221003",
            "class_name": CLASS_NAME,
            "bio": "更关注大模型、自然语言处理和项目复盘，希望用课程图谱梳理进阶路线。",
        },
    },
    {
        "key": "tea_wangqing",
        "username": "test_tea1",
        "role": "teacher",
        "class_id": CLASS_ID,
        "profile": {
            "real_name": "王清禾",
            "email": "wangqinghe@example.com",
            "school": SCHOOL_NAME,
            "major": "人工智能课程教学",
            "grade": "教师",
            "student_no": "T2026001",
            "class_name": CLASS_NAME,
            "bio": "负责基础概念与机器学习模块教学，关注学生提问质量和课堂讨论沉淀。",
        },
    },
    {
        "key": "tea_liming",
        "username": "test_tea2",
        "role": "teacher",
        "class_id": CLASS_ID,
        "profile": {
            "real_name": "李明舟",
            "email": "limingzhou@example.com",
            "school": SCHOOL_NAME,
            "major": "生成式AI应用教学",
            "grade": "教师",
            "student_no": "T2026002",
            "class_name": CLASS_NAME,
            "bio": "主要负责提示词设计、生成式 AI 和项目实践教学，偏好用案例引导学生提问。",
        },
    },
    {
        "key": "tea_sunrui",
        "username": "test_tea3",
        "role": "teacher",
        "class_id": CLASS_ID,
        "profile": {
            "real_name": "孙睿安",
            "email": "sunruian@example.com",
            "school": SCHOOL_NAME,
            "major": "AI伦理与治理",
            "grade": "教师",
            "student_no": "T2026003",
            "class_name": CLASS_NAME,
            "bio": "负责伦理素养与课程治理模块，擅长把课堂问题转化为讨论案例。",
        },
    },
    {
        "key": "admin_chenxi",
        "username": "test_adm1",
        "role": "admin",
        "class_id": None,
        "profile": {
            "real_name": "陈曦",
            "email": "chenxi@example.com",
            "school": SCHOOL_NAME,
            "major": "平台治理",
            "grade": "管理员",
            "student_no": "A2026001",
            "class_name": "系统管理组",
            "bio": "负责账号治理、协同事项处理和推荐参数维护。",
        },
    },
    {
        "key": "admin_zhaonan",
        "username": "test_adm2",
        "role": "admin",
        "class_id": None,
        "profile": {
            "real_name": "赵南一",
            "email": "zhaonanyi@example.com",
            "school": SCHOOL_NAME,
            "major": "内容运维",
            "grade": "管理员",
            "student_no": "A2026002",
            "class_name": "系统管理组",
            "bio": "负责讨论治理、用户资料维护和图谱内容协同。",
        },
    },
    {
        "key": "admin_hejun",
        "username": "test_adm3",
        "role": "admin",
        "class_id": None,
        "profile": {
            "real_name": "何钧远",
            "email": "hejunyuan@example.com",
            "school": SCHOOL_NAME,
            "major": "系统支持",
            "grade": "管理员",
            "student_no": "A2026003",
            "class_name": "系统管理组",
            "bio": "负责系统支持、日志追踪和演示环境维护。",
        },
    },
]


def utc_iso(*, days: int = 0, hours: int = 0, minutes: int = 0) -> str:
    return (NOW_UTC - timedelta(days=days, hours=hours, minutes=minutes)).isoformat()


def local_dt(*, days: int = 0, hours: int = 0, minutes: int = 0) -> datetime:
    return NOW_LOCAL - timedelta(days=days, hours=hours, minutes=minutes)


def truncate_mysql_tables() -> None:
    with engine.begin() as conn:
        tables = [row[0] for row in conn.execute(text("SHOW TABLES")).fetchall()]
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for table_name in tables:
            conn.execute(text(f"TRUNCATE TABLE `{table_name}`"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))


def build_concept_map() -> dict[str, str]:
    graph = GraphService(neo4j_driver).get_full_graph()
    concept_map = {node.name: node.id for node in graph.nodes}
    required_names = [
        "人工智能基础",
        "算法思维",
        "数据素养",
        "数据采集与清洗",
        "机器学习",
        "监督学习",
        "模型评估",
        "AI伦理与治理",
        "信息甄别与数字安全",
        "提示词设计",
        "生成式AI应用",
        "神经网络基础",
        "自然语言处理",
        "大模型基础",
        "AI幻觉与事实核验",
        "数字版权与学术规范",
        "AI项目式学习",
    ]
    missing = [name for name in required_names if name not in concept_map]
    if missing:
        raise RuntimeError(f"图谱中缺少这些节点，无法生成演示数据: {missing}")
    return concept_map


def create_mysql_users(session: Session) -> dict[str, dict]:
    created: dict[str, dict] = {}
    for spec in ACCOUNT_SPECS:
        password_hash = get_password_hash(PASSWORD)
        user = User(
            username=spec["username"],
            password_hash=password_hash,
            role=spec["role"],
            class_id=spec["class_id"],
        )
        session.add(user)
        session.flush()

        session.add(
            UserProfile(
                user_id=user.id,
                real_name=spec["profile"]["real_name"],
                email=spec["profile"]["email"],
                school=spec["profile"]["school"],
                major=spec["profile"]["major"],
                grade=spec["profile"]["grade"],
                student_no=spec["profile"]["student_no"],
                class_name=spec["profile"]["class_name"],
                bio=spec["profile"]["bio"],
            )
        )

        created[spec["key"]] = {
            "id": user.id,
            "username": spec["username"],
            "role": spec["role"],
            "class_id": spec["class_id"],
            "password_hash": password_hash,
            "profile": dict(spec["profile"]),
        }
    session.commit()
    return created


def seed_learning_statuses(session: Session, users: dict[str, dict], concept_map: dict[str, str]) -> list[dict]:
    status_plan = {
        "stu_linyu": [
            ("人工智能基础", 2, 7, 2),
            ("算法思维", 2, 7, 1),
            ("数据素养", 2, 6, 20),
            ("数据采集与清洗", 2, 6, 8),
            ("机器学习", 1, 4, 18),
            ("监督学习", 1, 3, 6),
            ("提示词设计", 1, 2, 3),
            ("生成式AI应用", 0, 1, 9),
        ],
        "stu_zhouqing": [
            ("人工智能基础", 2, 8, 1),
            ("数据素养", 2, 7, 10),
            ("信息甄别与数字安全", 2, 5, 15),
            ("提示词设计", 1, 3, 12),
            ("生成式AI应用", 1, 2, 10),
            ("AI幻觉与事实核验", 0, 1, 14),
            ("数字版权与学术规范", 0, 1, 4),
        ],
        "stu_qiaomu": [
            ("人工智能基础", 2, 9, 2),
            ("机器学习", 2, 8, 2),
            ("神经网络基础", 1, 4, 11),
            ("自然语言处理", 1, 3, 9),
            ("大模型基础", 0, 2, 8),
            ("AI项目式学习", 0, 1, 6),
            ("AI伦理与治理", 1, 2, 20),
        ],
    }

    json_statuses: list[dict] = []
    next_id = 1
    for user_key, records in status_plan.items():
        user_id = users[user_key]["id"]
        for concept_name, status, days, hours in records:
            update_time = local_dt(days=days, hours=hours)
            session.add(
                UserKnowledgeStatus(
                    user_id=user_id,
                    concept_id=concept_map[concept_name],
                    status=status,
                    update_time=update_time,
                )
            )
            json_statuses.append(
                {
                    "id": next_id,
                    "user_id": user_id,
                    "concept_id": concept_map[concept_name],
                    "status": status,
                    "update_time": update_time.astimezone().isoformat() if update_time.tzinfo else utc_iso(days=days, hours=hours),
                }
            )
            next_id += 1
    session.commit()
    return json_statuses


def build_json_state(users: dict[str, dict], concept_map: dict[str, str], learning_statuses: list[dict]) -> dict:
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
    state["learning_statuses"] = learning_statuses
    state["recommendation_settings"] = {
        "recommendation_limit": 6,
        "weak_point_limit": 4,
        "path_limit": 7,
        "mastery_weight": 1.0,
        "in_progress_weight": 0.65,
    }

    state["quiz_attempts"] = [
        {
            "id": 1,
            "user_id": users["stu_linyu"]["id"],
            "concept_id": concept_map["机器学习"],
            "concept_name": "机器学习",
            "total_questions": 10,
            "correct_answers": 7,
            "wrong_answers": 3,
            "accuracy": 0.7,
            "score": 70,
            "create_time": utc_iso(days=2, hours=5),
        },
        {
            "id": 2,
            "user_id": users["stu_linyu"]["id"],
            "concept_id": concept_map["提示词设计"],
            "concept_name": "提示词设计",
            "total_questions": 10,
            "correct_answers": 8,
            "wrong_answers": 2,
            "accuracy": 0.8,
            "score": 82,
            "create_time": utc_iso(days=1, hours=10),
        },
        {
            "id": 3,
            "user_id": users["stu_linyu"]["id"],
            "concept_id": concept_map["AI伦理与治理"],
            "concept_name": "AI伦理与治理",
            "total_questions": 10,
            "correct_answers": 6,
            "wrong_answers": 4,
            "accuracy": 0.6,
            "score": 58,
            "create_time": utc_iso(days=1, hours=3),
        },
        {
            "id": 4,
            "user_id": users["stu_zhouqing"]["id"],
            "concept_id": concept_map["生成式AI应用"],
            "concept_name": "生成式AI应用",
            "total_questions": 10,
            "correct_answers": 6,
            "wrong_answers": 4,
            "accuracy": 0.6,
            "score": 68,
            "create_time": utc_iso(days=2, hours=9),
        },
        {
            "id": 5,
            "user_id": users["stu_zhouqing"]["id"],
            "concept_id": concept_map["AI幻觉与事实核验"],
            "concept_name": "AI幻觉与事实核验",
            "total_questions": 10,
            "correct_answers": 5,
            "wrong_answers": 5,
            "accuracy": 0.5,
            "score": 54,
            "create_time": utc_iso(days=1, hours=14),
        },
        {
            "id": 6,
            "user_id": users["stu_zhouqing"]["id"],
            "concept_id": concept_map["信息甄别与数字安全"],
            "concept_name": "信息甄别与数字安全",
            "total_questions": 10,
            "correct_answers": 9,
            "wrong_answers": 1,
            "accuracy": 0.9,
            "score": 88,
            "create_time": utc_iso(days=1, hours=1),
        },
        {
            "id": 7,
            "user_id": users["stu_qiaomu"]["id"],
            "concept_id": concept_map["神经网络基础"],
            "concept_name": "神经网络基础",
            "total_questions": 10,
            "correct_answers": 6,
            "wrong_answers": 4,
            "accuracy": 0.6,
            "score": 62,
            "create_time": utc_iso(days=2, hours=4),
        },
        {
            "id": 8,
            "user_id": users["stu_qiaomu"]["id"],
            "concept_id": concept_map["自然语言处理"],
            "concept_name": "自然语言处理",
            "total_questions": 10,
            "correct_answers": 7,
            "wrong_answers": 3,
            "accuracy": 0.7,
            "score": 76,
            "create_time": utc_iso(days=1, hours=16),
        },
        {
            "id": 9,
            "user_id": users["stu_qiaomu"]["id"],
            "concept_id": concept_map["大模型基础"],
            "concept_name": "大模型基础",
            "total_questions": 10,
            "correct_answers": 5,
            "wrong_answers": 5,
            "accuracy": 0.5,
            "score": 49,
            "create_time": utc_iso(days=1, hours=4),
        },
    ]

    question_id = 1
    comment_id = 1

    def add_question(
        *,
        student_key: str,
        concept_name: str,
        title: str,
        description: str,
        create_time: str,
        teacher_key: str | None = None,
        teacher_reply: str | None = None,
        reply_time: str | None = None,
        featured: bool = False,
        featured_by: str | None = None,
        featured_time: str | None = None,
        favorite_user_keys: list[str] | None = None,
    ) -> dict:
        nonlocal question_id
        question = {
            "id": question_id,
            "student_id": users[student_key]["id"],
            "concept_id": concept_map[concept_name],
            "concept_name": concept_name,
            "title": title,
            "description": description,
            "teacher_reply": teacher_reply,
            "teacher_id": users[teacher_key]["id"] if teacher_key else None,
            "status": "answered" if teacher_key else "pending",
            "create_time": create_time,
            "reply_time": reply_time,
            "is_featured": featured,
            "featured_time": featured_time if featured else None,
            "featured_by": users[featured_by]["id"] if featured and featured_by else None,
            "favorite_user_ids": [users[key]["id"] for key in (favorite_user_keys or [])],
            "comments": [],
            "legacy_reply_migrated": bool(teacher_key),
        }
        state["questions"].append(question)
        question_id += 1
        return question

    def add_comment(
        question: dict,
        *,
        author_key: str,
        content: str,
        create_time: str,
        parent_comment_id: int | None = None,
        like_user_keys: list[str] | None = None,
        is_excellent: bool = False,
    ) -> int:
        nonlocal comment_id
        author = users[author_key]
        question["comments"].append(
            {
                "id": comment_id,
                "question_id": question["id"],
                "author_id": author["id"],
                "author_role": author["role"],
                "content": content,
                "create_time": create_time,
                "parent_comment_id": parent_comment_id,
                "like_user_ids": [users[key]["id"] for key in (like_user_keys or [])],
                "is_excellent": is_excellent,
            }
        )
        current_id = comment_id
        comment_id += 1
        return current_id

    q1 = add_question(
        student_key="stu_linyu",
        concept_name="机器学习",
        title="监督学习和无监督学习该先从哪一部分开始理解？",
        description="我已经看完机器学习的基本流程，但分类、聚类和评价指标容易混在一起，想知道课堂复习应该先抓哪条线。",
        create_time=utc_iso(days=3, hours=6),
        teacher_key="tea_wangqing",
        teacher_reply="建议先按“任务类型-数据形式-评价指标”三个维度梳理，再区分监督学习和无监督学习。",
        reply_time=utc_iso(days=3, hours=4),
        featured=True,
        featured_by="tea_wangqing",
        featured_time=utc_iso(days=2, hours=22),
        favorite_user_keys=["stu_zhouqing", "stu_qiaomu"],
    )
    c1 = add_comment(q1, author_key="tea_wangqing", content=q1["teacher_reply"], create_time=utc_iso(days=3, hours=4), like_user_keys=["stu_zhouqing", "stu_qiaomu"])
    c2 = add_comment(q1, author_key="stu_zhouqing", content="我也是先按任务目标分类，后来再补评价指标，感觉会清楚很多。", create_time=utc_iso(days=3, hours=2), parent_comment_id=c1, like_user_keys=["stu_linyu", "tea_wangqing"])
    c3 = add_comment(q1, author_key="tea_liming", content="可以把监督学习对应的分类/回归例子写成表格，再和无监督学习的聚类做对照。", create_time=utc_iso(days=2, hours=20), parent_comment_id=c2, like_user_keys=["stu_linyu"])
    add_comment(q1, author_key="stu_linyu", content="明白了，我准备按这个表格法重做一遍笔记。", create_time=utc_iso(days=2, hours=19), parent_comment_id=c3)
    add_comment(q1, author_key="admin_chenxi", content="管理员补充：资料区已同步更新了机器学习导学视频链接，刷新后可以直接查看。", create_time=utc_iso(days=2, hours=18), like_user_keys=["tea_wangqing", "stu_qiaomu"])

    q2 = add_question(
        student_key="stu_zhouqing",
        concept_name="生成式AI应用",
        title="提示词已经写得很详细，为什么生成结果还是不稳定？",
        description="我在做课程案例时补充了角色、目标和输出格式，但不同轮次的结果差异还是很大，想知道应该从哪里继续优化。",
        create_time=utc_iso(days=2, hours=15),
        teacher_key="tea_liming",
        teacher_reply="先固定任务目标和评价标准，再逐步增加约束条件，记录每轮输出差异，稳定性会更容易观察。",
        reply_time=utc_iso(days=2, hours=13),
        featured=True,
        featured_by="tea_liming",
        featured_time=utc_iso(days=2, hours=11),
        favorite_user_keys=["stu_linyu"],
    )
    c6 = add_comment(q2, author_key="tea_liming", content=q2["teacher_reply"], create_time=utc_iso(days=2, hours=13), like_user_keys=["stu_linyu", "stu_qiaomu"])
    c7 = add_comment(q2, author_key="stu_qiaomu", content="我后来会把“必须引用课堂材料”这类约束单独列出来，效果会稳定一些。", create_time=utc_iso(days=2, hours=10), parent_comment_id=c6)
    add_comment(q2, author_key="tea_wangqing", content="很好的补充。你还可以把输出拆成步骤，让模型先列提纲再写正文。", create_time=utc_iso(days=2, hours=9), parent_comment_id=c7, like_user_keys=["stu_zhouqing", "tea_liming"], is_excellent=True)
    add_comment(q2, author_key="admin_zhaonan", content="平台侧已经保留了该讨论，后续会把这类高质量问答沉淀到优秀案例区。", create_time=utc_iso(days=2, hours=8))

    q3 = add_question(
        student_key="stu_qiaomu",
        concept_name="AI伦理与治理",
        title="课堂项目里应该如何说明 AI 参与比例，才算符合学术规范？",
        description="我们的小组项目用了 AI 做资料整理和大纲生成，想知道在课程报告中应该怎么写才比较规范。",
        create_time=utc_iso(days=2, hours=6),
        teacher_key="tea_sunrui",
        teacher_reply="建议在方法说明中写清 AI 参与的环节、你们做了哪些人工核验，以及最终由谁对内容负责。",
        reply_time=utc_iso(days=2, hours=5),
        featured=False,
    )
    c10 = add_comment(q3, author_key="tea_sunrui", content=q3["teacher_reply"], create_time=utc_iso(days=2, hours=5), like_user_keys=["stu_linyu", "stu_zhouqing"])
    add_comment(q3, author_key="stu_linyu", content="这个说明方式很适合直接写进项目附录，我们组也准备这样做。", create_time=utc_iso(days=2, hours=4), parent_comment_id=c10)
    add_comment(q3, author_key="admin_hejun", content="管理员提醒：如果后续需要模板，我们可以在资源区补一份“AI参与说明”示例。", create_time=utc_iso(days=2, hours=3), like_user_keys=["tea_sunrui"])

    q4 = add_question(
        student_key="stu_linyu",
        concept_name="大模型基础",
        title="上下文窗口和模型参数规模到底有什么区别？",
        description="我知道这两个概念都和大模型能力有关，但总感觉解释时会混淆，想先听听大家怎么区分。",
        create_time=utc_iso(days=1, hours=20),
        featured=False,
    )
    add_comment(q4, author_key="stu_zhouqing", content="我理解参数规模更像“模型学到多少”，上下文窗口更像“一次能带多少材料”。", create_time=utc_iso(days=1, hours=18), like_user_keys=["stu_linyu"])
    add_comment(q4, author_key="admin_zhaonan", content="这个问题已经被记录到内容优化清单里，后续会补一张对比图示。", create_time=utc_iso(days=1, hours=17))

    q5 = add_question(
        student_key="stu_zhouqing",
        concept_name="提示词设计",
        title="链式提示在课程作业里该怎么写才比较规范？",
        description="想把提示过程写进作业过程记录，但不知道应该展示到什么粒度比较合适。",
        create_time=utc_iso(days=1, hours=15),
        teacher_key="tea_wangqing",
        teacher_reply="建议按“任务目标-步骤拆解-输出检查”三段来写，每一段只保留关键提示，不需要把无效尝试全部展开。",
        reply_time=utc_iso(days=1, hours=13),
        featured=False,
    )
    c14 = add_comment(q5, author_key="tea_wangqing", content=q5["teacher_reply"], create_time=utc_iso(days=1, hours=13))
    c15 = add_comment(q5, author_key="stu_qiaomu", content="我准备把“先提纲、再扩写、最后核验”的链路整理成三张截图。", create_time=utc_iso(days=1, hours=12), parent_comment_id=c14)
    add_comment(q5, author_key="tea_wangqing", content="这个做法很好，记得在最后加一段你人工修订的理由。", create_time=utc_iso(days=1, hours=11), parent_comment_id=c15, like_user_keys=["stu_zhouqing"])

    q6 = add_question(
        student_key="stu_qiaomu",
        concept_name="AI项目式学习",
        title="项目复盘里应该包含哪些部分，才算完整？",
        description="课程要求写项目复盘，我已经整理了结果，但不知道如何把失败尝试和修改过程组织得更清楚。",
        create_time=utc_iso(days=1, hours=8),
        teacher_key="tea_liming",
        teacher_reply="建议至少包含目标、方案迭代、关键问题、修正动作和最终反思五部分，让过程可追踪。",
        reply_time=utc_iso(days=1, hours=7),
        featured=True,
        featured_by="tea_liming",
        featured_time=utc_iso(days=1, hours=5),
        favorite_user_keys=["stu_linyu", "stu_zhouqing"],
    )
    c17 = add_comment(q6, author_key="tea_liming", content=q6["teacher_reply"], create_time=utc_iso(days=1, hours=7), like_user_keys=["stu_linyu", "stu_zhouqing", "stu_qiaomu"])
    c18 = add_comment(q6, author_key="admin_chenxi", content="为了便于演示，我们已经在后台记录了这个问题，后续会补一份复盘模板。", create_time=utc_iso(days=1, hours=6), parent_comment_id=c17)
    add_comment(q6, author_key="tea_sunrui", content="如果项目涉及 AI 生成内容，还要在复盘中补充来源核验和责任说明。", create_time=utc_iso(days=1, hours=5), parent_comment_id=c18, like_user_keys=["stu_qiaomu"], is_excellent=True)

    state["collaboration_requests"] = [
        {
            "id": 1,
            "teacher_id": users["tea_wangqing"]["id"],
            "type": "graph_content",
            "title": "补充大模型基础课堂案例",
            "description": "建议在“大模型基础”节点新增一份参数规模与上下文窗口的对比图，便于学生回答高频问题。",
            "status": "pending",
            "admin_reply": None,
            "create_time": utc_iso(days=1, hours=18),
            "update_time": utc_iso(days=1, hours=18),
            "handled_by": None,
        },
        {
            "id": 2,
            "teacher_id": users["tea_liming"]["id"],
            "type": "resource",
            "title": "补充生成式AI应用视频资源",
            "description": "课程案例中关于多轮提示的讲解视频较少，希望在资源区补一条短视频链接。",
            "status": "resolved",
            "admin_reply": "已在资源区补充“提示词迭代示例”视频，并同步到生成式AI应用节点。",
            "create_time": utc_iso(days=2, hours=16),
            "update_time": utc_iso(days=1, hours=22),
            "handled_by": users["admin_chenxi"]["id"],
        },
        {
            "id": 3,
            "teacher_id": users["tea_sunrui"]["id"],
            "type": "permission",
            "title": "希望开放项目式学习的班级展示区",
            "description": "当前班级项目作品已完成初稿，希望在教师工作台里增加班级展示入口，方便课堂互评。",
            "status": "processing",
            "admin_reply": "已纳入本周迭代，先保留展示字段与排序规则配置。",
            "create_time": utc_iso(days=2, hours=12),
            "update_time": utc_iso(days=1, hours=8),
            "handled_by": users["admin_zhaonan"]["id"],
        },
        {
            "id": 4,
            "teacher_id": users["tea_wangqing"]["id"],
            "type": "system_support",
            "title": "图谱页面关系标签遮挡需要调整",
            "description": "课堂演示时部分关系标签会遮挡节点，建议优化图谱画布的标签布局。",
            "status": "resolved",
            "admin_reply": "已完成标签间距优化，并在新版本中放宽节点详情抽屉宽度。",
            "create_time": utc_iso(days=3, hours=10),
            "update_time": utc_iso(days=1, hours=2),
            "handled_by": users["admin_hejun"]["id"],
        },
    ]

    template_specs = {
        "tea_wangqing": [
            ("先按任务类型梳理", "建议先从任务类型入手，把分类、回归、聚类分别写成对照表，再回来看模型差异。"),
            ("回看前置节点", "这个问题和当前节点的前置知识关系很强，建议先补看图谱中的前置依赖，再继续提问。"),
            ("先完成节点自测", "建议先完成当前节点自测题，把错题截图和困惑点一起发出来，方便老师定位问题。"),
        ],
        "tea_liming": [
            ("记录提示词变化", "建议把每轮提示词修改点单独列出来，再对照输出差异分析为什么会变。"),
            ("先固定评价标准", "生成结果不稳定时，先把“什么算好答案”写清楚，再逐步增加约束条件。"),
            ("补充案例材料", "这个问题适合结合案例一起看，建议先打开学习材料里的案例链接，再继续讨论。"),
        ],
        "tea_sunrui": [
            ("补充责任说明", "如果作业或项目使用了 AI，请补充“AI参与环节、人工核验方式、最终责任人”三项说明。"),
            ("引用来源要写清", "讨论伦理和版权问题时，建议把来源链接、引用方式和使用边界一起写清楚。"),
            ("先回顾治理原则", "建议先回顾节点中的公平性、透明性和责任归属三个关键词，再回来细化你的问题。"),
        ],
    }
    template_id = 1
    for teacher_key, entries in template_specs.items():
        for index, (title, content) in enumerate(entries, start=1):
            state["quick_reply_templates"].append(
                {
                    "id": template_id,
                    "teacher_id": users[teacher_key]["id"],
                    "title": title,
                    "content": content,
                    "create_time": utc_iso(days=1, hours=12 - index),
                }
            )
            template_id += 1

    state["notifications"] = [
        {
            "id": 1,
            "user_id": users["stu_linyu"]["id"],
            "category": "discussion",
            "title": "你的问题被教师置顶了",
            "content": "王清禾已将你在“机器学习”节点下的问题置顶，建议查看最新回复与优秀评论。",
            "link": f"/graph?focus={concept_map['机器学习']}",
            "is_read": False,
            "create_time": utc_iso(days=2, hours=22),
        },
        {
            "id": 2,
            "user_id": users["stu_zhouqing"]["id"],
            "category": "discussion",
            "title": "你的问题进入优秀讨论区",
            "content": "李明舟已将你在“生成式AI应用”节点下的问题置顶，并标记了优秀评论。",
            "link": f"/graph?focus={concept_map['生成式AI应用']}",
            "is_read": False,
            "create_time": utc_iso(days=2, hours=11),
        },
        {
            "id": 3,
            "user_id": users["stu_qiaomu"]["id"],
            "category": "discussion",
            "title": "你收藏的讨论有新回复",
            "content": "“AI项目式学习”节点下的置顶讨论新增了教师补充，建议继续查看。",
            "link": f"/graph?focus={concept_map['AI项目式学习']}",
            "is_read": True,
            "create_time": utc_iso(days=1, hours=4),
        },
        {
            "id": 4,
            "user_id": users["tea_wangqing"]["id"],
            "category": "coordination",
            "title": "管理员已处理你的协同事项",
            "content": "何钧远已完成“图谱页面关系标签遮挡需要调整”的处理，并给出了回复。",
            "link": "/teacher",
            "is_read": False,
            "create_time": utc_iso(days=1, hours=2),
        },
        {
            "id": 5,
            "user_id": users["tea_liming"]["id"],
            "category": "coordination",
            "title": "资源补充事项已办结",
            "content": "陈曦已完成“补充生成式AI应用视频资源”的处理，你可以在教师工作台查看结果。",
            "link": "/teacher",
            "is_read": True,
            "create_time": utc_iso(days=1, hours=22),
        },
        {
            "id": 6,
            "user_id": users["tea_sunrui"]["id"],
            "category": "coordination",
            "title": "班级展示区事项处理中",
            "content": "赵南一已将“开放项目式学习的班级展示区”标记为处理中。",
            "link": "/teacher",
            "is_read": False,
            "create_time": utc_iso(days=1, hours=8),
        },
        {
            "id": 7,
            "user_id": users["admin_chenxi"]["id"],
            "category": "system",
            "title": "今日演示数据已同步",
            "content": "账号、学习状态、讨论、通知和协同事项已重建，可用于系统演示。",
            "link": "/admin",
            "is_read": True,
            "create_time": utc_iso(hours=1),
        },
        {
            "id": 8,
            "user_id": users["admin_zhaonan"]["id"],
            "category": "governance",
            "title": "讨论区有新的优秀评论",
            "content": "当前共有多条优秀评论可供治理面板展示，请前往管理后台查看。",
            "link": "/admin",
            "is_read": False,
            "create_time": utc_iso(hours=2),
        },
        {
            "id": 9,
            "user_id": users["admin_hejun"]["id"],
            "category": "system",
            "title": "系统支持事项已归档",
            "content": "图谱标签遮挡问题已处理完毕，相关操作已经记录到管理员日志。",
            "link": "/admin",
            "is_read": True,
            "create_time": utc_iso(hours=3),
        },
    ]

    state["operation_logs"] = [
        {
            "id": 1,
            "actor_id": users["admin_chenxi"]["id"],
            "actor_name": users["admin_chenxi"]["profile"]["real_name"],
            "actor_role": "admin",
            "action": "update_recommendation_settings",
            "target_type": "settings",
            "target_id": "recommendation",
            "description": "调整推荐参数：推荐数 6，薄弱点 4，路径上限 7，并提高学习中节点的权重。",
            "create_time": utc_iso(days=1, hours=1),
        },
        {
            "id": 2,
            "actor_id": users["admin_chenxi"]["id"],
            "actor_name": users["admin_chenxi"]["profile"]["real_name"],
            "actor_role": "admin",
            "action": "update_coordination",
            "target_type": "coordination",
            "target_id": "2",
            "description": "处理教师协同事项《补充生成式AI应用视频资源》，状态更新为 resolved。",
            "create_time": utc_iso(days=1, hours=22),
        },
        {
            "id": 3,
            "actor_id": users["admin_zhaonan"]["id"],
            "actor_name": users["admin_zhaonan"]["profile"]["real_name"],
            "actor_role": "admin",
            "action": "update_coordination",
            "target_type": "coordination",
            "target_id": "3",
            "description": "处理教师协同事项《希望开放项目式学习的班级展示区》，状态更新为 processing。",
            "create_time": utc_iso(days=1, hours=8),
        },
        {
            "id": 4,
            "actor_id": users["admin_hejun"]["id"],
            "actor_name": users["admin_hejun"]["profile"]["real_name"],
            "actor_role": "admin",
            "action": "update_coordination",
            "target_type": "coordination",
            "target_id": "4",
            "description": "处理教师协同事项《图谱页面关系标签遮挡需要调整》，状态更新为 resolved。",
            "create_time": utc_iso(days=1, hours=2),
        },
        {
            "id": 5,
            "actor_id": users["admin_zhaonan"]["id"],
            "actor_name": users["admin_zhaonan"]["profile"]["real_name"],
            "actor_role": "admin",
            "action": "update_user",
            "target_type": "user",
            "target_id": str(users["stu_qiaomu"]["id"]),
            "description": "完善账号 stu_qiaomu 的专业、班级和个人简介信息。",
            "create_time": utc_iso(days=1, hours=6),
        },
        {
            "id": 6,
            "actor_id": users["admin_hejun"]["id"],
            "actor_name": users["admin_hejun"]["profile"]["real_name"],
            "actor_role": "admin",
            "action": "create_user",
            "target_type": "user",
            "target_id": str(users["admin_hejun"]["id"]),
            "description": "创建演示账号 admin_hejun，用于系统支持与日志演示。",
            "create_time": utc_iso(days=1, hours=5),
        },
    ]

    state["next_user_id"] = max(user["id"] for user in state["users"]) + 1
    state["next_status_id"] = max(item["id"] for item in state["learning_statuses"]) + 1
    state["next_question_id"] = max(item["id"] for item in state["questions"]) + 1
    state["next_comment_id"] = max(comment["id"] for item in state["questions"] for comment in item["comments"]) + 1
    state["next_collaboration_request_id"] = max(item["id"] for item in state["collaboration_requests"]) + 1
    state["next_quiz_attempt_id"] = max(item["id"] for item in state["quiz_attempts"]) + 1
    state["next_notification_id"] = max(item["id"] for item in state["notifications"]) + 1
    state["next_template_id"] = max(item["id"] for item in state["quick_reply_templates"]) + 1
    state["next_operation_log_id"] = max(item["id"] for item in state["operation_logs"]) + 1
    return state


def print_account_summary(users: dict[str, dict]) -> None:
    print("\n=== 演示账号（统一密码） ===")
    print(f"统一密码: {PASSWORD}")
    print("\n学生账号:")
    for key in ["stu_linyu", "stu_zhouqing", "stu_qiaomu"]:
        item = users[key]
        print(f"- {item['username']} / {PASSWORD} / {item['profile']['real_name']}")
    print("\n教师账号:")
    for key in ["tea_wangqing", "tea_liming", "tea_sunrui"]:
        item = users[key]
        print(f"- {item['username']} / {PASSWORD} / {item['profile']['real_name']}")
    print("\n管理员账号:")
    for key in ["admin_chenxi", "admin_zhaonan", "admin_hejun"]:
        item = users[key]
        print(f"- {item['username']} / {PASSWORD} / {item['profile']['real_name']}")


def verify_seed(session: Session, users: dict[str, dict], state: dict) -> None:
    mysql_user_count = session.query(User).count()
    mysql_status_count = session.query(UserKnowledgeStatus).count()
    if mysql_user_count != 9:
        raise RuntimeError(f"MySQL 用户数量异常，当前为 {mysql_user_count}")
    if mysql_status_count < 20:
        raise RuntimeError(f"MySQL 学习状态数量异常，当前为 {mysql_status_count}")

    sample_user = session.query(User).filter(User.username == "test_stu1").first()
    if sample_user is None or not verify_password(PASSWORD, sample_user.password_hash):
        raise RuntimeError("示例账号密码验证失败。")

    if len(state["questions"]) < 6 or len(state["notifications"]) < 9:
        raise RuntimeError("JSON 互动数据数量不足，未达到演示要求。")


def main() -> None:
    init_db()
    concept_map = build_concept_map()
    truncate_mysql_tables()

    session = SessionLocal()
    try:
        created_users = create_mysql_users(session)
        learning_statuses = seed_learning_statuses(session, created_users, concept_map)
        json_state = build_json_state(created_users, concept_map, learning_statuses)
        _save_state(json_state)
        verify_seed(session, created_users, json_state)
        print_account_summary(created_users)
        print("\nMySQL 用户数: 9")
        print(f"MySQL 学习状态数: {len(learning_statuses)}")
        print(f"节点讨论主题数: {len(json_state['questions'])}")
        print(f"节点评论数: {sum(len(item['comments']) for item in json_state['questions'])}")
        print(f"通知数: {len(json_state['notifications'])}")
        print(f"协同事项数: {len(json_state['collaboration_requests'])}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
