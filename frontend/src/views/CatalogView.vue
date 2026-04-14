<template>
  <div>
    <h1 class="section-title">Каталог блюд</h1>
    <div class="filter-bar">
      <input class="input" v-model="search" @input="onSearch" placeholder="Поиск блюд..." style="max-width:360px;" />
    </div>
    <div v-if="loading" class="empty">Загрузка...</div>
    <div v-else-if="dishes.length === 0" class="empty">Блюд не найдено</div>
    <div v-else class="dishes-grid">
      <div v-for="dish in dishes" :key="dish.id" class="dish-card card">
        <!-- Автор -->
        <div v-if="dish.author" class="author-row">
          <UserAvatar :src="dish.author.avatar" :username="dish.author.username" :size="28" />
          <span class="author-name">{{ dish.author.username }}</span>
        </div>

        <div class="dish-top">
          <span class="dish-name">{{ dish.name }}</span>
          <span class="badge badge-pub">Публичное</span>
        </div>
        <div v-if="dish.nutrition" class="dish-nutrition">
          <span>{{ dish.nutrition.calories }} ккал</span>
          <span>Б: {{ dish.nutrition.protein }}г</span>
          <span>Ж: {{ dish.nutrition.fat }}г</span>
          <span>У: {{ dish.nutrition.carbs }}г</span>
        </div>
        <div class="dish-meta">
          {{ dish.ingredients.length }} ингр. · {{ dish.nutrition?.weight_cooked }}г
          <span v-if="dish.cooking_method_name"> · {{ dish.cooking_method_name }}</span>
        </div>
        <div v-if="dish.nutrition?.per_100g" class="per100">
          На 100г: {{ dish.nutrition.per_100g.calories }} ккал
        </div>
        <div class="dish-actions">
          <button v-if="auth.isLoggedIn" class="btn btn-primary btn-sm" @click="copy(dish.id)" :disabled="copying === dish.id">
            {{ copying === dish.id ? 'Копирую...' : 'Скопировать в профиль' }}
          </button>
          <RouterLink v-else to="/auth" class="btn btn-outline btn-sm">Войти чтобы скопировать</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import UserAvatar from '@/components/UserAvatar.vue'

const auth = useAuthStore()
const router = useRouter()
const dishes = ref([])
const loading = ref(true)
const search = ref('')
const copying = ref(null)
let timer = null

async function load(q = '') {
  loading.value = true
  const { data } = await api.get('/catalog/', { params: q ? { q } : {} })
  dishes.value = data
  loading.value = false
}

onMounted(() => load())

function onSearch() {
  clearTimeout(timer)
  timer = setTimeout(() => load(search.value), 400)
}

async function copy(id) {
  copying.value = id
  try {
    await api.post(`/catalog/${id}/copy`)
    router.push('/profile')
  } finally {
    copying.value = null
  }
}
</script>

<style scoped>
.filter-bar { margin-bottom: 20px; }
.dishes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.dish-card { display: flex; flex-direction: column; gap: 8px; }
.author-row { display: flex; align-items: center; gap: 8px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
.author-name { font-size: 13px; font-weight: 600; color: var(--text-dark); }
.dish-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.dish-name { font-size: 15px; font-weight: 700; color: var(--text-dark); }
.dish-nutrition { display: flex; gap: 12px; font-size: 12px; color: var(--primary); font-weight: 600; flex-wrap: wrap; }
.dish-meta { font-size: 11px; color: #aaa; }
.per100 { font-size: 12px; color: var(--text-mid); }
.dish-actions { margin-top: 4px; }
.empty { text-align: center; color: #aaa; padding: 40px 0; font-size: 15px; }

@media (max-width: 640px) {
  .dishes-grid { grid-template-columns: 1fr; }
  .filter-bar .input { max-width: 100% !important; }
}
</style>
