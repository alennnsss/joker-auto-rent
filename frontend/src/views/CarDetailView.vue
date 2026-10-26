<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'

import { carsApi } from '@/api/cars'
import { errorMessage } from '@/api/http'
import type { Availability, Car } from '@/api/types'
import CarGallery from '@/components/CarGallery.vue'
import DateField from '@/components/DateField.vue'
import EmptyState from '@/components/EmptyState.vue'
import LocationSelect from '@/components/LocationSelect.vue'
import TermPicker from '@/components/TermPicker.vue'
import { whatsappMessageLink } from '@/config/contacts'
import { isLocationValid, locationLabel, TIMES } from '@/config/locations'
import { returnDate, useBookingStore } from '@/stores/booking'
import { busyDays, todayIso } from '@/utils/date'
import { categoryLabel, formatDate, formatPrice, fuelLabel, transmissionLabel } from '@/utils/format'

const props = defineProps<{ id: number }>()

const route = useRoute()
const booking = useBookingStore()
const { t, locale } = useI18n()

const car = ref<Car | null>(null)
const availability = ref<Availability | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const checking = ref(false)

const today = todayIso()
const { trip } = storeToRefs(booking)

// Дата получения и срок из каталога: /cars/7?start=2026-11-01&days=3
const queryStr = (key: string) => (typeof route.query[key] === 'string' ? (route.query[key] as string) : '')
const queryStart = queryStr('start') >= today ? queryStr('start') : ''
if (queryStart || queryStr('days')) {
  booking.setTerm(queryStart, Number(queryStr('days')) || 1)
}
if (trip.value.pickupDate < today) booking.setTerm(today, trip.value.days)

const start = computed(() => trip.value.pickupDate)
const end = computed(() => returnDate(trip.value))
const disabledDays = computed(() => busyDays(availability.value?.busy ?? []))

// Поля калькулятора пишут прямо в черновик брони
function field<K extends 'pickupLocation' | 'pickupDate' | 'pickupTime' | 'days'>(key: K) {
  return computed({
    get: () => trip.value[key],
    set: (value) => {
      trip.value = { ...trip.value, [key]: value }
    },
  })
}
const pickupLocation = field('pickupLocation')
const pickupDate = field('pickupDate')
const pickupTime = field('pickupTime')
const days = field('days')

const title = computed(() => (car.value ? `${car.value.brand} ${car.value.model}` : ''))
const datesValid = computed(() => Boolean(start.value) && start.value >= today)
const locationValid = computed(() => isLocationValid(trip.value.pickupLocation))
// Сумма считается сразу при выборе срока — по той же формуле, что и на сервере
const total = computed(() => (car.value ? Number(car.value.price_per_day) * days.value : 0))
const busy = computed(() => availability.value?.available === false)

const specs = computed(() => {
  if (!car.value) return []
  return [
    { label: t('carDetail.category'), value: categoryLabel(car.value.category.name) },
    { label: t('carDetail.year'), value: String(car.value.year) },
    { label: t('carDetail.transmission'), value: transmissionLabel(car.value.transmission) },
    { label: t('carDetail.fuel'), value: fuelLabel(car.value.fuel) },
    { label: t('carDetail.seats'), value: String(car.value.seats) },
  ]
})

async function load() {
  loading.value = true
  error.value = null
  try {
    car.value = await carsApi.get(props.id)
    await checkAvailability()
  } catch (e) {
    error.value = errorMessage(e, t('errors.loadCar'))
  } finally {
    loading.value = false
  }
}

async function checkAvailability() {
  if (!car.value) return
  checking.value = true
  try {
    availability.value = datesValid.value
      ? await carsApi.availability(car.value.id, start.value, end.value)
      : await carsApi.availability(car.value.id)
  } catch {
    availability.value = null
  } finally {
    checking.value = false
  }
}

watch([start, end], checkAvailability)

// Заголовок вкладки с названием авто; App.vue при смене языка ставит общий, этот watch — после него
watch([title, locale], () => {
  if (title.value) {
    document.title = `${t('carDetail.docTitle', { title: title.value })} — Joker Auto Rent`
  }
})

onMounted(load)

// Бронь оформляется в WhatsApp: собираем сообщение о машине, сроке и сумме для менеджера
function bookViaWhatsapp() {
  if (!car.value) return
  const tr = trip.value
  const lines = [
    t('carDetail.waGreeting', { car: `${title.value}, ${car.value.year}` }),
    t('carDetail.waPickup', {
      when: `${formatDate(tr.pickupDate)}, ${tr.pickupTime}`,
      where: locationLabel(tr.pickupLocation),
    }),
    t('carDetail.waReturn', { when: `${formatDate(end.value)}, ${tr.pickupTime}` }),
    t('carDetail.waTotal', {
      days: t('filters.termDays', tr.days),
      total: formatPrice(total.value),
    }),
  ]
  window.open(whatsappMessageLink(lines.join('\n')), '_blank', 'noopener')
}
</script>

<template>
  <div class="page container">
    <div v-if="loading" class="detail">
      <div class="skeleton detail__skeleton" />
      <div class="skeleton detail__skeleton" />
    </div>

    <EmptyState v-else-if="error || !car" :title="error ?? t('common.carNotFound')">
      <RouterLink :to="{ name: 'cars' }" class="btn btn--outline">{{ t('carDetail.back') }}</RouterLink>
    </EmptyState>

    <template v-else>
      <nav class="crumbs muted" :aria-label="t('carDetail.crumbs')">
        <RouterLink :to="{ name: 'cars' }">{{ t('common.fleet') }}</RouterLink>
        <span aria-hidden="true"> / </span>
        <span aria-current="page">{{ title }}</span>
      </nav>

      <div class="detail">
        <div class="detail__gallery">
          <CarGallery :images="car.images" :title="title" />
        </div>

        <aside class="booking card" aria-labelledby="booking-title">
          <h1 id="booking-title" class="booking__title">{{ title }}</h1>
          <p class="booking__meta muted">{{ categoryLabel(car.category.name) }} · {{ car.year }}</p>
          <p class="booking__price">
            <span class="text-gold">{{ formatPrice(car.price_per_day) }}</span>
            <span class="muted">&nbsp;{{ t('common.perDay') }}</span>
          </p>

          <fieldset class="booking__pickup">
            <legend class="booking__legend">
              <span class="booking__dot" aria-hidden="true" />{{ t('common.pickup') }}
            </legend>
            <LocationSelect id="detail-location" v-model="pickupLocation" :label="t('common.place')" />
            <div class="booking__row">
              <DateField
                id="detail-pickup-date"
                v-model="pickupDate"
                :label="t('common.date')"
                :min="today"
                :disabled-days="disabledDays"
              />
              <div class="field">
                <label class="field__label" for="detail-time">{{ t('common.time') }}</label>
                <select id="detail-time" v-model="pickupTime" class="select">
                  <option v-for="time in TIMES" :key="time" :value="time">{{ time }}</option>
                </select>
              </div>
            </div>
          </fieldset>

          <TermPicker id="detail-term" v-model="days" stepper :label="t('trip.term')" />

          <div class="summary" aria-live="polite" data-test="summary">
            <div class="summary__row muted">
              <span>{{ formatPrice(car.price_per_day) }} × {{ t('filters.termDays', days) }}</span>
            </div>
            <div class="summary__row summary__total">
              <span>{{ t('carDetail.total') }}</span>
              <strong data-test="total">{{ formatPrice(total) }}</strong>
            </div>
            <div v-if="datesValid" class="summary__row summary__return">
              <span class="muted">{{ t('carDetail.returnAt') }}</span>
              <span data-test="return">{{ formatDate(end) }}, {{ pickupTime }}</span>
            </div>
          </div>

          <div v-if="busy" class="alert alert--error" role="alert">
            {{ t('carDetail.busyAlert') }}
          </div>

          <button
            type="button"
            class="btn btn--gold btn--block"
            :disabled="!datesValid || !locationValid || checking || busy"
            @click="bookViaWhatsapp"
          >
            {{ t('carDetail.bookWhatsapp') }}
          </button>
          <p class="muted booking__hint">{{ t('carDetail.whatsappHint') }}</p>

          <div v-if="availability?.busy.length" class="busy">
            <p class="busy__title muted">{{ t('carDetail.busyTitle') }}</p>
            <ul>
              <li v-for="b in availability.busy" :key="b.start_date">
                {{ formatDate(b.start_date) }} — {{ formatDate(b.end_date) }}
              </li>
            </ul>
          </div>
        </aside>

        <div class="detail__info">
          <section class="detail__section">
            <h2>{{ t('carDetail.specs') }}</h2>
            <dl class="specs">
              <div v-for="s in specs" :key="s.label" class="specs__item">
                <dt class="muted">{{ s.label }}</dt>
                <dd>{{ s.value }}</dd>
              </div>
            </dl>
          </section>

          <section v-if="car.description" class="detail__section">
            <h2>{{ t('carDetail.description') }}</h2>
            <p class="detail__description">{{ car.description }}</p>
          </section>

          <section class="detail__section">
            <h2>{{ t('carDetail.conditions') }}</h2>
            <ul class="conditions">
              <li>{{ t('carDetail.condition1') }}</li>
              <li>{{ t('carDetail.condition2') }}</li>
              <li>{{ t('carDetail.condition3') }}</li>
              <li>{{ t('carDetail.condition4') }}</li>
            </ul>
          </section>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped lang="scss">
.crumbs {
  margin-bottom: 16px;
  font-size: 0.9rem;

  a {
    color: var(--color-text-muted);

    @include hover {
      color: var(--color-gold);
    }
  }
}

// Телефон: фото → калькулятор → характеристики (калькулятор не уезжает в конец страницы).
// Десктоп: слева фото и характеристики, справа липкий калькулятор.
.detail {
  display: grid;
  gap: 24px;
  // minmax(0, …): без явной колонки iOS Safari растягивал её по самому длинному
  // варианту в выпадающем списке места («Офис: ул. Казыбек би…») — шире экрана
  grid-template-columns: minmax(0, 1fr);
  grid-template-areas:
    'gallery'
    'booking'
    'info';

  @include media(lg) {
    grid-template-columns: minmax(0, 1.6fr) minmax(340px, 1fr);
    grid-template-rows: auto 1fr;
    grid-template-areas:
      'gallery booking'
      'info booking';
    gap: 0 32px;
    align-items: start;
  }

  &__gallery {
    grid-area: gallery;
    min-width: 0;
  }

  &__info {
    grid-area: info;
    min-width: 0;
  }

  &__skeleton {
    min-height: 360px;
  }

  &__section {
    margin-top: 16px;

    & + & {
      margin-top: 40px;
    }

    @include media(lg) {
      margin-top: 40px;
    }

    h2 {
      font-size: 1.5rem;
    }
  }

  &__description {
    white-space: pre-line;
    color: var(--color-text-muted);
  }
}

.specs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 0;

  @include media(md) {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  &__item {
    padding: 14px 16px;
    border-radius: var(--radius-sm);
    background: var(--color-surface);
    border: 1px solid var(--color-border);

    // В две колонки нечётная последняя плашка — на всю строку, без «дыры»
    @include media-down(md) {
      &:last-child:nth-child(odd) {
        grid-column: 1 / -1;
      }
    }
  }

  dt {
    font-size: 0.8rem;
  }

  dd {
    margin: 2px 0 0;
    font-weight: 500;
  }
}

.conditions {
  padding-left: 20px;
  color: var(--color-text-muted);

  li::marker {
    color: var(--color-gold);
  }
}

.booking {
  grid-area: booking;
  min-width: 0;

  @include media(lg) {
    position: sticky;
    top: calc(var(--header-height) + 24px);
  }

  &__title {
    font-size: clamp(1.6rem, 4vw, 2.2rem);
    margin-bottom: 4px;
  }

  &__meta {
    margin-bottom: 8px;
  }

  &__price {
    font-size: 1.6rem;
    font-weight: 600;
    margin-bottom: 20px;
  }

  &__pickup {
    min-width: 0;
    margin: 0 0 16px;
    padding: 16px 16px 0;
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
  }

  &__legend {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 6px;
    font-weight: 600;
  }

  &__dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 3px solid var(--color-gold-dark);
    background: var(--color-gold);
  }

  &__row {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 0 12px;

    @include media(sm) {
      grid-template-columns: minmax(0, 1.3fr) minmax(0, 1fr);
    }
  }

  &__hint {
    margin: 8px 0 0;
    font-size: 0.85rem;
    text-align: center;
  }
}

.summary {
  display: grid;
  gap: 6px;
  margin-bottom: 16px;
  padding: 16px;
  border-radius: var(--radius-sm);
  background: var(--color-surface-2);

  &__row {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: baseline;
    gap: 4px 12px;
    font-size: 0.95rem;
  }

  &__total {
    padding-top: 8px;
    border-top: 1px solid var(--color-border);
    font-weight: 600;

    strong {
      font-size: 1.5rem;
      color: var(--color-gold);
      white-space: nowrap;
      font-variant-numeric: tabular-nums;
    }
  }

  &__return {
    font-size: 0.9rem;
  }
}

.busy {
  margin-top: 20px;
  font-size: 0.9rem;

  &__title {
    margin-bottom: 4px;
  }

  ul {
    margin: 0;
    padding-left: 18px;
    color: var(--color-text-muted);
  }
}
</style>
