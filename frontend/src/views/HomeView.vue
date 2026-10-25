<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import { carsApi } from '@/api/cars'
import type { Car } from '@/api/types'
import CarCard from '@/components/CarCard.vue'
import { imageSources } from '@/utils/images'

const { t } = useI18n()

// 12 делится на 1, 2, 3 и 4 колонки — в сетке не остаётся «висящих» карточек
const FEATURED_LIMIT = 12

const cars = ref<Car[]>([])
const loading = ref(true)
const failed = ref(false)

const hero = imageSources(
  'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&q=80',
  1600,
)

onMounted(async () => {
  try {
    cars.value = (await carsApi.list({ limit: FEATURED_LIMIT, sort: 'price_desc' })).items
  } catch {
    failed.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="hero">
    <img
      class="hero__bg"
      :src="hero.src"
      :srcset="hero.srcset"
      sizes="100vw"
      alt=""
      fetchpriority="high"
      decoding="async"
    />
    <div class="hero__content container">
      <i18n-t keypath="home.heroTitle" tag="h1" class="hero__title" scope="global">
        <template #accent>
          <span class="text-gold">{{ t('home.heroAccent') }}</span>
        </template>
      </i18n-t>
      <p class="hero__lead">{{ t('home.heroLead') }}</p>
      <div class="hero__actions">
        <a href="#fleet" class="btn btn--gold">{{ t('common.chooseCar') }}</a>
        <RouterLink :to="{ name: 'cars' }" class="btn btn--outline">
          {{ t('home.allFleet') }}
        </RouterLink>
      </div>
    </div>
  </section>

  <section id="fleet" class="fleet container" aria-labelledby="fleet-title">
    <div class="fleet__head">
      <i18n-t id="fleet-title" keypath="home.featuredTitle" tag="h2" scope="global">
        <template #accent>
          <span class="text-gold">{{ t('home.featuredAccent') }}</span>
        </template>
      </i18n-t>
    </div>

    <div v-if="failed" class="alert alert--error" role="alert">{{ t('errors.loadCars') }}</div>

    <div class="cars-grid">
      <template v-if="loading">
        <div v-for="n in 6" :key="n" class="skeleton cars-grid__skeleton" />
      </template>
      <CarCard v-for="car in cars" :key="car.id" :car="car" />
    </div>

    <div v-if="cars.length" class="fleet__more">
      <RouterLink :to="{ name: 'cars' }" class="btn btn--outline">
        {{ t('home.allFleet') }}
      </RouterLink>
    </div>
  </section>
</template>

<style scoped lang="scss">
.hero {
  position: relative;
  display: flex;
  align-items: center;
  min-height: min(640px, calc(100dvh - var(--header-height)));
  padding-block: 56px;
  overflow: hidden;
  isolation: isolate;

  @include media(md) {
    padding-block: 80px;
  }

  &::after {
    content: '';
    position: absolute;
    inset: 0;
    z-index: -1;
    background: var(--gradient-hero-side), var(--gradient-hero);
  }

  &__bg {
    position: absolute;
    inset: 0;
    z-index: -2;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: 65% center;
  }

  &__title {
    max-width: 15ch;
  }

  &__lead {
    max-width: 52ch;
    color: var(--color-text-muted);
    font-size: 1.05rem;
    margin-bottom: 28px;
  }

  &__actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;

    // На узких телефонах кнопки во всю ширину — без «лесенки» разной длины
    .btn {
      flex: 1 1 220px;

      @include media(sm) {
        flex: 0 0 auto;
      }
    }
  }
}

.fleet {
  padding-block: 32px 64px;
  scroll-margin-top: var(--header-height);

  @include media(lg) {
    padding-block: 40px 96px;
  }

  &__head {
    margin-bottom: 24px;

    h2 {
      margin: 0;
    }
  }

  &__more {
    display: flex;
    justify-content: center;
    margin-top: 32px;
  }
}

.cars-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: minmax(0, 1fr);

  @include media(md) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  @include media(lg) {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  @include media(xxl) {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  &__skeleton {
    aspect-ratio: 4 / 5;
  }
}
</style>
