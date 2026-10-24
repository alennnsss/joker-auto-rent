<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { adminApi } from '@/api/admin'
import { errorMessage } from '@/api/http'
import type { Payment } from '@/api/types'
import StatusBadge from '@/components/StatusBadge.vue'
import { formatDate, formatPrice } from '@/utils/format'

const { t } = useI18n()
const payments = ref<Payment[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    payments.value = await adminApi.payments()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <h1 class="page-title">{{ t('admin.payments') }}</h1>
  <p class="muted">{{ t('adminPayments.text') }}</p>
  <div v-if="error" class="alert alert--error" role="alert">{{ error }}</div>
  <div class="table-wrap">
    <table class="table">
      <thead>
        <tr>
          <th>ID</th>
          <th>{{ t('adminPayments.booking') }}</th>
          <th>{{ t('adminPayments.amount') }}</th>
          <th>{{ t('adminPayments.provider') }}</th>
          <th>{{ t('adminPayments.providerId') }}</th>
          <th>{{ t('adminPayments.status') }}</th>
          <th>{{ t('adminPayments.date') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="7" class="muted">{{ t('common.loading') }}</td>
        </tr>
        <tr v-else-if="!payments.length">
          <td colspan="7" class="muted">{{ t('adminPayments.empty') }}</td>
        </tr>
        <tr v-for="p in payments" v-else :key="p.id">
          <td>{{ p.id }}</td>
          <td>№{{ p.booking_id }}</td>
          <td>{{ formatPrice(p.amount) }}</td>
          <td>{{ p.provider }}</td>
          <td class="muted">{{ p.provider_payment_id }}</td>
          <td><StatusBadge kind="payment" :status="p.status" /></td>
          <td>{{ formatDate(p.created_at) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
