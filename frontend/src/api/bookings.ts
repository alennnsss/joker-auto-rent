import { http } from './http'
import type { Booking, BookingPayload } from './types'

export const bookingsApi = {
  async create(payload: BookingPayload) {
    const { data } = await http.post<Booking>('/bookings', payload)
    return data
  },
  async my() {
    const { data } = await http.get<Booking[]>('/bookings/my')
    return data
  },
  async get(id: number) {
    const { data } = await http.get<Booking>(`/bookings/${id}`)
    return data
  },
  async cancel(id: number) {
    const { data } = await http.post<Booking>(`/bookings/${id}/cancel`)
    return data
  },
}
