<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'

import { contacts } from '@/config/contacts'

const { t } = useI18n()

// Иконки по ключу раздела benefits.* в словаре; тексты — на текущем языке
const ICONS = {
  prices:
    'M12 1v22M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6',
  delivery:
    'M12 22s7-6.3 7-12a7 7 0 1 0-14 0c0 5.7 7 12 7 12zm0-9a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
  fleet:
    'M5 17h-2v-5l2-5h14l2 5v5h-2M5 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0zm10 0a2 2 0 1 0 4 0 2 2 0 0 0-4 0zM9 17h6M3 12h18',
  support:
    'M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z',
} as const

const benefits = computed(() =>
  (Object.keys(ICONS) as (keyof typeof ICONS)[]).map((key) => ({
    key,
    icon: ICONS[key],
    title: t(`benefits.${key}.title`),
    short: t(`benefits.${key}.short`),
    details: [
      t(`benefits.${key}.d1`, { address: t('contacts.address') }),
      t(`benefits.${key}.d2`),
    ],
    points: [
      t(`benefits.${key}.p1`, { phone: contacts.phone }),
      t(`benefits.${key}.p2`),
      t(`benefits.${key}.p3`),
    ],
  })),
)

const activeIndex = ref<number | null>(null)
const active = computed(() => (activeIndex.value === null ? null : benefits.value[activeIndex.value]))
const visible = computed({
  get: () => activeIndex.value !== null,
  set: (value: boolean) => {
    if (!value) activeIndex.value = null
  },
})
</script>

<template>
  <ul class="benefits">
    <li v-for="(b, i) in benefits" :key="b.key">
      <button
        type="button"
        class="benefit"
        aria-haspopup="dialog"
        @click="activeIndex = i"
      >
        <span class="benefit__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="26" height="26">
            <path
              :d="b.icon"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span class="benefit__title">{{ b.title }}</span>
        <span class="benefit__text muted">{{ b.short }}</span>
        <span class="benefit__more">{{ t('benefits.more') }}</span>
      </button>
    </li>
  </ul>

  <Dialog
    v-model:visible="visible"
    modal
    dismissable-mask
    :draggable="false"
    :header="active?.title"
    class="benefit-dialog"
    :style="{ width: 'min(560px, calc(100vw - 32px))' }"
  >
    <template v-if="active">
      <p v-for="(paragraph, i) in active.details" :key="i" class="muted">{{ paragraph }}</p>
      <ul class="benefit-dialog__list">
        <li v-for="point in active.points" :key="point">{{ point }}</li>
      </ul>
    </template>
  </Dialog>
</template>

<style scoped lang="scss">
.benefits {
  display: grid;
  gap: 16px;
  padding: 0;
  margin: 0;
  list-style: none;

  @include media(md) {
    grid-template-columns: 1fr 1fr;
  }

  @include media(lg) {
    grid-template-columns: repeat(4, 1fr);
  }

  li {
    display: flex;
  }
}

.benefit {
  @include card;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  width: 100%;
  padding: 24px;
  text-align: left;
  font: inherit;
  color: var(--color-text);
  cursor: pointer;

  @include motion {
    transition:
      border-color var(--duration) var(--ease),
      transform var(--duration) var(--ease);
  }

  @include hover {
    border-color: var(--color-gold-dark);
    transform: translateY(-3px);
  }

  &:active {
    transform: scale(0.98);
  }

  &__icon {
    display: grid;
    place-items: center;
    width: 52px;
    height: 52px;
    margin-bottom: 8px;
    border-radius: var(--radius-sm);
    background: var(--color-gold-alpha);
    color: var(--color-gold);
  }

  &__title {
    font-size: 1.1rem;
    font-weight: 700;
  }

  &__text {
    flex: 1;
    font-size: 0.95rem;
  }

  &__more {
    margin-top: 8px;
    color: var(--color-gold);
    font-weight: 600;
    font-size: 0.9rem;
  }
}

.benefit-dialog__list {
  margin: 0;
  padding-left: 20px;

  li {
    margin-bottom: 6px;
  }

  li::marker {
    color: var(--color-gold);
  }
}
</style>
