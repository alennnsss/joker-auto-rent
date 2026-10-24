import { definePreset } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'

// Цвета берутся из CSS-переменных (_variables.scss), а не хардкодятся
const SHADES = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950] as const

function palette(name: string): Record<number, string> {
  return Object.fromEntries(SHADES.map((shade) => [shade, `var(--${name}-${shade})`]))
}

export const JokerPreset = definePreset(Aura, {
  semantic: {
    primary: palette('gold'),
    colorScheme: {
      dark: {
        surface: { 0: 'var(--neutral-0)', ...palette('neutral') },
        primary: {
          color: '{primary.500}',
          contrastColor: 'var(--color-on-gold)',
          hoverColor: '{primary.400}',
          activeColor: '{primary.600}',
        },
        highlight: {
          background: '{primary.500}',
          focusBackground: '{primary.400}',
          color: 'var(--color-on-gold)',
          focusColor: 'var(--color-on-gold)',
        },
        formField: {
          background: 'var(--color-surface-2)',
          borderColor: 'var(--color-border)',
          hoverBorderColor: 'var(--color-gold-dark)',
          focusBorderColor: 'var(--color-gold)',
          color: 'var(--color-text)',
          placeholderColor: 'var(--color-text-muted)',
        },
        overlay: {
          popover: { background: 'var(--color-surface)', borderColor: 'var(--color-border)' },
          modal: { background: 'var(--color-surface)', borderColor: 'var(--color-border)' },
        },
      },
    },
  },
})

const ruLocale = {
  firstDayOfWeek: 1,
  dateFormat: 'dd.mm.yy',
  dayNames: ['воскресенье', 'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота'],
  dayNamesShort: ['вс', 'пн', 'вт', 'ср', 'чт', 'пт', 'сб'],
  dayNamesMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
  monthNames: [
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентябрь',
    'Октябрь',
    'Ноябрь',
    'Декабрь',
  ],
  monthNamesShort: ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'],
  today: 'Сегодня',
  clear: 'Очистить',
  weekHeader: 'Нед',
  chooseDate: 'Выберите дату',
  chooseMonth: 'Выберите месяц',
  chooseYear: 'Выберите год',
  prevMonth: 'Предыдущий месяц',
  nextMonth: 'Следующий месяц',
  prevYear: 'Предыдущий год',
  nextYear: 'Следующий год',
  prevDecade: 'Предыдущее десятилетие',
  nextDecade: 'Следующее десятилетие',
  emptyMessage: 'Нет вариантов',
}

const kkLocale: typeof ruLocale = {
  firstDayOfWeek: 1,
  dateFormat: 'dd.mm.yy',
  dayNames: ['жексенбі', 'дүйсенбі', 'сейсенбі', 'сәрсенбі', 'бейсенбі', 'жұма', 'сенбі'],
  dayNamesShort: ['жс', 'дс', 'сс', 'ср', 'бс', 'жм', 'сб'],
  dayNamesMin: ['Жс', 'Дс', 'Сс', 'Ср', 'Бс', 'Жм', 'Сб'],
  monthNames: [
    'Қаңтар',
    'Ақпан',
    'Наурыз',
    'Сәуір',
    'Мамыр',
    'Маусым',
    'Шілде',
    'Тамыз',
    'Қыркүйек',
    'Қазан',
    'Қараша',
    'Желтоқсан',
  ],
  monthNamesShort: ['қаң', 'ақп', 'нау', 'сәу', 'мам', 'мау', 'шіл', 'там', 'қыр', 'қаз', 'қар', 'жел'],
  today: 'Бүгін',
  clear: 'Тазалау',
  weekHeader: 'Апта',
  chooseDate: 'Күнді таңдаңыз',
  chooseMonth: 'Айды таңдаңыз',
  chooseYear: 'Жылды таңдаңыз',
  prevMonth: 'Алдыңғы ай',
  nextMonth: 'Келесі ай',
  prevYear: 'Алдыңғы жыл',
  nextYear: 'Келесі жыл',
  prevDecade: 'Алдыңғы онжылдық',
  nextDecade: 'Келесі онжылдық',
  emptyMessage: 'Нұсқалар жоқ',
}

// Локали календаря PrimeVue по языку сайта (переключаются в App.vue)
export const primeLocales = { ru: ruLocale, kk: kkLocale }
