<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import { bookingsApi } from '@/api/bookings'
import { errorMessage } from '@/api/http'
import { paymentsApi } from '@/api/payments'
import type { Booking } from '@/api/types'
import EmptyState from '@/components/EmptyState.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { formatDate, formatDays, formatPrice } from '@/utils/format'

const props = defineProps<{ bookingId: number }>()

const { t } = useI18n()
const booking = ref<Booking | null>(null)
const loading = ref(true)
const paying = ref(false)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    booking.value = await bookingsApi.get(props.bookingId)
  } catch (e) {
    error.value = errorMessage(e, t('errors.bookingNotFound'))
  } finally {
    loading.value = false
  }
})

async function pay() {
  paying.value = true
  error.value = null
  try {
    const init = await paymentsApi.create(props.bookingId)
    // Переход на страницу провайдера (или сразу на /payment/success для тестовой оплаты)
    window.location.assign(init.redirect_url)
  } catch (e) {
    error.value = errorMessage(e)
    paying.value = false
  }
}
</script>

<template>
  <div class="page container payment">
    <h1 class="page-title">{{ t('payment.title') }}</h1>

    <div v-if="loading" class="skeleton" style="height: 280px" />

    <EmptyState v-else-if="!booking" :title="error ?? t('errors.bookingNotFound')">
      <RouterLink :to="{ name: 'account-bookings' }" class="btn btn--outline">
        {{ t('payment.myBookings') }}
      </RouterLink>
    </EmptyState>

    <section v-else class="card payment__card">
      <div class="payment__head">
        <h2>{{ booking.car.brand }} {{ booking.car.model }}</h2>
        <StatusBadge kind="booking" :status="booking.status" />
      </div>
      <dl class="payment__list">
        <div>
          <dt class="muted">{{ t('payment.booking') }}</dt>
          <dd>№{{ booking.id }}</dd>
        </div>
        <div>
          <dt class="muted">{{ t('payment.dates') }}</dt>
          <dd>{{ formatDate(booking.start_date) }} — {{ formatDate(booking.end_date) }}</dd>
        </div>
        <div>
          <dt class="muted">{{ t('payment.term') }}</dt>
          <dd>{{ formatDays(booking.days) }}</dd>
        </div>
      </dl>
      <div class="payment__total">
        <span>{{ t('payment.due') }}</span>
        <strong>{{ formatPrice(booking.total_price) }}</strong>
      </div>

      <div v-if="error" class="alert alert--error" role="alert">{{ error }}</div>

      <div v-if="booking.is_paid" class="alert alert--success">{{ t('payment.alreadyPaid') }}</div>
      <div v-else-if="booking.payment_method !== 'online'" class="alert alert--info">
        {{ t('payment.cashSelected') }}
      </div>
      <button
        v-else
        type="button"
        class="btn btn--gold btn--block"
        :disabled="paying || booking.status !== 'pending'"
        @click="pay"
      >
        {{
          paying
            ? t('payment.redirecting')
            : t('payment.payAmount', { amount: formatPrice(booking.total_price) })
        }}
      </button>

      <RouterLink :to="{ name: 'account-bookings' }" class="btn btn--ghost btn--block payment__back">
        {{ t('payment.back') }}
      </RouterLink>
    </section>
  </div>
</template>

<style scoped lang="scss">
.payment {
  max-width: 640px;

  &__head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 16px;

    h2 {
      margin: 0;
      font-size: 1.5rem;
    }
  }

  &__list div {
    display: flex;
    justify-content: space-between;
    padding-block: 6px;

    dd {
      margin: 0;
    }
  }

  &__total {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding-block: 16px;
    margin-block: 8px 16px;
    border-top: 1px solid var(--color-border);

    strong {
      font-size: 1.6rem;
      color: var(--color-gold);
    }
  }

  &__back {
    margin-top: 8px;
  }
}
</style>
