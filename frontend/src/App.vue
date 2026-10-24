<script setup lang="ts">
import { usePrimeVue } from 'primevue/config'
import { watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterView, useRoute } from 'vue-router'
import type { Locale } from '@/i18n'
import { applyTitle } from '@/router'
import { primeLocales } from '@/styles/primevue'

const { locale } = useI18n()
const primevue = usePrimeVue()
const route = useRoute()

// Всё, что живёт вне шаблонов: <html lang>, календари PrimeVue, заголовок вкладки
watch(
  locale,
  (value) => {
    document.documentElement.lang = value
    // Дополняем локаль PrimeVue (в ней есть и другие ключи), config реактивный — календари обновятся
    Object.assign(primevue.config.locale ?? {}, primeLocales[value as Locale])
    applyTitle(route)
  },
  { immediate: true },
)
</script>

<template>
  <RouterView />
</template>
