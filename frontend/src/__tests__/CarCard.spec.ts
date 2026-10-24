import { mount, RouterLinkStub } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import type { Car } from '@/api/types'
import CarCard from '@/components/CarCard.vue'

const car: Car = {
  id: 7,
  brand: 'Toyota',
  model: 'Camry',
  year: 2023,
  images: [{ id: 1, url: '/media/cars/camry.webp', sort_order: 0 }],
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

function mountCard(props: Record<string, unknown> = {}) {
  return mount(CarCard, {
    props: { car, ...props },
    global: { stubs: { RouterLink: RouterLinkStub } },
  })
}

describe('CarCard', () => {
  it('renders title, category, specs and formatted price', () => {
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('Toyota Camry')
    expect(wrapper.text()).toContain('Комфорт')
    expect(wrapper.text()).toContain('Автомат')
    expect(wrapper.text()).toContain('5 мест')
    expect(wrapper.get('[data-test="price"]').text()).toBe('30 000 ₸')
  })

  it('renders lazy image with alt text', () => {
    const img = mountCard().get('img')
    expect(img.attributes('loading')).toBe('lazy')
    expect(img.attributes('alt')).toBe('Toyota Camry')
  })

  it('passes selected dates to the detail page link', () => {
    const wrapper = mountCard({ startDate: '2026-11-01', endDate: '2026-11-04' })
    const links = wrapper.findAllComponents(RouterLinkStub)
    expect(links[links.length - 1]?.props('to')).toEqual({
      name: 'car-detail',
      params: { id: 7 },
      query: { start: '2026-11-01', end: '2026-11-04' },
    })
  })
})
