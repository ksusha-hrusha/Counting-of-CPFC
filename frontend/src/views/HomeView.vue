<template>
  <div>
    <!-- Hero -->
    <div class="hero">
      <h1>Считайте КБЖУ точно</h1>
      <p>Учитываем изменение пищевой ценности при термической обработке</p>
      <div class="hero-actions">
        <RouterLink to="/calculator" class="btn btn-primary">Калькулятор</RouterLink>
        <RouterLink to="/dishes/new" class="btn btn-outline">Создать блюдо</RouterLink>
      </div>
    </div>

    <!-- Профиль (только для авторизованных) -->
    <template v-if="auth.isLoggedIn">
      <!-- Статистика -->
      <div class="stats-row">
        <div class="stat-card card">
          <span class="stat-val">{{ dishes.length }}</span>
          <span class="stat-label">всего блюд</span>
        </div>
        <div class="stat-card card">
          <span class="stat-val">{{ publicCount }}</span>
          <span class="stat-label">публичных</span>
        </div>
        <div class="stat-card card">
          <span class="stat-val">{{ privateCount }}</span>
          <span class="stat-label">приватных</span>
        </div>
      </div>

      <!-- Последние блюда -->
      <div class="section-header">
        <span class="section-title" style="margin-bottom:0;">Последние блюда</span>
        <RouterLink to="/profile" class="see-all">Все блюда →</RouterLink>
      </div>

      <div v-if="loading" class="empty">Загрузка...</div>
      <div v-else-if="recent.length === 0" class="empty">
        Блюд пока нет. <RouterLink to="/dishes/new">Создайте первое!</RouterLink>
      </div>
      <div v-else class="dishes-grid">
        <div v-for="dish in recent" :key="dish.id" class="dish-card card">
          <div class="dish-top">
            <span class="dish-name">{{ dish.name }}</span>
            <span :class="dish.is_public ? 'badge badge-pub' : 'badge badge-priv'">
              {{ dish.is_public ? 'Публичное' : 'Приватное' }}
            </span>
          </div>
          <div v-if="dish.nutrition" class="dish-nutrition">
            <span>{{ dish.nutrition.calories }} ккал</span>
            <span>Б: {{ dish.nutrition.protein }}г</span>
            <span>Ж: {{ dish.nutrition.fat }}г</span>
            <span>У: {{ dish.nutrition.carbs }}г</span>
          </div>
          <div class="dish-meta">
            {{ dish.ingredients.length }} ингр. · {{ dish.nutrition?.weight_cooked }}г
          </div>
          <RouterLink :to="`/dishes/${dish.id}/edit`" class="btn btn-outline btn-sm" style="margin-top:8px;">
            Редактировать
          </RouterLink>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()
const dishes = ref([])
const loading = ref(false)

const recent = computed(() => dishes.value.slice(0, 4))
const publicCount = computed(() => dishes.value.filter(d => d.is_public).length)
const privateCount = computed(() => dishes.value.filter(d => !d.is_public).length)

onMounted(async () => {
  if (!auth.isLoggedIn) return
  loading.value = true
  try {
    const { data } = await api.get('/dishes/')
    dishes.value = data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.hero {
  background: var(--bg-accent);
  border-radius: 16px;
  padding: 48px 40px;
  text-align: center;
  margin-bottom: 32px;
}
.hero h1 { font-size: 32px; color: var(--text-dark); margin-bottom: 10px; }
.hero p { font-size: 16px; color: var(--text-mid); margin-bottom: 24px; }
.hero-actions { display: flex; gap: 12px; justify-content: center; }

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}
.stat-card {
  display: flex; flex-direction: column; align-items: center;
  padding: 20px; gap: 4px;
}
.stat-val { font-size: 32px; font-weight: 700; color: var(--primary); }
.stat-label { font-size: 13px; color: #888; }

.section-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.see-all { font-size: 13px; color: var(--primary); font-weight: 600; }

.dishes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.dish-card { display: flex; flex-direction: column; gap: 6px; }
.dish-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.dish-name { font-size: 15px; font-weight: 700; color: var(--text-dark); }
.dish-nutrition { display: flex; gap: 10px; font-size: 12px; color: var(--primary); font-weight: 600; flex-wrap: wrap; }
.dish-meta { font-size: 11px; color: #aaa; }
.empty { text-align: center; color: #aaa; padding: 30px 0; font-size: 14px; }
.empty a { color: var(--primary); font-weight: 600; }

@media (max-width: 640px) {
  .hero { padding: 28px 16px; }
  .hero h1 { font-size: 24px; }
  .hero p { font-size: 14px; }
  .hero-actions { flex-direction: column; }
  .hero-actions .btn { width: 100%; }
  .stats-row { grid-template-columns: repeat(3, 1fr); gap: 10px; }
  .stat-val { font-size: 24px; }
  .dishes-grid { grid-template-columns: 1fr; }
}
</style>
