<template>
  <div>
    <h1 class="section-title">Калькулятор КБЖУ</h1>

    <!-- Переключатель режимов -->
    <div class="mode-tabs">
      <button :class="['mode-tab', mode === 'single' && 'active']" @click="switchMode('single')">
        Продукт
      </button>
      <button :class="['mode-tab', mode === 'dish' && 'active']" @click="switchMode('dish')">
        Блюдо
      </button>
    </div>

    <!-- Режим: один ингредиент -->
    <div v-if="mode === 'single'" class="calc-layout">
      <div class="card">
        <div class="field">
          <label>Продукт</label>
          <ProductSearch @select="onProduct" />
        </div>
        <div v-if="product" class="product-info">
          <span>{{ product.name }}</span>
          <span class="muted">{{ product.calories }} ккал / 100г</span>
        </div>
        <div class="field">
          <label>Вес сырого (г)</label>
          <input class="input" v-model.number="weight" type="number" min="1" placeholder="200" />
        </div>
        <div class="field">
          <label>Термообработка</label>
          <CookingMethodSelect v-model="cookingMethodId" />
        </div>
        <button class="btn btn-primary" style="width:100%;" @click="calculate" :disabled="!product || !weight">
          Рассчитать
        </button>
      </div>

      <div v-if="result" class="card">
        <h3 style="margin-bottom:14px; color:var(--text-dark);">Результат</h3>
        <NutritionBox :n="result" :label="`на ${result.weight_cooked}г готового`" />
        <button v-if="auth.isLoggedIn" class="btn btn-outline" style="width:100%; margin-top:14px;" @click="goCreate">
          <PlusIcon style="width:16px;height:16px;" /> Добавить в блюдо
        </button>
      </div>
    </div>

    <!-- Режим: целое блюдо -->
    <div v-if="mode === 'dish'" class="dish-mode card">
      <p class="dish-hint">Создайте блюдо из нескольких ингредиентов и получите суммарное КБЖУ.</p>
      <button class="btn btn-primary" style="width:100%;" @click="goNewDish">
        <PlusIcon style="width:16px;height:16px;" /> Создать блюдо
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'
import ProductSearch from '@/components/ProductSearch.vue'
import CookingMethodSelect from '@/components/CookingMethodSelect.vue'
import NutritionBox from '@/components/NutritionBox.vue'

const auth = useAuthStore()
const router = useRouter()

const mode = ref('single')
const product = ref(null)
const weight = ref(100)
const cookingMethodId = ref('')
const result = ref(null)

function switchMode(m) {
  mode.value = m
  result.value = null
}

function onProduct(p) { product.value = p }

async function calculate() {
  const { data } = await api.post('/calculate/', {
    product_id: product.value.id,
    weight_raw: weight.value,
    cooking_method_id: cookingMethodId.value || null,
  })
  result.value = data
}

function goCreate() {
  router.push({
    path: '/dishes/new',
    query: {
      product_id: product.value.id,
      product_name: product.value.name,
      weight: weight.value,
      cooking_method_id: cookingMethodId.value || '',
    }
  })
}

function goNewDish() {
  router.push('/dishes/new')
}
</script>

<style scoped>
.mode-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}
.mode-tab {
  flex: 1;
  padding: 10px 0;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  background: var(--bg-soft);
  color: var(--text-dark);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all .15s;
}
.mode-tab.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}
.calc-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 700px) { .calc-layout { grid-template-columns: 1fr; } }
.field { margin-bottom: 14px; }
.field label { display: block; font-size: 13px; color: #555; margin-bottom: 5px; }
.product-info { display: flex; justify-content: space-between; font-size: 13px; background: var(--bg-soft); border-radius: 6px; padding: 8px 12px; margin-bottom: 14px; }
.muted { color: #888; }
.dish-mode { max-width: 480px; }
.dish-hint { font-size: 14px; color: #666; margin-bottom: 18px; line-height: 1.5; }
</style>
