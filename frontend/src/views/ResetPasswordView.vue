<template>
  <div class="auth-wrap">
    <div class="card auth-card">
      <h2>Новый пароль</h2>
      <p class="sub">Придумайте новый пароль для вашего аккаунта</p>

      <div v-if="done" class="success-box">
        Пароль изменён. <RouterLink to="/auth">Войти</RouterLink>
      </div>
      <form v-else @submit.prevent="submit">
        <div class="field">
          <label>Новый пароль</label>
          <input class="input" v-model="password" type="password" placeholder="Минимум 6 символов" required minlength="6" />
        </div>
        <div class="field">
          <label>Повторите пароль</label>
          <input class="input" v-model="confirm" type="password" placeholder="Повторите пароль" required />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button class="btn btn-primary" style="width:100%; margin-top:8px;" :disabled="loading">
          {{ loading ? 'Сохранение...' : 'Сохранить пароль' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const password = ref('')
const confirm = ref('')
const loading = ref(false)
const error = ref('')
const done = ref(false)

async function submit() {
  if (password.value !== confirm.value) {
    error.value = 'Пароли не совпадают'; return
  }
  loading.value = true; error.value = ''
  try {
    await api.post('/auth/reset-password', {
      token: route.query.token,
      password: password.value,
    })
    done.value = true
  } catch (e) {
    error.value = e.response?.data?.error || 'Ошибка. Ссылка могла устареть.'
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
.success-box a { color: var(--primary); font-weight: 600; }
</style>
