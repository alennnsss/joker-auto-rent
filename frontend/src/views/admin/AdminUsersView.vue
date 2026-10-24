<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { adminApi } from '@/api/admin'
import { errorMessage } from '@/api/http'
import type { User } from '@/api/types'
import { formatDate } from '@/utils/format'

const { t } = useI18n()
const users = ref<User[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    users.value = await adminApi.users()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <h1 class="page-title">{{ t('admin.users') }}</h1>
  <div v-if="error" class="alert alert--error" role="alert">{{ error }}</div>
  <div class="table-wrap">
    <table class="table">
      <thead>
        <tr>
          <th>ID</th>
          <th>{{ t('adminUsers.name') }}</th>
          <th>{{ t('common.phone') }}</th>
          <th>{{ t('common.email') }}</th>
          <th>{{ t('adminUsers.role') }}</th>
          <th>{{ t('adminUsers.registered') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="6" class="muted">{{ t('common.loading') }}</td>
        </tr>
        <tr v-for="u in users" v-else :key="u.id">
          <td>{{ u.id }}</td>
          <td>{{ u.full_name }}</td>
          <td>
            <a v-if="u.phone" :href="`tel:${u.phone.replace(/[^\d+]/g, '')}`">{{ u.phone }}</a>
            <span v-else class="muted">—</span>
          </td>
          <td>{{ u.email }}</td>
          <td>{{ u.role === 'admin' ? t('adminUsers.admin') : t('adminUsers.client') }}</td>
          <td>{{ formatDate(u.created_at) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
