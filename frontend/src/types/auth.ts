export type UserRole = 'boss' | 'department_head' | 'pmo' | 'project_manager' | 'member'

export interface UserSummary {
  id: number
  username: string
  display_name: string
  role: UserRole
  department_id: number
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserSummary
}

