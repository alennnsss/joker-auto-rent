<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import { whatsappLink } from '@/config/contacts'

const { t } = useI18n()

// Ключи разделов rules.* в словаре: у каждого заголовок и пункты i1…iN
const SECTIONS = [
  { key: 'driver', items: 2 },
  { key: 'payment', items: 2 },
  { key: 'pickup', items: 3 },
  { key: 'booking', items: 2 },
] as const
</script>

<template>
  <div class="page container rules">
    <h1 class="page-title">{{ t('rules.title') }}</h1>
    <p class="page-subtitle">{{ t('rules.subtitle') }}</p>

    <div class="rules__grid">
      <section v-for="s in SECTIONS" :key="s.key" class="card">
        <h2 class="rules__h">{{ t(`rules.${s.key}.title`) }}</h2>
        <ul class="list">
          <li v-for="n in s.items" :key="n">{{ t(`rules.${s.key}.i${n}`) }}</li>
        </ul>
      </section>
    </div>

    <p class="muted rules__note">{{ t('rules.note') }}</p>

    <div class="rules__cta">
      <RouterLink :to="{ name: 'cars' }" class="btn btn--gold">{{ t('common.chooseCar') }}</RouterLink>
      <a :href="whatsappLink" class="btn btn--outline" target="_blank" rel="noopener">
        {{ t('rules.ask') }}
      </a>
    </div>
  </div>
</template>

<style scoped lang="scss">
.rules {
  &__grid {
    display: grid;
    gap: 20px;

    @include media(md) {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  &__h {
    font-size: 1.3rem;
  }

  &__note {
    margin-top: 24px;
  }

  &__cta {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 16px;
  }
}
</style>
