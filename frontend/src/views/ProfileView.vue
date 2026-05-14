<template>
  <div>
    <!-- Шапка профиля -->
    <div class="profile-header card">
      <!-- Аватарка с кнопкой загрузки -->
      <div class="avatar-section">
        <UserAvatar :src="avatarUrl" :username="auth.user?.username" :size="70" />
        <label class="avatar-upload-btn" title="Сменить аватар">
          <CameraIcon style="width:14px;height:14px;" />
          <input type="file" accept="image/*" @change="uploadAvatar" hidden />
        </label>
      </div>
      <div class="profile-info">
        <h2>{{ auth.user?.username }}</h2>
        <p>{{ auth.user?.email }}</p>
      </div>
      <div class="profile-stats">
        <div class="stat"><span class="stat-val">{{ dishes.length }}</span><span class="stat-label">блюд</span></div>
        <div class="stat"><span class="stat-val">{{ publicCount }}</span><span class="stat-label">публичных</span></div>
      </div>
      <RouterLink to="/dishes/new" class="btn btn-primary" style="margin-left:auto;">
        <PlusIcon style="width:16px;height:16px;" /> Новое блюдо
      </RouterLink>
    </div>

    <!-- Фильтр -->
    <div class="filter-bar">
      <input class="input" v-model="search" placeholder="Поиск по блюдам..." style="max-width:300px;" />
      <select class="input" v-model="filterPub" style="max-width:160px;">
        <option value="">Все</option>
        <option value="public">Публичные</option>
        <option value="private">Приватные</option>
      </select>
    </div>

    <!-- Список блюд -->
    <div v-if="loading" class="empty">Загрузка...</div>
    <div v-else-if="filtered.length === 0" class="empty">Блюд не найдено</div>
    <div v-else class="dishes-grid">
      <div v-for="dish in filtered" :key="dish.id" class="dish-card card">
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
          <span v-if="dish.cooking_method_name"> · {{ dish.cooking_method_name }}</span>
        </div>
        <div class="dish-actions">
          <RouterLink :to="`/dishes/${dish.id}/edit`" class="btn btn-outline btn-sm">
            <PencilSquareIcon style="width:14px;height:14px;" /> Редактировать
          </RouterLink>
          <button class="btn btn-outline btn-sm" @click="togglePublish(dish)">
            {{ dish.is_public ? 'Скрыть' : 'Опубликовать' }}
          </button>
          <button class="btn btn-danger btn-sm" @click="deleteDish(dish.id)">
            <TrashIcon style="width:14px;height:14px;" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { PlusIcon, PencilSquareIcon, TrashIcon, CameraIcon } from '@heroicons/vue/24/outline'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import UserAvatar from '@/components/UserAvatar.vue'

const auth = useAuthStore()
const dishes = ref([])
const loading = ref(true)
const search = ref('')
const filterPub = ref('')
const avatarUrl = ref(null)

const publicCount = computed(() => dishes.value.filter(d => d.is_public).length)

const filtered = computed(() => dishes.value.filter(d => {
  const matchSearch = d.name.toLowerCase().includes(search.value.toLowerCase())
  const matchPub = !filterPub.value ||
    (filterPub.value === 'public' && d.is_public) ||
    (filterPub.value === 'private' && !d.is_public)
  return matchSearch && matchPub
}))

onMounted(async () => {
  const { data } = await api.get('/dishes/')
  dishes.value = data
  loading.value = false
  // Загружаем данные профиля с аватаркой
  try {
    const { data: me } = await api.get('/users/me')
    if (me.avatar) avatarUrl.value = me.avatar + '?t=' + Date.now()
  } catch {}
})

async function uploadAvatar(e) {
  const file = e.target.files[0]
  if (!file) return
  const form = new FormData()
  form.append('avatar', file)
  try {
    const { data } = await api.post('/users/me/avatar', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    avatarUrl.value = data.avatar + '?t=' + Date.now()
  } catch (err) {
    alert(err.response?.data?.error || 'Ошибка загрузки')
  }
}

async function togglePublish(dish) {
  const { data } = await api.post(`/dishes/${dish.id}/publish`)
  dish.is_public = data.is_public
}

async function deleteDish(id) {
  if (!confirm('Удалить блюдо?')) return
  await api.delete(`/dishes/${id}`)
  dishes.value = dishes.value.filter(d => d.id !== id)
}
</script>

<style scoped>
.profile-header { display: flex; align-items: center; gap: 20px; margin-bottom: 24px; flex-wrap: wrap; }
.avatar-section { position: relative; flex-shrink: 0; }
.avatar-upload-btn {
  position: absolute; bottom: 0; right: 0;
  background: var(--primary); color: #fff;
  border-radius: 50%; width: 22px; height: 22px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; border: 2px solid #fff;
}
.profile-info h2 { font-size: 20px; color: var(--text-dark); }
.profile-info p { font-size: 13px; color: #888; }
.profile-stats { display: flex; gap: 20px; }
.stat { display: flex; flex-direction: column; align-items: center; }
.stat-val { font-size: 22px; font-weight: 700; color: var(--primary); }
.stat-label { font-size: 11px; color: #888; }
.filter-bar { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.dishes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.dish-card { display: flex; flex-direction: column; gap: 8px; }
.dish-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
.dish-name { font-size: 15px; font-weight: 700; color: var(--text-dark); }
.dish-nutrition { display: flex; gap: 12px; font-size: 12px; color: var(--primary); font-weight: 600; flex-wrap: wrap; }
.dish-meta { font-size: 11px; color: #aaa; }
.dish-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px; }
.empty { text-align: center; color: #aaa; padding: 40px 0; font-size: 15px; }

@media (max-width: 640px) {
  .profile-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .profile-header .btn { width: 100%; margin-left: 0 !important; }
  .profile-stats { width: 100%; justify-content: space-around; }
  .filter-bar { flex-direction: column; }
  .filter-bar .input { max-width: 100% !important; }
  .dishes-grid { grid-template-columns: 1fr; }
  .dish-actions { flex-wrap: wrap; }
}
</style>
