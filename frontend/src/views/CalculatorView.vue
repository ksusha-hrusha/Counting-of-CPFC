<template>
  <div>
    <h1 class="section-title">Калькулятор КБЖУ</h1>
    <div class="calc-layout">
      <!-- Форма -->
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

      <!-- Результат -->
      <div v-if="result" class="card">
        <h3 style="margin-bottom:14px; color:var(--text-dark);">Результат</h3>
        <NutritionBox :n="result" :label="`на ${result.weight_cooked}г готового`" />
        <button v-if="auth.isLoggedIn" class="btn btn-outline" style="width:100%; margin-top:14px;" @click="goCreate">
          <PlusIcon style="width:16px;height:16px;" /> Добавить в блюдо
        </button>
      </div>
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
const product = ref(null)
const weight = ref(100)
const cookingMethodId = ref('')
const result = ref(null)

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
</script>

<style scoped>
.calc-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 700px) { .calc-layout { grid-template-columns: 1fr; } }
.field { margin-bottom: 14px; }
.field label { display: block; font-size: 13px; color: #555; margin-bottom: 5px; }
.product-info { display: flex; justify-content: space-between; font-size: 13px; background: var(--bg-soft); border-radius: 6px; padding: 8px 12px; margin-bottom: 14px; }
.muted { color: #888; }
</style>
