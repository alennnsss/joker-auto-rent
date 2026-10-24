import { defineStore } from 'pinia'
import { ref } from 'vue'

import { carsApi } from '@/api/cars'
import { errorMessage } from '@/api/http'
import type { Car, CarFilters, Category } from '@/api/types'
import { i18n } from '@/i18n'

export const PAGE_SIZE = 12

export const useCarsStore = defineStore('cars', () => {
  const items = ref<Car[]>([])
  const total = ref(0)
  const categories = ref<Category[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Защита от гонки: учитываем только ответ на последний запрос
  let requestId = 0

  async function fetchCars(filters: CarFilters, append = false) {
    const id = ++requestId
    loading.value = true
    error.value = null
    try {
      const data = await carsApi.list({ limit: PAGE_SIZE, ...filters })
      if (id !== requestId) return
      items.value = append ? [...items.value, ...data.items] : data.items
      total.value = data.total
    } catch (e) {
      if (id === requestId) error.value = errorMessage(e, i18n.global.t('errors.loadCars'))
    } finally {
      if (id === requestId) loading.value = false
    }
  }

  async function fetchCategories() {
    if (categories.value.length) return
    try {
      categories.value = await carsApi.categories()
    } catch {
      // фильтр по категории просто будет пустым
    }
  }

  return { items, total, categories, loading, error, fetchCars, fetchCategories }
})
