import { http } from './http'
import type { RegisterPayload, TokenPair, User } from './types'

export const authApi = {
  async login(email: string, password: string) {
    const { data } = await http.post<TokenPair>('/auth/login', { email, password })
    return data
  },
  async register(payload: RegisterPayload) {
    const { data } = await http.post<TokenPair>('/auth/register', payload)
    return data
  },
  async me() {
    const { data } = await http.get<User>('/auth/me')
    return data
  },
  async verifyEmail(code: string) {
    const { data } = await http.post<User>('/auth/verify-email', { code })
    return data
  },
  async resendVerification() {
    await http.post('/auth/resend-verification')
  },
  async updateMe(payload: Partial<Pick<User, 'full_name' | 'phone'>>) {
    const { data } = await http.patch<User>('/auth/me', payload)
    return data
  },
}
