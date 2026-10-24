<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { imageSources } from '@/utils/images'

const props = withDefaults(
  defineProps<{
    url?: string
    alt: string
    sizes?: string
    maxWidth?: number
    eager?: boolean
  }>(),
  { url: undefined, sizes: '100vw', maxWidth: 1200, eager: false },
)

const failed = ref(false)
watch(
  () => props.url,
  () => {
    failed.value = false
  },
)

const sources = computed(() => imageSources(props.url, props.maxWidth))
</script>

<template>
  <img
    v-if="url && !failed"
    class="picture"
    :src="sources.src"
    :srcset="sources.srcset"
    :sizes="sources.srcset ? sizes : undefined"
    :alt="alt"
    :loading="eager ? 'eager' : 'lazy'"
    :fetchpriority="eager ? 'high' : undefined"
    decoding="async"
    @error="failed = true"
  />
  <div v-else class="picture picture--placeholder" role="img" :aria-label="alt">
    <svg viewBox="0 0 64 32" width="72" aria-hidden="true">
      <path
        fill="currentColor"
        d="M10 22h-4a2 2 0 0 1-2-2v-4l5-1 6-7h22l8 7 11 2a4 4 0 0 1 4 4v1a2 2 0 0 1-2 2h-4a6 6 0 0 0-12 0H22a6 6 0 0 0-12 0zm6 6a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm32 0a4 4 0 1 1 0-8 4 4 0 0 1 0 8z"
      />
    </svg>
  </div>
</template>

<style scoped lang="scss">
.picture {
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: var(--color-surface-2);

  &--placeholder {
    display: grid;
    place-items: center;
    color: var(--color-gold-dark);
  }
}
</style>
