# 大数据项目管理平台

内部项目管理系统，当前按阶段建设。第一阶段先实现登录、角色权限和 PMO 项目台账。

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Element Plus、Pinia、Vue Router、Axios
- 后端：FastAPI、SQLAlchemy、Alembic、Pydantic
- 数据库：PostgreSQL

## 目录

- `backend/`：FastAPI 后端
- `frontend/`：Vue 3 前端
- `docs/superpowers/specs/`：已确认的系统设计
- `docs/superpowers/plans/`：分阶段实施计划

## 本地开发准备

1. 安装 Python 3.12+、Node.js 20+ 和 PostgreSQL 18+。没有本地 PostgreSQL 时，可以使用 `docker compose up -d postgres`。
2. 复制 `.env.example` 为 `.env`，填写本机 PostgreSQL 用户和密码。`.env` 不会进入 Git。
3. 创建后端虚拟环境并安装依赖：

   ```powershell
   cd backend
   py -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -e ".[test]"
   ```

4. 创建数据库 `pm_test` 后执行迁移：

   ```powershell
   .\.venv\Scripts\python.exe -m alembic upgrade head
   .\.venv\Scripts\python.exe -m scripts.seed_demo
   ```

   开发种子账号统一使用密码 `ChangeMe123!`，只用于本地验证，正式环境禁止运行种子脚本。

5. 启动后端：

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
   ```

   API 文档地址：`http://127.0.0.1:8000/docs`。

6. 另开终端启动前端：

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

   前端地址：`http://localhost:5173`。

## 测试

后端测试使用独立的 `TEST_DATABASE_URL` 数据库：

```powershell
cd backend
\.venv\Scripts\python.exe -m pytest -v
```

前端检查和生产构建：

```powershell
cd frontend
npm run typecheck
npm run build
```

