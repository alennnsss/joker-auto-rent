import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { authApi } from '@/api/auth'
import { tokens } from '@/api/tokens'
import type { TokenPair, User } from '@/api/types'

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
    logout,
  }
})
