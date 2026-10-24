<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import { LOCALE_LABELS, LOCALES, setLocale } from '@/i18n'

const { locale, t } = useI18n()
</script>

<template>
  <div class="lang" role="group" :aria-label="t('lang.label')">
    <button
      v-for="l in LOCALES"
      :key="l"
      type="button"
      class="lang__btn"
      :class="{ 'is-active': locale === l }"
      :aria-pressed="locale === l"
      :lang="l"
      @click="setLocale(l)"
    >
      {{ LOCALE_LABELS[l] }}
    </button>
  </div>
</template>

<style scoped lang="scss">
.lang {
  display: inline-flex;
  flex-shrink: 0;
  border: 1px solid var(--color-border);
  border-radius: 999px;
}

.lang__btn {
  min-width: 44px;
  min-height: 42px;
  padding: 0 10px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--color-text-muted);
  font: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;

  @include motion {
    transition:
      color var(--duration-fast) var(--ease),
      background-color var(--duration-fast) var(--ease);
  }

  @include hover {
    color: var(--color-text);
  }

  &.is-active {
    background: var(--color-gold-alpha);
    color: var(--color-gold);
  }
}
</style>
