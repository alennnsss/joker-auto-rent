<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink, RouterView, useRouter } from 'vue-router'

import LangSwitch from '@/components/LangSwitch.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const { t } = useI18n()

const links = [
  { name: 'admin-bookings', label: 'admin.bookings' },
  { name: 'admin-cars', label: 'admin.cars' },
  { name: 'admin-users', label: 'admin.users' },
  { name: 'admin-payments', label: 'admin.payments' },
] as const

function logout() {
  auth.logout()
  router.push({ name: 'home' })
}
</script>

<template>
  <div class="admin">
    <aside class="admin__side">
      <RouterLink :to="{ name: 'home' }" class="admin__logo">
        <span class="text-gold">JOKER</span>
        <small class="muted">{{ t('admin.panel') }}</small>
      </RouterLink>
      <nav class="admin__nav" :aria-label="t('header.adminPanel')">
        <RouterLink v-for="link in links" :key="link.name" :to="{ name: link.name }">
          {{ t(link.label) }}
        </RouterLink>
      </nav>
      <div class="admin__footer">
        <LangSwitch />
        <span class="muted admin__user">{{ auth.user?.email }}</span>
        <RouterLink :to="{ name: 'home' }" class="btn btn--ghost btn--sm">{{ t('admin.toSite') }}</RouterLink>
        <button type="button" class="btn btn--ghost btn--sm" @click="logout">{{ t('common.logout') }}</button>
      </div>
    </aside>
    <main class="admin__main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped lang="scss">
.admin {
  min-height: 100dvh;

  @include media(lg) {
    display: grid;
    grid-template-columns: 240px 1fr;
  }

  &__side {
    position: sticky;
    top: 0;
    z-index: 10;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px 16px;
    background: var(--color-surface);
    border-bottom: 1px solid var(--color-border);

    @include media(lg) {
      height: 100dvh;
      padding: 24px 16px;
      border-bottom: 0;
      border-right: 1px solid var(--color-border);
    }
  }

  &__logo {
    display: flex;
    flex-direction: column;
    font-family: var(--font-display);
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: 0.08em;

    small {
      font-family: var(--font-body);
      font-size: 0.75rem;
      letter-spacing: 0.1em;
      font-weight: 400;
    }

    @include media(lg) {
      margin-bottom: 24px;
    }
  }

  &__nav {
    display: flex;
    gap: 4px;
    overflow-x: auto;

    @include media(lg) {
      flex-direction: column;
    }

    a {
      display: flex;
      align-items: center;
      min-height: 44px;
      padding: 0 14px;
      border-radius: var(--radius-sm);
      color: var(--color-text-muted);
      white-space: nowrap;

      @include hover {
        background: var(--color-surface-2);
        color: var(--color-text);
      }

      &.router-link-active {
        background: var(--color-gold-alpha);
        color: var(--color-gold);
      }
    }
  }

  &__footer {
    display: none;

    @include media(lg) {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-top: auto;
    }
  }

  &__user {
    font-size: 0.8rem;
    overflow-wrap: anywhere;
    margin-bottom: 8px;
  }

  &__main {
    padding: 24px 16px 64px;
    min-width: 0;

    @include media(md) {
      padding: 32px;
    }
  }
}
</style>
