# 基于知识图谱的《人工智能与数字素养》助学系统

这是一个前后端分离的项目初始化骨架，包含：

- `backend/`：基于 FastAPI 的后端结构，已包含用户认证基础接口、MySQL 与 Neo4j 连接配置、`/api/graph/all` 图谱全量接口。
- `frontend/`：基于 Vue3 + Vite + Element Plus 的前端结构，已包含首页、登录注册页、图谱浏览页和多角色工作台页面骨架。
- `database/`：提供 MySQL 建表脚本和 Neo4j 初始知识图谱数据脚本。

## 快速启动

### 1. 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

### 3. 初始化数据库

- MySQL 执行 `database/mysql_init.sql`
- Neo4j 执行 `database/neo4j_init.cypher`

## 当前已完成

- FastAPI 基础结构与统一配置
- 用户注册 / 登录接口
- Neo4j 图谱全量查询接口 `GET /api/graph/all`
- Vue3 基础路由与页面布局
- `GraphExplore.vue` 图谱浏览页与可视化组件接入预留
- 多角色业务流程说明见 `docs/business_flows.md`

## 后续建议

- 补充 JWT 鉴权依赖与角色权限控制
- 完成学习状态、评论、收藏、提问、推荐算法接口
- 将 `GraphCanvas.vue` 接入 ECharts Graph 或 AntV G6
- 增加 Alembic、单元测试与接口文档说明
