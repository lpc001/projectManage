import type { LoginResponse, UserSummary } from '@/types/auth'

import { http } from './http'

export async function login(username: string, password: string) {
  const body = new URLSearchParams({ username, password })
  const { data } = await http.post<LoginResponse>('/auth/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export async function getCurrentUser() {
  const { data } = await http.get<UserSummary>('/auth/me')
  return data
}

