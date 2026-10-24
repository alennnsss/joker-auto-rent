const TIMEZONE = 'Asia/Almaty'

/** Сегодняшняя дата в Алматы в формате YYYY-MM-DD. */
export function todayIso(now: Date = new Date()): string {
  // en-CA форматирует как YYYY-MM-DD
  return new Intl.DateTimeFormat('en-CA', { timeZone: TIMEZONE }).format(now)
}

export function addDays(iso: string, days: number): string {
  const date = new Date(`${iso}T00:00:00Z`)
  date.setUTCDate(date.getUTCDate() + days)
  return date.toISOString().slice(0, 10)
}

export function daysBetween(start: string, end: string): number {
  const ms = Date.parse(`${end}T00:00:00Z`) - Date.parse(`${start}T00:00:00Z`)
  return Math.round(ms / 86_400_000)
}

/** YYYY-MM-DD → Date (локальная полночь) или null. */
export function fromIso(iso: string): Date | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso)
  if (!match) return null
  return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]))
}

/** Date → YYYY-MM-DD по локальной дате (без сдвига часового пояса). */
export function toIso(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

/** Все занятые дни из интервалов [start, end) — для блокировки в календаре. */
export function busyDays(busy: { start_date: string; end_date: string }[], limit = 400): string[] {
  const days: string[] = []
  for (const range of busy) {
    for (let day = range.start_date; day < range.end_date && days.length < limit; ) {
      days.push(day)
      day = addDays(day, 1)
    }
  }
  return days
}

/** Пересекается ли [start, end) с хотя бы одним занятым интервалом. */
export function overlapsAny(
  start: string,
  end: string,
  busy: { start_date: string; end_date: string }[],
): boolean {
  return busy.some((b) => start < b.end_date && end > b.start_date)
}
