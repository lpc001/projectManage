import type {
  DepartmentOption,
  ProjectCreatePayload,
  ProjectDetail,
  ProjectListItem,
  ProjectUpdatePayload,
  UserOption,
} from '@/types/project'

import { http } from './http'

export async function fetchProjects(includeArchived = false) {
  const { data } = await http.get<ProjectListItem[]>('/projects', {
    params: { include_archived: includeArchived },
  })
  return data
}

export async function fetchProject(projectId: number, includeArchived = false) {
  const { data } = await http.get<ProjectDetail>(`/projects/${projectId}`, {
    params: { include_archived: includeArchived },
  })
  return data
}

export async function createProject(payload: ProjectCreatePayload) {
  const { data } = await http.post<ProjectDetail>('/projects', payload)
  return data
}

export async function updateProject(projectId: number, payload: ProjectUpdatePayload) {
  const { data } = await http.patch<ProjectDetail>(`/projects/${projectId}`, payload)
  return data
}

export async function archiveProject(projectId: number) {
  const { data } = await http.post<ProjectDetail>(`/projects/${projectId}/archive`)
  return data
}

export async function fetchDepartments() {
  const { data } = await http.get<DepartmentOption[]>('/system/departments')
  return data
}

export async function fetchProjectManagers(departmentId?: number) {
  const { data } = await http.get<UserOption[]>('/system/users', {
    params: { role: 'project_manager', department_id: departmentId },
  })
  return data
}

