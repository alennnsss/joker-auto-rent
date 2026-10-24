<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'

const props = defineProps<{ success: boolean }>()
const route = useRoute()
const { t } = useI18n()

const bookingId = computed(() => Number(route.query.booking) || null)
</script>

<template>
  <div class="page container result">
    <div class="card result__card">
      <div class="result__icon" :class="success ? 'is-success' : 'is-fail'" aria-hidden="true">
        {{ success ? '✓' : '!' }}
      </div>
      <template v-if="props.success">
        <h1 class="result__title">{{ t('payment.successTitle') }}</h1>
        <p class="muted">
          {{
            bookingId
              ? t('payment.successText', { id: bookingId })
              : t('payment.successTextNoId')
          }}
        </p>
      </template>
      <template v-else>
        <h1 class="result__title">{{ t('payment.failTitle') }}</h1>
        <p class="muted">{{ t('payment.failText') }}</p>
      </template>
      <div class="result__actions">
        <RouterLink
          v-if="!success && bookingId"
          :to="{ name: 'payment', params: { bookingId } }"
          class="btn btn--gold"
        >
          {{ t('payment.retry') }}
        </RouterLink>
        <RouterLink :to="{ name: 'account-bookings' }" class="btn btn--outline">
          {{ t('common.myBookings') }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.result {
  display: flex;
  justify-content: center;

  &__card {
    max-width: 520px;
    text-align: center;
  }

  &__icon {
    display: grid;
    place-items: center;
    width: 64px;
    height: 64px;
    margin: 0 auto 16px;
    border-radius: 50%;
    font-size: 1.8rem;
    font-weight: 700;

    &.is-success {
      background: var(--color-success-alpha);
      color: var(--color-success);
    }

    &.is-fail {
      background: var(--color-danger-alpha);
      color: var(--color-danger);
    }
  }

  &__title {
    font-size: 2rem;
  }

  &__actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 12px;
    margin-top: 24px;
  }
}
</style>
