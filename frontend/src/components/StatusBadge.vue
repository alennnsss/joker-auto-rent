<script setup lang="ts">
import { computed } from 'vue'

import type { BookingStatus } from '@/api/types'
import { bookingStatusLabel } from '@/utils/format'

const props = defineProps<{ kind: 'booking'; status: BookingStatus }>()

const label = computed(() => bookingStatusLabel(props.status))

const tone = computed(() => {
  switch (props.status) {
    case 'confirmed':
    case 'active':
      return 'success'
    case 'cancelled':
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
