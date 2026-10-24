import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { User } from '@/api/types'

vi.mock('@/api/auth', () => ({
  authApi: {
    me: vi.fn<() => Promise<User>>(),
    login: vi.fn<() => Promise<unknown>>(),
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

  it('redirects guests from the admin panel to the admin login with redirect param', async () => {
    const router = createAppRouter()
    await router.push('/admin/cars')
    expect(router.currentRoute.value.name).toBe('admin-login')
    expect(router.currentRoute.value.query.redirect).toBe('/admin/cars')
  })

  it('keeps a signed-in admin out of the admin login page', async () => {
    localStorage.setItem('access_token', 'token')
    vi.mocked(authApi.me).mockResolvedValue({ ...client, role: 'admin' })
    const router = createAppRouter()

    await router.push('/admin/login')
    expect(router.currentRoute.value.name).toBe('admin-bookings')
  })

  it('has no client account pages', async () => {
    const router = createAppRouter()
    for (const path of ['/login', '/register', '/account', '/account/bookings']) {
      await router.push(path)
      expect(router.currentRoute.value.name).toBe('not-found')
    }
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
