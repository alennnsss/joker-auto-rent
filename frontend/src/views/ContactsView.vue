<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { contacts, whatsappLink } from '@/config/contacts'

const { t } = useI18n()
const { lat, lon, zoom } = contacts.map
const mapSrc = `https://yandex.kz/map-widget/v1/?ll=${lon}%2C${lat}&z=${zoom}&pt=${lon}%2C${lat}%2Cpm2ylm`

const cards = computed(() => [
  {
    title: 'WhatsApp',
    value: contacts.phone,
    action: t('contactsPage.write'),
    href: whatsappLink,
    external: true,
    icon: 'M21 11.5a8.4 8.4 0 0 1-12.4 7.4L3 21l2.1-5.5A8.5 8.5 0 1 1 21 11.5z',
  },
  {
    title: t('contactsPage.address'),
    value: t('contacts.address'),
    action: t('contactsPage.open2gis'),
    href: contacts.twoGis,
    external: true,
    icon: 'M12 22s7-6.3 7-12a7 7 0 1 0-14 0c0 5.7 7 12 7 12zm0-9a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
  },
  {
    title: t('contactsPage.hours'),
    value: t('contacts.workingHours'),
    action: null,
    href: null,
    external: false,
    icon: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 6v6l4 2',
  },
  {
    title: 'Instagram',
    value: '@joker_autorent',
    action: t('contactsPage.go'),
    href: contacts.instagram,
    external: true,
    icon: 'M17 2H7a5 5 0 0 0-5 5v10a5 5 0 0 0 5 5h10a5 5 0 0 0 5-5V7a5 5 0 0 0-5-5zm-1 9.4A4 4 0 1 1 12.6 8a4 4 0 0 1 3.4 3.4zM17.5 6.5h.01',
  },
])
</script>

<template>
  <div class="page container">
    <h1 class="page-title">{{ t('contactsPage.title') }}</h1>
    <p class="page-subtitle">{{ t('contactsPage.subtitle') }}</p>

    <ul class="cards">
      <li v-for="c in cards" :key="c.icon" class="contact-card">
        <span class="contact-card__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path
              :d="c.icon"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span class="contact-card__title muted">{{ c.title }}</span>
        <span class="contact-card__value">{{ c.value }}</span>
        <a
          v-if="c.href"
          :href="c.href"
          class="contact-card__action"
          :target="c.external ? '_blank' : undefined"
          :rel="c.external ? 'noopener' : undefined"
        >
          {{ c.action }} →
        </a>
      </li>
    </ul>

    <div class="map">
      <iframe
        :src="mapSrc"
        :title="t('contactsPage.mapTitle')"
        loading="lazy"
        referrerpolicy="no-referrer-when-downgrade"
        allowfullscreen
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.cards {
  display: grid;
  gap: 48px;
  padding: 0;
  margin: 0 0 24px;
  list-style: none;
  padding: 30px 0;
  @include media(sm) {
    grid-template-columns: 1fr 1fr;
  }

  @include media(lg) {
    grid-template-columns: repeat(3, 1fr);
  }

  @include media(xl) {
    grid-template-columns: repeat(5, 1fr);
  }
}

.contact-card {
  @include card;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px;

  &__icon {
    display: grid;
    place-items: center;
    width: 48px;
    height: 48px;
    margin-bottom: 8px;
    border-radius: var(--radius-sm);
    background: var(--color-gold-alpha);
    color: var(--color-gold);
  }

  &__title {
    font-size: 0.85rem;
  }

  &__value {
    flex: 1;
    font-weight: 600;
    overflow-wrap: anywhere;
  }

  &__action {
    display: inline-flex;
    align-items: center;
    min-height: 44px;
    font-weight: 600;
    width: fit-content;
  }
}

.map {
  min-height: 360px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--color-border);
  background: var(--color-surface);

  @include media(lg) {
    min-height: 480px;
  }

  iframe {
    display: block;
    width: 100%;
    height: 100%;
    min-height: inherit;
    border: 0;
  }
}
</style>
