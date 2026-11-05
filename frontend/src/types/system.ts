import type { RoleSummary } from './auth'

export type DataScopeType = 'all' | 'department' | 'owned' | 'member' | 'custom_department'
export type PermissionType = 'menu' | 'action' | 'api'

export interface SystemUser {
  id: number
  username: string
  display_name: string
  department_id: number
  is_active: boolean
  roles: RoleSummary[]
  created_at: string
  updated_at: string
}

export interface SystemRole {
  id: number
  code: string
  name: string
  description: string | null
  is_builtin: boolean
  is_active: boolean
  data_scope: DataScopeType
  permission_ids: number[]
}

export interface SystemPermission {
  id: number
  code: string
  name: string
  permission_type: PermissionType
  parent_id: number | null
  route_path: string | null
  http_method: string | null
  api_path: string | null
  sort_order: number
  is_builtin: boolean
  is_active: boolean
}

export interface SystemDepartment {
  id: number
  name: string
  code: string
  parent_id: number | null
  is_active: boolean
}

export interface AuditLog {
  id: number
  user_id: number | null
  module: string
  action: string
  target_type: string | null
  target_id: string | null
  result: string
  summary: string | null
  created_at: string
}

