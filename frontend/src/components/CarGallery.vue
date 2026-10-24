<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import type { CarImage } from '@/api/types'
import CarPicture from '@/components/CarPicture.vue'

const props = defineProps<{ images: CarImage[]; title: string }>()

const { t } = useI18n()
const index = ref(0)
const current = computed(() => props.images[index.value])
const hasMany = computed(() => props.images.length > 1)

function go(step: number) {
  const n = props.images.length
  if (n) index.value = (index.value + step + n) % n
}
</script>

<template>
  <section class="gallery" :aria-roledescription="t('gallery.role')" :aria-label="t('gallery.label', { title })">
    <div class="gallery__main" @keydown.left.prevent="go(-1)" @keydown.right.prevent="go(1)">
      <CarPicture
        :url="current?.url"
        :alt="t('gallery.photo', { title, n: index + 1 })"
        sizes="(min-width: 1024px) 60vw, 100vw"
        :max-width="1600"
        eager
      />
      <template v-if="hasMany">
        <button
          type="button"
          class="gallery__nav gallery__nav--prev"
          :aria-label="t('gallery.prev')"
          @click="go(-1)"
        >
          ‹
        </button>
        <button
          type="button"
          class="gallery__nav gallery__nav--next"
          :aria-label="t('gallery.next')"
          @click="go(1)"
        >
          ›
        </button>
        <span class="gallery__counter">{{ index + 1 }} / {{ images.length }}</span>
      </template>
    </div>

    <div v-if="hasMany" class="gallery__thumbs">
      <button
        v-for="(image, i) in images"
        :key="image.id"
        type="button"
        class="gallery__thumb"
        :class="{ 'is-active': i === index }"
        :aria-label="t('gallery.show', { n: i + 1 })"
        :aria-current="i === index"
        @click="index = i"
      >
        <CarPicture :url="image.url" alt="" sizes="120px" :max-width="400" />
      </button>
    </div>
  </section>
</template>

<style scoped lang="scss">
.gallery {
  &__main {
    position: relative;
    aspect-ratio: 16 / 10;
    border-radius: var(--radius-lg);
    overflow: hidden;
    border: 1px solid var(--color-border);
  }

  &__nav {
    position: absolute;
    top: 50%;
    translate: 0 -50%;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    border: 1px solid var(--color-border);
    background: var(--color-overlay);
    color: var(--color-text);
    font-size: 1.6rem;
    line-height: 1;
    cursor: pointer;

    @include hover {
      border-color: var(--color-gold);
      color: var(--color-gold);
    }

    &--prev {
      left: 12px;
    }

    &--next {
      right: 12px;
    }
  }

  &__counter {
    position: absolute;
    right: 12px;
    bottom: 12px;
    padding: 2px 10px;
    border-radius: 999px;
    background: var(--color-overlay);
    font-size: 0.8rem;
  }

  &__thumbs {
    display: flex;
    gap: 8px;
    margin-top: 12px;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    padding-bottom: 4px;
  }

  &__thumb {
    flex: 0 0 96px;
    height: 64px;
    padding: 0;
    border-radius: var(--radius-sm);
    border: 2px solid transparent;
    overflow: hidden;
    cursor: pointer;
    background: none;
    scroll-snap-align: start;
    opacity: 0.6;

    &.is-active {
      border-color: var(--color-gold);
      opacity: 1;
    }
  }
}
</style>
