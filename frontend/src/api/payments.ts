import { http } from './http'
import type { PaymentInit } from './types'

export const paymentsApi = {
  async create(bookingId: number) {
    const { data } = await http.post<PaymentInit>(`/payments/${bookingId}/create`)
    return data
  },
}
