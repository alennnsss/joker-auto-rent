<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterView } from 'vue-router'

import AppFooter from '@/components/AppFooter.vue'
import AppHeader from '@/components/AppHeader.vue'
import MobileContactBar from '@/components/MobileContactBar.vue'

const { t } = useI18n()
</script>

<template>
  <div class="layout">
    <a href="#main" class="skip-link">{{ t('header.skip') }}</a>
    <AppHeader />
    <main id="main" class="layout__main">
      <RouterView />
    </main>
    <AppFooter />
    <MobileContactBar />
  </div>
</template>

<style scoped lang="scss">
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  // место под фиксированную панель «Позвонить / WhatsApp»
  padding-bottom: calc(var(--mobile-bar-height) + var(--safe-bottom));

  @include media(lg) {
    padding-bottom: 0;
  }

  &__main {
    flex: 1;
  }
}

.skip-link {
  @include visually-hidden;

  &:focus {
    position: fixed;
    top: 8px;
    left: 8px;
    z-index: 100;
    width: auto;
    height: auto;
    padding: 12px 16px;
    clip-path: none;
    background: var(--color-gold);
    color: var(--color-on-gold);
    border-radius: var(--radius-sm);
  }
}
</style>
