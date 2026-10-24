<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

withDefaults(
  defineProps<{
    id: string
    autocomplete: 'current-password' | 'new-password'
    minlength?: number
  }>(),
  { minlength: undefined },
)

const model = defineModel<string>({ required: true })
const visible = ref(false)
const { t } = useI18n()
</script>

<template>
  <div class="password">
    <input
      :id="id"
      v-model="model"
      class="input password__input"
      :type="visible ? 'text' : 'password'"
      :autocomplete="autocomplete"
      :minlength="minlength"
      autocapitalize="off"
      spellcheck="false"
      required
    />
    <button
      type="button"
      class="password__toggle"
      :aria-label="visible ? t('password.hide') : t('password.show')"
      :aria-pressed="visible"
      :aria-controls="id"
      @click="visible = !visible"
    >
      <svg v-if="visible" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
        <path
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          d="M3 3l18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 5.1A10.4 10.4 0 0 1 12 5c5 0 9 4.5 10 7a12.8 12.8 0 0 1-3.2 4.2M6.6 6.6C4.3 8 2.7 10.2 2 12c1 2.5 5 7 10 7a10 10 0 0 0 5.4-1.6"
        />
      </svg>
      <svg v-else viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
        <path
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          d="M2 12c1-2.5 5-7 10-7s9 4.5 10 7c-1 2.5-5 7-10 7S3 14.5 2 12z"
        />
        <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="2" />
      </svg>
    </button>
  </div>
</template>

<style scoped lang="scss">
.password {
  position: relative;

  &__input {
    padding-right: 52px;
  }

  &__toggle {
    position: absolute;
    top: 50%;
    right: 2px;
    translate: 0 -50%;
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    border: 0;
    border-radius: var(--radius-sm);
    background: transparent;
    color: var(--color-text-muted);
    cursor: pointer;

    @include hover {
      color: var(--color-gold);
    }

    &[aria-pressed='true'] {
      color: var(--color-gold);
    }
  }
}
</style>
