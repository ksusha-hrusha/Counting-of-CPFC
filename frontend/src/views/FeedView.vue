<template>
  <div class="feed-wrap">
    <h1 class="section-title">Лента блюд</h1>

    <div class="feed-search">
      <input class="input" v-model="search" @input="onSearch" placeholder="Поиск по ленте..." />
    </div>

    <div v-if="loading" class="empty">Загрузка...</div>
    <div v-else-if="dishes.length === 0" class="empty">Блюд пока нет</div>

    <div v-else class="feed">
      <div v-for="dish in dishes" :key="dish.id" class="post card">

        <!-- Шапка поста: автор -->
        <div class="post-header">
          <UserAvatar
            :src="dish.author?.avatar"
            :username="dish.author?.username || '?'"
            :size="42"
          />
          <div class="post-author">
            <span class="author-name">{{ dish.author?.username || 'Аноним' }}</span>
            <span class="post-date">{{ formatDate(dish.created_at) }}</span>
          </div>
          <span class="badge badge-pub" style="margin-left:auto;">Публичное</span>
        </div>

        <!-- Название блюда -->
        <h3 class="post-title">{{ dish.name }}</h3>
        <p v-if="dish.description" class="post-desc">{{ dish.description }}</p>

        <!-- КБЖУ -->
        <div v-if="dish.nutrition" class="nutrition-strip">
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
          <div class="nutr-divider" />
          <div class="nutr-item">
            <span class="nutr-val">{{ dish.nutrition.weight_cooked }}г</span>
            <span class="nutr-label">вес</span>
          </div>
        </div>

        <!-- На 100г -->
        <div v-if="dish.nutrition?.per_100g" class="per100">
          На 100г: {{ dish.nutrition.per_100g.calories }} ккал ·
          Б {{ dish.nutrition.per_100g.protein }}г ·
          Ж {{ dish.nutrition.per_100g.fat }}г ·
          У {{ dish.nutrition.per_100g.carbs }}г
        </div>

        <!-- Ингредиенты (сворачиваемые) -->
        <div class="ingredients-toggle" @click="toggleIngredients(dish.id)">
          <span>{{ dish.ingredients.length }} ингредиентов</span>
          <ChevronDownIcon v-if="!expanded.has(dish.id)" style="width:16px;height:16px;" />
          <ChevronUpIcon v-else style="width:16px;height:16px;" />
        </div>
        <div v-if="expanded.has(dish.id)" class="ingredients-list">
          <div v-for="ing in dish.ingredients" :key="ing.id" class="ing-row">
            <span>{{ ing.label }}</span>
            <span class="ing-meta">{{ ing.weight_raw }}г<span v-if="ing.cooking_method_name"> · {{ ing.cooking_method_name }}</span></span>
          </div>
        </div>

        <!-- Действия -->
        <div class="post-actions">
          <button
            v-if="auth.isLoggedIn"
            class="btn btn-primary btn-sm"
            @click="copy(dish.id)"
            :disabled="copying === dish.id"
          >
            {{ copying === dish.id ? 'Копирую...' : 'Скопировать в профиль' }}
          </button>
          <RouterLink v-else to="/auth" class="btn btn-outline btn-sm">
            Войти чтобы скопировать
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Загрузить ещё -->
    <div v-if="hasMore && !loading" class="load-more">
      <button class="btn btn-outline" @click="loadMore" :disabled="loadingMore">
        {{ loadingMore ? 'Загрузка...' : 'Загрузить ещё' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/vue/24/outline'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import UserAvatar from '@/components/UserAvatar.vue'

const auth = useAuthStore()
const router = useRouter()

const dishes = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const search = ref('')
const copying = ref(null)
const expanded = reactive(new Set())
const page = ref(1)
const hasMore = ref(true)
const PAGE_SIZE = 10
let timer = null

async function load(reset = true) {
  if (reset) { page.value = 1; dishes.value = []; loading.value = true }
  else loadingMore.value = true

  try {
    const { data } = await api.get('/catalog/', {
      params: { q: search.value || undefined, page: page.value, per_page: PAGE_SIZE }
    })
    if (reset) dishes.value = data
    else dishes.value.push(...data)
    hasMore.value = data.length === PAGE_SIZE
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

onMounted(() => load())

function onSearch() {
  clearTimeout(timer)
  timer = setTimeout(() => load(true), 400)
}

async function loadMore() {
  page.value++
  await load(false)
}

function toggleIngredients(id) {
  if (expanded.has(id)) expanded.delete(id)
  else expanded.add(id)
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

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}
</script>

<style scoped>
.feed-wrap { max-width: 680px; margin: 0 auto; }
.feed-search { margin-bottom: 20px; }
.feed { display: flex; flex-direction: column; gap: 16px; }

.post { display: flex; flex-direction: column; gap: 12px; }

.post-header { display: flex; align-items: center; gap: 12px; }
.post-author { display: flex; flex-direction: column; gap: 2px; }
.author-name { font-size: 14px; font-weight: 700; color: var(--text-dark); }
.post-date { font-size: 11px; color: #aaa; }

.post-title { font-size: 18px; font-weight: 700; color: var(--text-dark); }
.post-desc { font-size: 13px; color: #666; line-height: 1.5; }

.nutrition-strip {
  display: flex; align-items: center; gap: 0;
  background: var(--bg-accent); border-radius: 10px;
  padding: 12px 16px; flex-wrap: wrap; gap: 8px;
}
.nutr-item { display: flex; flex-direction: column; align-items: center; flex: 1; min-width: 60px; }
.nutr-val { font-size: 18px; font-weight: 700; color: var(--primary); }
.nutr-label { font-size: 11px; color: #888; }
.nutr-divider { width: 1px; height: 32px; background: var(--border); }

.per100 { font-size: 12px; color: var(--text-mid); }

.ingredients-toggle {
  display: flex; align-items: center; justify-content: space-between;
  cursor: pointer; font-size: 13px; color: var(--primary); font-weight: 600;
  padding: 8px 0; border-top: 1px solid var(--border);
}
.ingredients-list { display: flex; flex-direction: column; gap: 4px; }
.ing-row {
  display: flex; justify-content: space-between;
  font-size: 13px; padding: 4px 0;
  border-bottom: 1px solid var(--border);
}
.ing-row:last-child { border-bottom: none; }
.ing-meta { color: #888; font-size: 12px; }

.post-actions { padding-top: 4px; border-top: 1px solid var(--border); }

.load-more { text-align: center; margin-top: 24px; }
.empty { text-align: center; color: #aaa; padding: 40px 0; }

@media (max-width: 640px) {
  .nutr-divider { display: none; }
  .nutr-item { min-width: 50px; }
}
</style>
