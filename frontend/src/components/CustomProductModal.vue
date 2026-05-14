<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box card">
      <h3 class="modal-title">Добавить свой продукт</h3>
      <p class="modal-sub">Введите КБЖУ на 100г продукта. Продукт будет виден только вам.</p>

      <div v-if="!auth.isLoggedIn" class="auth-warn">
        <RouterLink to="/auth" @click="$emit('close')">Войдите</RouterLink>, чтобы сохранить свой продукт
      </div>

      <div class="field">
        <label>Название</label>
        <input class="input" v-model="form.name" placeholder="Например: Домашний творог" />
      </div>
      <div class="grid2">
        <div class="field">
          <label>Калории (ккал)</label>
          <input class="input" v-model.number="form.calories" type="number" min="0" placeholder="0" />
        </div>
        <div class="field">
          <label>Белки (г)</label>
          <input class="input" v-model.number="form.protein" type="number" min="0" placeholder="0" />
        </div>
        <div class="field">
          <label>Жиры (г)</label>
          <input class="input" v-model.number="form.fat" type="number" min="0" placeholder="0" />
        </div>
        <div class="field">
          <label>Углеводы (г)</label>
          <input class="input" v-model.number="form.carbs" type="number" min="0" placeholder="0" />
        </div>
      </div>

      <p v-if="error" class="error-msg">{{ error }}</p>

      <div class="modal-actions">
        <button class="btn btn-outline" @click="$emit('close')">Отмена</button>
        <button class="btn btn-primary" @click="submit" :disabled="loading">
          {{ loading ? 'Сохранение...' : 'Сохранить и выбрать' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({ initialName: { type: String, default: '' } })
const emit = defineEmits(['close', 'select'])

const auth = useAuthStore()
const loading = ref(false)
const error = ref('')
const form = reactive({
  name: props.initialName,
  calories: 0, protein: 0, fat: 0, carbs: 0,
})

async function submit() {
  if (!form.name.trim()) { error.value = 'Введите название'; return }
  loading.value = true; error.value = ''
  try {
    const { data } = await api.post('/products/', form)
    emit('select', data)
    emit('close')
  } catch (e) {
    error.value = e.response?.data?.error || 'Ошибка сохранения'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0,0,0,.4);
  display: flex; align-items: center; justify-content: center;
  padding: 16px;
}
.modal-box { width: 100%; max-width: 440px; }
.modal-title { font-size: 18px; font-weight: 700; color: var(--text-dark); margin-bottom: 4px; }
.modal-sub { font-size: 13px; color: #888; margin-bottom: 16px; }
.auth-warn {
  background: var(--bg-accent); border-radius: 8px;
  padding: 10px 14px; font-size: 13px; color: var(--text-dark);
  margin-bottom: 14px;
}
.auth-warn a { color: var(--primary); font-weight: 600; }
.field { margin-bottom: 12px; }
.field label { display: block; font-size: 13px; color: #555; margin-bottom: 4px; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.modal-actions { display: flex; gap: 10px; margin-top: 16px; justify-content: flex-end; }
</style>
