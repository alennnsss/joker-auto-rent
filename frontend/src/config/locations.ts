import { i18n } from '@/i18n'

import { contacts } from './contacts'

export const OFFICE_LOCATION = `Офис: ${contacts.address}`

// Точки выдачи и возврата. В бронь сохраняется value на русском (его читает менеджер),
// на экране показывается перевод по key. «Доставка» хранится как «Доставка: <адрес>».
export const LOCATIONS = [
  { value: OFFICE_LOCATION, key: 'office' },
  { value: 'Аэропорт Алматы (ALA)', key: 'airport' },
  { value: 'Ж/д вокзал Алматы-1', key: 'station1' },
  { value: 'Ж/д вокзал Алматы-2', key: 'station2' },
] as const

export const DELIVERY_PREFIX = 'Доставка: '

/** Сохранённое значение места → подпись на текущем языке. */
export function locationLabel(value: string): string {
  const { t } = i18n.global
  const known = LOCATIONS.find((l) => l.value === value)
  if (known) return t(`locations.${known.key}`, { address: t('contacts.address') })
  if (value.startsWith(DELIVERY_PREFIX)) {
    return t('locations.deliveryTo', { address: value.slice(DELIVERY_PREFIX.length) })
  }
  return value
}

export function isLocationValid(location: string): boolean {
  if (location.startsWith(DELIVERY_PREFIX)) {
    return location.slice(DELIVERY_PREFIX.length).trim().length >= 3
  }
  return location.trim().length >= 2
}

// Работаем круглосуточно — время с шагом 30 минут
export const TIMES = Array.from({ length: 48 }, (_, i) => {
  const hours = String(Math.floor(i / 2)).padStart(2, '0')
  return `${hours}:${i % 2 ? '30' : '00'}`
})
