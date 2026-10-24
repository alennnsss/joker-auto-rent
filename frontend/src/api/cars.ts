import { http } from './http'
import type { Availability, Car, CarFilters, CarList, Category, PublicConfig } from './types'

export const carsApi = {
  async list(filters: CarFilters = {}) {
    const { data } = await http.get<CarList>('/cars', { params: filters })
    return data
  },
  async get(id: number) {
    const { data } = await http.get<Car>(`/cars/${id}`)
    return data
  },
  async categories() {
    const { data } = await http.get<Category[]>('/cars/categories')
    return data
  },
  async availability(id: number, startDate?: string, endDate?: string) {
    const params = startDate && endDate ? { start_date: startDate, end_date: endDate } : {}
    const { data } = await http.get<Availability>(`/cars/${id}/availability`, { params })
    return data
  },
}

export const configApi = {
  async get() {
    const { data } = await http.get<PublicConfig>('/config')
    return data
  },
}
