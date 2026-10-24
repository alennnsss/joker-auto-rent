import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'

import App from './App.vue'
import { currentLocale, i18n } from './i18n'
import router from './router'
import { JokerPreset, primeLocales } from './styles/primevue'
import './styles/main.scss'

const app = createApp(App)

app.use(createPinia())
app.use(i18n)
app.use(router)
app.use(PrimeVue, {
  theme: { preset: JokerPreset, options: { darkModeSelector: '.app-dark', cssLayer: false } },
  // При смене языка App.vue переключает локаль календаря
  locale: primeLocales[currentLocale()],
})

app.mount('#app')
