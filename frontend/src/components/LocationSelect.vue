<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { DELIVERY_PREFIX, LOCATIONS, locationLabel } from '@/config/locations'

defineProps<{ id: string; label: string }>()
const model = defineModel<string>({ required: true })
const { t } = useI18n()

const DELIVERY = 'delivery'
const isDelivery = computed(() => model.value.startsWith(DELIVERY_PREFIX))

const selected = computed({
  get: () => (isDelivery.value ? DELIVERY : model.value),
  set: (value: string) => {
    model.value = value === DELIVERY ? DELIVERY_PREFIX : value
  },
})

const address = computed({
  get: () => (isDelivery.value ? model.value.slice(DELIVERY_PREFIX.length) : ''),
  set: (value: string) => {
    model.value = DELIVERY_PREFIX + value
  },
})
</script>

<template>
  <div class="field">
    <label class="field__label" :for="id">{{ label }}</label>
    <select :id="id" v-model="selected" class="select">
      <option v-for="location in LOCATIONS" :key="location.key" :value="location.value">
        {{ locationLabel(location.value) }}
      </option>
      <option :value="DELIVERY">{{ t('locations.delivery') }}</option>
    </select>
    <template v-if="isDelivery">
      <input
        v-model="address"
        class="input"
        :aria-label="t('locations.deliveryAria', { label })"
        :placeholder="t('locations.deliveryPlaceholder')"
        autocomplete="street-address"
      />
      <span class="field__hint muted">{{ t('locations.deliveryHint') }}</span>
    </template>
  </div>
</template>

<style scoped lang="scss">
.field__hint {
  font-size: 0.8rem;
}
</style>
