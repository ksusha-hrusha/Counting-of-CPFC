<template>
  <div>
    <!-- Hero -->
    <div class="hero">
      <h1>Считайте КБЖУ точно</h1>
      <p>Учитываем изменение пищевой ценности при термической обработке</p>
      <div class="hero-actions">
        <RouterLink to="/calculator" class="btn btn-primary">Калькулятор</RouterLink>
        <RouterLink to="/dishes/new" class="btn btn-outline">Создать блюдо</RouterLink>
        <RouterLink v-if="auth.isLoggedIn" to="/diary" class="btn btn-outline">Дневник</RouterLink>
      </div>
    </div>

    <!-- Авторизованный пользователь -->
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

      <!-- Заголовок секции -->
      <div class="section-header">
        <span class="section-title" style="margin-bottom:0;">Последние блюда</span>
        <RouterLink to="/profile" class="see-all">Все блюда →</RouterLink>
      </div>

      <div v-if="loading" class="empty">Загрузка...</div>

      <div v-else class="dishes-grid">
        <div v-for="dish in recent" :key="dish.id" class="dish-card card">

          <!-- Шапка: название + бейдж -->
          <div class="dish-top">
            <span class="dish-name">{{ dish.name }}</span>
            <span :class="dish.is_public ? 'badge badge-pub' : 'badge badge-priv'">
              {{ dish.is_public ? 'Публичное' : 'Приватное' }}
            </span>
          </div>

          <!-- КБЖУ полоска -->
          <div v-if="dish.nutrition" class="nutr-strip">
            <div class="nutr-item">
              <span class="nutr-val">{{ dish.nutrition.calories }}</span>
              <span class="nutr-label">ккал</span>
            </div>
            <div class="nutr-divider" />
            <div class="nutr-item">
              <span class="nutr-val">{{ dish.nutrition.protein }}г</span>
              <span class="nutr-label">белки</span>
            </div>
            <div class="nutr-divider" />
            <div class="nutr-item">
              <span class="nutr-val">{{ dish.nutrition.fat }}г</span>
              <span class="nutr-label">жиры</span>
            </div>
            <div class="nutr-divider" />
            <div class="nutr-item">
              <span class="nutr-val">{{ dish.nutrition.carbs }}г</span>
              <span class="nutr-label">углеводы</span>
            </div>
          </div>

          <!-- Мета: ингредиенты и вес -->
          <div class="dish-meta">
            <span>{{ dish.ingredients.length }} ингр.</span>
            <span v-if="dish.nutrition?.weight_cooked">· {{ dish.nutrition.weight_cooked }}г готового</span>
          </div>

          <!-- Кнопка -->
          <RouterLink :to="`/dishes/${dish.id}/edit`" class="btn btn-outline btn-sm dish-btn">
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
/* Hero */
.hero {
  background: var(--bg-accent);
  border-radius: 16px;
  padding: 48px 40px;
  text-align: center;
  margin-bottom: 32px;
}
.hero h1 { font-size: 32px; color: var(--text-dark); margin-bottom: 10px; }
.hero p { font-size: 16px; color: var(--text-mid); margin-bottom: 24px; }
.hero-actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }

/* Статистика */
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

/* Заголовок секции */
.section-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.see-all { font-size: 13px; color: var(--primary); font-weight: 600; }

/* Сетка блюд */
.dishes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

/* Карточка блюда */
.dish-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dish-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}
.dish-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-dark);
  line-height: 1.3;
}

/* КБЖУ полоска */
.nutr-strip {
  display: flex;
  align-items: center;
  background: var(--bg-accent);
  border-radius: 8px;
  padding: 10px 12px;
  gap: 4px;
}
.nutr-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}
.nutr-val {
  font-size: 15px;
  font-weight: 700;
  color: var(--primary);
}
.nutr-label {
  font-size: 10px;
  color: #999;
  margin-top: 1px;
}
.nutr-divider {
  width: 1px;
  height: 28px;
  background: var(--border);
  flex-shrink: 0;
}

/* Мета */
.dish-meta {
  display: flex;
  gap: 6px;
  font-size: 12px;
  color: #aaa;
}

/* Кнопка */
.dish-btn { margin-top: auto; }

/* Пустое состояние */
.empty { text-align: center; color: #aaa; padding: 30px 0; font-size: 14px; }
.empty a { color: var(--primary); font-weight: 600; }

/* Мобильная адаптация */
@media (max-width: 640px) {
  .hero { padding: 28px 16px; }
  .hero h1 { font-size: 24px; }
  .hero p { font-size: 14px; }
  .hero-actions { flex-direction: column; }
  .hero-actions .btn { width: 100%; }
  .stats-row { gap: 10px; }
  .stat-val { font-size: 24px; }
  .dishes-grid { grid-template-columns: 1fr; }
  .nutr-divider { display: none; }
}
</style>
