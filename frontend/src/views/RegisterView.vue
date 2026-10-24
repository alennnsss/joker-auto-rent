<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { errorMessage } from '@/api/http'
import PasswordInput from '@/components/PasswordInput.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const form = reactive({ full_name: '', phone: '', email: '', password: '' })
const error = ref<string | null>(null)
const loading = ref(false)

/** Маска +7 (7XX) XXX-XX-XX по мере ввода. */
function onPhoneInput(event: Event) {
  let digits = (event.target as HTMLInputElement).value.replace(/\D/g, '')
  if (digits.startsWith('8')) digits = '7' + digits.slice(1)
  if (!digits.startsWith('7')) digits = '7' + digits
  digits = digits.slice(0, 11)
  const p = digits.slice(1)
  let out = '+7'
  if (p.length) out += ` (${p.slice(0, 3)}`
  if (p.length >= 3) out += ')'
  if (p.length > 3) out += ` ${p.slice(3, 6)}`
  if (p.length > 6) out += `-${p.slice(6, 8)}`
  if (p.length > 8) out += `-${p.slice(8, 10)}`
  form.phone = out
}

async function submit() {
  if (form.password.length < 8) {
    error.value = t('auth.passwordTooShort')
    return
  }
  loading.value = true
  error.value = null
  try {
    await auth.register({ ...form, email: form.email.trim() })
    // Сразу просим подтвердить email кодом из письма
    const redirect = route.query.redirect
    const safe =
      typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')
    await router.replace({ name: 'verify-email', query: { redirect: safe ? redirect : '/cars' } })
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page container auth">
    <form class="auth__card card" @submit.prevent="submit">
      <h1 class="auth__title">{{ t('auth.registerTitle') }}</h1>
      <p class="muted">{{ t('auth.registerText') }}</p>

      <div v-if="error" class="alert alert--error" role="alert">{{ error }}</div>

      <div class="field">
        <label class="field__label" for="r-name">{{ t('common.fullName') }}</label>
        <input
          id="r-name"
          v-model="form.full_name"
          class="input"
          autocomplete="name"
          minlength="2"
          required
        />
      </div>
      <div class="field">
        <label class="field__label" for="r-phone">{{ t('common.phone') }}</label>
        <input
          id="r-phone"
          :value="form.phone"
          class="input"
          type="tel"
          autocomplete="tel"
          inputmode="tel"
          placeholder="+7 (7XX) XXX-XX-XX"
          required
          @input="onPhoneInput"
        />
      </div>
      <div class="field">
        <label class="field__label" for="r-email">{{ t('common.email') }}</label>
        <input
          id="r-email"
          v-model="form.email"
          class="input"
          type="email"
          autocomplete="email"
          inputmode="email"
          required
        />
      </div>
      <div class="field">
        <label class="field__label" for="r-password">{{ t('common.password') }}</label>
        <PasswordInput
          id="r-password"
          v-model="form.password"
          autocomplete="new-password"
          :minlength="8"
        />
        <span class="muted field__hint">{{ t('auth.passwordHint') }}</span>
      </div>

      <button type="submit" class="btn btn--gold btn--block" :disabled="loading">
        {{ loading ? t('auth.creating') : t('auth.signUp') }}
      </button>

      <p class="auth__alt muted">
        {{ t('auth.haveAccount') }}
        <RouterLink :to="{ name: 'login', query: route.query }">{{ t('common.login') }}</RouterLink>
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

.field__hint {
  font-size: 0.8rem;
}
</style>
