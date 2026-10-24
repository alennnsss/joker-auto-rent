<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import type { CarSort, Category } from '@/api/types'
import DateField from '@/components/DateField.vue'
import { addDays, todayIso } from '@/utils/date'
import { TRANSMISSIONS, transmissionLabel } from '@/utils/format'

export interface FilterState {
  category_id: string
  transmission: string
  seats: string
  min_price: string
  max_price: string
  start_date: string
  end_date: string
  sort: CarSort
}

defineProps<{ categories: Category[] }>()
const filters = defineModel<FilterState>({ required: true })
const emit = defineEmits<{ reset: [] }>()

const { t } = useI18n()
const expanded = ref(false)
const today = todayIso()
const minEnd = computed(() => (filters.value.start_date ? addDays(filters.value.start_date, 1) : today))

function update<K extends keyof FilterState>(key: K, value: FilterState[K]) {
  const next = { ...filters.value, [key]: value }
  // Дата окончания не может быть раньше начала
  if (key === 'start_date' && next.end_date && next.end_date <= String(value)) {
    next.end_date = addDays(String(value), 1)
  }
  filters.value = next
}

const activeCount = computed(
  () =>
    [
      filters.value.category_id,
      filters.value.transmission,
      filters.value.seats,
      filters.value.min_price,
      filters.value.max_price,
      filters.value.start_date,
    ].filter(Boolean).length,
)
</script>

<template>
  <section class="filters card" :aria-label="t('filters.label')">
    <button
      type="button"
      class="filters__toggle btn btn--ghost btn--block"
      :aria-expanded="expanded"
      aria-controls="filters-body"
      @click="expanded = !expanded"
    >
      {{ t('filters.label') }}<span v-if="activeCount" class="filters__count">{{ activeCount }}</span>
    </button>

    <div id="filters-body" class="filters__body" :class="{ 'is-open': expanded }">
      <DateField
        id="f-start"
        :label="t('filters.start')"
        :min="today"
        :model-value="filters.start_date"
        @update:model-value="update('start_date', $event)"
      />
      <DateField
        id="f-end"
        :label="t('filters.end')"
        :min="minEnd"
        :model-value="filters.end_date"
        @update:model-value="update('end_date', $event)"
      />
      <div class="field">
        <label class="field__label" for="f-category">{{ t('filters.category') }}</label>
        <select
          id="f-category"
          class="select"
          :value="filters.category_id"
          @change="update('category_id', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">{{ t('filters.allCategories') }}</option>
          <option v-for="c in categories" :key="c.id" :value="String(c.id)">{{ c.name }}</option>
        </select>
      </div>
      <div class="field">
        <label class="field__label" for="f-transmission">{{ t('filters.transmission') }}</label>
        <select
          id="f-transmission"
          class="select"
          :value="filters.transmission"
          @change="update('transmission', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">{{ t('filters.anyTransmission') }}</option>
          <option v-for="value in TRANSMISSIONS" :key="value" :value="value">
            {{ transmissionLabel(value) }}
          </option>
        </select>
      </div>
      <div class="field">
        <label class="field__label" for="f-seats">{{ t('filters.seats') }}</label>
        <select
          id="f-seats"
          class="select"
          :value="filters.seats"
          @change="update('seats', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">{{ t('filters.anySeats') }}</option>
          <option v-for="n in [4, 5, 7, 9]" :key="n" :value="String(n)">{{ n }}+</option>
        </select>
      </div>
      <div class="field filters__price">
        <span class="field__label" id="f-price">{{ t('filters.price') }}</span>
        <div class="filters__range" role="group" aria-labelledby="f-price">
          <input
            class="input"
            type="number"
            inputmode="numeric"
            min="0"
            step="1000"
            :placeholder="t('filters.from')"
            :aria-label="t('filters.priceFrom')"
            :value="filters.min_price"
            @change="update('min_price', ($event.target as HTMLInputElement).value)"
          />
          <input
            class="input"
            type="number"
            inputmode="numeric"
            min="0"
            step="1000"
            :placeholder="t('filters.to')"
            :aria-label="t('filters.priceTo')"
            :value="filters.max_price"
            @change="update('max_price', ($event.target as HTMLInputElement).value)"
          />
        </div>
      </div>
      <div class="field">
        <label class="field__label" for="f-sort">{{ t('filters.sort') }}</label>
        <select
          id="f-sort"
          class="select"
          :value="filters.sort"
          @change="update('sort', ($event.target as HTMLSelectElement).value as CarSort)"
        >
          <option value="price_asc">{{ t('filters.priceAsc') }}</option>
          <option value="price_desc">{{ t('filters.priceDesc') }}</option>
          <option value="newest">{{ t('filters.newest') }}</option>
        </select>
      </div>
      <div class="filters__actions">
        <button type="button" class="btn btn--ghost btn--block" @click="emit('reset')">
          {{ t('filters.reset') }}
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">
.filters {
  padding: 8px;
  margin-bottom: 24px;

  @include media(lg) {
    padding: 20px;
  }

  &__toggle {
    @include media(lg) {
      display: none;
    }
  }

  &__count {
    display: inline-grid;
    place-items: center;
    min-width: 22px;
    height: 22px;
    padding: 0 6px;
    margin-left: 8px;
    border-radius: 999px;
    background: var(--gradient-gold);
    color: var(--color-on-gold);
    font-size: 0.8rem;
  }

  &__body {
    display: none;
    grid-template-columns: 1fr;
    gap: 0 16px;
    padding: 16px 8px 8px;

    &.is-open {
      display: grid;
    }

    @include media(sm) {
      grid-template-columns: 1fr 1fr;
    }

    @include media(lg) {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      padding: 0;
    }

    @include media(xl) {
      grid-template-columns: repeat(4, 1fr) 1.4fr;
    }

    .field {
      margin-bottom: 12px;
    }
  }

  &__range {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  &__actions {
    display: flex;
    align-items: flex-end;
    padding-bottom: 12px;
  }
}
</style>
