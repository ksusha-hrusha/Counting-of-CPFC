<template>
  <div class="auth-wrap">
    <div class="card auth-card">
      <!-- Tabs -->
      <div class="tabs">
        <button :class="['tab', { active: tab === 'login' }]" @click="tab = 'login'">Вход</button>
        <button :class="['tab', { active: tab === 'register' }]" @click="tab = 'register'">Регистрация</button>
      </div>

      <h2>{{ tab === 'login' ? 'Добро пожаловать!' : 'Создать аккаунт' }}</h2>
      <p class="sub">{{ tab === 'login' ? 'Войдите, чтобы сохранять блюда' : 'Регистрация займёт минуту' }}</p>

      <form @submit.prevent="submit">
        <div v-if="tab === 'register'" class="field">
          <label>Имя пользователя</label>
          <input class="input" v-model="form.username" placeholder="Ваше имя" required />
        </div>
        <div class="field">
          <label>Email</label>
          <input class="input" v-model="form.email" type="email" placeholder="example@mail.com" required />
        </div>
        <div class="field">
          <label>Пароль</label>
          <input class="input" v-model="form.password" type="password" placeholder="••••••••" required minlength="6" />
        </div>
        <div v-if="tab === 'login'" class="forgot">
          <RouterLink to="/forgot-password">Забыли пароль?</RouterLink>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button class="btn btn-primary" style="width:100%; margin-top:8px;" :disabled="loading">
          {{ loading ? 'Загрузка...' : (tab === 'login' ? 'Войти' : 'Зарегистрироваться') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const tab = ref('login')
const loading = ref(false)
const error = ref('')
const form = reactive({ username: '', email: '', password: '' })

async function submit() {
  error.value = ''
  loading.value = true
  try {
    if (tab.value === 'login') {
      await auth.login(form.email, form.password)
    } else {
      await auth.register(form.username, form.email, form.password)
    }
    router.push('/profile')
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
.tabs { display: flex; margin-bottom: 24px; border-radius: 8px; overflow: hidden; border: 1.5px solid var(--border); }
.tab { flex: 1; padding: 10px; background: #fff; border: none; cursor: pointer; font-size: 15px; font-weight: 600; color: #888; transition: all .15s; }
.tab.active { background: var(--primary); color: #fff; }
h2 { font-size: 22px; color: var(--text-dark); margin-bottom: 4px; }
.sub { font-size: 13px; color: #888; margin-bottom: 20px; }
.field { margin-bottom: 14px; }
.field label { display: block; font-size: 13px; color: #555; margin-bottom: 5px; }
.forgot { text-align: right; margin-bottom: 8px; }
.forgot a { font-size: 12px; color: var(--primary); }
</style>
