<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import { clampTerm, MAX_TERM, MIN_TERM, RENTAL_TERMS } from '@/config/terms'

const props = withDefaults(
  defineProps<{
    id: string
    label: string
    /** Кнопки −/+ для произвольного срока (калькулятор на карточке авто). */
    stepper?: boolean
  }>(),
  { stepper: false },
)

/** Срок в сутках. */
const days = defineModel<number>({ required: true })
const { t } = useI18n()

function set(value: number) {
  days.value = clampTerm(value)
}
</script>

<template>
  <div class="field term">
    <span :id="`${props.id}-label`" class="field__label">{{ label }}</span>
    <div class="term__chips" role="radiogroup" :aria-labelledby="`${props.id}-label`">
      <button
        v-for="n in RENTAL_TERMS"
        :key="n"
        type="button"
        role="radio"
        class="term__chip"
        :class="{ 'is-active': days === n }"
        :aria-checked="days === n"
        @click="set(n)"
      >
        {{ t('filters.termDays', n) }}
      </button>
    </div>

    <div v-if="stepper" class="term__stepper">
      <button
        type="button"
        class="term__step"
        :aria-label="t('trip.fewer')"
        :disabled="days <= MIN_TERM"
        @click="set(days - 1)"
      >
        −
      </button>
      <label class="visually-hidden" :for="`${props.id}-input`">{{ t('trip.daysCount') }}</label>
      <input
        :id="`${props.id}-input`"
        class="input term__input"
        type="number"
        inputmode="numeric"
        :min="MIN_TERM"
        :max="MAX_TERM"
        :value="days"
        @change="set(Number(($event.target as HTMLInputElement).value))"
      />
      <button
        type="button"
        class="term__step"
        :aria-label="t('trip.more')"
        :disabled="days >= MAX_TERM"
        @click="set(days + 1)"
      >
        +
      </button>
      <span class="term__unit muted" aria-hidden="true">{{ t('trip.daysUnit', days) }}</span>
    </div>
  </div>
</template>

<style scoped lang="scss">
.term {
  container-type: inline-size;

  // Ровная сетка: в узкой колонке 3 + 2 одинаковых кнопки, когда хватает места — все 5 в ряд
  &__chips {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;

    @container (min-width: 480px) {
      grid-template-columns: repeat(5, minmax(0, 1fr));
    }
  }

  &__chip {
    min-width: 0;
    min-height: 44px;
    padding: 4px 6px;
    line-height: 1.2;
    border: 1px solid var(--color-border);
    border-radius: 999px;
    background: var(--color-surface-2);
    color: var(--color-text);
    font: inherit;
    // На самых узких телефонах чуть мельче, чтобы «30 дней» помещалось в ячейку
    font-size: clamp(0.85rem, 3.6vw, 0.95rem);
    cursor: pointer;

    @include motion {
      transition:
        border-color var(--duration-fast) var(--ease),
        background-color var(--duration-fast) var(--ease),
        color var(--duration-fast) var(--ease);
    }

    @include hover {
      border-color: var(--color-gold-dark);
    }

    &.is-active {
      border-color: var(--color-gold);
      background: var(--color-gold-alpha);
      color: var(--color-gold);
    }
  }

  &__stepper {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 10px;
  }

  &__step {
    display: grid;
    place-items: center;
    flex: none;
    width: 48px;
    height: 48px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-surface-2);
    color: var(--color-gold);
    font: inherit;
    font-size: 1.4rem;
    line-height: 1;
    cursor: pointer;

    @include hover {
      border-color: var(--color-gold-dark);
    }

    &:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
  }

  &__input {
    width: 72px;
    padding-inline: 8px;
    text-align: center;
    font-weight: 600;
    appearance: textfield;

    &::-webkit-inner-spin-button,
    &::-webkit-outer-spin-button {
      appearance: none;
      margin: 0;
    }
  }

  &__unit {
    min-width: 0;
  }
}
</style>
