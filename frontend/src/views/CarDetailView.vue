<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { carsApi } from '@/api/cars'
import { errorMessage } from '@/api/http'
import type { Availability, Car } from '@/api/types'
import CarGallery from '@/components/CarGallery.vue'
import EmptyState from '@/components/EmptyState.vue'
import TripPanel from '@/components/TripPanel.vue'
import { useBookingStore } from '@/stores/booking'
import { busyDays, todayIso } from '@/utils/date'
import { formatDate, formatDays, formatPrice, fuelLabel, transmissionLabel } from '@/utils/format'

const props = defineProps<{ id: number }>()

const route = useRoute()
const router = useRouter()
const booking = useBookingStore()
const { t, locale } = useI18n()

const car = ref<Car | null>(null)
const availability = ref<Availability | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const checking = ref(false)

const today = todayIso()
const { trip } = storeToRefs(booking)
const queryStr = (key: string) => (typeof route.query[key] === 'string' ? (route.query[key] as string) : '')
if (queryStr('start') && queryStr('end') > queryStr('start')) {
  booking.setDates(queryStr('start'), queryStr('end'))
}
const start = computed(() => trip.value.pickupDate)
const end = computed(() => trip.value.returnDate)
const disabledDays = computed(() => busyDays(availability.value?.busy ?? []))

const title = computed(() => (car.value ? `${car.value.brand} ${car.value.model}` : ''))
const datesValid = computed(() => start.value >= today && end.value > start.value)

const specs = computed(() => {
  if (!car.value) return []
  return [
    { label: t('carDetail.category'), value: car.value.category.name },
    { label: t('carDetail.year'), value: String(car.value.year) },
    { label: t('carDetail.transmission'), value: transmissionLabel(car.value.transmission) },
    { label: t('carDetail.fuel'), value: fuelLabel(car.value.fuel) },
    { label: t('carDetail.seats'), value: String(car.value.seats) },
    { label: t('carDetail.deposit'), value: formatPrice(car.value.deposit) },
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

function book() {
  router.push({ name: 'booking', params: { carId: props.id } })
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
        <span>{{ title }}</span>
      </nav>

      <div class="detail">
        <div class="detail__main">
          <CarGallery :images="car.images" :title="title" />

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

        <aside class="booking card" aria-labelledby="booking-title">
          <h1 id="booking-title" class="booking__title">{{ title }}</h1>
          <p class="muted">{{ car.category.name }} · {{ car.year }}</p>
          <p class="booking__price">
            <span class="text-gold">{{ formatPrice(car.price_per_day) }}</span>
            <span class="muted"> {{ t('common.perDay') }}</span>
          </p>

          <TripPanel v-model="trip" :disabled-days="disabledDays" compact id-prefix="detail" />

          <div aria-live="polite">
            <template v-if="availability?.available === true && availability.total_price">
              <div class="booking__total">
                <span>{{ formatDays(availability.days ?? 0) }}</span>
                <strong>{{ formatPrice(availability.total_price) }}</strong>
              </div>
              <p class="muted booking__note">
                {{ t('carDetail.depositNote', { amount: formatPrice(car.deposit) }) }}
              </p>
            </template>
            <div v-else-if="availability?.available === false" class="alert alert--error">
              {{ t('carDetail.busyAlert') }}
            </div>
          </div>

          <button
            type="button"
            class="btn btn--gold btn--block"
            :disabled="!datesValid || checking || availability?.available === false"
            @click="book"
          >
            {{ t('common.book') }}
          </button>

          <div v-if="availability?.busy.length" class="busy">
            <p class="busy__title muted">{{ t('carDetail.busyTitle') }}</p>
            <ul>
              <li v-for="b in availability.busy" :key="b.start_date">
                {{ formatDate(b.start_date) }} — {{ formatDate(b.end_date) }}
              </li>
            </ul>
          </div>
        </aside>
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

.detail {
  display: grid;
  gap: 32px;

  @include media(lg) {
    grid-template-columns: minmax(0, 1.6fr) minmax(320px, 1fr);
    align-items: start;
  }

  &__skeleton {
    min-height: 360px;
  }

  &__section {
    margin-top: 40px;

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
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 0;

  @include media(md) {
    grid-template-columns: repeat(3, 1fr);
  }

  &__item {
    padding: 14px 16px;
    border-radius: var(--radius-sm);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
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
  @include media(lg) {
    position: sticky;
    top: calc(var(--header-height) + 24px);
  }

  &__title {
    font-size: clamp(1.6rem, 4vw, 2.2rem);
    margin-bottom: 4px;
  }

  &__price {
    font-size: 1.6rem;
    font-weight: 600;
    margin-bottom: 20px;
  }

  &__total {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--color-border);

    strong {
      font-size: 1.3rem;
      color: var(--color-gold);
    }
  }

  &__note {
    font-size: 0.85rem;
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
