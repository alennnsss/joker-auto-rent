import type { BookingStatus, Fuel, Transmission } from '@/api/types'
import { i18n } from '@/i18n'

const NBSP = ' '

/** 15000 → «15 000 ₸» (неразрывные пробелы между разрядами и перед знаком). */
export function formatPrice(value: number | string | null | undefined): string {
  const amount = Math.round(Number(value ?? 0))
  const sign = amount < 0 ? '-' : ''
  const digits = Math.abs(amount)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, NBSP)
  return `${sign}${digits}${NBSP}₸`
}

/** ISO-дата или дата-время → ДД.ММ.ГГГГ (по Алматы для дат со временем). */
export function formatDate(value: string | null | undefined): string {
  if (!value) return ''
  const plain = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)
  if (plain) return `${plain[3]}.${plain[2]}.${plain[1]}`
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return new Intl.DateTimeFormat('ru-RU', {
    timeZone: 'Asia/Almaty',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date)
}

const { t } = i18n.global

/** 1 → «1 сутки» / «1 тәулік» — на текущем языке. */
export function formatDays(n: number): string {
  return t('common.days', n)
}

/** "08:30:00" → "08:30" */
export function formatTime(value: string | null | undefined): string {
  return value ? value.slice(0, 5) : ''
}

export function formatPhoneHref(phone: string): string {
  return `tel:+${phone.replace(/\D/g, '')}`
}

// Подписи к значениям с бэкенда — функции, чтобы перевод брался на момент отрисовки
export const TRANSMISSIONS: Transmission[] = ['automatic', 'manual']
export const FUELS: Fuel[] = ['petrol', 'diesel', 'hybrid', 'electric', 'gas']
export const BOOKING_STATUSES: BookingStatus[] = [
  'pending',
  'confirmed',
  'active',
  'completed',
  'cancelled',
]

export const transmissionLabel = (value: Transmission) => t(`transmission.${value}`)
export const fuelLabel = (value: Fuel) => t(`fuel.${value}`)
export const bookingStatusLabel = (value: BookingStatus) => t(`status.booking.${value}`)
