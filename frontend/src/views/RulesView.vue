<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import { whatsappLink } from '@/config/contacts'

const { t } = useI18n()

// Ключи разделов rules.* в словаре: у каждого заголовок и пункты i1…iN.
// icon — path для svg 24×24 (обводка, без заливки)
const SECTIONS = [
  {
    key: 'driver',
    items: 4,
    icon: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
  },
  {
    key: 'car',
    items: 4,
    icon: 'M5 17H3v-5l2.5-5h13L21 12v5h-2M3 12h18M9 17h6M5 17a2 2 0 1 0 4 0 2 2 0 1 0-4 0zM15 17a2 2 0 1 0 4 0 2 2 0 1 0-4 0z',
  },
  {
    key: 'territory',
    items: 2,
    icon: 'M12 22s7-6.3 7-12a7 7 0 1 0-14 0c0 5.7 7 12 7 12zm0-9a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
  },
  {
    key: 'payment',
    items: 2,
    icon: 'M3 6h18v12H3zM12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM6 9v.01M18 15v.01',
  },
  {
    key: 'pickup',
    items: 2,
    icon: 'M7.5 21a5.5 5.5 0 1 0 0-11 5.5 5.5 0 0 0 0 11zM11.4 11.6 21 2M15.5 7.5l3 3M18 5l3 3',
  },
  {
    key: 'booking',
    items: 2,
    icon: 'M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zM9 16l2 2 4-4',
  },
] as const

const FORBIDDEN_ITEMS = 3

const ICON_FORBIDDEN = 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM4.9 4.9l14.2 14.2'
const ICON_CHECK = 'M20 6 9 17l-5-5'
const ICON_CROSS = 'M18 6 6 18M6 6l12 12'
const ICON_INFO = 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 16v-4M12 8h.01'
</script>

<template>
  <div class="page container rules">
    <h1 class="page-title">{{ t('rules.title') }}</h1>
    <p class="page-subtitle">{{ t('rules.subtitle') }}</p>

    <div class="rules__grid">
      <section v-for="s in SECTIONS" :key="s.key" class="rule-card">
        <header class="rule-card__head">
          <span class="rule-card__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path :d="s.icon" />
            </svg>
          </span>
          <h2 class="rule-card__title">{{ t(`rules.${s.key}.title`) }}</h2>
        </header>
        <ul class="rule-card__list">
          <li v-for="n in s.items" :key="n" class="rule-card__item">
            <span class="rule-card__mark" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="14" height="14">
                <path :d="ICON_CHECK" />
              </svg>
            </span>
            <span>{{ t(`rules.${s.key}.i${n}`) }}</span>
          </li>
        </ul>
      </section>

      <section class="rule-card rule-card--danger">
        <header class="rule-card__head">
          <span class="rule-card__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path :d="ICON_FORBIDDEN" />
            </svg>
          </span>
          <h2 class="rule-card__title">{{ t('rules.forbidden.title') }}</h2>
        </header>
        <ul class="rule-card__list rule-card__list--row">
          <li v-for="n in FORBIDDEN_ITEMS" :key="n" class="rule-card__item">
            <span class="rule-card__mark" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="14" height="14">
                <path :d="ICON_CROSS" />
              </svg>
            </span>
            <span>{{ t(`rules.forbidden.i${n}`) }}</span>
          </li>
        </ul>
      </section>
    </div>

    <p class="rules__note">
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <path :d="ICON_INFO" />
      </svg>
      <span>{{ t('rules.note') }}</span>
    </p>

    <div class="rules__cta">
      <RouterLink :to="{ name: 'cars' }" class="btn btn--gold">{{ t('common.chooseCar') }}</RouterLink>
      <a :href="whatsappLink" class="btn btn--outline" target="_blank" rel="noopener">
        {{ t('rules.ask') }}
      </a>
    </div>
  </div>
</template>

<style scoped lang="scss">
svg {
  flex-shrink: 0;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.rules {
  &__grid {
    display: grid;
    gap: 16px;

    @include media(md) {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 20px;
    }

    @include media(xl) {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
  }

  &__note {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin: 24px 0 0;
    padding: 14px 16px;
    border-left: 3px solid var(--color-gold);
    border-radius: var(--radius-sm);
    background: var(--color-surface);
    color: var(--color-text-muted);

    svg {
      margin-top: 1px;
      color: var(--color-gold);
    }
  }

  &__cta {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 20px;
  }
}

.rule-card {
  @include card;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  overflow: hidden;

  @include media(md) {
    padding: 24px;
  }

  @include motion {
    transition:
      border-color 200ms ease,
      transform 200ms ease;
  }

  // Тонкая золотая линия сверху — проявляется при наведении
  &::before {
    content: '';
    position: absolute;
    inset: 0 0 auto;
    height: 2px;
    background: var(--gradient-gold);
    opacity: 0;

    @include motion {
      transition: opacity 200ms ease;
    }
  }

  @include hover {
    border-color: var(--color-gold-dark);
    transform: translateY(-2px);

    &::before {
      opacity: 1;
    }
  }

  &__head {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  &__icon {
    display: grid;
    place-items: center;
    flex-shrink: 0;
    width: 48px;
    height: 48px;
    border-radius: var(--radius-sm);
    background: var(--color-gold-alpha);
    color: var(--color-gold);
  }

  &__title {
    margin: 0;
    font-size: 1.2rem;
  }

  &__list {
    display: grid;
    margin: 0;
    padding: 0;
    list-style: none;
  }

  &__item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-top: 1px solid var(--color-border);
    line-height: 1.45;
  }

  &__mark {
    display: grid;
    place-items: center;
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    margin-top: 1px;
    border-radius: 50%;
    background: var(--color-gold-alpha);
    color: var(--color-gold);

    svg {
      stroke-width: 2.6;
    }
  }

  // Запреты — на всю ширину сетки, в красных тонах
  &--danger {
    border-color: var(--color-danger);
    background: linear-gradient(var(--color-danger-alpha), var(--color-danger-alpha)), var(--color-surface);

    @include media(md) {
      grid-column: 1 / -1;
    }

    &::before {
      display: none;
    }

    @include hover {
      border-color: var(--color-danger);
      transform: none;
    }

    .rule-card__icon,
    .rule-card__mark {
      background: var(--color-danger-alpha);
      color: var(--color-danger);
    }

    .rule-card__title {
      color: var(--color-danger);
    }
  }

  // На широких экранах пункты запретов — в ряд
  &__list--row {
    @include media(md) {
      grid-template-columns: repeat(3, minmax(0, 1fr));
      column-gap: 24px;
    }
  }
}
</style>
