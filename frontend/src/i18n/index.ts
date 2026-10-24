import { createI18n } from 'vue-i18n'

import kk from './locales/kk'
import ru, { type MessageSchema } from './locales/ru'

// Ключи в t('…') проверяются TypeScript по структуре ru.ts
declare module 'vue-i18n' {
  // eslint-disable-next-line @typescript-eslint/no-empty-object-type
  export interface DefineLocaleMessage extends MessageSchema {}
}

export const LOCALES = ['ru', 'kk'] as const
export type Locale = (typeof LOCALES)[number]

export const LOCALE_LABELS: Record<Locale, string> = { ru: 'Рус', kk: 'Қаз' }

const STORAGE_KEY = 'locale'

function isLocale(value: unknown): value is Locale {
  return LOCALES.includes(value as Locale)
}

function savedLocale(): Locale {
  try {
    const value = localStorage.getItem(STORAGE_KEY)
    if (isLocale(value)) return value
  } catch {
    // localStorage недоступен (приватный режим) — остаётся русский
  }
  return 'ru'
}

/** Индекс формы в «1 сутки | 2 суток | 5 суток». */
export function ruPluralIndex(choice: number, choicesLength: number): number {
  const n = Math.abs(choice)
  if (choicesLength < 3) return n === 1 ? 0 : 1
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return 0
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return 1
  return 2
}

export const i18n = createI18n<[MessageSchema], Locale, false>({
  legacy: false,
  locale: savedLocale(),
  fallbackLocale: 'ru',
  messages: { ru, kk },
  // В казахском существительное после числа не меняется — всегда первая форма
  pluralRules: { ru: ruPluralIndex, kk: () => 0 },
})

export function currentLocale(): Locale {
  return i18n.global.locale.value
}

export function setLocale(locale: Locale) {
  i18n.global.locale.value = locale
  try {
    localStorage.setItem(STORAGE_KEY, locale)
  } catch {
    // язык просто не запомнится между визитами
  }
}
