<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'

import { errorMessage } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils/format'

const auth = useAuthStore()
const { t } = useI18n()

const form = reactive({
  full_name: auth.user?.full_name ?? '',
  phone: auth.user?.phone ?? '',
})
const saving = ref(false)
const message = ref<{ type: 'success' | 'error'; text: string } | null>(null)

async function save() {
  saving.value = true
  message.value = null
  try {
    await auth.updateProfile({ full_name: form.full_name.trim(), phone: form.phone || null })
    form.phone = auth.user?.phone ?? ''
    message.value = { type: 'success', text: t('account.profileSaved') }
  } catch (e) {
    message.value = { type: 'error', text: errorMessage(e) }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <form class="profile card" @submit.prevent="save">
    <h2 class="profile__title">{{ t('common.profile') }}</h2>

    <div v-if="message" class="alert" :class="`alert--${message.type}`" role="status">
      {{ message.text }}
    </div>

    <div class="field">
      <label class="field__label" for="p-email">{{ t('common.email') }}</label>
      <input id="p-email" class="input" :value="auth.user?.email" disabled />
      <span v-if="auth.user?.email_verified" class="verified">{{ t('account.emailVerified') }}</span>
      <RouterLink v-else :to="{ name: 'verify-email' }" class="unverified">
        {{ t('account.emailNotVerified') }}
      </RouterLink>
    </div>
    <div class="field">
      <label class="field__label" for="p-name">{{ t('common.fullName') }}</label>
      <input id="p-name" v-model="form.full_name" class="input" autocomplete="name" required />
    </div>
    <div class="field">
      <label class="field__label" for="p-phone">{{ t('common.phone') }}</label>
      <input
        id="p-phone"
        v-model="form.phone"
        class="input"
        type="tel"
        inputmode="tel"
        autocomplete="tel"
        placeholder="+7 (7XX) XXX-XX-XX"
      />
    </div>

    <p class="muted profile__since">
      {{ t('account.clientSince', { date: formatDate(auth.user?.created_at) }) }}
    </p>

    <button type="submit" class="btn btn--gold" :disabled="saving">
      {{ saving ? t('common.saving') : t('common.save') }}
    </button>
  </form>
</template>

<style scoped lang="scss">
.profile {
  max-width: 560px;

  &__title {
    font-size: 1.5rem;
  }

  .verified {
    font-size: 0.85rem;
    color: var(--color-success);
  }

  .unverified {
    display: inline-flex;
    align-items: center;
    min-height: 44px;
    font-size: 0.85rem;
  }

  &__since {
    font-size: 0.875rem;
  }
}
</style>
