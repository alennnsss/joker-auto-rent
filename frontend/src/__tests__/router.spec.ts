import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { User } from '@/api/types'

vi.mock('@/api/auth', () => ({
  authApi: {
    me: vi.fn<() => Promise<User>>(),
    login: vi.fn<() => Promise<unknown>>(),
    register: vi.fn<() => Promise<unknown>>(),
    updateMe: vi.fn<() => Promise<User>>(),
  },
}))

const { authApi } = await import('@/api/auth')
const { createAppRouter } = await import('@/router')

const client: User = {
  id: 1,
  email: 'client@example.com',
  phone: '+7 (701) 123-45-67',
  full_name: 'Клиент',
  role: 'client',
  email_verified: true,
  created_at: '2026-10-01T00:00:00Z',
}

describe('router guards', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.mocked(authApi.me).mockReset()
  })

  it('redirects guests from protected pages to login with redirect param', async () => {
    const router = createAppRouter()
    await router.push('/account/bookings')
    expect(router.currentRoute.value.name).toBe('login')
    expect(router.currentRoute.value.query.redirect).toBe('/account/bookings')
  })

  it('lets authenticated users into the account and keeps them out of /login', async () => {
    localStorage.setItem('access_token', 'token')
    vi.mocked(authApi.me).mockResolvedValue(client)
    const router = createAppRouter()

    await router.push('/account/bookings')
    expect(router.currentRoute.value.name).toBe('account-bookings')

    await router.push('/login')
    expect(router.currentRoute.value.name).toBe('home')
  })

  it('blocks non-admins from the admin panel', async () => {
    localStorage.setItem('access_token', 'token')
    vi.mocked(authApi.me).mockResolvedValue(client)
    const router = createAppRouter()

    await router.push('/admin/cars')
    expect(router.currentRoute.value.name).toBe('home')
  })

  it('allows admins into the admin panel', async () => {
    localStorage.setItem('access_token', 'token')
    vi.mocked(authApi.me).mockResolvedValue({ ...client, role: 'admin' })
    const router = createAppRouter()

    await router.push('/admin/cars')
    expect(router.currentRoute.value.name).toBe('admin-cars')
  })

  it('sets page title and resolves unknown paths to not-found', async () => {
    const router = createAppRouter()
    await router.push('/no-such-page')
    expect(router.currentRoute.value.name).toBe('not-found')
    expect(document.title).toBe('Страница не найдена — Joker Auto Rent')
  })
})
