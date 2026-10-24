<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

const { t } = useI18n()

const facts = [
  { value: '24/7', label: 'about.fact1' },
  { value: '4,4 ★', label: 'about.fact2' },
  { value: '5', label: 'about.fact3' },
] as const
</script>

<template>
  <div class="page container about">
    <h1 class="page-title">{{ t('about.title') }}</h1>
    <p class="page-subtitle">{{ t('about.subtitle') }}</p>

    <div class="about__grid">
      <section class="card">
        <h2>{{ t('about.approachTitle') }}</h2>
        <p class="muted">{{ t('about.approach1') }}</p>
        <p class="muted">{{ t('about.approach2') }}</p>
      </section>

      <section class="card">
        <h2>{{ t('about.includedTitle') }}</h2>
        <ul class="list">
          <li>{{ t('about.included1') }}</li>
          <li>{{ t('about.included2') }}</li>
          <li>{{ t('about.included3') }}</li>
          <li>{{ t('about.included4') }}</li>
        </ul>
      </section>
    </div>

    <ul class="facts">
      <li v-for="f in facts" :key="f.label" class="facts__item">
        <span class="facts__value text-gold">{{ f.value }}</span>
        <span class="muted">{{ t(f.label) }}</span>
      </li>
    </ul>

    <div class="about__cta">
      <RouterLink :to="{ name: 'cars' }" class="btn btn--gold">{{ t('common.chooseCar') }}</RouterLink>
      <RouterLink :to="{ name: 'contacts' }" class="btn btn--outline">
        {{ t('about.contactUs') }}
      </RouterLink>
    </div>
  </div>
</template>

<style scoped lang="scss">
.about {
  &__grid {
    display: grid;
    gap: 20px;

    @include media(md) {
      grid-template-columns: 1fr 1fr;
    }
  }

  &__cta {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }
}

.list {
  padding-left: 20px;
  color: var(--color-text-muted);

  li {
    margin-bottom: 8px;
  }

  li::marker {
    color: var(--color-gold);
  }
}

.facts {
  display: grid;
  gap: 16px;
  padding: 0;
  margin: 48px 0;
  list-style: none;

  @include media(md) {
    grid-template-columns: repeat(3, 1fr);
  }

  &__item {
    display: flex;
    flex-direction: column;
    padding: 24px;
    border-left: 2px solid var(--color-gold-dark);
  }

  &__value {
    font-family: var(--font-display);
    font-size: 2.5rem;
    font-weight: 600;
    line-height: 1.1;
  }
}
</style>
