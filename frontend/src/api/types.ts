// Типы соответствуют Pydantic-схемам бэкенда (backend/app/schemas).
// Деньги приходят строкой ("15000.00"), даты — ISO (YYYY-MM-DD).

export type UserRole = 'client' | 'admin'
export type Transmission = 'automatic' | 'manual'
export type Fuel = 'petrol' | 'diesel' | 'hybrid' | 'electric' | 'gas'
export type BookingStatus = 'pending' | 'confirmed' | 'active' | 'completed' | 'cancelled'
export type Money = string

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface User {
  id: number
  email: string
  phone: string | null
  full_name: string
  role: UserRole
  email_verified: boolean
  created_at: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  phone: string
}

export interface Category {
  id: number
  name: string
}

export interface CarImage {
  id: number
  url: string
  sort_order: number
}

export interface CarShort {
  id: number
  brand: string
  model: string
  year: number
  images: CarImage[]
}

export interface Car extends CarShort {
  category: Category
  transmission: Transmission
  fuel: Fuel
  seats: number
  price_per_day: Money
  deposit: Money
  description: string
  is_active: boolean
  created_at: string
}

export interface CarList {
  items: Car[]
  total: number
}

export type CarSort = 'price_asc' | 'price_desc' | 'newest'

export interface CarFilters {
  category_id?: number
  transmission?: Transmission
  min_price?: number
  max_price?: number
  seats?: number
  start_date?: string
  end_date?: string
  sort?: CarSort
  limit?: number
  offset?: number
}

export interface DateRange {
  start_date: string
  end_date: string
}

export interface Availability {
  car_id: number
  busy: DateRange[]
  available: boolean | null
  days: number | null
  total_price: Money | null
}

export interface Booking {
  id: number
  car: CarShort
  start_date: string
  end_date: string
  pickup_location: string
  return_location: string
  /** HH:MM:SS */
  pickup_time: string
  return_time: string
  days: number
  total_price: Money
  status: BookingStatus
  created_at: string
}

export interface AdminBooking extends Booking {
  user: User
}

export interface BookingPayload {
  car_id: number
  start_date: string
  end_date: string
  pickup_location: string
  return_location: string
  pickup_time: string
  return_time: string
}

export interface CarPayload {
  brand: string
  model: string
  year: number
  category_id: number
  transmission: Transmission
  fuel: Fuel
  seats: number
  price_per_day: string
  deposit: string
  description: string
  is_active: boolean
}
