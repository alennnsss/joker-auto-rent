import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { authApi } from '@/api/auth'
import { tokens } from '@/api/tokens'
import type { RegisterPayload, TokenPair, User } from '@/api/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const initialized = ref(false)

  const isAuthenticated = computed(() => user.value !== null)
  const isAdmin = computed(() => user.value?.role === 'admin')

  let initPromise: Promise<void> | null = null

  /** Восстанавливает сессию из сохранённых токенов. Вызывается роутером один раз. */
  function init(): Promise<void> {
    initPromise ??= (async () => {
      if (tokens.access || tokens.refresh) {
        try {
          user.value = await authApi.me()
        } catch {
          tokens.clear()
          user.value = null
        }
      }
      initialized.value = true
    })()
    return initPromise
  }

  async function applyTokens(pair: TokenPair) {
    tokens.set(pair.access_token, pair.refresh_token)
    user.value = await authApi.me()
  }

  async function login(email: string, password: string) {
    await applyTokens(await authApi.login(email, password))
  }

  async function register(payload: RegisterPayload) {
    await applyTokens(await authApi.register(payload))
  }

  async function updateProfile(payload: Partial<Pick<User, 'full_name' | 'phone'>>) {
    user.value = await authApi.updateMe(payload)
  }

  async function verifyEmail(code: string) {
    user.value = await authApi.verifyEmail(code)
  }

  async function resendVerification() {
    await authApi.resendVerification()
  }

  function logout() {
    tokens.clear()
    user.value = null
  }

  return {
    user,
    initialized,
    isAuthenticated,
    isAdmin,
    init,
    login,
    register,
    updateProfile,
    verifyEmail,
    resendVerification,
    logout,
  }
})
