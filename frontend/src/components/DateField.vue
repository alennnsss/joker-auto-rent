<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import DatePicker from 'primevue/datepicker'

import { fromIso, toIso } from '@/utils/date'

const props = withDefaults(
  defineProps<{
    id: string
    label: string
    min?: string
    disabledDays?: string[]
    placeholder?: string
  }>(),
  { min: undefined, disabledDays: () => [], placeholder: undefined },
)

const { t } = useI18n()

/** Дата в формате YYYY-MM-DD ('' — не выбрана). */
const model = defineModel<string>({ required: true })

const value = computed({
  get: () => fromIso(model.value),
  set: (date: unknown) => {
    model.value = date instanceof Date ? toIso(date) : ''
  },
})

const minDate = computed(() => fromIso(props.min ?? '') ?? undefined)
const disabledDates = computed(() =>
  props.disabledDays.map(fromIso).filter((d): d is Date => d !== null),
)
</script>

<template>
  <div class="field date-field">
    <label class="field__label" :for="id">{{ label }}</label>
    <DatePicker
      v-model="value"
      :input-id="id"
      date-format="dd.mm.yy"
      :min-date="minDate"
      :disabled-dates="disabledDates"
      :manual-input="false"
      :placeholder="placeholder ?? t('common.datePlaceholder')"
      show-icon
      icon-display="input"
      append-to="body"
      fluid
    />
  </div>
</template>
