<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRouter } from 'vue-router'

import { carsApi } from '@/api/cars'
import type { Car } from '@/api/types'
import BenefitCards from '@/components/BenefitCards.vue'
import CarCard from '@/components/CarCard.vue'
import ReviewsSection from '@/components/ReviewsSection.vue'
import TripPanel from '@/components/TripPanel.vue'
import { useBookingStore } from '@/stores/booking'
import { imageSources } from '@/utils/images'

const router = useRouter()
const { t } = useI18n()
const { trip } = storeToRefs(useBookingStore())

const featured = ref<Car[]>([])
const featuredLoading = ref(true)
const canSearch = computed(
  () => Boolean(trip.value.pickupDate && trip.value.returnDate > trip.value.pickupDate),
)

const hero = imageSources(
  'https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&q=80',
  1600,
)

const steps = [
  { title: 'home.step1Title', text: 'home.step1Text' },
  { title: 'home.step2Title', text: 'home.step2Text' },
  { title: 'home.step3Title', text: 'home.step3Text' },
] as const

onMounted(async () => {
  try {
    featured.value = (await carsApi.list({ limit: 6, sort: 'price_desc' })).items
  } catch {
    featured.value = []
  } finally {
    featuredLoading.value = false
  }
})

function onSearch() {
  if (!canSearch.value) return
  router.push({
    name: 'cars',
    query: { start_date: trip.value.pickupDate, end_date: trip.value.returnDate },
  })
}
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
        <RouterLink :to="{ name: 'cars' }" class="btn btn--gold">{{ t('common.chooseCar') }}</RouterLink>
        <a href="#search" class="btn btn--outline">{{ t('home.pickDates') }}</a>
      </div>
    </div>
  </section>

  <section id="search" class="search container" aria-labelledby="search-title">
    <h2 id="search-title" class="visually-hidden">{{ t('home.searchTitle') }}</h2>
    <form class="search__form" @submit.prevent="onSearch">
      <TripPanel v-model="trip" id-prefix="home" />
      <button type="submit" class="btn btn--gold search__submit" :disabled="!canSearch">
        {{ t('home.search') }}
      </button>
    </form>
  </section>

  <section class="section container" aria-labelledby="benefits-title">
    <i18n-t id="benefits-title" keypath="home.benefitsTitle" tag="h2" scope="global">
      <template #accent><span class="text-gold">Joker</span></template>
    </i18n-t>
    <p class="muted section__lead">{{ t('home.benefitsLead') }}</p>
    <BenefitCards />
  </section>

  <section class="section container" aria-labelledby="featured-title">
    <div class="section__head">
      <i18n-t id="featured-title" keypath="home.featuredTitle" tag="h2" scope="global">
        <template #accent>
          <span class="text-gold">{{ t('home.featuredAccent') }}</span>
        </template>
      </i18n-t>
      <RouterLink :to="{ name: 'cars' }" class="btn btn--outline btn--sm">
        {{ t('home.allFleet') }}
      </RouterLink>
    </div>
    <div class="cars-grid">
      <template v-if="featuredLoading">
        <div v-for="n in 6" :key="n" class="skeleton cars-grid__skeleton" />
      </template>
      <CarCard v-for="car in featured" :key="car.id" :car="car" />
    </div>
  </section>

  <section class="section container" aria-labelledby="steps-title">
    <h2 id="steps-title">{{ t('home.stepsTitle') }}</h2>
    <ol class="steps">
      <li v-for="(s, i) in steps" :key="s.title" class="step card">
        <span class="step__num">{{ i + 1 }}</span>
        <h3>{{ t(s.title) }}</h3>
        <p class="muted">{{ t(s.text) }}</p>
      </li>
    </ol>
  </section>

  <div class="section container">
    <ReviewsSection />
  </div>

  <section class="section container">
    <div class="cta card">
      <h2>{{ t('home.ctaTitle') }}</h2>
      <p class="muted">{{ t('home.ctaText') }}</p>
      <RouterLink :to="{ name: 'cars' }" class="btn btn--gold">{{ t('common.chooseCar') }}</RouterLink>
    </div>
  </section>
</template>

<style scoped lang="scss">
.hero {
  position: relative;
  display: flex;
  align-items: center;
  min-height: min(720px, calc(100dvh - var(--header-height)));
  padding-block: 64px 120px;
  overflow: hidden;
  isolation: isolate;

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
  }
}

// Панель «Получение / Возврат» наезжает на hero, как в макете
.search {
  position: relative;
  z-index: 1;
  margin-top: -80px;
  scroll-margin-top: calc(var(--header-height) + 16px);

  &__form {
    display: grid;
    gap: 16px;
    padding: 16px;
    background: var(--color-overlay);
    backdrop-filter: blur(12px);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);

    @include media(md) {
      padding: 20px;
    }
  }

  &__submit {
    justify-self: stretch;

    @include media(md) {
      justify-self: end;
      min-width: 280px;
    }
  }
}

.section {
  padding-block: 56px;

  @include media(lg) {
    padding-block: 80px;
  }

  &__lead {
    margin-top: -8px;
    margin-bottom: 24px;
  }

  &__head {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 24px;

    h2 {
      margin: 0;
    }
  }
}

.cars-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: 1fr;

  @include media(md) {
    grid-template-columns: repeat(2, 1fr);
  }

  // 6 авто: 2×3 на планшете, 3×2 на десктопе
  @include media(lg) {
    grid-template-columns: repeat(3, 1fr);
  }

  &__skeleton {
    aspect-ratio: 4 / 5;
  }
}

.steps {
  display: grid;
  gap: 16px;
  padding: 0;
  margin: 24px 0 0;
  list-style: none;

  @include media(md) {
    grid-template-columns: repeat(3, 1fr);
  }
}

.step__num {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  margin-bottom: 16px;
  border-radius: 50%;
  background: var(--gradient-gold);
  color: var(--color-on-gold);
  font-weight: 700;
}

.cta {
  text-align: center;
  padding-block: 48px;
  background:
    radial-gradient(circle at 50% 0%, var(--color-gold-alpha), transparent 70%),
    var(--color-surface);

  p {
    max-width: 48ch;
    margin-inline: auto;
    margin-bottom: 24px;
  }
}
</style>
