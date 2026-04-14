<template>
  <div>
    <h1 class="section-title">{{ isEdit ? 'Редактировать блюдо' : 'Новое блюдо' }}</h1>
    <div class="form-layout">
      <!-- Левая колонка: форма -->
      <div class="left">
        <div class="card" style="margin-bottom:20px;">
          <div class="field"><label>Название</label>
            <input class="input" v-model="form.name" placeholder="Куриный суп" />
          </div>
          <div class="field"><label>Описание</label>
            <textarea class="input" v-model="form.description" rows="2" placeholder="Необязательно" />
          </div>
          <div class="row2">
            <div class="field"><label>Категория</label>
              <select class="input" v-model="form.category">
                <option value="">— выбрать —</option>
                <option v-for="c in categories" :key="c">{{ c }}</option>
              </select>
            </div>
            <div class="field"><label>Порций</label>
              <input class="input" v-model.number="form.servings" type="number" min="1" />
            </div>
          </div>
          <div class="field">
            <label>Термообработка на всё блюдо</label>
            <CookingMethodSelect v-model="form.cooking_method_id" />
          </div>
          <label class="toggle-wrap">
            <span class="toggle">
              <input type="checkbox" v-model="form.is_public" />
              <span class="toggle-slider"></span>
            </span>
            Опубликовать в каталог
          </label>
        </div>

        <!-- Ингредиенты -->
        <div class="card">
          <h3 class="section-title" style="font-size:16px;">Ингредиенты</h3>

          <!-- Добавить продукт -->
          <div class="add-ing">
            <ProductSearch placeholder="Найти продукт..." @select="onProductSelect" />
            <div v-if="newIng.product" class="ing-params">
              <div class="row2">
                <div class="field">
                  <label>{{ newIng.product?.unit === 'pcs' ? 'Количество (шт)' : 'Вес (г)' }}</label>
                  <input class="input" v-model.number="newIng.weight_raw" type="number" min="1" />
                </div>
                <div class="field"><label>Термообработка</label>
                  <CookingMethodSelect v-model="newIng.cooking_method_id" />
                </div>
              </div>
              <button class="btn btn-primary btn-sm" @click="addIngredient">
                <PlusIcon style="width:14px;height:14px;" /> Добавить
              </button>
            </div>
          </div>

          <hr class="divider" />

          <!-- Список ингредиентов -->
          <div v-if="form.ingredients.length === 0" class="empty">Ингредиентов пока нет</div>
          <div v-for="(ing, i) in form.ingredients" :key="i" class="ing-row">
            <div class="ing-info">
              <span class="ing-name">{{ ing.label }}</span>
              <span class="ing-meta">{{ ing.weight_raw }}{{ ing.unit === 'pcs' ? ' шт' : 'г' }} · {{ ing.cooking_method_name || 'без обработки' }}</span>
            </div>
            <button class="btn btn-danger btn-sm" @click="removeIngredient(i)">
              <XMarkIcon style="width:14px;height:14px;" />
            </button>
          </div>
        </div>
      </div>

      <!-- Правая колонка: итог -->
      <div class="right">
        <div class="card sticky-card">
          <h3 style="margin-bottom:14px; color:var(--text-dark);">Пищевая ценность</h3>
          <div v-if="nutrition">
            <NutritionBox :n="nutrition" label="на всё блюдо" />
            <hr class="divider" />
            <NutritionBox :n="nutrition.per_100g" label="на 100г" />
            <div v-if="form.servings > 1" style="margin-top:12px;">
              <hr class="divider" />
              <NutritionBox :n="perServing" :label="`на 1 порцию (из ${form.servings})`" />
            </div>
          </div>
          <div v-else class="empty">Добавьте ингредиенты</div>

          <hr class="divider" />
          <div style="display:flex; gap:10px;">
            <button class="btn btn-outline" style="flex:1" @click="$router.back()">Отмена</button>
            <button class="btn btn-primary" style="flex:1" @click="save" :disabled="saving">
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
          <p v-if="error" class="error-msg">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { PlusIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import ProductSearch from '@/components/ProductSearch.vue'
import CookingMethodSelect from '@/components/CookingMethodSelect.vue'
import NutritionBox from '@/components/NutritionBox.vue'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const error = ref('')
const nutrition = ref(null)
const categories = ['Супы', 'Салаты', 'Основные блюда', 'Завтраки', 'Десерты', 'Напитки', 'Другое']

const form = reactive({
  name: '',
  description: '',
  category: '',
  servings: 1,
  is_public: false,
  cooking_method_id: '',
  ingredients: [],
})

const newIng = reactive({ product: null, weight_raw: 100, cooking_method_id: '' })

// Если пришли с калькулятора — предзаполняем
onMounted(async () => {
  if (isEdit.value) {
    const { data } = await api.get(`/dishes/${route.params.id}`)
    Object.assign(form, {
      name: data.name, description: data.description, category: data.category,
      servings: data.servings, is_public: data.is_public,
      cooking_method_id: data.cooking_method_id || '',
      ingredients: data.ingredients.map(i => ({
        product_id: i.ref_type === 'product' ? i.ref_id : null,
        nested_dish_id: i.ref_type === 'dish' ? i.ref_id : null,
        label: i.label,
        weight_raw: i.weight_raw,
        cooking_method_id: i.cooking_method_id || '',
        cooking_method_name: i.cooking_method_name,
      }))
    })
    nutrition.value = data.nutrition
  } else if (route.query.product_id) {
    // Предзаполнение из калькулятора
    const { data: p } = await api.get(`/products/${route.query.product_id}`)
    newIng.product = p
    newIng.weight_raw = Number(route.query.weight) || 100
    newIng.cooking_method_id = route.query.cooking_method_id || ''
  }
})

function onProductSelect(p) { newIng.product = p }

function addIngredient() {
  if (!newIng.product) return
  form.ingredients.push({
    product_id: newIng.product.id,
    nested_dish_id: null,
    label: newIng.product.name,
    weight_raw: newIng.weight_raw,
    unit: newIng.product.unit || 'g',
    cooking_method_id: newIng.cooking_method_id || null,
    cooking_method_name: null,
  })
  newIng.product = null
  newIng.weight_raw = 100
  newIng.cooking_method_id = ''
  recalc()
}

function removeIngredient(i) { form.ingredients.splice(i, 1); recalc() }

async function recalc() {
  if (!form.ingredients.length) { nutrition.value = null; return }
  try {
    const { data } = await api.post('/calculate/dish-preview', {
      ingredients: form.ingredients.map(i => ({
        product_id: i.product_id,
        weight_raw: i.weight_raw,
        cooking_method_id: i.cooking_method_id || null,
      })),
      cooking_method_id: form.cooking_method_id || null,
    })
    nutrition.value = data
  } catch {}
}

watch(() => form.cooking_method_id, recalc)
watch(() => form.ingredients.length, recalc)

const perServing = computed(() => {
  if (!nutrition.value || form.servings <= 1) return null
  const s = form.servings
  return {
    calories: round(nutrition.value.calories / s),
    protein: round(nutrition.value.protein / s),
    fat: round(nutrition.value.fat / s),
    carbs: round(nutrition.value.carbs / s),
  }
})

function round(v) { return Math.round(v * 10) / 10 }

async function save() {
  saving.value = true; error.value = ''
  try {
    const payload = {
      name: form.name,
      description: form.description,
      category: form.category,
      servings: form.servings,
      is_public: form.is_public,
      cooking_method_id: form.cooking_method_id || null,
      ingredients: form.ingredients.map(i => ({
        product_id: i.product_id || null,
        nested_dish_id: i.nested_dish_id || null,
        weight_raw: i.weight_raw,
        cooking_method_id: i.cooking_method_id || null,
      })),
    }
    let data
    if (isEdit.value) {
      ;({ data } = await api.put(`/dishes/${route.params.id}`, payload))
    } else {
      ;({ data } = await api.post('/dishes/', payload))
    }
    nutrition.value = data.nutrition
    router.push('/profile')
  } catch (e) {
    error.value = e.response?.data?.error || 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.form-layout { display: grid; grid-template-columns: 1fr 380px; gap: 24px; align-items: start; }
@media (max-width: 900px) { .form-layout { grid-template-columns: 1fr; } }
.field { margin-bottom: 14px; }
.field label { display: block; font-size: 13px; color: #555; margin-bottom: 5px; }
.row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.add-ing { margin-bottom: 14px; }
.ing-params { margin-top: 10px; }
.ing-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border); }
.ing-row:last-child { border-bottom: none; }
.ing-info { display: flex; flex-direction: column; gap: 2px; }
.ing-name { font-size: 13px; font-weight: 600; }
.ing-meta { font-size: 11px; color: #888; }
.empty { color: #aaa; font-size: 13px; text-align: center; padding: 20px 0; }
.sticky-card { position: sticky; top: 80px; }
</style>
