# Phase 1 Foundation and Project Register Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable local Web application with PostgreSQL-backed authentication, role/data permissions, and a PMO-managed project register that the user can test before the progress modules are added.

**Architecture:** Keep the approved Vue 3 SPA and FastAPI monolith. The backend owns authentication, authorization, project validation, and project lifecycle rules; the frontend consumes typed HTTP APIs and does not duplicate permission decisions. PostgreSQL is the development and test database for this phase.

**Tech Stack:** Vue 3.5, Vite 6, TypeScript 5.6, Element Plus 2.9, Pinia 2.3, Vue Router 4.5, Axios 1.7, FastAPI 0.162, SQLAlchemy 2.1, Pydantic 2.12, Alembic, PostgreSQL, pytest, TestClient.

---

## Delivery Stages

This plan covers only Stage 1. Each later stage gets its own reviewed plan after the current stage is accepted.

1. **Stage 1: Foundation and project register** — login, roles, departments, PMO project creation, project list/detail/edit, soft archive, local run instructions.
2. **Stage 2: Work items and progress** — project stages/modules, weights, milestones, progress aggregation, health rules.
3. **Stage 3: Execution and management view** — status updates, risks/issues, financial records, Seafile links, dashboard.
4. **Stage 4: Operations and hardening** — reminders, Excel migration, audit views, deployment packaging, PostgreSQL integration coverage.

After Stage 1, the user verifies the workflow with representative projects and confirms field names before Stage 2 begins.

## File Map

### Repository-level files

- Create: `README.md` — Windows setup, PostgreSQL configuration, run commands, test commands.
- Create: `.gitignore` — Python, Node, environment, build and editor artifacts.
- Create: `.env.example` — backend and frontend development settings without secrets.
- Create: `docker-compose.yml` — optional local PostgreSQL service for developers who do not already have PostgreSQL.

### Backend files

- Create: `backend/pyproject.toml` — pinned runtime and test dependencies plus pytest configuration.
- Create: `backend/alembic.ini` — Alembic entry point.
- Create: `backend/app/main.py` — FastAPI application, CORS, health endpoint, and route registration.
- Create: `backend/app/core/config.py` — typed environment settings.
- Create: `backend/app/core/security.py` — password hashing and JWT encode/decode helpers.
- Create: `backend/app/db/session.py` — SQLAlchemy engine, session factory, and request dependency.
- Create: `backend/app/db/base.py` — declarative base and model imports used by Alembic.
- Create: `backend/app/models/system.py` — department, user, and role models.
- Create: `backend/app/models/project.py` — project and project-member models needed in Stage 1.
- Create: `backend/app/schemas/auth.py` — login and current-user response schemas.
- Create: `backend/app/schemas/project.py` — project create, update, list, and detail schemas.
- Create: `backend/app/api/deps.py` — current-user and role/data-scope dependencies.
- Create: `backend/app/api/routes/auth.py` — login and current-user endpoints.
- Create: `backend/app/api/routes/projects.py` — project list, create, read, update, and archive endpoints.
- Create: `backend/app/services/auth.py` — user lookup and token creation.
- Create: `backend/app/services/projects.py` — project validation and permission-aware queries.
- Create: `backend/alembic/env.py` and `backend/alembic/versions/0001_foundation.py` — first schema migration.
- Create: `backend/scripts/seed_demo.py` — deterministic local users, departments, and one sample project.
- Create: `backend/tests/conftest.py` — PostgreSQL test session and authenticated client fixtures.
- Create: `backend/tests/test_auth.py` — login, invalid credentials, and current-user tests.
- Create: `backend/tests/test_projects.py` — PMO creation, role permissions, data scope, update and archive tests.

### Frontend files

- Create: `frontend/package.json` — scripts and pinned dependencies.
- Create: `frontend/vite.config.ts` — development proxy from `/api` to FastAPI.
- Create: `frontend/tsconfig.json` and `frontend/tsconfig.node.json` — strict TypeScript configuration.
- Create: `frontend/index.html` and `frontend/src/main.ts` — application entry point.
- Create: `frontend/src/router/index.ts` — login guard and application routes.
- Create: `frontend/src/api/http.ts` — Axios instance and token/error interceptors.
- Create: `frontend/src/api/auth.ts` and `frontend/src/api/projects.ts` — typed API calls.
- Create: `frontend/src/stores/auth.ts` — token, current user, login and logout state.
- Create: `frontend/src/types/auth.ts` and `frontend/src/types/project.ts` — API-facing types.
- Create: `frontend/src/layouts/AppLayout.vue` — authenticated navigation shell.
- Create: `frontend/src/views/LoginView.vue` — login form and error state.
- Create: `frontend/src/views/dashboard/DashboardView.vue` — Stage 1 project count summary.
- Create: `frontend/src/views/projects/ProjectListView.vue` — filterable project table and create action.
- Create: `frontend/src/views/projects/ProjectCreateView.vue` — PMO-only project creation form.
- Create: `frontend/src/views/projects/ProjectDetailView.vue` — project baseline and archive action.
- Create: `frontend/src/components/ProjectStatusTag.vue` — consistent lifecycle status display.

## Task 1: Establish the runnable repository skeleton

**Files:** `README.md`, `.gitignore`, `.env.example`, `docker-compose.yml`, `backend/pyproject.toml`, `frontend/package.json`, frontend TypeScript/Vite files.

- [ ] **Step 1: Add the repository-level configuration.**

  `.env.example` must define `DATABASE_URL`, `TEST_DATABASE_URL`, `JWT_SECRET`, `JWT_EXPIRE_MINUTES`, `CORS_ORIGINS`, and `VITE_API_BASE_URL`. The example uses `postgresql+psycopg2://project_manage:project_manage@localhost:5432/project_manage` and a separate `project_manage_test` database.

  `.gitignore` must exclude `.env`, `__pycache__/`, `.pytest_cache/`, `.venv/`, `node_modules/`, `dist/`, `.idea/`, `.vscode/`, and `*.pyc`.

- [ ] **Step 2: Add the optional PostgreSQL compose service.**

  Use PostgreSQL 18 with database `project_manage`, user `project_manage`, and password `project_manage`, exposing port `5432`. The application must still work with an externally managed PostgreSQL instance by using `.env`.

- [ ] **Step 3: Add backend dependency metadata.**

  `backend/pyproject.toml` declares FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic Settings, psycopg2-binary, python-jose, passlib/bcrypt, pytest, httpx, and anyio. The project requires Python 3.12 or newer and configures `pytest` to discover `backend/tests`.

- [ ] **Step 4: Add the Vite frontend shell.**

  `frontend/package.json` includes `dev`, `build`, `typecheck`, and `test` scripts. Vite proxies `/api` to `http://127.0.0.1:8000`. The TypeScript compiler runs in strict mode.

- [ ] **Step 5: Verify the empty skeleton before adding application code.**

  Run:

  ```powershell
  docker compose config
  cd backend
  py -m pip install -e ".[test]"
  cd ..\frontend
  npm install
  npm run build
  ```

  Expected: compose configuration is valid, dependency installation succeeds, and the initial Vite shell builds.

- [ ] **Step 6: Commit the skeleton.**

  ```powershell
  git add README.md .gitignore .env.example docker-compose.yml backend frontend
  git commit -m "chore: scaffold project management application"
  ```

## Task 2: Implement database foundation and system users

**Files:** `backend/app/core/config.py`, `backend/app/db/session.py`, `backend/app/db/base.py`, `backend/app/models/system.py`, `backend/alembic.ini`, `backend/alembic/env.py`, `backend/alembic/versions/0001_foundation.py`, `backend/scripts/seed_demo.py`.

- [ ] **Step 1: Write model tests for the required constraints.**

  Add tests that create a department and users with roles `boss`, `department_head`, `pmo`, `project_manager`, and `member`; assert usernames are unique, role values are constrained to the five values, and a user belongs to one department. Run the tests against `TEST_DATABASE_URL` and confirm they fail because the models do not exist.

- [ ] **Step 2: Implement typed settings and database sessions.**

  `Settings` reads the environment variables. `get_db()` yields a SQLAlchemy session and always closes it. The application must fail at startup with a clear configuration error when `DATABASE_URL` is missing.

- [ ] **Step 3: Implement the system models.**

  `Department` has `id`, `name`, `code`, `is_active`, `created_at`, and `updated_at`. `User` has `id`, `username`, `display_name`, `password_hash`, `role`, `department_id`, `is_active`, and timestamps. Use a Python enum for roles and database uniqueness on username and department code.

- [ ] **Step 4: Create and run the first migration.**

  Alembic must create `sys_department` and `sys_user` tables and the role enum/check constraint. Run:

  ```powershell
  cd backend
  alembic upgrade head
  ```

  Expected: the migration completes against the configured PostgreSQL database.

- [ ] **Step 5: Add deterministic seed data.**

  `seed_demo.py` is idempotent. It creates one department named `大数据业务部` and one demo user for each role with documented development-only passwords. It must refuse to run when `APP_ENV=production`.

- [ ] **Step 6: Run model tests and commit.**

  ```powershell
  cd backend
  pytest tests/test_system_models.py -v
  git add backend/app backend/alembic.ini backend/alembic backend/scripts backend/tests
  git commit -m "feat: add system users and departments"
  ```

## Task 3: Implement authentication and authorization

**Files:** `backend/app/core/security.py`, `backend/app/schemas/auth.py`, `backend/app/api/deps.py`, `backend/app/services/auth.py`, `backend/app/api/routes/auth.py`, `backend/tests/test_auth.py`.

- [ ] **Step 1: Write failing authentication tests.**

  Cover successful login returning a bearer token, invalid password returning HTTP 401, inactive user returning HTTP 403, `/api/auth/me` returning the current user, missing token returning HTTP 401, and malformed token returning HTTP 401.

- [ ] **Step 2: Implement password and JWT helpers.**

  Use bcrypt for password hashes. JWT payloads contain `sub` as the user id, `role`, `department_id`, and an expiration. Never return `password_hash` from a schema.

- [ ] **Step 3: Implement the auth endpoints.**

  `POST /api/auth/login` accepts `username` and `password` using OAuth2-compatible form data and returns `{access_token, token_type, user}`. `GET /api/auth/me` returns the current user and department.

- [ ] **Step 4: Implement role dependencies.**

  `require_roles(*roles)` checks the authenticated user's role. `get_data_scope()` returns `all`, `department`, `owned`, or `member` scope according to the five roles. These dependencies are reusable by project routes.

- [ ] **Step 5: Run auth tests and commit.**

  ```powershell
  cd backend
  pytest tests/test_auth.py -v
  git add backend/app backend/tests/test_auth.py
  git commit -m "feat: add JWT authentication and role permissions"
  ```

## Task 4: Implement the Stage 1 project register API

**Files:** `backend/app/models/project.py`, `backend/app/schemas/project.py`, `backend/app/services/projects.py`, `backend/app/api/routes/projects.py`, `backend/alembic/versions/0002_projects.py`, `backend/tests/test_projects.py`.

- [ ] **Step 1: Write failing project permission tests.**

  Cover these rules:

  - PMO can create a project.
  - Non-PMO users receive HTTP 403 on project creation.
  - PMO and department head can list all visible projects in their organization.
  - Project managers see only projects where they are the manager.
  - Members see only projects where they are members.
  - Project detail hides archived projects from the normal list unless `include_archived=true` is requested by PMO.
  - Project update validates end date is not before start date.
  - Archive changes lifecycle status to `archived` without deleting the row.

- [ ] **Step 2: Implement the project models and migration.**

  `Project` contains `id`, `code`, `name`, `description`, `department_id`, `project_manager_id`, `client_name`, `region`, `planned_start_date`, `planned_end_date`, `lifecycle_status`, `seafile_url`, `is_archived`, `created_at`, `updated_at`. `ProjectMember` links a project and user with a `responsibility` field. Add uniqueness on project code and `(project_id, user_id)`.

- [ ] **Step 3: Implement project schemas and service rules.**

  `ProjectCreate` requires code, name, department, project manager, and planned dates. `ProjectUpdate` allows baseline fields but not computed progress fields, which are introduced in Stage 2. The service validates that the manager belongs to the selected department and that the Seafile URL is absolute when supplied.

- [ ] **Step 4: Implement project routes.**

  Add:

  - `GET /api/projects`
  - `POST /api/projects`
  - `GET /api/projects/{project_id}`
  - `PATCH /api/projects/{project_id}`
  - `POST /api/projects/{project_id}/archive`

  All routes apply backend data-scope checks. List responses include code, name, manager, department, lifecycle status, planned end date, and timestamps.

- [ ] **Step 5: Run project API tests and commit.**

  ```powershell
  cd backend
  alembic upgrade head
  pytest tests/test_projects.py -v
  git add backend/app backend/alembic backend/tests/test_projects.py
  git commit -m "feat: add PMO project register API"
  ```

## Task 5: Build the authenticated frontend workflow

**Files:** frontend files listed in the file map.

- [ ] **Step 1: Add typed API clients and auth store.**

  Axios stores the access token in session storage, injects `Authorization: Bearer <token>`, clears the session on HTTP 401, and exposes a typed error message. The Pinia store implements `login`, `loadCurrentUser`, and `logout`.

- [ ] **Step 2: Add route guards and application layout.**

  Unauthenticated users are redirected to `/login`; authenticated users are redirected from `/login` to `/dashboard`. The layout shows the current user's name and role, Dashboard, Projects, and Logout actions. The navigation must not be treated as the permission boundary; the API remains authoritative.

- [ ] **Step 3: Add the login screen.**

  The form has username and password fields, a submit button with loading state, a clear invalid-credentials message, and no development passwords displayed in the UI.

- [ ] **Step 4: Add the project list and creation form.**

  The project list supports lifecycle status filtering, name/code search, loading, empty, and error states. The create action is rendered only for PMO users, while the API also enforces the rule. The form covers project code, name, department, manager, client, region, planned dates, description, and Seafile URL.

- [ ] **Step 5: Add project detail and archive flow.**

  The detail page displays the project baseline and member list. PMO sees the archive action. The archive action requires confirmation, shows a success message, and refreshes the project state.

- [ ] **Step 6: Verify the frontend manually and commit.**

  Run:

  ```powershell
  cd frontend
  npm run typecheck
  npm run build
  ```

  Start backend and frontend, log in as each seeded role, and verify that the visible project list matches the API data scope. Commit with:

  ```powershell
  git add frontend
  git commit -m "feat: add login and project register screens"
  ```

## Task 6: Documentation, end-to-end checkpoint, and Stage 1 handoff

**Files:** `README.md`, `.env.example`, `backend/scripts/seed_demo.py`.

- [ ] **Step 1: Document the exact Windows setup.**

  README must include Python and Node prerequisites, PostgreSQL option, `.env` creation, migration, seed, backend start, frontend start, API docs URL, and test commands.

- [ ] **Step 2: Run the complete automated checks.**

  ```powershell
  cd backend
  pytest -v
  cd ..\frontend
  npm run typecheck
  npm run build
  ```

  Expected: all backend tests pass, TypeScript has no errors, and the production build succeeds.

- [ ] **Step 3: Perform the user acceptance walkthrough.**

  Use the seeded PMO account to create two projects in different departments, assign different managers, and add members. Verify each role's list and detail access, archive one project, and confirm the archived project is excluded from the default list. Record any changed field labels or workflow decisions before Stage 2.

- [ ] **Step 4: Commit the handoff.**

  ```powershell
  git add README.md .env.example
  git commit -m "docs: add local setup and stage 1 verification"
  git status --short --branch
  ```

## Stage 1 Acceptance Gate

Stage 1 is complete only when all of the following are true:

- The application starts locally on Windows with PostgreSQL.
- A PMO can log in and create, view, edit, and archive projects.
- Each other role can log in and sees only its allowed projects.
- No role can bypass project permissions by calling the API directly.
- Automated backend tests, frontend type checking, and production build pass.
- The user has manually tested the workflow and confirmed the project baseline fields before Stage 2 begins.

## Self-review

- **Spec coverage:** Stage 1 covers authentication, role/data permissions, project register, project lifecycle, Seafile URL storage, soft archive, setup, and tests. Stage/module progress, milestones, risks, finance, dashboard metrics, reminders, import, and audit views are intentionally assigned to later stages.
- **Completeness scan:** No unfinished or unspecified implementation step is required in this plan.
- **Type consistency:** Role names, lifecycle statuses, endpoint paths, and project fields are defined once and reused throughout the tasks.
- **Scope check:** This plan is limited to a coherent, testable foundation and does not implement the independent progress, finance, dashboard, or reminder subsystems prematurely.
