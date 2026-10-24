import { describe, expect, it } from 'vitest'

import { addDays, daysBetween, overlapsAny, todayIso } from '@/utils/date'
import { formatDate, formatDays, formatPrice } from '@/utils/format'
import { imageSources } from '@/utils/images'

const NBSP = ' '

describe('formatPrice', () => {
  it('groups thousands and puts ₸ after the number', () => {
    expect(formatPrice(15000)).toBe(`15${NBSP}000${NBSP}₸`)
    expect(formatPrice('1250000.00')).toBe(`1${NBSP}250${NBSP}000${NBSP}₸`)
    expect(formatPrice(900)).toBe(`900${NBSP}₸`)
    expect(formatPrice(null)).toBe(`0${NBSP}₸`)
  })
})

describe('formatDate', () => {
  it('formats ISO date as DD.MM.YYYY', () => {
    expect(formatDate('2026-03-08')).toBe('08.03.2026')
  })

  it('formats datetime in Asia/Almaty timezone', () => {
    // 20:30 UTC = 01:30 следующего дня в Алматы (UTC+5)
    expect(formatDate('2026-12-31T20:30:00Z')).toBe('01.01.2027')
  })

  it('returns empty string for empty input', () => {
    expect(formatDate(undefined)).toBe('')
  })
})

describe('formatDays', () => {
  it('uses correct Russian plural', () => {
    expect(formatDays(1)).toBe('1 сутки')
    expect(formatDays(3)).toBe('3 суток')
    expect(formatDays(21)).toBe('21 сутки')
  })
})

describe('date utils', () => {
  it('computes today in Almaty', () => {
    expect(todayIso(new Date('2026-10-22T20:00:00Z'))).toBe('2026-10-23')
  })

  it('adds days and counts the difference', () => {
    expect(addDays('2026-02-27', 2)).toBe('2026-03-01')
    expect(daysBetween('2026-10-01', '2026-10-04')).toBe(3)
  })

  it('treats the return day as free', () => {
    const busy = [{ start_date: '2026-10-10', end_date: '2026-10-13' }]
    expect(overlapsAny('2026-10-12', '2026-10-15', busy)).toBe(true)
    expect(overlapsAny('2026-10-13', '2026-10-15', busy)).toBe(false)
  })
})

describe('imageSources', () => {
  it('builds WebP srcset for Unsplash images', () => {
    const { src, srcset } = imageSources('https://images.unsplash.com/photo-1?auto=format&w=1200', 800)
    expect(src).toContain('fm=webp')
    expect(srcset).toContain('400w')
    expect(srcset).toContain('800w')
    expect(srcset).not.toContain('1200w')
  })

  it('passes local images through unchanged', () => {
    expect(imageSources('/media/cars/a.webp')).toEqual({ src: '/media/cars/a.webp', srcset: undefined })
  })
})
