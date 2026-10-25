<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import type { CarSort, Category } from '@/api/types'
import DateField from '@/components/DateField.vue'
import TermPicker from '@/components/TermPicker.vue'
import { clampTerm } from '@/config/terms'
import { todayIso } from '@/utils/date'

export interface FilterState {
  category_id: string
  /** Срок аренды в сутках — для расчёта цены в карточках и проверки занятости */
  days: string
  min_price: string
  max_price: string
  /** Дата получения; дата возврата = получение + срок */
  start_date: string
  sort: CarSort
}

defineProps<{ categories: Category[] }>()
const filters = defineModel<FilterState>({ required: true })
const emit = defineEmits<{ reset: [] }>()

const { t } = useI18n()
const expanded = ref(false)
const today = todayIso()

function update<K extends keyof FilterState>(key: K, value: FilterState[K]) {
  filters.value = { ...filters.value, [key]: value }
}

const term = computed({
  get: () => clampTerm(filters.value.days || 1),
  set: (n: number) => update('days', String(n)),
})

const activeCount = computed(
  () =>
    [
      filters.value.category_id,
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
      <TermPicker id="f-term" v-model="term" class="filters__terms" :label="t('filters.term')" />
      <DateField
        id="f-start"
        :label="t('filters.start')"
        :min="today"
        :model-value="filters.start_date"
        @update:model-value="update('start_date', $event)"
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
      <div class="field filters__price">
        <span id="f-price" class="field__label">{{ t('filters.price') }}</span>
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
    grid-template-columns: minmax(0, 1fr);
    gap: 0 16px;
    padding: 16px 8px 8px;

    &.is-open {
      display: grid;
    }

    @include media(sm) {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    @include media(lg) {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      padding: 0;
    }

    // Под сроком — одна строка: дата, класс, цена, сортировка, сброс
    @include media(xl) {
      grid-template-columns: repeat(2, minmax(0, 1fr)) minmax(0, 1.4fr) minmax(0, 1fr) auto;
    }

    .field {
      margin-bottom: 12px;
    }
  }

  &__terms {
    grid-column: 1 / -1;
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
