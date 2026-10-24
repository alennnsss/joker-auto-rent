<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { errorMessage } from '@/api/http'
import PasswordInput from '@/components/PasswordInput.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const loading = ref(false)

function redirectTarget() {
  const redirect = route.query.redirect
  return typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')
    ? redirect
    : null
}

async function submit() {
  loading.value = true
  error.value = null
  try {
    await auth.login(email.value.trim(), password.value)
    const target = redirectTarget()
    await router.replace(target ?? (auth.isAdmin ? { name: 'admin' } : { name: 'account-bookings' }))
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page container auth">
    <form class="auth__card card" novalidate @submit.prevent="submit">
      <h1 class="auth__title">{{ t('auth.loginTitle') }}</h1>
      <p class="muted">{{ t('auth.loginText') }}</p>

      <div v-if="error" class="alert alert--error" role="alert">{{ error }}</div>

      <div class="field">
        <label class="field__label" for="l-email">{{ t('common.email') }}</label>
        <input
          id="l-email"
          v-model="email"
          class="input"
          type="email"
          autocomplete="email"
          inputmode="email"
          required
        />
      </div>
      <div class="field">
        <label class="field__label" for="l-password">{{ t('common.password') }}</label>
        <PasswordInput id="l-password" v-model="password" autocomplete="current-password" />
      </div>

      <button type="submit" class="btn btn--gold btn--block" :disabled="loading || !email || !password">
        {{ loading ? t('auth.loggingIn') : t('common.login') }}
      </button>

      <p class="auth__alt muted">
        {{ t('auth.noAccount') }}
        <RouterLink :to="{ name: 'register', query: route.query }">{{ t('auth.signUp') }}</RouterLink>
      </p>
    </form>
  </div>
</template>

<style scoped lang="scss">
.auth {
  display: flex;
  justify-content: center;

  &__card {
    width: 100%;
    max-width: 440px;
  }

  &__title {
    font-size: 2rem;
  }

  &__alt {
    margin: 16px 0 0;
    text-align: center;
  }
}
</style>
