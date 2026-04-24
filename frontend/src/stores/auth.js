/**
 * Pinia Store: 认证状态管理
 */
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import api from '../api/axios'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isStudent = computed(() => user.value?.role === 'student')
  const displayName = computed(() => user.value?.display_name || user.value?.username || '')

  // ---------- Actions ----------

  async function login(username, password) {
    const res = await api.post('/api/auth/login', { username, password })
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', res.data.access_token)
    return res.data
  }

  async function register(data) {
    const res = await api.post('/api/auth/register', data)
    return res.data
  }

  async function fetchMe() {
    try {
      const res = await api.get('/api/auth/me')
      user.value = res.data
    } catch {
      logout()
    }
  }

  async function changePassword(oldPassword, newPassword) {
    await api.put('/api/auth/password', { old_password: oldPassword, new_password: newPassword })
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  // 恢复登录状态
  async function restore() {
    if (token.value) {
      await fetchMe()
    }
  }

  return { token, user, isLoggedIn, isAdmin, isStudent, displayName, login, register, fetchMe, changePassword, logout, restore }
})
