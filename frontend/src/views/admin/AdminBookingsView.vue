<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { adminApi } from '@/api/admin'
import { errorMessage } from '@/api/http'
import type { AdminBooking, BookingStatus } from '@/api/types'
import StatusBadge from '@/components/StatusBadge.vue'
import { locationLabel } from '@/config/locations'
import {
  BOOKING_STATUSES,
  bookingStatusLabel,
  formatDate,
  formatPrice,
  formatTime,
} from '@/utils/format'

// Должно совпадать с ADMIN_TRANSITIONS в backend/app/services/bookings.py
const TRANSITIONS: Record<BookingStatus, BookingStatus[]> = {
  pending: ['confirmed', 'cancelled'],
  confirmed: ['active', 'cancelled'],
  active: ['completed'],
  completed: [],
  cancelled: [],
}

const { t } = useI18n()

// Кнопка перехода в статус (в pending перейти нельзя — кнопки нет)
const ACTION_LABELS = {
  confirmed: 'adminBookings.confirm',
  active: 'adminBookings.issue',
  completed: 'adminBookings.complete',
  cancelled: 'common.cancel',
} as const

function actionLabel(next: BookingStatus) {
  return next === 'pending' ? '' : t(ACTION_LABELS[next])
}

const FILTERS = computed<{ value: BookingStatus | ''; label: string }[]>(() => [
  { value: '', label: t('adminBookings.all') },
  ...BOOKING_STATUSES.map((s) => ({ value: s, label: bookingStatusLabel(s) })),
])

const status = ref<BookingStatus | ''>('pending')
const bookings = ref<AdminBooking[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const busyId = ref<number | null>(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    bookings.value = await adminApi.bookings(status.value || undefined)
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

async function change(b: AdminBooking, next: BookingStatus) {
  if (next === 'cancelled' && !window.confirm(t('myBookings.confirmCancel', { id: b.id }))) return
  busyId.value = b.id
  error.value = null
  try {
    const updated = await adminApi.setBookingStatus(b.id, next)
    bookings.value = bookings.value.map((x) => (x.id === updated.id ? updated : x))
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busyId.value = null
  }
}

watch(status, load)
onMounted(load)
</script>

<template>
  <h1 class="page-title">{{ t('admin.bookings') }}</h1>

  <div class="chips" role="tablist" :aria-label="t('adminBookings.filterLabel')">
    <button
      v-for="f in FILTERS"
      :key="f.value"
      type="button"
      role="tab"
      class="chip"
      :class="{ 'is-active': status === f.value }"
      :aria-selected="status === f.value"
      @click="status = f.value"
    >
      {{ f.label }}
    </button>
  </div>

  <div v-if="error" class="alert alert--error" role="alert">{{ error }}</div>

  <div class="table-wrap">
    <table class="table">
      <thead>
        <tr>
          <th>№</th>
          <th>{{ t('adminBookings.client') }}</th>
          <th>{{ t('adminBookings.car') }}</th>
          <th>{{ t('adminBookings.dates') }}</th>
          <th>{{ t('adminBookings.sum') }}</th>
          <th>{{ t('adminBookings.status') }}</th>
          <th><span class="visually-hidden">{{ t('common.actions') }}</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="7" class="muted">{{ t('common.loading') }}</td>
        </tr>
        <tr v-else-if="!bookings.length">
          <td colspan="7" class="muted">{{ t('adminBookings.empty') }}</td>
        </tr>
        <tr v-for="b in bookings" v-else :key="b.id">
          <td>{{ b.id }}</td>
          <td>
            {{ b.user.full_name }}<br />
            <a v-if="b.user.phone" :href="`tel:${b.user.phone.replace(/[^\d+]/g, '')}`">
              {{ b.user.phone }}
            </a>
          </td>
          <td>{{ b.car.brand }} {{ b.car.model }}</td>
          <td>
            {{ formatDate(b.start_date) }} {{ formatTime(b.pickup_time) }} —
            {{ formatDate(b.end_date) }} {{ formatTime(b.return_time) }}
            <br />
            <span class="muted where">
              {{ locationLabel(b.pickup_location) }} → {{ locationLabel(b.return_location) }}
            </span>
          </td>
          <td>{{ formatPrice(b.total_price) }}</td>
          <td><StatusBadge kind="booking" :status="b.status" /></td>
          <td class="actions">
            <button
              v-for="next in TRANSITIONS[b.status]"
              :key="next"
              type="button"
              class="btn btn--sm"
              :class="next === 'cancelled' ? 'btn--danger' : 'btn--outline'"
              :disabled="busyId === b.id"
              @click="change(b, next)"
            >
              {{ actionLabel(next) }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped lang="scss">
.chips {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.chip {
  min-height: 44px;
  padding: 0 16px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-muted);
  font: inherit;
  white-space: nowrap;
  cursor: pointer;

  &.is-active {
    border-color: var(--color-gold);
    color: var(--color-gold);
    background: var(--color-gold-alpha);
  }
}

.actions {
  display: flex;
  gap: 8px;
}

.where {
  display: inline-block;
  max-width: 320px;
  white-space: normal;
  font-size: 0.85rem;
}

</style>
