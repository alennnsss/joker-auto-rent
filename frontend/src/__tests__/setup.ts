import { config } from '@vue/test-utils'

import { i18n } from '@/i18n'

// Компоненты используют useI18n() — подключаем плагин во всех mount()
config.global.plugins = [i18n]
