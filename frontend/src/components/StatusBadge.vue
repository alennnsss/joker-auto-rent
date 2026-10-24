<script setup lang="ts">
import { computed } from 'vue'

import type { BookingStatus, PaymentStatus } from '@/api/types'
import { bookingStatusLabel, paymentStatusLabel } from '@/utils/format'

const props = defineProps<
  { kind: 'booking'; status: BookingStatus } | { kind: 'payment'; status: PaymentStatus }
>()

const label = computed(() =>
  props.kind === 'booking' ? bookingStatusLabel(props.status) : paymentStatusLabel(props.status),
)

const tone = computed(() => {
  switch (props.status) {
    case 'confirmed':
    case 'active':
    case 'succeeded':
      return 'success'
    case 'cancelled':
    case 'failed':
      return 'danger'
    case 'pending':
      return 'gold'
    default:
      return 'neutral'
  }
})
</script>

<template>
  <span class="badge" :class="`badge--${tone}`">{{ label }}</span>
</template>

<style scoped lang="scss">
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
  color: var(--color-text-muted);

  &--success {
    border-color: var(--color-success);
    color: var(--color-success);
    background: var(--color-success-alpha);
  }

  &--danger {
    border-color: var(--color-danger);
    color: var(--color-danger);
    background: var(--color-danger-alpha);
  }

  &--gold {
    border-color: var(--color-gold-dark);
    color: var(--color-gold);
    background: var(--color-gold-alpha);
  }
}
</style>
