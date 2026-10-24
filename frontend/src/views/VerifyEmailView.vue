<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'

import { errorMessage } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const RESEND_COOLDOWN = 60

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const code = ref('')
const error = ref<string | null>(null)
const info = ref<string | null>(null)
const loading = ref(false)
const cooldown = ref(RESEND_COOLDOWN)
let timer: ReturnType<typeof setInterval> | undefined

function startCooldown() {
  cooldown.value = RESEND_COOLDOWN
  clearInterval(timer)
  timer = setInterval(() => {
    cooldown.value = Math.max(0, cooldown.value - 1)
    if (!cooldown.value) clearInterval(timer)
  }, 1000)
}

function done() {
  const redirect = route.query.redirect
  const safe = typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')
  router.replace(safe ? redirect : { name: 'account-bookings' })
}

onMounted(() => {
  if (auth.user?.email_verified) done()
  else startCooldown()
})
onBeforeUnmount(() => clearInterval(timer))

function onInput(event: Event) {
  code.value = (event.target as HTMLInputElement).value.replace(/\D/g, '').slice(0, 6)
  if (code.value.length === 6) submit()
}

async function submit() {
  if (code.value.length !== 6 || loading.value) return
  loading.value = true
  error.value = null
  try {
    await auth.verifyEmail(code.value)
    done()
  } catch (e) {
    error.value = errorMessage(e)
    code.value = ''
  } finally {
    loading.value = false
  }
}

async function resend() {
  error.value = null
  info.value = null
  try {
    await auth.resendVerification()
    info.value = t('verify.sent')
    startCooldown()
  } catch (e) {
    error.value = errorMessage(e)
  }
}
</script>

<template>
  <div class="page container verify">
    <form class="verify__card card" @submit.prevent="submit">
      <div class="verify__icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="30" height="30">
          <path
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linejoin="round"
            d="M3 6h18v12H3zM3 7l9 6 9-6"
          />
        </svg>
      </div>
      <h1 class="verify__title">{{ t('verify.title') }}</h1>
      <i18n-t keypath="verify.text" tag="p" class="muted" scope="global">
        <template #email>
          <strong>{{ auth.user?.email }}</strong>
        </template>
      </i18n-t>

      <div v-if="error" class="alert alert--error" role="alert">{{ error }}</div>
      <div v-if="info" class="alert alert--success" role="status">{{ info }}</div>

      <label class="visually-hidden" for="verify-code">{{ t('verify.codeLabel') }}</label>
      <input
        id="verify-code"
        :value="code"
        class="input verify__code"
        inputmode="numeric"
        autocomplete="one-time-code"
        maxlength="6"
        placeholder="••••••"
        @input="onInput"
      />

      <button type="submit" class="btn btn--gold btn--block" :disabled="code.length !== 6 || loading">
        {{ loading ? t('verify.checking') : t('verify.submit') }}
      </button>

      <button type="button" class="btn btn--ghost btn--block verify__resend" :disabled="cooldown > 0" @click="resend">
        {{ cooldown > 0 ? t('verify.resendIn', { n: cooldown }) : t('verify.resend') }}
      </button>
    </form>
  </div>
</template>

<style scoped lang="scss">
.verify {
  display: flex;
  justify-content: center;

  &__card {
    width: 100%;
    max-width: 460px;
    text-align: center;
  }

  &__icon {
    display: grid;
    place-items: center;
    width: 64px;
    height: 64px;
    margin: 0 auto 16px;
    border-radius: 50%;
    background: var(--color-gold-alpha);
    color: var(--color-gold);
  }

  &__title {
    font-size: 1.8rem;
  }

  &__code {
    height: 64px;
    margin-bottom: 16px;
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: 0.5em;
    padding-left: 0.5em;
  }

  &__resend {
    margin-top: 8px;
  }
}
</style>
