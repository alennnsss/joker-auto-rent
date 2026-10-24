<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

const { t } = useI18n()
</script>

<template>
  <div class="page container not-found">
    <p class="not-found__code text-gold">404</p>
    <h1>{{ t('notFound.title') }}</h1>
    <p class="muted">{{ t('notFound.text') }}</p>
    <div class="not-found__actions">
      <RouterLink :to="{ name: 'home' }" class="btn btn--gold">{{ t('notFound.home') }}</RouterLink>
      <RouterLink :to="{ name: 'cars' }" class="btn btn--outline">{{ t('common.fleet') }}</RouterLink>
    </div>
  </div>
</template>

<style scoped lang="scss">
.not-found {
  text-align: center;

  &__code {
    font-family: var(--font-display);
    font-size: clamp(5rem, 20vw, 9rem);
    font-weight: 700;
    line-height: 1;
    margin: 0;
  }

  &__actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 12px;
    margin-top: 24px;
  }
}
</style>
