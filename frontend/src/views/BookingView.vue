<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'

import { bookingsApi } from '@/api/bookings'
import { carsApi } from '@/api/cars'
import { errorMessage } from '@/api/http'
import type { Availability, Car, PaymentMethod } from '@/api/types'
import CarPicture from '@/components/CarPicture.vue'
import EmailVerifyNotice from '@/components/EmailVerifyNotice.vue'
import EmptyState from '@/components/EmptyState.vue'
import TripPanel from '@/components/TripPanel.vue'
import { isLocationValid } from '@/config/locations'
import { useAuthStore } from '@/stores/auth'
import { useBookingStore } from '@/stores/booking'
import { busyDays, todayIso } from '@/utils/date'
import { formatDate, formatDays, formatPrice } from '@/utils/format'

const props = defineProps<{ carId: number }>()

const router = useRouter()
const auth = useAuthStore()
const booking = useBookingStore()
const { t } = useI18n()

const today = todayIso()
const car = ref<Car | null>(null)
const quote = ref<Availability | null>(null)
const loading = ref(true)
const loadError = ref<string | null>(null)
const submitError = ref<string | null>(null)
const submitting = ref(false)

const { trip } = storeToRefs(booking)
const start = computed(() => trip.value.pickupDate)
const end = computed(() => trip.value.returnDate)
const disabledDays = computed(() => busyDays(quote.value?.busy ?? []))
const paymentMethod = ref<PaymentMethod>('cash')
const agreed = ref(false)

const datesValid = computed(() => start.value >= today && end.value > start.value)
const locationsValid = computed(
  () => isLocationValid(trip.value.pickupLocation) && isLocationValid(trip.value.returnLocation),
)
const emailVerified = computed(() => auth.user?.email_verified === true)
const canSubmit = computed(
  () =>
    datesValid.value &&
    locationsValid.value &&
    emailVerified.value &&
    agreed.value &&
    quote.value?.available === true &&
    !submitting.value,
)

async function refreshQuote() {
  if (!car.value || !datesValid.value) {
    quote.value = null
    return
  }
  try {
    quote.value = await carsApi.availability(car.value.id, start.value, end.value)
  } catch {
    quote.value = null
  }
}

watch([start, end], refreshQuote)

onMounted(async () => {
  booking.loadConfig()
  try {
    car.value = await carsApi.get(props.carId)
    await refreshQuote()
  } catch (e) {
    loadError.value = errorMessage(e, t('errors.loadCar'))
  } finally {
    loading.value = false
  }
})

async function submit() {
  if (!car.value || !canSubmit.value) return
  submitting.value = true
  submitError.value = null
  try {
    const created = await bookingsApi.create({
      car_id: car.value.id,
      start_date: start.value,
      end_date: end.value,
      pickup_location: trip.value.pickupLocation.trim(),
      return_location: trip.value.returnLocation.trim(),
      pickup_time: trip.value.pickupTime,
      return_time: trip.value.returnTime,
      payment_method: paymentMethod.value,
    })
    booking.reset()
    if (created.payment_method === 'online') {
      await router.push({ name: 'payment', params: { bookingId: created.id } })
    } else {
      await router.push({ name: 'account-bookings', query: { created: String(created.id) } })
    }
  } catch (e) {
    submitError.value = errorMessage(e)
    refreshQuote()
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="page container">
    <h1 class="page-title">{{ t('booking.title') }}</h1>
    <p class="page-subtitle">{{ t('booking.subtitle') }}</p>

    <div v-if="loading" class="skeleton" style="min-height: 320px" />

    <EmptyState v-else-if="loadError || !car" :title="loadError ?? t('common.carNotFound')">
      <RouterLink :to="{ name: 'cars' }" class="btn btn--outline">{{ t('booking.toFleet') }}</RouterLink>
    </EmptyState>

    <form v-else class="booking" @submit.prevent="submit">
      <div class="booking__form card">
        <EmailVerifyNotice />
        <section>
          <h2 class="booking__h">{{ t('booking.tripTitle') }}</h2>
          <TripPanel v-model="trip" :disabled-days="disabledDays" compact id-prefix="booking" />
          <p v-if="!locationsValid" class="muted booking__hint">{{ t('booking.deliveryHint') }}</p>
          <div v-if="quote?.available === false" class="alert alert--error" role="alert">
            {{ t('booking.busy') }}
          </div>
        </section>

        <fieldset class="booking__payment">
          <legend class="booking__h">{{ t('booking.paymentTitle') }}</legend>
          <label class="option" :class="{ 'is-selected': paymentMethod === 'cash' }">
            <input v-model="paymentMethod" type="radio" name="payment" value="cash" />
            <span>
              <strong>{{ t('booking.cash') }}</strong>
              <span class="muted">{{ t('booking.cashText') }}</span>
            </span>
          </label>
          <label
            v-if="booking.onlinePaymentEnabled"
            class="option"
            :class="{ 'is-selected': paymentMethod === 'online' }"
          >
            <input v-model="paymentMethod" type="radio" name="payment" value="online" />
            <span>
              <strong>{{ t('booking.online') }}</strong>
              <span class="muted">{{ t('booking.onlineText') }}</span>
            </span>
          </label>
        </fieldset>

        <section>
          <h2 class="booking__h">{{ t('booking.contactTitle') }}</h2>
          <p class="muted">
            {{ auth.user?.full_name }} · {{ auth.user?.phone ?? t('booking.noPhone') }} ·
            {{ auth.user?.email }}
            <RouterLink :to="{ name: 'account' }">{{ t('common.edit') }}</RouterLink>
          </p>
        </section>

        <label class="checkbox">
          <input v-model="agreed" type="checkbox" required />
          <span>{{ t('booking.agree') }}</span>
        </label>

        <div v-if="submitError" class="alert alert--error" role="alert">{{ submitError }}</div>
      </div>

      <aside class="summary card">
        <div class="summary__media">
          <CarPicture :url="car.images[0]?.url" :alt="`${car.brand} ${car.model}`" sizes="400px" :max-width="800" />
        </div>
        <h2 class="summary__title">{{ car.brand }} {{ car.model }}</h2>
        <dl class="summary__list">
          <div>
            <dt class="muted">{{ t('common.pickup') }}</dt>
            <dd>{{ formatDate(start) }}, {{ trip.pickupTime }}</dd>
          </div>
          <div>
            <dt class="muted">{{ t('common.return') }}</dt>
            <dd>{{ formatDate(end) }}, {{ trip.returnTime }}</dd>
          </div>
          <div v-if="quote?.days">
            <dt class="muted">{{ t('booking.term') }}</dt>
            <dd>{{ formatDays(quote.days) }}</dd>
          </div>
          <div>
            <dt class="muted">{{ t('booking.pricePerDay') }}</dt>
            <dd>{{ formatPrice(car.price_per_day) }}</dd>
          </div>
          <div>
            <dt class="muted">{{ t('booking.depositReturnable') }}</dt>
            <dd>{{ formatPrice(car.deposit) }}</dd>
          </div>
        </dl>
        <div class="summary__total">
          <span>{{ t('booking.total') }}</span>
          <strong>{{ quote?.total_price ? formatPrice(quote.total_price) : '—' }}</strong>
        </div>
        <button type="submit" class="btn btn--gold btn--block" :disabled="!canSubmit">
          {{
            submitting
              ? t('booking.submitting')
              : paymentMethod === 'online'
                ? t('booking.toPayment')
                : t('common.book')
          }}
        </button>
      </aside>
    </form>
  </div>
</template>

<style scoped lang="scss">
.booking {
  display: grid;
  gap: 24px;

  @include media(lg) {
    grid-template-columns: minmax(0, 1.5fr) minmax(320px, 1fr);
    align-items: start;
  }

  &__form {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  &__h {
    font-size: 1.25rem;
    margin-bottom: 12px;
  }

  &__hint {
    margin: 8px 0 0;
    font-size: 0.875rem;
  }

  &__payment {
    border: 0;
    padding: 0;
    margin: 0;
    display: grid;
    gap: 12px;
  }
}

.option {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 16px;
  min-height: 44px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;

  &.is-selected {
    border-color: var(--color-gold);
    background: var(--color-gold-alpha);
  }

  input {
    width: 20px;
    height: 20px;
    margin-top: 2px;
    accent-color: var(--color-gold);
  }

  span {
    display: flex;
    flex-direction: column;
  }
}

.summary {
  @include media(lg) {
    position: sticky;
    top: calc(var(--header-height) + 24px);
  }

  &__media {
    aspect-ratio: 16 / 9;
    border-radius: var(--radius-sm);
    overflow: hidden;
    margin-bottom: 16px;
  }

  &__title {
    font-size: 1.4rem;
  }

  &__list {
    margin: 0 0 16px;

    div {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding-block: 6px;
    }

    dd {
      margin: 0;
      text-align: right;
    }
  }

  &__total {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding-block: 16px;
    margin-bottom: 16px;
    border-top: 1px solid var(--color-border);

    strong {
      font-size: 1.5rem;
      color: var(--color-gold);
    }
  }
}
</style>
