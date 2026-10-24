<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import { contacts, whatsappLink } from '@/config/contacts'
import { formatPhoneHref } from '@/utils/format'

const { t } = useI18n()
const year = new Date().getFullYear()
</script>

<template>
  <footer class="footer">
    <div class="footer__inner container">
      <div class="footer__brand">
        <span class="footer__logo text-gold">JOKER</span>
        <p class="muted">{{ t('footer.tagline') }}</p>
      </div>

      <nav class="footer__col" :aria-label="t('footer.sectionsLabel')">
        <h3 class="footer__title">{{ t('footer.sections') }}</h3>
        <RouterLink :to="{ name: 'cars' }">{{ t('common.fleet') }}</RouterLink>
        <RouterLink :to="{ name: 'about' }">{{ t('footer.aboutCompany') }}</RouterLink>
        <RouterLink :to="{ name: 'contacts' }">{{ t('footer.contacts') }}</RouterLink>
      </nav>

      <div class="footer__col">
        <h3 class="footer__title">{{ t('footer.contact') }}</h3>
        <a :href="formatPhoneHref(contacts.phone)">{{ contacts.phone }}</a>
        <a :href="whatsappLink" target="_blank" rel="noopener">WhatsApp</a>
        <a :href="contacts.twoGis" target="_blank" rel="noopener">{{ t('footer.twoGis') }}</a>
        <a :href="contacts.instagram" target="_blank" rel="noopener">Instagram</a>
      </div>

      <div class="footer__col">
        <h3 class="footer__title">{{ t('footer.hours') }}</h3>
        <span class="muted">{{ t('contacts.workingHours') }}</span>
        <span class="muted">{{ t('contacts.address') }}</span>
      </div>
    </div>
    <div class="footer__bottom container muted">{{ t('footer.copyright', { year }) }}</div>
  </footer>
</template>

<style scoped lang="scss">
.footer {
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  padding-top: 48px;

  &__inner {
    display: grid;
    gap: 32px;
    grid-template-columns: 1fr;

    @include media(md) {
      grid-template-columns: 1fr 1fr;
    }

    @include media(lg) {
      grid-template-columns: 2fr 1fr 1fr 1fr;
    }
  }

  &__logo {
    font-family: var(--font-display);
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
  }

  &__brand p {
    max-width: 320px;
    margin-top: 8px;
  }

  &__col {
    display: flex;
    flex-direction: column;
    gap: 4px;

    a {
      display: inline-flex;
      align-items: center;
      min-height: 44px;
      color: var(--color-text);
      width: fit-content;

      @include hover {
        color: var(--color-gold);
      }
    }
  }

  &__title {
    font-family: var(--font-body);
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--color-gold);
    margin-bottom: 8px;
  }

  &__bottom {
    margin-top: 40px;
    padding-block: 20px;
    border-top: 1px solid var(--color-border);
    font-size: 0.875rem;
  }
}
</style>
