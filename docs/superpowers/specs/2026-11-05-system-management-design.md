# 平台系统管理设计

## 1. 目标

在项目业务功能之前，建立平台级的用户、部门、角色、权限、数据范围和操作审计能力。系统管理必须由数据库配置驱动，使平台管理员可以在不修改代码的情况下调整角色授权，并保证后端 API 始终执行权限校验。

本阶段不改变现有项目台账的业务目标，只替换其硬编码的角色判断和数据范围实现。

## 2. 已确认决策

- 角色和权限均可配置。
- 新增独立的“平台管理员”角色。
- 权限控制到菜单、按钮/操作和 API 三层。
- 数据范围支持全部数据、所属部门、本人负责、本人参与和自定义部门。
- 一个用户可以拥有多个角色。
- 多角色的权限和数据范围取并集。
- 每个用户保留一个主部门；跨部门访问通过角色数据范围实现。
- 客户和第三方不进入本阶段的系统管理范围。

## 3. 领域模型

### 3.1 用户

用户字段包括：

- 登录名
- 显示名
- 密码哈希
- 主部门
- 启用状态
- 最后登录时间
- 创建和更新时间

用户通过 `sys_user_role` 关联多个角色，不再在用户表中保存单一角色字段。

### 3.2 部门

部门字段包括：

- 部门名称
- 部门编码
- 上级部门
- 启用状态
- 创建和更新时间

第一阶段支持部门树结构，但用户只保存一个主部门。自定义数据范围通过角色和部门关联实现。

### 3.3 角色

角色字段包括：

- 角色编码
- 角色名称
- 描述
- 是否系统内置
- 是否启用
- 创建和更新时间

系统预置角色：

- `platform_admin`：平台管理员
- `boss`：老板
- `department_head`：部门负责人
- `pmo`：PMO
- `project_manager`：项目经理
- `member`：项目成员

系统内置角色不能直接删除。平台管理员角色和最后一个平台管理员账号受到保护。

### 3.4 权限

权限字段包括：

- 权限编码
- 权限名称
- 权限类型：`menu`、`action`、`api`
- 父权限
- 前端路由或菜单信息
- API HTTP 方法和路径（API 权限）
- 排序号
- 启用状态
- 是否系统内置

权限编码必须稳定、唯一。示例：

```text
system:user:list
system:user:create
system:user:update
system:user:disable
system:role:list
system:role:update
system:permission:list
system:department:update
project:list
project:create
project:update
project:archive
```

### 3.5 数据范围

角色的数据范围类型：

- `all`：全部数据
- `department`：用户主部门及其组织范围内的数据
- `owned`：用户作为负责人负责的数据
- `member`：用户作为成员参与的数据
- `custom_department`：角色明确绑定的部门数据

同一用户拥有多个角色时：

- 任一角色为 `all`，最终范围为全部数据。
- 其他范围取并集。
- 自定义部门取所有角色绑定部门的并集。

### 3.6 审计日志

审计字段包括：

- 操作人
- 操作时间
- 操作模块
- 操作类型
- 目标类型和目标 ID
- 请求方法和路径
- 结果状态
- 关键变更摘要

密码和 Token 永远不写入审计日志。

## 4. 数据表

```text
sys_user
sys_department
sys_role
sys_permission
sys_user_role
sys_role_permission
sys_role_department
sys_audit_log
```

### 4.1 关系约束

- 用户名、部门编码、角色编码和权限编码唯一。
- 用户-角色关系唯一。
- 角色-权限关系唯一。
- 角色-自定义部门关系唯一。
- 停用用户不能登录，也不能调用业务 API。
- 停用角色不再授予新权限，但历史审计仍保留。
- 停用权限不再通过授权计算，但权限记录不物理删除。

## 5. 授权流程

```text
请求携带 JWT
  ↓
解析用户身份
  ↓
加载用户有效角色
  ↓
加载角色有效权限和数据范围
  ↓
校验 API 权限
  ↓
把数据范围转换为查询条件
  ↓
执行 API
  ↓
写入关键操作审计
```

JWT 只包含用户 ID 和过期时间，不缓存完整角色或权限。权限变更后，用户重新请求即可获得最新授权结果；后续可以增加短时缓存，但不作为本阶段前置依赖。

## 6. API 设计

### 6.1 用户管理

- `GET /api/system/users`
- `POST /api/system/users`
- `GET /api/system/users/{user_id}`
- `PATCH /api/system/users/{user_id}`
- `POST /api/system/users/{user_id}/enable`
- `POST /api/system/users/{user_id}/disable`
- `POST /api/system/users/{user_id}/reset-password`
- `PUT /api/system/users/{user_id}/roles`

### 6.2 角色管理

- `GET /api/system/roles`
- `POST /api/system/roles`
- `GET /api/system/roles/{role_id}`
- `PATCH /api/system/roles/{role_id}`
- `DELETE /api/system/roles/{role_id}`
- `PUT /api/system/roles/{role_id}/permissions`
- `PUT /api/system/roles/{role_id}/data-scope`

### 6.3 权限和部门

- `GET /api/system/permissions/tree`
- `PATCH /api/system/permissions/{permission_id}`
- `GET /api/system/departments/tree`
- `POST /api/system/departments`
- `PATCH /api/system/departments/{department_id}`
- `POST /api/system/departments/{department_id}/disable`

### 6.4 当前用户

`GET /api/auth/me` 返回：

- 用户基本信息
- 主部门
- 当前有效角色列表
- 菜单权限编码
- 操作权限编码

## 7. 前端页面

平台管理员看到“系统管理”导航，包含：

- 用户管理
- 角色管理
- 权限目录
- 部门管理
- 操作审计

页面要求：

- 用户列表支持姓名/账号、部门、状态和角色筛选。
- 用户编辑支持启停、主部门和多角色分配。
- 角色编辑使用权限树，区分菜单、按钮/API 权限，并配置数据范围。
- 权限目录按树展示，系统权限编码不可直接删除。
- 部门管理使用树形结构，停用前检查是否仍有启用用户。
- 所有写操作显示明确成功/失败反馈。

## 8. 迁移策略

当前系统的 `sys_user.role` 单角色字段和 `UserRole` 枚举只作为迁移输入：

1. 新增角色、权限及关系表。
2. 创建六个预置角色。
3. 根据旧角色值把现有用户迁移到 `sys_user_role`。
4. 创建初始平台管理员账号或由部署脚本指定账号。
5. 修改认证响应、授权依赖和项目数据范围服务。
6. 通过回归测试后，移除旧的单角色字段和枚举依赖。

迁移必须可重复执行，不能覆盖已有用户密码、项目或审计数据。

## 9. 安全规则

- 密码只保存 bcrypt 哈希。
- 重置密码后使现有登录 Token 失效，或通过用户认证版本号强制重新登录。
- 停用用户立即禁止登录和 API 访问。
- 删除角色前检查绑定用户；系统内置角色不允许删除。
- 禁止删除或停用最后一个平台管理员。
- 后端 API 权限校验失败统一返回 HTTP 403，不泄漏资源是否存在。
- 所有系统管理写操作写入审计日志。

## 10. 测试和验收

### 10.1 授权计算

- 单角色菜单、操作和 API 权限正确。
- 多角色权限取并集。
- `all` 数据范围覆盖其他范围。
- 自定义部门范围只返回绑定部门数据。
- 停用角色和权限不再参与授权。

### 10.2 管理规则

- 平台管理员可以维护用户、角色、权限和部门。
- 非平台管理员不能调用系统管理 API。
- 一个用户可以分配多个角色。
- 不能删除或停用最后一个平台管理员。
- 停用用户不能登录。

### 10.3 回归测试

- PMO 仍可创建项目。
- 项目经理仍只能编辑负责项目。
- 项目成员仍只能查看参与项目。
- 项目 API 不能通过隐藏前端按钮绕过权限。
- 用户、角色和权限写操作生成审计记录。

## 11. 阶段交付

本设计拆为三个可验收阶段：

1. 授权模型、数据库迁移和授权服务。
2. 系统管理 API 和审计接口。
3. 系统管理前端、权限驱动导航和验收回归。

在系统管理阶段完成并验收前，不继续增加新的项目业务模块。
