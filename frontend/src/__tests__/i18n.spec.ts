import { mount, RouterLinkStub } from '@vue/test-utils'
import { afterEach, describe, expect, it } from 'vitest'

import type { Car } from '@/api/types'
import CarCard from '@/components/CarCard.vue'
import { DELIVERY_PREFIX, OFFICE_LOCATION, locationLabel } from '@/config/locations'
import { currentLocale, i18n, ruPluralIndex, setLocale } from '@/i18n'
import en from '@/i18n/locales/en'
import kk from '@/i18n/locales/kk'
import ru from '@/i18n/locales/ru'
import { bookingStatusLabel, categoryLabel, formatDays } from '@/utils/format'

/** Все пути ключей словаря: «common.save», «benefits.prices.title», … */
function keyPaths(messages: object, prefix = ''): string[] {
  return Object.entries(messages).flatMap(([key, value]) =>
    typeof value === 'object' && value !== null
      ? keyPaths(value, `${prefix}${key}.`)
      : [`${prefix}${key}`],
  )
}

afterEach(() => {
  setLocale('ru')
  localStorage.clear()
})

describe('dictionaries', () => {
  it('kk has exactly the same keys as ru', () => {
    expect(keyPaths(kk).sort()).toEqual(keyPaths(ru).sort())
  })

  it('kk has no empty translations', () => {
    const empty = keyPaths(kk).filter((path) => !i18n.global.t(path, {}, { locale: 'kk' }).trim())
    expect(empty).toEqual([])
  })

  it('en has exactly the same keys as ru', () => {
    expect(keyPaths(en).sort()).toEqual(keyPaths(ru).sort())
  })

  it('en has no empty translations', () => {
    const empty = keyPaths(en).filter((path) => !i18n.global.t(path, {}, { locale: 'en' }).trim())
    expect(empty).toEqual([])
  })
})

describe('locale switching', () => {
  it('switches language and remembers the choice', () => {
    setLocale('kk')
    expect(currentLocale()).toBe('kk')
    expect(localStorage.getItem('locale')).toBe('kk')
    expect(i18n.global.t('common.book')).toBe('Брондау')

    setLocale('ru')
    expect(i18n.global.t('common.book')).toBe('Забронировать')
  })
})

describe('plurals', () => {
  it('picks Russian plural forms', () => {
    expect([1, 2, 5, 11, 21, 22, 25].map((n) => ruPluralIndex(n, 3))).toEqual([0, 1, 2, 2, 0, 1, 2])
  })

  it('formats days in both languages', () => {
    expect(formatDays(21)).toBe('21 сутки')
    expect(formatDays(3)).toBe('3 суток')
    setLocale('kk')
    expect(formatDays(3)).toBe('3 тәулік')
    setLocale('en')
    expect(formatDays(1)).toBe('1 day')
    expect(formatDays(3)).toBe('3 days')
  })
})

describe('labels for backend values', () => {
  it('translates statuses', () => {
    expect(bookingStatusLabel('confirmed')).toBe('Подтверждена')
    setLocale('kk')
    expect(bookingStatusLabel('confirmed')).toBe('Расталды')
  })

  it('translates known car classes and keeps custom ones', () => {
    expect(categoryLabel('Комфорт')).toBe('Комфорт')
    setLocale('en')
    expect(categoryLabel('Комфорт')).toBe('Comfort')
    expect(categoryLabel('Минивэн')).toBe('Minivan')
    expect(categoryLabel('Кабриолет')).toBe('Кабриолет')
  })

  it('translates stored locations without changing the stored value', () => {
    setLocale('kk')
    expect(locationLabel('Аэропорт Алматы (ALA)')).toBe('Алматы әуежайы (ALA)')
    expect(locationLabel(OFFICE_LOCATION)).toContain('Кеңсе: Қазыбек би')
    expect(locationLabel(`${DELIVERY_PREFIX}Абая 10`)).toBe('Жеткізу: Абая 10')
    // Неизвестное значение (старая бронь) показываем как есть
    expect(locationLabel('Медеу')).toBe('Медеу')
  })
})

describe('components in Kazakh', () => {
  const car: Car = {
    id: 1,
    brand: 'Toyota',
    model: 'Camry',
    year: 2023,
    images: [],
    category: { id: 1, name: 'Комфорт' },
    transmission: 'automatic',
    fuel: 'petrol',
    seats: 5,
    price_per_day: '30000.00',
    deposit: '100000.00',
    description: '',
    is_active: true,
    created_at: '2026-10-01T10:00:00Z',
  }

  it('renders CarCard texts on the selected language', async () => {
    const wrapper = mount(CarCard, {
      props: { car },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    expect(wrapper.text()).toContain('Арендовать')

    setLocale('kk')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Жалға алу')
    expect(wrapper.text()).toContain('5 орын')
    expect(wrapper.text()).toContain('1 күн үшін')
  })
})
