<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import LangSwitch from '@/components/LangSwitch.vue'
import { contacts } from '@/config/contacts'
import { useAuthStore } from '@/stores/auth'
import { formatPhoneHref } from '@/utils/format'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const menuOpen = ref(false)

const links = [
  { to: { name: 'cars' }, label: 'common.fleet' },
  { to: { name: 'about' }, label: 'header.about' },
  { to: { name: 'contacts' }, label: 'header.contacts' },
] as const

watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false
  },
)

function logout() {
  auth.logout()
  router.push({ name: 'home' })
}
</script>

<template>
  <header class="header">
    <div class="header__inner container">
      <RouterLink :to="{ name: 'home' }" class="logo" :aria-label="t('header.logo')">
        <span class="logo__mark text-gold">JOKER</span>
        <span class="logo__sub">Auto Rent</span>
      </RouterLink>

      <nav class="nav" :aria-label="t('header.mainNav')">
        <RouterLink v-for="link in links" :key="link.label" :to="link.to" class="nav__link">
          {{ t(link.label) }}
        </RouterLink>
      </nav>

      <div class="header__actions">
        <a :href="formatPhoneHref(contacts.phone)" class="header__phone">{{ contacts.phone }}</a>
        <template v-if="auth.isAuthenticated">
          <RouterLink v-if="auth.isAdmin" :to="{ name: 'admin' }" class="btn btn--ghost btn--sm">
            {{ t('header.admin') }}
          </RouterLink>
          <RouterLink :to="{ name: 'account-bookings' }" class="btn btn--outline btn--sm">
            {{ t('header.account') }}
          </RouterLink>
        </template>
        <RouterLink v-else :to="{ name: 'login' }" class="btn btn--outline btn--sm">
          {{ t('common.login') }}
        </RouterLink>
      </div>

      <LangSwitch class="header__lang" />

      <button
        type="button"
        class="burger"
        :aria-expanded="menuOpen"
        aria-controls="mobile-menu"
        :aria-label="menuOpen ? t('header.closeMenu') : t('header.openMenu')"
        @click="menuOpen = !menuOpen"
      >
        <span class="burger__line" :class="{ 'is-open': menuOpen }" />
      </button>
    </div>

    <Transition name="menu">
      <div v-if="menuOpen" id="mobile-menu" class="mobile-menu">
        <nav class="mobile-menu__nav container" :aria-label="t('header.mobileNav')">
          <RouterLink v-for="link in links" :key="link.label" :to="link.to" class="mobile-menu__link">
            {{ t(link.label) }}
          </RouterLink>
          <template v-if="auth.isAuthenticated">
            <RouterLink :to="{ name: 'account-bookings' }" class="mobile-menu__link">
              {{ t('common.myBookings') }}
            </RouterLink>
            <RouterLink :to="{ name: 'account' }" class="mobile-menu__link">
              {{ t('common.profile') }}
            </RouterLink>
            <RouterLink v-if="auth.isAdmin" :to="{ name: 'admin' }" class="mobile-menu__link">
              {{ t('header.adminPanel') }}
            </RouterLink>
            <button type="button" class="mobile-menu__link mobile-menu__logout" @click="logout">
              {{ t('common.logout') }}
            </button>
          </template>
          <template v-else>
            <RouterLink :to="{ name: 'login' }" class="btn btn--outline btn--block">
              {{ t('common.login') }}
            </RouterLink>
            <RouterLink :to="{ name: 'register' }" class="btn btn--gold btn--block">
              {{ t('common.register') }}
            </RouterLink>
          </template>
        </nav>
      </div>
    </Transition>
  </header>
</template>

<style scoped lang="scss">
.header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--color-overlay);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);

  &__inner {
    display: flex;
    align-items: center;
    gap: 24px;
    height: var(--header-height);
  }

  &__actions {
    display: none;
    align-items: center;
    gap: 12px;
    margin-left: auto;

    @include media(lg) {
      display: flex;
    }
  }

  // На мобильном переключатель языка прижат вправо к бургеру, на десктопе — после кнопок
  &__lang {
    margin-left: auto;

    @include media(lg) {
      margin-left: 0;
    }
  }

  &__phone {
    color: var(--color-text);
    font-weight: 500;
    white-space: nowrap;
    padding: 10px 8px;

    @include hover {
      color: var(--color-gold);
    }
  }
}

.logo {
  display: flex;
  align-items: baseline;
  gap: 8px;
  min-height: 44px;
  align-items: center;

  &__mark {
    font-family: var(--font-display);
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 0.08em;
  }

  &__sub {
    color: var(--color-text-muted);
    font-size: 0.8rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
  }
}

.nav {
  display: none;
  gap: 4px;

  @include media(lg) {
    display: flex;
  }

  &__link {
    padding: 10px 14px;
    border-radius: 999px;
    color: var(--color-text-muted);

    @include motion {
      transition: color var(--duration-fast) var(--ease);
    }

    @include hover {
      color: var(--color-text);
    }

    &.router-link-active {
      color: var(--color-gold);
    }
  }
}

.burger {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  margin-left: -12px; // gap шапки 24px слишком велик между языком и бургером
  border: 0;
  background: transparent;
  cursor: pointer;

  @include media(lg) {
    display: none;
  }

  &__line,
  &__line::before,
  &__line::after {
    display: block;
    width: 22px;
    height: 2px;
    background: var(--color-text);
    border-radius: 2px;
    position: relative;

    @include motion {
      transition: transform var(--duration) var(--ease), background-color var(--duration-fast);
    }
  }

  &__line::before,
  &__line::after {
    content: '';
    position: absolute;
    left: 0;
  }

  &__line::before {
    top: -7px;
  }

  &__line::after {
    top: 7px;
  }

  &__line.is-open {
    background: transparent;

    &::before {
      transform: translateY(7px) rotate(45deg);
    }

    &::after {
      transform: translateY(-7px) rotate(-45deg);
    }
  }
}

.mobile-menu {
  position: absolute;
  inset: var(--header-height) 0 auto;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow);

  @include media(lg) {
    display: none;
  }

  &__nav {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-block: 16px 24px;
  }

  &__link {
    display: flex;
    align-items: center;
    min-height: 48px;
    padding: 0 4px;
    color: var(--color-text);
    font-size: 1.1rem;
    border-bottom: 1px solid var(--color-border);

    &.router-link-active {
      color: var(--color-gold);
    }
  }

  &__logout {
    background: none;
    border: 0;
    border-bottom: 1px solid var(--color-border);
    font: inherit;
    font-size: 1.1rem;
    color: var(--color-danger);
    text-align: left;
    cursor: pointer;
    margin-bottom: 8px;
  }
}

.menu-enter-active,
.menu-leave-active {
  @include motion {
    transition:
      opacity var(--duration) var(--ease),
      transform var(--duration) var(--ease);
  }
}

.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
