<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import type { Car } from '@/api/types'
import CarPicture from '@/components/CarPicture.vue'
import { formatPrice, fuelLabel, transmissionLabel } from '@/utils/format'

const props = defineProps<{
  car: Car
  startDate?: string
  endDate?: string
}>()

const { t } = useI18n()
const title = computed(() => `${props.car.brand} ${props.car.model}`)
const query = computed(() =>
  props.startDate && props.endDate ? { start: props.startDate, end: props.endDate } : undefined,
)

const specs = computed(() => [
  {
    label: fuelLabel(props.car.fuel),
    icon: 'M4 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16M3 21h12M4 10h10M14 8h2a2 2 0 0 1 2 2v6a1.5 1.5 0 0 0 3 0V8l-3-3',
  },
  {
    label: transmissionLabel(props.car.transmission),
    icon: 'M6 4v16M12 4v16M18 4v8H6',
  },
  {
    label: t('carCard.seats', props.car.seats),
    icon: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8',
  },
])
</script>

<template>
  <article class="car-card">
    <header class="car-card__head">
      <h3 class="car-card__title">
        <RouterLink :to="{ name: 'car-detail', params: { id: car.id }, query }">
          {{ title }}
        </RouterLink>
      </h3>
      <p class="car-card__meta muted">{{ car.category.name }} · {{ car.year }}</p>
    </header>

    <RouterLink
      :to="{ name: 'car-detail', params: { id: car.id }, query }"
      class="car-card__media"
      tabindex="-1"
      aria-hidden="true"
    >
      <CarPicture
        :url="car.images[0]?.url"
        :alt="title"
        sizes="(min-width: 1536px) 25vw, (min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw"
        :max-width="800"
      />
    </RouterLink>

    <ul class="car-card__specs" :aria-label="t('carCard.specs')">
      <li v-for="s in specs" :key="s.label">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
          <path
            :d="s.icon"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
        {{ s.label }}
      </li>
    </ul>

    <footer class="car-card__footer">
      <p class="car-card__price">
        <span class="car-card__amount" data-test="price">{{ formatPrice(car.price_per_day) }}</span>
        <span class="muted">{{ t('common.perDay') }}</span>
      </p>
      <RouterLink
        :to="{ name: 'car-detail', params: { id: car.id }, query }"
        class="btn btn--gold btn--sm"
      >
        {{ t('carCard.rent') }}
      </RouterLink>
    </footer>
  </article>
</template>

<style scoped lang="scss">
.car-card {
  @include card;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;

  @include motion {
    transition:
      border-color var(--duration) var(--ease),
      transform var(--duration) var(--ease);
  }

  @include hover {
    border-color: var(--color-gold-dark);
    transform: translateY(-3px);
  }

  &__title {
    margin: 0;
    font-size: 1.2rem;

    a {
      color: var(--color-text);
    }
  }

  &__meta {
    margin: 2px 0 0;
    font-size: 0.875rem;
  }

  &__media {
    display: block;
    aspect-ratio: 16 / 10;
    border-radius: var(--radius-sm);
    overflow: hidden;
  }

  &__specs {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 8px;
    padding: 0;
    margin: 0;
    list-style: none;
    color: var(--color-text-muted);
    font-size: 0.875rem;

    li {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    svg {
      color: var(--color-gold);
    }
  }

  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-top: auto;
  }

  &__price {
    display: flex;
    align-items: baseline;
    gap: 4px;
    margin: 0;
    font-size: 0.875rem;
  }

  &__amount {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--color-text);
    white-space: nowrap;
  }
}
</style>
