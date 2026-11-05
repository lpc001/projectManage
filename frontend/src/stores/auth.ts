import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { getCurrentUser, login as loginRequest } from '@/api/auth'
import type { UserSummary } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(sessionStorage.getItem('access_token'))
  const user = ref<UserSummary | null>(null)
  const loading = ref(false)
  const isAuthenticated = computed(() => Boolean(accessToken.value && user.value))

  function hasPermission(code: string) {
    if (!user.value) return false
    return [
      ...user.value.menu_permission_codes,
      ...user.value.action_permission_codes,
      ...user.value.api_permission_codes,
    ].includes(code)
  }

  function hasAnyPermission(codes: string[]) {
    return codes.some((code) => hasPermission(code))
  }

  async function login(username: string, password: string) {
    loading.value = true
    try {
      const response = await loginRequest(username, password)
      accessToken.value = response.access_token
      user.value = response.user
      sessionStorage.setItem('access_token', response.access_token)
    } finally {
      loading.value = false
    }
  }

  async function loadCurrentUser() {
    if (!accessToken.value) return false
    try {
      user.value = await getCurrentUser()
      return true
    } catch {
      logout()
      return false
    }
  }

  function logout() {
    accessToken.value = null
    user.value = null
    sessionStorage.removeItem('access_token')
  }

  return { accessToken, user, loading, isAuthenticated, hasPermission, hasAnyPermission, login, loadCurrentUser, logout }
})

