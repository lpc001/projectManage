# Platform System Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current hardcoded single-role authorization with database-driven users, departments, configurable roles, menu/action/API permissions, data scopes, platform-admin APIs, and permission-aware navigation without regressing the existing project register.

**Architecture:** Keep the FastAPI monolith and Vue SPA. Authorization becomes a backend service that resolves a user's active roles, permission codes, and unioned data scopes from PostgreSQL; API dependencies enforce permissions, while the frontend uses `/api/auth/me` only to render the authorized experience. The migration keeps the legacy `sys_user.role` column until the new authorization path has passed regression tests, then removes it in a follow-up migration.

**Tech Stack:** FastAPI 0.162, SQLAlchemy 2.1, Alembic, PostgreSQL, Pydantic 2, Vue 3, TypeScript, Pinia, Element Plus, pytest, TestClient.

---

## Delivery Checkpoints

1. **Authorization foundation:** new tables, seed roles/permissions, migration of existing users, dynamic authorization service, and regression tests.
2. **System management API:** platform-admin CRUD for users, roles, permissions, departments, data scopes, and audit records.
3. **System management UI:** permission-driven navigation, user/role/permission/department pages, and platform-admin acceptance walkthrough.

No new project business module is added until Checkpoint 3 is accepted.

## Current Code Constraints

- `backend/app/models/system.py` currently stores one `UserRole` enum on `sys_user`.
- `backend/app/api/deps.py` currently exposes `require_roles()` and project routes call it directly.
- `backend/app/services/projects.py` currently switches on `UserRole` for data scope.
- `backend/app/core/security.py` currently writes `role` into JWT claims.
- `frontend/src/types/auth.ts`, `AppLayout.vue`, and project views assume one role string.
- `backend/alembic/versions/0001_foundation.py` creates the legacy role column and check constraint.
- Existing project register tests must remain green throughout the migration.

## File Map

### Backend authorization foundation

- Modify: `backend/app/models/system.py` — replace the single role field with role, permission, association, data-scope, and audit models while retaining a temporary legacy column during migration.
- Modify: `backend/app/models/__init__.py` — export all system models.
- Create: `backend/app/models/authorization.py` if the system models become too large; keep one responsibility per module.
- Create: `backend/app/services/authorization.py` — resolve active roles, permission codes, and unioned data scope.
- Modify: `backend/app/api/deps.py` — add `require_permission()` and current authorization context.
- Modify: `backend/app/core/security.py` — remove role claims from new tokens and support token version invalidation.
- Modify: `backend/app/schemas/auth.py` — return roles, menu permissions, action permissions, and API permissions from `/auth/me`.
- Modify: `backend/app/api/routes/auth.py` — return the expanded current-user payload.
- Create: `backend/alembic/versions/0003_system_authorization.py` — add new authorization tables, seed built-ins, and migrate legacy user roles.
- Create: `backend/alembic/versions/0004_remove_legacy_role.py` — remove the legacy `sys_user.role` column after the new path is proven.
- Modify: `backend/scripts/seed_demo.py` — seed one platform admin and preserve the five business roles with deterministic assignments.

### Backend system management API

- Create: `backend/app/schemas/authorization.py` — role, permission, data-scope, and assignment schemas.
- Create: `backend/app/schemas/system_admin.py` — user, department, and audit response schemas.
- Create: `backend/app/api/routes/system_admin.py` — platform-admin endpoints.
- Create: `backend/app/services/system_admin.py` — validation, protected-role rules, and audit writes.
- Modify: `backend/app/api/routes/system.py` — replace role checks with permission checks for lookup endpoints.
- Modify: `backend/app/api/routes/projects.py` — replace PMO role dependency with permission codes.
- Modify: `backend/app/services/projects.py` — consume authorization data-scope predicates instead of `UserRole` branches.
- Modify: `backend/app/main.py` — register the platform-admin router.

### Backend tests

- Modify: `backend/tests/conftest.py` — register new models and reset all authorization tables.
- Modify: `backend/tests/test_system_models.py` — test multiple roles and association uniqueness.
- Modify: `backend/tests/test_auth.py` — test dynamic `/auth/me`, disabled users, token invalidation, and permission resolution.
- Modify: `backend/tests/test_projects.py` — use seeded permission assignments and verify data-scope regression behavior.
- Create: `backend/tests/test_authorization.py` — permission union, data-scope union, disabled role/permission behavior.
- Create: `backend/tests/test_system_admin.py` — platform-admin CRUD and protected-resource rules.

### Frontend system management

- Modify: `frontend/src/types/auth.ts` — replace one role with roles and permission collections.
- Create: `frontend/src/types/system.ts` — users, roles, permissions, departments, and audit types.
- Modify: `frontend/src/api/auth.ts` — consume expanded current-user response.
- Create: `frontend/src/api/systemAdmin.ts` — typed system management API client.
- Modify: `frontend/src/stores/auth.ts` — add `hasPermission()` and `hasAnyPermission()` helpers.
- Modify: `frontend/src/router/index.ts` — route metadata for required menu permissions.
- Modify: `frontend/src/layouts/AppLayout.vue` — render navigation based on menu permissions and show System Management only to authorized users.
- Create: `frontend/src/views/system/UsersView.vue` — user list, enable/disable, reset password, role assignment.
- Create: `frontend/src/views/system/RolesView.vue` — role list and role editor.
- Create: `frontend/src/views/system/PermissionsView.vue` — permission tree and status display.
- Create: `frontend/src/views/system/DepartmentsView.vue` — department tree and maintenance.
- Create: `frontend/src/views/system/AuditView.vue` — audit list and filters.
- Create: `frontend/src/components/PermissionTree.vue` — reusable permission tree with selected-state handling.

## Task 1: Write failing tests for the authorization model

**Files:** `backend/tests/test_system_models.py`, `backend/tests/test_authorization.py`, `backend/tests/conftest.py`.

- [ ] **Step 1: Add model tests for many-to-many roles.**

  Create a user with two roles, persist two `UserRoleLink` records, and assert duplicate `(user_id, role_id)` inserts fail. Assert role and permission codes are unique.

- [ ] **Step 2: Add permission-union tests.**

  Create role A with `project:list`, role B with `project:create`, assign both to one user, and assert the authorization context contains both codes. Disable role B and assert `project:create` disappears without changing the user assignment.

- [ ] **Step 3: Add data-scope union tests.**

  Assert `all` dominates other scopes, `department` and `custom_department` merge department IDs, and `owned` plus `member` are both retained in the resolved context.

- [ ] **Step 4: Run the new tests before implementation.**

  ```powershell
  cd backend
  $env:TEST_DATABASE_URL="postgresql+psycopg2://postgres:<local-password>@127.0.0.1:5432/pm_test"
  .\.venv\Scripts\python.exe -m pytest tests/test_authorization.py tests/test_system_models.py -v
  ```

  Expected: collection or assertion failures because the new models and authorization service do not exist yet.

## Task 2: Add authorization models and migration

**Files:** `backend/app/models/system.py`, `backend/app/models/authorization.py`, `backend/app/models/__init__.py`, `backend/alembic/versions/0003_system_authorization.py`, `backend/alembic/versions/0004_remove_legacy_role.py`.

- [ ] **Step 1: Implement model enums and tables.**

  Define `PermissionType` with `menu`, `action`, and `api`; `DataScopeType` with `all`, `department`, `owned`, `member`, and `custom_department`. Add `Role`, `Permission`, `UserRoleLink`, `RolePermissionLink`, `RoleDepartmentLink`, and `AuditLog` with timestamps, active flags, and uniqueness constraints.

- [ ] **Step 2: Keep the legacy role only as a migration bridge.**

  Add relationships from `User` to roles. Do not use the legacy role in new application services. Keep `User.legacy_role` mapped to the existing database column until migration `0004` is applied.

- [ ] **Step 3: Seed built-in roles and permissions in migration `0003`.**

  Seed `platform_admin`, `boss`, `department_head`, `pmo`, `project_manager`, and `member`. Seed system and current project permissions, including menu, action, and API records. Map old values `boss`, `department_head`, `pmo`, `project_manager`, and `member` into `sys_user_role`.

- [ ] **Step 4: Add migration `0004` to remove legacy authorization.**

  Drop the old role check constraint and column only after all application code uses role associations. The downgrade must restore the column with a default role and must not delete users or projects.

- [ ] **Step 5: Run migration and model tests.**

  ```powershell
  cd backend
  .\.venv\Scripts\python.exe -m alembic upgrade head
  .\.venv\Scripts\python.exe -m pytest tests/test_system_models.py tests/test_authorization.py -v
  ```

## Task 3: Implement dynamic authorization and authentication responses

**Files:** `backend/app/services/authorization.py`, `backend/app/api/deps.py`, `backend/app/core/security.py`, `backend/app/schemas/auth.py`, `backend/app/api/routes/auth.py`, `backend/tests/test_auth.py`, `backend/tests/test_authorization.py`.

- [ ] **Step 1: Implement `AuthorizationContext`.**

  The context exposes `role_codes`, `permission_codes`, `menu_permission_codes`, `action_permission_codes`, `api_permission_codes`, `data_scope_types`, and `custom_department_ids`. It loads only active roles and active permissions.

- [ ] **Step 2: Implement permission dependencies.**

  Add `require_permission("project:create")` and `require_any_permission(...)`. They return HTTP 403 when the current user is active but lacks the permission. They must use the database associations, not JWT role claims.

- [ ] **Step 3: Update token handling.**

  New tokens contain only user ID, token version, and expiration. Incrementing a user's token version on password reset or disable invalidates old tokens. Existing development tokens are allowed to expire naturally.

- [ ] **Step 4: Expand `/api/auth/me`.**

  Return the user, primary department, role list, menu permission codes, action permission codes, and API permission codes. Never return password hashes or raw tokens.

- [ ] **Step 5: Run auth and authorization tests.**

  ```powershell
  cd backend
  .\.venv\Scripts\python.exe -m pytest tests/test_auth.py tests/test_authorization.py -v
  ```

## Task 4: Migrate existing project authorization to permission/data-scope services

**Files:** `backend/app/api/routes/projects.py`, `backend/app/services/projects.py`, `backend/app/api/routes/system.py`, `backend/tests/test_projects.py`.

- [ ] **Step 1: Replace `require_roles()` from project routes.**

  PMO project creation requires `project:create`; archive requires `project:archive`; project reads require `project:list`; edits require `project:update` plus the resolved data scope.

- [ ] **Step 2: Implement reusable data-scope predicates.**

  The project service converts the authorization context to SQL predicates for all, department, owned, member, and custom department scope. Avoid role-name branches in project queries.

- [ ] **Step 3: Preserve existing behavior through assignments.**

  Seed the built-in business roles with the permission/data-scope combinations that reproduce the current behavior. Keep the PMO-only create rule as a permission assignment, not a special role check.

- [ ] **Step 4: Run the complete backend regression suite.**

  ```powershell
  cd backend
  .\.venv\Scripts\python.exe -m pytest -v
  ```

  Expected: all existing project, auth, model, and new authorization tests pass.

## Task 5: Implement platform-admin system management APIs

**Files:** `backend/app/schemas/authorization.py`, `backend/app/schemas/system_admin.py`, `backend/app/services/system_admin.py`, `backend/app/api/routes/system_admin.py`, `backend/app/main.py`, `backend/tests/test_system_admin.py`.

- [ ] **Step 1: Write failing API tests for platform-admin access.**

  Verify that platform admins can list/create/update users, assign multiple roles, create/update roles, assign permissions and data scopes, list permission trees, maintain departments, and query audit records. Verify every non-platform-admin receives 403 for these endpoints.

- [ ] **Step 2: Implement user management.**

  Add list filters for username, display name, department, role, and active state. Create/update validates username uniqueness and department existence. Disable and reset-password increment the token version. Role assignment replaces the selected set atomically.

- [ ] **Step 3: Implement role and permission management.**

  Protect built-in roles and permission codes from deletion. Reject deleting a role with assigned users. Update permission assignments and data scope in one transaction.

- [ ] **Step 4: Implement department management and audit writes.**

  Support department tree reads, create, update, and disable. Reject disabling a department with active users. Record every system management mutation in `sys_audit_log`.

- [ ] **Step 5: Run system-admin API tests.**

  ```powershell
  cd backend
  .\.venv\Scripts\python.exe -m pytest tests/test_system_admin.py -v
  ```

## Task 6: Build permission-aware frontend state and navigation

**Files:** `frontend/src/types/auth.ts`, `frontend/src/types/system.ts`, `frontend/src/api/auth.ts`, `frontend/src/api/systemAdmin.ts`, `frontend/src/stores/auth.ts`, `frontend/src/router/index.ts`, `frontend/src/layouts/AppLayout.vue`.

- [ ] **Step 1: Update frontend auth types and store.**

  Replace `role: UserRole` with `roles: RoleSummary[]` and permission arrays. Implement `hasPermission(code)` and `hasAnyPermission(codes)` using exact code matches.

- [ ] **Step 2: Add typed system-admin API clients.**

  Implement user, role, permission, department, and audit list/mutation functions matching the backend routes. Centralize API error extraction through the existing Axios helper.

- [ ] **Step 3: Add route metadata and guards.**

  Add `meta.requiredPermission` to system-management routes. Unauthenticated users go to login; authenticated users without the required menu permission see a 403 result instead of a blank page.

- [ ] **Step 4: Make the layout permission-driven.**

  Show the System Management navigation only when the user has `system:user:list`, `system:role:list`, or `system:permission:list`. Existing project navigation uses the corresponding menu permissions.

## Task 7: Build system management pages

**Files:** `frontend/src/views/system/UsersView.vue`, `RolesView.vue`, `PermissionsView.vue`, `DepartmentsView.vue`, `AuditView.vue`, `frontend/src/components/PermissionTree.vue`.

- [ ] **Step 1: Build the user management page.**

  Add filters, paginated table, create/edit drawer, active toggle, reset-password action, primary department selector, and multi-role selector. Hide actions when the corresponding action permission is absent.

- [ ] **Step 2: Build the role management page.**

  Add role list, create/edit drawer, protected built-in role indicators, permission tree assignment, and data-scope selector with custom department selection.

- [ ] **Step 3: Build permission and department pages.**

  Render permission tree with type and active state. Render department tree with create/edit/disable actions and active-user validation feedback.

- [ ] **Step 4: Build audit page.**

  Add filters for operator, module, operation, result, target, and date range. Display summaries without passwords, tokens, or sensitive credential values.

- [ ] **Step 5: Verify frontend quality.**

  ```powershell
  cd frontend
  npm run typecheck
  npm run build
  ```

## Task 8: Update seed data, documentation, and acceptance checkpoint

**Files:** `backend/scripts/seed_demo.py`, `README.md`, `.env.example`, backend and frontend tests.

- [ ] **Step 1: Update seed data.**

  Create `admin@example.com` with the platform-admin role, preserve the five business demo users, and assign permissions/data scopes that reproduce the current project behavior. Keep the development password documented and refuse seeding in production.

- [ ] **Step 2: Run a clean database verification.**

  ```powershell
  cd backend
  .\.venv\Scripts\python.exe -m alembic downgrade base
  .\.venv\Scripts\python.exe -m alembic upgrade head
  .\.venv\Scripts\python.exe -m scripts.seed_demo
  .\.venv\Scripts\python.exe -m pytest -v
  ```

- [ ] **Step 3: Run the UI acceptance walkthrough.**

  Verify platform admin can create a role, assign `project:list` and `project:create`, assign a data scope, create a user with two roles, and observe the menu/action changes after reload. Verify a non-admin cannot open system management or call its API.

- [ ] **Step 4: Commit each checkpoint and final system-management implementation.**

  Use focused commits:

  ```powershell
  git commit -m "feat: add database-driven authorization"
  git commit -m "feat: add platform system management API"
  git commit -m "feat: add system management UI"
  ```

## Acceptance Gate

The system-management stage is complete only when:

- Platform admin is independent from project business roles.
- Roles, permissions, and data scopes are configurable in the UI.
- A user can hold multiple roles and receives the union of permissions/scopes.
- Backend APIs enforce permission codes and data scopes directly.
- Existing project register behavior passes regression tests.
- User, role, permission, department, and audit mutations are tested and auditable.
- Frontend type checking and production build pass.

## Self-review

- **Spec coverage:** All decisions in `2026-11-05-system-management-design.md` map to tasks: models, migration, dynamic authorization, system API, UI, protection rules, audit, seed migration, and project regression.
- **Completeness scan:** Every task names files, a concrete behavior, a verification command, and an expected result where code is introduced.
- **Type consistency:** Role codes, permission codes, data-scope values, API paths, and frontend permission helpers are defined consistently across the tasks.
- **Scope check:** This plan does not add new project business features; it only creates the platform foundation required by later stages.
