<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const { t } = useI18n()
</script>

<template>
  <div v-if="auth.user && !auth.user.email_verified" class="alert alert--info notice" role="status">
    <span>
      <strong>{{ t('notice.title') }}</strong>
      {{ t('notice.text', { email: auth.user.email }) }}
    </span>
    <RouterLink
      :to="{ name: 'verify-email', query: { redirect: route.fullPath } }"
      class="btn btn--gold btn--sm"
    >
      {{ t('notice.enterCode') }}
    </RouterLink>
  </div>
</template>

<style scoped lang="scss">
.notice {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
</style>
