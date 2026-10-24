import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'

import { currentLocale, i18n } from '@/i18n'

import { tokens } from './tokens'
import type { TokenPair } from './types'

export const http = axios.create({ baseURL: '/api/v1', timeout: 15000 })

http.interceptors.request.use((config) => {
  const access = tokens.access
  if (access) config.headers.Authorization = `Bearer ${access}`
  // Бэкенд отдаёт тексты ошибок (detail) на языке интерфейса
  config.headers['Accept-Language'] = currentLocale()
  return config
})

// Один общий refresh на все запросы, упавшие с 401 одновременно
let refreshing: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const refresh = tokens.refresh
  if (!refresh) return null
  try {
    const { data } = await axios.post<TokenPair>('/api/v1/auth/refresh', {
      refresh_token: refresh,
    })
    tokens.set(data.access_token, data.refresh_token)
    return data.access_token
  } catch {
    tokens.clear()
    return null
  }
}

type RetriableConfig = InternalAxiosRequestConfig & { _retried?: boolean }

http.interceptors.response.use(undefined, async (error: AxiosError) => {
  const config = error.config as RetriableConfig | undefined
  const isAuthCall = config?.url?.startsWith('/auth/')
  if (error.response?.status !== 401 || !config || config._retried || isAuthCall) {
    throw error
  }
  refreshing ??= refreshAccessToken().finally(() => {
    refreshing = null
  })
  const access = await refreshing
  if (!access) throw error
  config._retried = true
  config.headers.Authorization = `Bearer ${access}`
  return http(config)
})

/** Текст ошибки для пользователя (detail с бэкенда уже на языке из Accept-Language). */
export function errorMessage(error: unknown, fallback?: string) {
  if (axios.isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)?.detail
    if (typeof detail === 'string') return detail
    if (!error.response) return i18n.global.t('errors.network')
  }
  return fallback ?? i18n.global.t('errors.generic')
}
