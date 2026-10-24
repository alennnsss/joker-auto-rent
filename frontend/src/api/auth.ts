import { http } from './http'
import type { TokenPair, User } from './types'

// Аккаунты есть только у администраторов: клиенты бронируют через WhatsApp
export const authApi = {
  async login(email: string, password: string) {
    const { data } = await http.post<TokenPair>('/auth/login', { email, password })
    return data
  },
  async me() {
    const { data } = await http.get<User>('/auth/me')
    return data
  },
}
