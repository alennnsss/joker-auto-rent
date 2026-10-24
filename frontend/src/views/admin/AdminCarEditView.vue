<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'

import { adminApi } from '@/api/admin'
import { carsApi } from '@/api/cars'
import { errorMessage } from '@/api/http'
import type { Car, CarPayload, Category } from '@/api/types'
import CarPicture from '@/components/CarPicture.vue'
import { FUELS, fuelLabel, TRANSMISSIONS, transmissionLabel } from '@/utils/format'

const props = defineProps<{ id?: number }>()
const router = useRouter()
const { t } = useI18n()

const isNew = computed(() => props.id === undefined)
const car = ref<Car | null>(null)
const categories = ref<Category[]>([])
const loading = ref(true)
const saving = ref(false)
const error = ref<string | null>(null)
const notice = ref<string | null>(null)
const newCategory = ref('')
const imageUrl = ref('')
const uploading = ref(false)

const form = reactive<CarPayload>({
  brand: '',
  model: '',
  year: new Date().getFullYear(),
  category_id: 0,
  transmission: 'automatic',
  fuel: 'petrol',
  seats: 5,
  price_per_day: '',
  deposit: '0',
  description: '',
  is_active: true,
})

function fill(c: Car) {
  car.value = c
  Object.assign(form, {
    brand: c.brand,
    model: c.model,
    year: c.year,
    category_id: c.category.id,
    transmission: c.transmission,
    fuel: c.fuel,
    seats: c.seats,
    price_per_day: String(Number(c.price_per_day)),
    deposit: String(Number(c.deposit)),
    description: c.description,
    is_active: c.is_active,
  })
}

onMounted(async () => {
  try {
    categories.value = await carsApi.categories()
    if (props.id !== undefined) fill(await adminApi.car(props.id))
    else if (categories.value[0]) form.category_id = categories.value[0].id
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
})

async function save() {
  saving.value = true
  error.value = null
  notice.value = null
  try {
    if (isNew.value) {
      const created = await adminApi.createCar({ ...form })
      await router.replace({ name: 'admin-car-edit', params: { id: created.id } })
      fill(created)
      notice.value = t('adminCarEdit.created')
    } else if (car.value) {
      fill(await adminApi.updateCar(car.value.id, { ...form }))
      notice.value = t('adminCarEdit.saved')
    }
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    saving.value = false
  }
}

async function addCategory() {
  const name = newCategory.value.trim()
  if (!name) return
  try {
    const created = await adminApi.createCategory(name)
    categories.value.push(created)
    form.category_id = created.id
    newCategory.value = ''
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function onFiles(event: Event) {
  const input = event.target as HTMLInputElement
  if (!car.value || !input.files?.length) return
  uploading.value = true
  error.value = null
  try {
    for (const file of Array.from(input.files)) {
      fill(await adminApi.uploadImage(car.value.id, file))
    }
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function addByUrl() {
  if (!car.value || !imageUrl.value.trim()) return
  try {
    fill(await adminApi.addImageUrl(car.value.id, imageUrl.value.trim()))
    imageUrl.value = ''
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function removeImage(imageId: number) {
  if (!car.value || !window.confirm(t('adminCarEdit.confirmDeletePhoto'))) return
  try {
    fill(await adminApi.deleteImage(car.value.id, imageId))
  } catch (e) {
    error.value = errorMessage(e)
  }
}
</script>

<template>
  <RouterLink :to="{ name: 'admin-cars' }" class="back">{{ t('adminCarEdit.back') }}</RouterLink>
  <h1 class="page-title">
    {{ isNew ? t('adminCarEdit.newTitle') : `${car?.brand ?? ''} ${car?.model ?? ''}` }}
  </h1>

  <div v-if="error" class="alert alert--error" role="alert">{{ error }}</div>
  <div v-if="notice" class="alert alert--success" role="status">{{ notice }}</div>

  <div v-if="loading" class="skeleton" style="height: 400px" />

  <div v-else class="editor">
    <form class="card" @submit.prevent="save">
      <div class="grid">
        <div class="field">
          <label class="field__label" for="c-brand">{{ t('adminCarEdit.brand') }}</label>
          <input id="c-brand" v-model="form.brand" class="input" required />
        </div>
        <div class="field">
          <label class="field__label" for="c-model">{{ t('adminCarEdit.model') }}</label>
          <input id="c-model" v-model="form.model" class="input" required />
        </div>
        <div class="field">
          <label class="field__label" for="c-year">{{ t('adminCarEdit.year') }}</label>
          <input id="c-year" v-model.number="form.year" class="input" type="number" min="1990" required />
        </div>
        <div class="field">
          <label class="field__label" for="c-category">{{ t('adminCarEdit.category') }}</label>
          <select id="c-category" v-model.number="form.category_id" class="select" required>
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
        <div class="field">
          <label class="field__label" for="c-trans">{{ t('adminCarEdit.transmission') }}</label>
          <select id="c-trans" v-model="form.transmission" class="select">
            <option v-for="value in TRANSMISSIONS" :key="value" :value="value">
              {{ transmissionLabel(value) }}
            </option>
          </select>
        </div>
        <div class="field">
          <label class="field__label" for="c-fuel">{{ t('adminCarEdit.fuel') }}</label>
          <select id="c-fuel" v-model="form.fuel" class="select">
            <option v-for="value in FUELS" :key="value" :value="value">{{ fuelLabel(value) }}</option>
          </select>
        </div>
        <div class="field">
          <label class="field__label" for="c-seats">{{ t('adminCarEdit.seats') }}</label>
          <input id="c-seats" v-model.number="form.seats" class="input" type="number" min="1" max="60" required />
        </div>
        <div class="field">
          <label class="field__label" for="c-price">{{ t('adminCarEdit.price') }}</label>
          <input
            id="c-price"
            v-model="form.price_per_day"
            class="input"
            type="number"
            min="1"
            step="any"
            inputmode="decimal"
            required
          />
        </div>
        <div class="field">
          <label class="field__label" for="c-deposit">{{ t('adminCarEdit.deposit') }}</label>
          <input
            id="c-deposit"
            v-model="form.deposit"
            class="input"
            type="number"
            min="0"
            step="any"
            inputmode="decimal"
            required
          />
        </div>
      </div>

      <div class="field">
        <label class="field__label" for="c-desc">{{ t('adminCarEdit.description') }}</label>
        <textarea id="c-desc" v-model="form.description" class="textarea" />
      </div>

      <label class="checkbox">
        <input v-model="form.is_active" type="checkbox" />
        <span>{{ t('adminCarEdit.showInCatalog') }}</span>
      </label>

      <div class="form-actions">
        <button type="submit" class="btn btn--gold" :disabled="saving">
          {{ saving ? t('common.saving') : isNew ? t('adminCarEdit.create') : t('common.save') }}
        </button>
      </div>

      <details class="new-category">
        <summary class="muted">{{ t('adminCarEdit.newCategory') }}</summary>
        <div class="inline">
          <input v-model="newCategory" class="input" :placeholder="t('adminCarEdit.categoryPlaceholder')" />
          <button type="button" class="btn btn--outline btn--sm" @click="addCategory">
            {{ t('common.add') }}
          </button>
        </div>
      </details>
    </form>

    <section v-if="car" class="card">
      <h2 class="section-title">{{ t('adminCarEdit.photos') }}</h2>
      <p class="muted hint">{{ t('adminCarEdit.photosHint') }}</p>

      <ul class="images">
        <li v-for="image in car.images" :key="image.id" class="images__item">
          <CarPicture
            :url="image.url"
            :alt="t('adminCarEdit.photoAlt', { n: image.sort_order + 1 })"
            sizes="200px"
            :max-width="400"
          />
          <button
            type="button"
            class="images__remove"
            :aria-label="t('adminCarEdit.deletePhoto')"
            @click="removeImage(image.id)"
          >
            ×
          </button>
        </li>
      </ul>

      <label class="btn btn--outline btn--block upload">
        {{ uploading ? t('common.loading') : t('adminCarEdit.upload') }}
        <input
          type="file"
          accept="image/webp,image/jpeg,image/png"
          multiple
          class="visually-hidden"
          :disabled="uploading"
          @change="onFiles"
        />
      </label>

      <div class="inline">
        <input v-model="imageUrl" class="input" type="url" :placeholder="t('adminCarEdit.urlPlaceholder')" />
        <button type="button" class="btn btn--ghost btn--sm" @click="addByUrl">{{ t('common.add') }}</button>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
.back {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  margin-bottom: 8px;
}

.editor {
  display: grid;
  gap: 24px;

  @include media(xl) {
    grid-template-columns: minmax(0, 1.5fr) minmax(320px, 1fr);
    align-items: start;
  }
}

.grid {
  display: grid;
  gap: 0 16px;

  @include media(sm) {
    grid-template-columns: 1fr 1fr;
  }

  @include media(lg) {
    grid-template-columns: repeat(3, 1fr);
  }
}

.form-actions {
  margin-top: 16px;
}

.new-category {
  margin-top: 24px;

  summary {
    min-height: 44px;
    display: flex;
    align-items: center;
    cursor: pointer;
  }
}

.inline {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 12px;

  .input {
    flex: 1;
  }
}

.section-title {
  font-size: 1.3rem;
}

.hint {
  font-size: 0.875rem;
}

.images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
  padding: 0;
  margin: 0 0 16px;
  list-style: none;

  &__item {
    position: relative;
    aspect-ratio: 4 / 3;
    border-radius: var(--radius-sm);
    overflow: hidden;
  }

  &__remove {
    position: absolute;
    top: 4px;
    right: 4px;
    width: 44px;
    height: 44px;
    border: 0;
    border-radius: 50%;
    background: var(--color-overlay);
    color: var(--color-text);
    font-size: 1.4rem;
    cursor: pointer;

    @include hover {
      color: var(--color-danger);
    }
  }
}

.upload {
  position: relative;
  cursor: pointer;
}
</style>
