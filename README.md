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

1. 安装 Python 3.12+、Node.js 20+ 和 PostgreSQL 18+。
2. 复制 `.env.example` 为 `.env`，按本机 PostgreSQL 修改连接信息。
3. 后端和前端的具体启动命令会随着第一阶段骨架完成补充。

