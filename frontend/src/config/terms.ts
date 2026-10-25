// Быстрый выбор срока аренды (в сутках) — в каталоге и в калькуляторе на карточке авто
export const RENTAL_TERMS = [1, 3, 7, 10, 30] as const

export const MIN_TERM = 1
export const MAX_TERM = 90

/** Любое значение → целое число суток в допустимых пределах. */
export function clampTerm(value: unknown): number {
  const n = Math.round(Number(value))
  if (!Number.isFinite(n)) return MIN_TERM
  return Math.min(MAX_TERM, Math.max(MIN_TERM, n))
}
