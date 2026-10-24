<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink, RouterView, useRouter } from 'vue-router'

import EmailVerifyNotice from '@/components/EmailVerifyNotice.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const { t } = useI18n()

const sections = [
  {
    name: 'account-bookings',
    title: 'common.myBookings',
    text: 'account.bookingsText',
    icon: 'M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z',
  },
  {
    name: 'account',
    title: 'common.profile',
    text: 'account.profileText',
    icon: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
  },
] as const

function logout() {
  auth.logout()
  router.push({ name: 'home' })
}
</script>

<template>
  <div class="account page container">
    <h1 class="page-title">{{ t('account.title') }}</h1>

    <EmailVerifyNotice />

    <nav class="sections" :aria-label="t('account.sectionsLabel')">
      <RouterLink
        v-for="s in sections"
        :key="s.name"
        :to="{ name: s.name }"
        class="section-card"
        exact-active-class="is-active"
      >
        <span class="section-card__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path
              :d="s.icon"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span class="section-card__body">
          <span class="section-card__title">{{ t(s.title) }}</span>
          <span class="section-card__text muted">{{ t(s.text) }}</span>
        </span>
      </RouterLink>
      <button type="button" class="section-card section-card--logout" @click="logout">
        <span class="section-card__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path
              d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span class="section-card__body">
          <span class="section-card__title">{{ t('common.logout') }}</span>
          <span class="section-card__text muted">{{ t('account.logoutText') }}</span>
        </span>
      </button>
    </nav>

    <RouterView />
  </div>
</template>

<style scoped lang="scss">
.sections {
  display: grid;
  gap: 12px;
  margin-bottom: 32px;

  @include media(sm) {
    grid-template-columns: 1fr 1fr;
  }

  @include media(lg) {
    grid-template-columns: 1fr 1fr 1fr;
  }
}

.section-card {
  @include card;
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 88px;
  padding: 16px 20px;
  color: var(--color-text);
  font: inherit;
  text-align: left;
  cursor: pointer;

  @include motion {
    transition:
      border-color var(--duration-fast) var(--ease),
      background-color var(--duration-fast) var(--ease);
  }

  @include hover {
    border-color: var(--color-gold-dark);
  }

  &.is-active {
    border-color: var(--color-gold);
    background: var(--color-gold-alpha);
  }

  &__icon {
    display: grid;
    place-items: center;
    flex: 0 0 48px;
    height: 48px;
    border-radius: var(--radius-sm);
    background: var(--color-surface-2);
    color: var(--color-gold);
  }

  &__body {
    display: flex;
    flex-direction: column;
  }

  &__title {
    font-weight: 700;
  }

  &__text {
    font-size: 0.85rem;
  }

  &--logout {
    @include hover {
      border-color: var(--color-danger);
    }

    .section-card__icon {
      color: var(--color-danger);
    }
  }
}
</style>
