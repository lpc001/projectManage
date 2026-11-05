export type ProjectLifecycleStatus = 'planning' | 'active' | 'completed' | 'paused' | 'archived'

export interface ProjectListItem {
  id: number
  code: string
  name: string
  department_id: number
  project_manager_id: number
  project_manager_name: string
  lifecycle_status: ProjectLifecycleStatus
  planned_end_date: string
  is_archived: boolean
  updated_at: string
}

export interface ProjectDetail extends ProjectListItem {
  description: string | null
  client_name: string | null
  region: string | null
  planned_start_date: string
  seafile_url: string | null
}

export interface ProjectCreatePayload {
  code: string
  name: string
  description?: string
  department_id: number
  project_manager_id: number
  client_name?: string
  region?: string
  planned_start_date: string
  planned_end_date: string
  seafile_url?: string
}

export interface ProjectUpdatePayload {
  name?: string
  description?: string
  department_id?: number
  project_manager_id?: number
  client_name?: string
  region?: string
  planned_start_date?: string
  planned_end_date?: string
  lifecycle_status?: ProjectLifecycleStatus
  seafile_url?: string
}

export interface DepartmentOption {
  id: number
  name: string
  code: string
}

export interface UserOption {
  id: number
  username: string
  display_name: string
  role: string
  department_id: number
}

