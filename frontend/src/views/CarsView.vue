<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter, type LocationQuery } from 'vue-router'

import type { CarFilters as ApiFilters, CarSort } from '@/api/types'
import CarCard from '@/components/CarCard.vue'
import CarFilters, { type FilterState } from '@/components/CarFilters.vue'
import EmptyState from '@/components/EmptyState.vue'
import { PAGE_SIZE, useCarsStore } from '@/stores/cars'
import { useBookingStore } from '@/stores/booking'
import { daysBetween } from '@/utils/date'

const route = useRoute()
const router = useRouter()
const store = useCarsStore()
const booking = useBookingStore()
const { t } = useI18n()

const SORTS: CarSort[] = ['price_asc', 'price_desc', 'newest']

function fromQuery(query: LocationQuery): FilterState {
  const str = (key: string) => (typeof query[key] === 'string' ? (query[key] as string) : '')
  const sort = str('sort') as CarSort
  return {
    category_id: str('category_id'),
    days: str('days'),
    min_price: str('min_price'),
    max_price: str('max_price'),
    start_date: str('start_date'),
    end_date: str('end_date'),
    sort: SORTS.includes(sort) ? sort : 'price_asc',
  }
}

function toApi(state: FilterState): ApiFilters {
  const num = (v: string) => (v ? Number(v) : undefined)
  const hasDates = Boolean(state.start_date && state.end_date && state.end_date > state.start_date)
  return {
    category_id: num(state.category_id),
    min_price: num(state.min_price),
    max_price: num(state.max_price),
    start_date: hasDates ? state.start_date : undefined,
    end_date: hasDates ? state.end_date : undefined,
    sort: state.sort,
  }
}

const filters = ref<FilterState>(fromQuery(route.query))

const hasMore = computed(() => store.items.length < store.total)
const datesSelected = computed(() => Boolean(toApi(filters.value).start_date))
// Срок для цены в карточках: из выбранных дат, иначе из переключателя срока
const termDays = computed(() => {
  const api = toApi(filters.value)
  if (api.start_date && api.end_date) return daysBetween(api.start_date, api.end_date)
  return Math.max(1, Number(filters.value.days) || 1)
})

// Фильтры → URL (можно поделиться ссылкой, кнопка «назад» работает)
watch(
  filters,
  (state) => {
    const query = Object.fromEntries(
      Object.entries(state).filter(([key, v]) => v && !(key === 'sort' && v === 'price_asc')),
    )
    router.replace({ query })
  },
  { deep: true },
)

// URL → загрузка
watch(
  () => route.query,
  (query) => {
    filters.value = fromQuery(query)
    const api = toApi(filters.value)
    if (api.start_date && api.end_date) booking.setDates(api.start_date, api.end_date)
    store.fetchCars(api)
  },
)

onMounted(() => {
  store.fetchCategories()
  store.fetchCars(toApi(filters.value))
})

function loadMore() {
  store.fetchCars({ ...toApi(filters.value), offset: store.items.length }, true)
}

function reset() {
  filters.value = fromQuery({})
}
</script>

<template>
  <div class="page container">
    <h1 class="page-title">{{ t('cars.title') }}</h1>
    <p class="page-subtitle">{{ t('cars.subtitle') }}</p>

    <CarFilters v-model="filters" :categories="store.categories" @reset="reset" />

    <p class="results muted" aria-live="polite">
      <template v-if="!store.loading || store.items.length">
        {{ t('cars.found', store.total) }}<template v-if="datesSelected">{{
          t('cars.freeOnDates')
        }}</template>
      </template>
    </p>

    <div v-if="store.error" class="alert alert--error" role="alert">{{ store.error }}</div>

    <div class="cars-grid">
      <CarCard
        v-for="car in store.items"
        :key="car.id"
        :car="car"
        :start-date="toApi(filters).start_date"
        :end-date="toApi(filters).end_date"
        :days="termDays"
      />
      <template v-if="store.loading && !store.items.length">
        <div v-for="n in PAGE_SIZE / 2" :key="n" class="skeleton cars-grid__skeleton" />
      </template>
    </div>

    <EmptyState
      v-if="!store.loading && !store.error && !store.items.length"
      :title="t('cars.emptyTitle')"
      :text="t('cars.emptyText')"
    >
      <button type="button" class="btn btn--outline" @click="reset">
        {{ t('cars.resetFilters') }}
      </button>
    </EmptyState>

    <div v-if="hasMore" class="more">
      <button type="button" class="btn btn--outline" :disabled="store.loading" @click="loadMore">
        {{ store.loading ? t('common.loading') : t('cars.showMore') }}
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.results {
  min-height: 1.6em;
  margin-bottom: 16px;
}
.cars-grid {
  display: grid;
  width: 100%;
  min-width: 0;
  gap: 20px;
  grid-template-columns: minmax(0, 1fr);

  @include media(md) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  @include media(lg) {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  @include media(xxl) {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  > * {
    min-width: 0;
    max-width: 100%;
  }

  &__skeleton {
    aspect-ratio: 4 / 5;
  }
}
.more {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}
</style>
