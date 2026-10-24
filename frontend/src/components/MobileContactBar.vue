<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import { contacts, whatsappLink } from '@/config/contacts'
import { formatPhoneHref } from '@/utils/format'

const { t } = useI18n()
</script>

<template>
  <div class="contact-bar" role="region" :aria-label="t('contactBar.label')">
    <a :href="formatPhoneHref(contacts.phone)" class="btn btn--outline">
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <path
          fill="currentColor"
          d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"
        />
      </svg>
      {{ t('contactBar.call') }}
    </a>
    <a :href="whatsappLink" class="btn btn--gold" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
        <path
          fill="currentColor"
          d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.4-.7-2.8-1.1-4.6-4-4.8-4.2-.1-.2-1.1-1.5-1.1-2.8s.7-2 1-2.3c.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.9 2.1c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.2-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.3 2.4 1.5.3.1.5.1.6-.1l.9-1c.2-.3.4-.2.6-.1l2 .9c.3.1.5.2.5.3.1.2.1.7-.1 1.3z"
        />
      </svg>
      WhatsApp
    </a>
  </div>
</template>

<style scoped lang="scss">
.contact-bar {
  position: fixed;
  inset: auto 0 0;
  z-index: 40;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 8px 16px calc(8px + var(--safe-bottom));
  background: var(--color-overlay);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--color-border);

  @include media(lg) {
    display: none;
  }

  .btn {
    min-height: 48px;
  }
}
</style>
