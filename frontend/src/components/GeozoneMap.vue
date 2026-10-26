<script setup lang="ts">
import 'leaflet/dist/leaflet.css'

import L from 'leaflet'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import { GEOZONE_POINTS, MAP_TILES } from '@/config/geozone'

const { t, locale } = useI18n()

const el = ref<HTMLDivElement>()
let map: L.Map | null = null
let resizeObserver: ResizeObserver | null = null
const markers: L.CircleMarker[] = []

const pointName = (key: string) => t(`rules.geozone.points.${key}`)

// Leaflet рисует в SVG — цвета берём из CSS-переменных темы, а не хардкодим
function cssVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

onMounted(() => {
  if (!el.value) return
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const gold = cssVar('--color-gold')

  map = L.map(el.value, {
    scrollWheelZoom: false,
    // Дробный масштаб — зона заполняет карту, а не прыгает между целыми уровнями
    zoomSnap: 0.25,
    zoomDelta: 0.5,
    // На телефоне один палец прокручивает страницу, а не карту
    dragging: !L.Browser.mobile,
    zoomAnimation: !reduceMotion,
    fadeAnimation: !reduceMotion,
    attributionControl: true,
  })
  map.attributionControl.setPrefix(false)

  L.tileLayer(MAP_TILES.url, {
    attribution: MAP_TILES.attribution,
    maxZoom: MAP_TILES.maxZoom,
    className: 'geozone-map__tiles',
  }).addTo(map)

  const ring = GEOZONE_POINTS.map((p) => L.latLng(p.lat, p.lon))
  const zone = L.polygon(ring, {
    color: gold,
    weight: 3,
    dashArray: '8 6',
    fillColor: gold,
    fillOpacity: 0.12,
    interactive: false,
  }).addTo(map)

  for (const p of GEOZONE_POINTS) {
    const marker = L.circleMarker([p.lat, p.lon], {
      radius: 8,
      color: cssVar('--color-bg'),
      weight: 3,
      fillColor: gold,
      fillOpacity: 1,
    })
      .bindTooltip(pointName(p.key), {
        permanent: true,
        direction: 'top',
        offset: [0, -10],
        className: 'geozone-tip',
      })
      .addTo(map)
    markers.push(marker)
  }

  // Сверху запас больше — над точками висят подписи
  const fit = { paddingTopLeft: L.point(36, 64), paddingBottomRight: L.point(36, 36) }
  map.fitBounds(zone.getBounds(), fit)

  // Карта в гибкой сетке: при смене ширины пересчитываем размер и границы
  resizeObserver = new ResizeObserver(() => {
    map?.invalidateSize()
    map?.fitBounds(zone.getBounds(), { ...fit, animate: false })
  })
  resizeObserver.observe(el.value)
})

watch(locale, () => {
  markers.forEach((m, i) => m.setTooltipContent(pointName(GEOZONE_POINTS[i]!.key)))
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  map?.remove()
  map = null
})
</script>

<template>
  <div ref="el" class="geozone-map" role="region" :aria-label="t('rules.geozone.mapTitle')" />
</template>

<style scoped lang="scss">
.geozone-map {
  width: 100%;
  height: 100%;
  min-height: inherit;
  background: var(--color-surface-2);
  font: inherit;

  // Элементы Leaflet создаются вне шаблона — стилизуем через :deep.
  // Светлые плитки OSM → тёмная карта в тон сайту
  :deep(.geozone-map__tiles) {
    filter: invert(1) hue-rotate(180deg) brightness(0.85) contrast(0.9) saturate(0.35);
  }

  :deep(.geozone-tip) {
    padding: 4px 10px;
    border: 1px solid var(--color-gold-dark);
    border-radius: 999px;
    background: var(--color-surface);
    color: var(--color-text);
    font-size: 0.8rem;
    font-weight: 600;
    box-shadow: none;

    &::before {
      border-top-color: var(--color-gold-dark);
    }
  }

  :deep(.leaflet-control-zoom) {
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    overflow: hidden;

    a {
      width: 44px;
      height: 44px;
      line-height: 44px;
      background: var(--color-surface);
      color: var(--color-text);
      border-color: var(--color-border);

      @include hover {
        background: var(--color-surface-2);
        color: var(--color-gold);
      }
    }
  }

  :deep(.leaflet-control-attribution) {
    background: var(--color-overlay);
    color: var(--color-text-muted);
    font-size: 0.7rem;

    a {
      color: var(--color-text-muted);
    }
  }
}
</style>
