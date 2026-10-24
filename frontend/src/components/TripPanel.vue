<script setup lang="ts">
import { computed, type WritableComputedRef } from 'vue'
import { useI18n } from 'vue-i18n'

import DateField from '@/components/DateField.vue'
import LocationSelect from '@/components/LocationSelect.vue'
import { TIMES } from '@/config/locations'
import type { Trip } from '@/stores/booking'
import { addDays, todayIso } from '@/utils/date'

const props = withDefaults(
  defineProps<{
    /** Занятые дни (YYYY-MM-DD) — блокируются в календаре. */
    disabledDays?: string[]
    /** Вертикальная раскладка для узких колонок (карточка авто, бронирование). */
    compact?: boolean
    /** Один блок «Получение и возврат»: одно место и одно время для обеих точек. */
    single?: boolean
    idPrefix?: string
  }>(),
  { disabledDays: () => [], compact: false, single: false, idPrefix: 'trip' },
)

const trip = defineModel<Trip>({ required: true })
const { t } = useI18n()
const today = todayIso()

function field<K extends keyof Trip>(key: K): WritableComputedRef<Trip[K]> {
  return computed({
    get: () => trip.value[key],
    set: (value) => {
      const next = { ...trip.value, [key]: value }
      // Возврат не раньше следующего дня после получения
      if (key === 'pickupDate' && next.pickupDate && next.returnDate <= next.pickupDate) {
        next.returnDate = addDays(next.pickupDate, 1)
      }
      trip.value = next
    },
  })
}

const pickupLocation = field('pickupLocation')
const pickupDate = field('pickupDate')
const pickupTime = field('pickupTime')
const returnLocation = field('returnLocation')
const returnDate = field('returnDate')
const returnTime = field('returnTime')

// Режим single: место и время общие — пишем сразу в обе точки
const sharedLocation = computed({
  get: () => trip.value.pickupLocation,
  set: (value: string) => {
    trip.value = { ...trip.value, pickupLocation: value, returnLocation: value }
  },
})
const sharedTime = computed({
  get: () => trip.value.pickupTime,
  set: (value: string) => {
    trip.value = { ...trip.value, pickupTime: value, returnTime: value }
  },
})

const minReturn = computed(() => (trip.value.pickupDate ? addDays(trip.value.pickupDate, 1) : today))
const id = (name: string) => `${props.idPrefix}-${name}`

function swapLocations() {
  trip.value = {
    ...trip.value,
    pickupLocation: trip.value.returnLocation,
    returnLocation: trip.value.pickupLocation,
  }
}
</script>

<template>
  <div v-if="single" class="trip trip--single">
    <fieldset class="trip__card">
      <legend class="trip__legend">
        <span class="trip__dot" aria-hidden="true" />{{ t('trip.together') }}
      </legend>
      <div class="trip__fields">
        <LocationSelect :id="id('location')" v-model="sharedLocation" :label="t('common.place')" />
        <DateField
          :id="id('pickup-date')"
          v-model="pickupDate"
          :label="t('trip.pickupDate')"
          :min="today"
          :disabled-days="disabledDays"
        />
        <DateField
          :id="id('return-date')"
          v-model="returnDate"
          :label="t('trip.returnDate')"
          :min="minReturn"
          :disabled-days="disabledDays"
        />
        <div class="field">
          <label class="field__label" :for="id('time')">{{ t('common.time') }}</label>
          <select :id="id('time')" v-model="sharedTime" class="select">
            <option v-for="t in TIMES" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
      </div>
    </fieldset>
  </div>

  <div v-else class="trip" :class="{ 'trip--compact': compact }">
    <fieldset class="trip__card">
      <legend class="trip__legend">
        <span class="trip__dot" aria-hidden="true" />{{ t('common.pickup') }}
      </legend>
      <div class="trip__fields">
        <LocationSelect
          :id="id('pickup-location')"
          v-model="pickupLocation"
          :label="t('common.place')"
        />
        <DateField
          :id="id('pickup-date')"
          v-model="pickupDate"
          :label="t('common.date')"
          :min="today"
          :disabled-days="disabledDays"
        />
        <div class="field">
          <label class="field__label" :for="id('pickup-time')">{{ t('common.time') }}</label>
          <select :id="id('pickup-time')" v-model="pickupTime" class="select">
            <option v-for="t in TIMES" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
      </div>
    </fieldset>

    <button
      type="button"
      class="trip__swap"
      :aria-label="t('trip.swap')"
      :title="t('trip.swapTitle')"
      @click="swapLocations"
    >
      <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
        <path
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M7 4v16M7 4 3 8M7 4l4 4M17 20V4m0 16-4-4m4 4 4-4"
        />
      </svg>
    </button>

    <fieldset class="trip__card">
      <legend class="trip__legend">
        <span class="trip__dot trip__dot--return" aria-hidden="true" />{{ t('common.return') }}
      </legend>
      <div class="trip__fields">
        <LocationSelect
          :id="id('return-location')"
          v-model="returnLocation"
          :label="t('common.place')"
        />
        <DateField
          :id="id('return-date')"
          v-model="returnDate"
          :label="t('common.date')"
          :min="minReturn"
          :disabled-days="disabledDays"
        />
        <div class="field">
          <label class="field__label" :for="id('return-time')">{{ t('common.time') }}</label>
          <select :id="id('return-time')" v-model="returnTime" class="select">
            <option v-for="t in TIMES" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
      </div>
    </fieldset>
  </div>
</template>

<style scoped lang="scss">
.trip {
  display: grid;
  gap: 12px;
  align-items: center;

  // Две карточки с кнопкой обмена между ними; в режиме single карточка одна — на всю ширину
  &:not(.trip--compact, .trip--single) {
    @include media(xl) {
      grid-template-columns: 1fr auto 1fr;
      gap: 20px;
    }
  }

  &__card {
    min-width: 0;
    margin: 0;
    padding: 16px 16px 4px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    background: var(--color-surface);
  }

  &__legend {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 6px;
    font-weight: 600;
  }

  &__dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 3px solid var(--color-gold-dark);
    background: var(--color-gold);

    &--return {
      background: var(--color-surface);
    }
  }

  &__fields {
    display: grid;
    gap: 0 12px;
    margin-top: 8px;

    @include media(sm) {
      grid-template-columns: 1.4fr 1fr 0.8fr;
    }
  }

  &--compact &__fields {
    @include media(sm) {
      grid-template-columns: 1fr 1fr;

      > :first-child {
        grid-column: 1 / -1;
      }
    }
  }

  &__swap {
    justify-self: center;
    display: grid;
    place-items: center;
    width: 48px;
    height: 48px;
    border: 0;
    border-radius: var(--radius-sm);
    background: var(--gradient-gold);
    color: var(--color-on-gold);
    cursor: pointer;
    box-shadow: var(--shadow);

    @include motion {
      transition: transform var(--duration) var(--ease);
    }

    @include hover {
      transform: rotate(180deg);
    }

    &:active {
      transform: scale(0.95);
    }
  }

  &--single &__fields {
    @include media(sm) {
      grid-template-columns: repeat(2, minmax(0, 1fr));

      > :first-child {
        grid-column: 1 / -1;
      }
    }

    @include media(lg) {
      grid-template-columns: minmax(0, 1.4fr) repeat(2, minmax(0, 1fr)) minmax(0, 0.8fr);

      > :first-child {
        grid-column: auto;
      }
    }
  }

  &--compact &__swap {
    margin-block: -4px;
  }
}
</style>
