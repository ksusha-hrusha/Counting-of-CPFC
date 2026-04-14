<template>
  <div class="auth-wrap">
    <div class="card auth-card">
      <h2>Забыли пароль?</h2>
      <p class="sub">Введите email — мы отправим ссылку для сброса</p>

      <div v-if="sent" class="success-box">
        Письмо отправлено. Проверьте почту (и папку «Спам»).
      </div>
      <form v-else @submit.prevent="submit">
        <div class="field">
          <label>Email</label>
          <input class="input" v-model="email" type="email" placeholder="example@mail.com" required />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button class="btn btn-primary" style="width:100%; margin-top:8px;" :disabled="loading">
          {{ loading ? 'Отправка...' : 'Отправить ссылку' }}
        </button>
      </form>

      <div style="margin-top:16px; text-align:center;">
        <RouterLink to="/auth" style="font-size:13px; color:var(--primary);">← Вернуться ко входу</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api'

const email = ref('')
const loading = ref(false)
const error = ref('')
const sent = ref(false)

async function submit() {
  loading.value = true; error.value = ''
  try {
    await api.post('/auth/forgot-password', { email: email.value })
    sent.value = true
  } catch (e) {
    error.value = e.response?.data?.error || 'Ошибка. Попробуйте снова.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-wrap { display: flex; justify-content: center; padding: 40px 0; }
.auth-card { width: 100%; max-width: 420px; }
h2 { font-size: 22px; color: var(--text-dark); margin-bottom: 4px; }
.sub { font-size: 13px; color: #888; margin-bottom: 20px; }
.field { margin-bottom: 14px; }
.field label { display: block; font-size: 13px; color: #555; margin-bottom: 5px; }
.success-box {
  background: var(--bg-accent); border-radius: 8px;
  padding: 14px; font-size: 14px; color: var(--text-dark);
}
</style>
