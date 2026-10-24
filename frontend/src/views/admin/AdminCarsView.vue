<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import { adminApi } from '@/api/admin'
import { errorMessage } from '@/api/http'
import type { Car } from '@/api/types'
import CarPicture from '@/components/CarPicture.vue'
import { formatPrice, transmissionLabel } from '@/utils/format'

const { t } = useI18n()
const cars = ref<Car[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

async function load() {
  loading.value = true
  try {
    cars.value = (await adminApi.cars({ limit: 100, sort: 'newest' })).items
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

async function toggleActive(car: Car) {
  error.value = null
  try {
    const updated = await adminApi.updateCar(car.id, { is_active: !car.is_active })
    cars.value = cars.value.map((c) => (c.id === updated.id ? updated : c))
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function remove(car: Car) {
  if (!window.confirm(t('adminCars.confirmDelete', { name: `${car.brand} ${car.model}` }))) return
  error.value = null
  try {
    await adminApi.deleteCar(car.id)
    cars.value = cars.value.filter((c) => c.id !== car.id)
  } catch (e) {
    error.value = errorMessage(e)
  }
}

onMounted(load)
</script>

<template>
  <div class="head">
    <h1 class="page-title">{{ t('admin.cars') }}</h1>
    <RouterLink :to="{ name: 'admin-car-new' }" class="btn btn--gold btn--sm">
      {{ t('adminCars.add') }}
    </RouterLink>
  </div>

  <div v-if="error" class="alert alert--error" role="alert">{{ error }}</div>

  <div class="table-wrap">
    <table class="table">
      <thead>
        <tr>
          <th>{{ t('adminCars.photo') }}</th>
          <th>{{ t('adminCars.car') }}</th>
          <th>{{ t('adminCars.category') }}</th>
          <th>{{ t('adminCars.gearbox') }}</th>
          <th>{{ t('adminCars.price') }}</th>
          <th>{{ t('adminCars.onSite') }}</th>
          <th><span class="visually-hidden">{{ t('common.actions') }}</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="7" class="muted">{{ t('common.loading') }}</td>
        </tr>
        <tr v-for="car in cars" v-else :key="car.id">
          <td>
            <div class="thumb">
              <CarPicture :url="car.images[0]?.url" :alt="car.model" sizes="80px" :max-width="400" />
            </div>
          </td>
          <td>
            <RouterLink :to="{ name: 'admin-car-edit', params: { id: car.id } }">
              {{ car.brand }} {{ car.model }}
            </RouterLink>
            <span class="muted"> · {{ car.year }}</span>
          </td>
          <td>{{ car.category.name }}</td>
          <td>{{ transmissionLabel(car.transmission) }}</td>
          <td>{{ formatPrice(car.price_per_day) }}</td>
          <td>
            <label class="checkbox">
              <input type="checkbox" :checked="car.is_active" @change="toggleActive(car)" />
              <span class="visually-hidden">{{ t('adminCars.showOnSite') }}</span>
            </label>
          </td>
          <td class="actions">
            <RouterLink
              :to="{ name: 'admin-car-edit', params: { id: car.id } }"
              class="btn btn--outline btn--sm"
            >
              {{ t('common.edit') }}
            </RouterLink>
            <button type="button" class="btn btn--danger btn--sm" @click="remove(car)">
              {{ t('common.delete') }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped lang="scss">
.head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;

  h1 {
    margin: 0;
  }
}

.thumb {
  width: 80px;
  height: 50px;
  border-radius: 6px;
  overflow: hidden;
}

.actions {
  display: flex;
  gap: 8px;
}
</style>
