import type { DataScopeType, AuditLog, SystemDepartment, SystemPermission, SystemRole, SystemUser } from '@/types/system'

import { http } from './http'

export async function listSystemUsers(params?: { username?: string; department_id?: number; is_active?: boolean }) {
  const { data } = await http.get<SystemUser[]>('/system-admin/users', { params })
  return data
}

export async function createSystemUser(payload: { username: string; display_name: string; password: string; department_id: number; role_ids: number[] }) {
  const { data } = await http.post<SystemUser>('/system-admin/users', payload)
  return data
}

export async function updateSystemUser(userId: number, payload: { display_name?: string; department_id?: number; is_active?: boolean }) {
  const { data } = await http.patch<SystemUser>(`/system-admin/users/${userId}`, payload)
  return data
}

export async function disableSystemUser(userId: number) {
  const { data } = await http.post<SystemUser>(`/system-admin/users/${userId}/disable`)
  return data
}

export async function setSystemUserRoles(userId: number, roleIds: number[]) {
  const { data } = await http.put<SystemUser>(`/system-admin/users/${userId}/roles`, roleIds)
  return data
}

export async function listSystemRoles() {
  const { data } = await http.get<SystemRole[]>('/system-admin/roles')
  return data
}

export async function createSystemRole(payload: { code: string; name: string; description?: string; data_scope: DataScopeType }) {
  const { data } = await http.post<SystemRole>('/system-admin/roles', payload)
  return data
}

export async function updateSystemRole(roleId: number, payload: { name?: string; description?: string; is_active?: boolean; data_scope?: DataScopeType }) {
  const { data } = await http.patch<SystemRole>(`/system-admin/roles/${roleId}`, payload)
  return data
}

export async function updateRolePermissions(roleId: number, permissionIds: number[]) {
  const { data } = await http.put<SystemRole>(`/system-admin/roles/${roleId}/permissions`, { permission_ids: permissionIds })
  return data
}

export async function updateRoleDataScope(roleId: number, dataScope: DataScopeType, departmentIds: number[]) {
  const { data } = await http.put<SystemRole>(`/system-admin/roles/${roleId}/data-scope`, { data_scope: dataScope, department_ids: departmentIds })
  return data
}

export async function listSystemPermissions() {
  const { data } = await http.get<SystemPermission[]>('/system-admin/permissions')
  return data
}

export async function listSystemDepartments() {
  const { data } = await http.get<SystemDepartment[]>('/system-admin/departments')
  return data
}

export async function createSystemDepartment(payload: { name: string; code: string; parent_id?: number }) {
  const { data } = await http.post<SystemDepartment>('/system-admin/departments', payload)
  return data
}

export async function updateSystemDepartment(departmentId: number, payload: { name?: string; parent_id?: number; is_active?: boolean }) {
  const { data } = await http.patch<SystemDepartment>(`/system-admin/departments/${departmentId}`, payload)
  return data
}

export async function listAuditLogs() {
  const { data } = await http.get<AuditLog[]>('/system-admin/audit')
  return data
}

