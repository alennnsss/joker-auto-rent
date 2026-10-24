<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'

import { bookingsApi } from '@/api/bookings'
import { errorMessage } from '@/api/http'
import type { Booking } from '@/api/types'
import CarPicture from '@/components/CarPicture.vue'
import EmptyState from '@/components/EmptyState.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { locationLabel } from '@/config/locations'
import { formatDate, formatDays, formatPrice, formatTime } from '@/utils/format'

const route = useRoute()
const { t } = useI18n()

const bookings = ref<Booking[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const busyId = ref<number | null>(null)

const createdId = computed(() => Number(route.query.created) || null)

onMounted(async () => {
  try {
    bookings.value = await bookingsApi.my()
  } catch (e) {
    error.value = errorMessage(e, t('errors.loadBookings'))
  } finally {
    loading.value = false
  }
})

function canCancel(b: Booking) {
  return b.status === 'pending' || b.status === 'confirmed'
}

async function cancel(b: Booking) {
  if (!window.confirm(t('myBookings.confirmCancel', { id: b.id }))) return
  busyId.value = b.id
  error.value = null
  try {
    const updated = await bookingsApi.cancel(b.id)
    bookings.value = bookings.value.map((x) => (x.id === updated.id ? updated : x))
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busyId.value = null
  }
}
</script>

<template>
  <div>
    <div v-if="createdId" class="alert alert--success" role="status">
      {{ t('myBookings.created', { id: createdId }) }}
    </div>
    <div v-if="error" class="alert alert--error" role="alert">{{ error }}</div>

    <div v-if="loading" class="list">
      <div v-for="n in 2" :key="n" class="skeleton" style="height: 160px" />
    </div>

    <EmptyState
      v-else-if="!bookings.length && !error"
      :title="t('myBookings.emptyTitle')"
      :text="t('myBookings.emptyText')"
    >
      <RouterLink :to="{ name: 'cars' }" class="btn btn--gold">{{ t('myBookings.toFleet') }}</RouterLink>
    </EmptyState>

    <ul v-else class="list">
      <li
        v-for="b in bookings"
        :key="b.id"
        class="item card"
        :class="{ 'is-new': b.id === createdId }"
      >
        <div class="item__media">
          <CarPicture
            :url="b.car.images[0]?.url"
            :alt="`${b.car.brand} ${b.car.model}`"
            sizes="200px"
            :max-width="400"
          />
        </div>
        <div class="item__body">
          <div class="item__head">
            <h3 class="item__title">{{ b.car.brand }} {{ b.car.model }}</h3>
            <StatusBadge kind="booking" :status="b.status" />
          </div>
          <p class="muted item__meta">
            {{ t('myBookings.meta', { id: b.id, days: formatDays(b.days) }) }}
          </p>

          <dl class="trip">
            <div class="trip__leg">
              <dt><span class="trip__dot" aria-hidden="true" />{{ t('common.pickup') }}</dt>
              <dd>
                <span class="trip__when">{{ formatDate(b.start_date) }}, {{ formatTime(b.pickup_time) }}</span>
                <span class="trip__where muted">{{ locationLabel(b.pickup_location) }}</span>
              </dd>
            </div>
            <div class="trip__leg">
              <dt>
                <span class="trip__dot trip__dot--return" aria-hidden="true" />{{ t('common.return') }}
              </dt>
              <dd>
                <span class="trip__when">{{ formatDate(b.end_date) }}, {{ formatTime(b.return_time) }}</span>
                <span class="trip__where muted">{{ locationLabel(b.return_location) }}</span>
              </dd>
            </div>
          </dl>

          <p class="item__price">{{ formatPrice(b.total_price) }}</p>
          <div class="item__actions">
            <button
              v-if="canCancel(b)"
              type="button"
              class="btn btn--danger btn--sm"
              :disabled="busyId === b.id"
              @click="cancel(b)"
            >
              {{ t('common.cancel') }}
            </button>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped lang="scss">
.trip {
  display: grid;
  gap: 8px;
  margin: 0 0 12px;

  @include media(lg) {
    grid-template-columns: 1fr 1fr;
  }

  &__leg {
    padding: 12px 14px;
    border-radius: var(--radius-sm);
    background: var(--color-surface-2);

    dt {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.8rem;
      color: var(--color-text-muted);
      margin-bottom: 4px;
    }

    dd {
      display: flex;
      flex-direction: column;
      margin: 0;
    }
  }

  &__when {
    font-weight: 600;
  }

  &__where {
    font-size: 0.9rem;
  }

  &__dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    border: 2px solid var(--color-gold-dark);
    background: var(--color-gold);

    &--return {
      background: transparent;
    }
  }
}

.list {
  display: grid;
  gap: 16px;
  padding: 0;
  margin: 0;
  list-style: none;
}

.item {
  display: grid;
  gap: 16px;
  padding: 16px;

  @include media(md) {
    grid-template-columns: 200px 1fr;
    padding: 20px;
  }

  &.is-new {
    border-color: var(--color-gold);
  }

  &__media {
    aspect-ratio: 16 / 10;
    border-radius: var(--radius-sm);
    overflow: hidden;
  }

  &__head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }

  &__title {
    margin: 0;
  }

  &__meta {
    margin: 6px 0;
    font-size: 0.9rem;
  }

  &__price {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--color-gold);

    .muted {
      font-size: 0.875rem;
      font-weight: 400;
    }
  }

  &__actions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>
