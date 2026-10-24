import { http } from './http'
import type {
  AdminBooking,
  BookingStatus,
  Car,
  CarFilters,
  CarList,
  CarPayload,
  Category,
  Payment,
  User,
} from './types'

export const adminApi = {
  async cars(filters: CarFilters = {}) {
    const { data } = await http.get<CarList>('/admin/cars', { params: filters })
    return data
  },
  async car(id: number) {
    const { data } = await http.get<Car>(`/admin/cars/${id}`)
    return data
  },
  async createCar(payload: CarPayload) {
    const { data } = await http.post<Car>('/admin/cars', payload)
    return data
  },
  async updateCar(id: number, payload: Partial<CarPayload>) {
    const { data } = await http.patch<Car>(`/admin/cars/${id}`, payload)
    return data
  },
  async deleteCar(id: number) {
    await http.delete(`/admin/cars/${id}`)
  },
  async uploadImage(carId: number, file: File) {
    const form = new FormData()
    form.append('file', file)
    const { data } = await http.post<Car>(`/admin/cars/${carId}/images`, form)
    return data
  },
  async addImageUrl(carId: number, url: string) {
    const { data } = await http.post<Car>(`/admin/cars/${carId}/images/url`, { url })
    return data
  },
  async deleteImage(carId: number, imageId: number) {
    const { data } = await http.delete<Car>(`/admin/cars/${carId}/images/${imageId}`)
    return data
  },
  async createCategory(name: string) {
    const { data } = await http.post<Category>('/admin/categories', { name })
    return data
  },
  async bookings(status?: BookingStatus) {
    const { data } = await http.get<AdminBooking[]>('/admin/bookings', {
      params: { status, limit: 200 },
    })
    return data
  },
  async setBookingStatus(id: number, status: BookingStatus) {
    const { data } = await http.patch<AdminBooking>(`/admin/bookings/${id}/status`, { status })
    return data
  },
  async users() {
    const { data } = await http.get<User[]>('/admin/users', { params: { limit: 200 } })
    return data
  },
  async payments() {
    const { data } = await http.get<Payment[]>('/admin/payments', { params: { limit: 200 } })
    return data
  },
}
