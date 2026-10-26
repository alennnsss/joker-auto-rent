// Геозона: до этих точек выезд бесплатный, дальше — с доплатой.
// Названия — в словарях i18n (rules.geozone.points.*), здесь только координаты для карты.
// Порядок — по часовой стрелке: в этом порядке точки соединяются в границу.
export const GEOZONE_POINTS = [
  { key: 'baiserke', lat: 43.4869, lon: 77.0476 },
  { key: 'talgar', lat: 43.3036, lon: 77.24 },
  { key: 'almaArasan', lat: 43.1196, lon: 76.8616 },
  { key: 'kaskelen', lat: 43.2008, lon: 76.6247 },
] as const

// Подложка OpenStreetMap (без ключа API, подписи на местных языках).
// Плитки светлые — в тёмную тему их переводит CSS-фильтр в GeozoneMap.vue
export const MAP_TILES = {
  url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  maxZoom: 18,
}
