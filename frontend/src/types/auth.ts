export interface RoleSummary {
  code: string
  name: string
}

export interface UserSummary {
  id: number
  username: string
  display_name: string
  department_id: number
  roles: RoleSummary[]
  menu_permission_codes: string[]
  action_permission_codes: string[]
  api_permission_codes: string[]
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserSummary
}

