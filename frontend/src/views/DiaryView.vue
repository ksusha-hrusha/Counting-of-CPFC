<template>
  <div class="diary-wrap">
    <h1 class="section-title">Дневник питания</h1>

    <!-- Переключатель вкладок -->
    <div class="tabs">
      <button :class="['tab', tab === 'diary' && 'active']" @click="tab = 'diary'">Дневник</button>
      <button :class="['tab', tab === 'bmi' && 'active']" @click="tab = 'bmi'">ИМТ и норма</button>
    </div>

    <!-- ВКЛАДКА ДНЕВНИК -->
    <div v-if="tab === 'diary'">
      <!-- Дата -->
      <div class="date-row card">
        <button class="nav-btn" @click="shiftDate(-1)">◀</button>
        <input type="date" class="input date-input" v-model="currentDate" @change="load" />
        <button class="nav-btn" @click="shiftDate(1)">▶</button>
        <button class="btn btn-outline btn-sm" @click="setToday">Сегодня</button>
      </div>

      <!-- Итоги дня -->
      <div class="totals card" v-if="target">
        <h3 class="totals-title">Итого за день</h3>
        <div class="totals-grid">
          <div class="ring">
            <div class="ring-val">{{ Math.round(totals.calories) }}</div>
            <div class="ring-label">ккал</div>
            <div class="ring-of">из {{ target.calories }}</div>
            <div class="progress">
              <div class="progress-bar" :style="{ width: pct(totals.calories, target.calories) + '%' }" />
            </div>
          </div>
          <div class="ring">
            <div class="ring-val">{{ totals.protein.toFixed(1) }}г</div>
            <div class="ring-label">белки</div>
            <div class="ring-of">из {{ target.protein }}г</div>
            <div class="progress">
              <div class="progress-bar p" :style="{ width: pct(totals.protein, target.protein) + '%' }" />
            </div>
          </div>
          <div class="ring">
            <div class="ring-val">{{ totals.fat.toFixed(1) }}г</div>
            <div class="ring-label">жиры</div>
            <div class="ring-of">из {{ target.fat }}г</div>
            <div class="progress">
              <div class="progress-bar f" :style="{ width: pct(totals.fat, target.fat) + '%' }" />
            </div>
          </div>
          <div class="ring">
            <div class="ring-val">{{ totals.carbs.toFixed(1) }}г</div>
            <div class="ring-label">углеводы</div>
            <div class="ring-of">из {{ target.carbs }}г</div>
            <div class="progress">
              <div class="progress-bar c" :style="{ width: pct(totals.carbs, target.carbs) + '%' }" />
            </div>
          </div>
        </div>
      </div>

      <div class="totals card" v-else>
        <h3 class="totals-title">Итого за день</h3>
        <div class="simple-totals">
          <div><b>{{ Math.round(totals.calories) }}</b> ккал</div>
          <div><b>{{ totals.protein.toFixed(1) }}</b>г белков</div>
          <div><b>{{ totals.fat.toFixed(1) }}</b>г жиров</div>
          <div><b>{{ totals.carbs.toFixed(1) }}</b>г углеводов</div>
        </div>
        <p class="hint">Перейдите на вкладку «ИМТ и норма», чтобы увидеть прогресс относительно дневной нормы.</p>
      </div>

      <!-- Приёмы пищи -->
      <div v-for="type in mealTypes" :key="type.key" class="meal-block card">
        <div class="meal-head">
          <span class="meal-title">{{ type.label }}</span>
          <button class="btn btn-primary btn-sm" @click="openAdd(type.key)">+ Добавить</button>
        </div>
        <div v-if="mealsByType(type.key).length === 0" class="meal-empty">Ничего не добавлено</div>
        <div v-else class="meal-list">
          <div v-for="m in mealsByType(type.key)" :key="m.id" class="meal-row">
            <div class="meal-info">
              <span class="meal-name">{{ m.label }}</span>
              <span class="meal-amt">{{ formatAmount(m) }}</span>
            </div>
            <div class="meal-nutr">
              <span>{{ Math.round(m.calories) }} ккал</span>
              <span>Б {{ m.protein.toFixed(1) }}</span>
              <span>Ж {{ m.fat.toFixed(1) }}</span>
              <span>У {{ m.carbs.toFixed(1) }}</span>
            </div>
            <button class="btn-del" @click="removeMeal(m.id)" title="Удалить">×</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ВКЛАДКА ИМТ -->
    <div v-if="tab === 'bmi'">
      <div class="card">
        <h3 class="totals-title">Параметры</h3>
        <div class="bmi-grid">
          <div class="field">
            <label>Вес (кг)</label>
            <input class="input" type="number" v-model.number="form.weight_kg" min="20" step="0.1" />
          </div>
          <div class="field">
            <label>Рост (см)</label>
            <input class="input" type="number" v-model.number="form.height_cm" min="50" step="1" />
          </div>
          <div class="field">
            <label>Возраст</label>
            <input class="input" type="number" v-model.number="form.age" min="1" step="1" />
          </div>
          <div class="field">
            <label>Пол</label>
            <select class="input" v-model="form.sex">
              <option value="female">Женский</option>
              <option value="male">Мужской</option>
            </select>
          </div>
          <div class="field">
            <label>Активность</label>
            <select class="input" v-model.number="form.activity">
              <option :value="1.2">Минимальная (сидячая)</option>
              <option :value="1.375">Лёгкая (1-3 тренировки/нед)</option>
              <option :value="1.55">Средняя (3-5 тренировок/нед)</option>
              <option :value="1.725">Высокая (6-7 тренировок/нед)</option>
              <option :value="1.9">Очень высокая</option>
            </select>
          </div>
          <div class="field">
            <label>Цель</label>
            <select class="input" v-model="form.goal">
              <option value="lose">Похудение</option>
              <option value="maintain">Поддержание веса</option>
              <option value="gain">Набор массы</option>
            </select>
          </div>
        </div>
        <button class="btn btn-primary" style="width:100%; margin-top:8px;" @click="calcBmi">Рассчитать</button>
      </div>

      <div v-if="bmiResult" class="card bmi-result">
        <h3 class="totals-title">Результат</h3>
        <div class="bmi-summary">
          <div class="bmi-main">
            <div class="bmi-val">{{ bmiResult.bmi }}</div>
            <div class="bmi-cls">{{ bmiResult.bmi_class }}</div>
          </div>
          <div class="bmi-extra">
            <div><span class="muted">Идеальный вес:</span> <b>{{ bmiResult.ideal_weight }} кг</b></div>
            <div><span class="muted">Базовый обмен:</span> <b>{{ bmiResult.bmr }} ккал</b></div>
            <div><span class="muted">Расход с активностью:</span> <b>{{ bmiResult.tdee }} ккал</b></div>
          </div>
        </div>

        <h4 class="subhead">Дневная норма для цели «{{ goalLabel(bmiResult.goal) }}»</h4>
        <div class="target-grid">
          <div class="t-card">
            <div class="t-val">{{ bmiResult.target.calories }}</div>
            <div class="t-lab">ккал</div>
          </div>
          <div class="t-card">
            <div class="t-val">{{ bmiResult.target.protein }}г</div>
            <div class="t-lab">белки</div>
          </div>
          <div class="t-card">
            <div class="t-val">{{ bmiResult.target.fat }}г</div>
            <div class="t-lab">жиры</div>
          </div>
          <div class="t-card">
            <div class="t-val">{{ bmiResult.target.carbs }}г</div>
            <div class="t-lab">углеводы</div>
          </div>
        </div>
        <p class="hint" style="margin-top:12px;">Норма сохранена — на вкладке «Дневник» будет показан прогресс.</p>
      </div>
    </div>

    <!-- МОДАЛКА ДОБАВЛЕНИЯ -->
    <div v-if="addOpen" class="modal-bg" @click.self="addOpen = false">
      <div class="modal">
        <h3 class="modal-title">Добавить: {{ mealTypeLabel(addType) }}</h3>

        <div class="src-tabs">
          <button :class="['src-tab', src === 'dish' && 'active']" @click="src = 'dish'">Моё блюдо</button>
          <button :class="['src-tab', src === 'product' && 'active']" @click="src = 'product'">Продукт</button>
        </div>

        <div v-if="src === 'dish'">
          <div v-if="userDishes.length === 0" class="empty-hint">Блюд пока нет. <RouterLink to="/dishes/new">Создать</RouterLink></div>
          <div v-else class="field">
            <label>Блюдо</label>
            <select class="input" v-model="addForm.dish_id">
              <option value="">— выберите —</option>
              <option v-for="d in userDishes" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>
          <div class="field">
            <label>Порций</label>
            <input class="input" type="number" min="0.1" step="0.1" v-model.number="addForm.amount" />
          </div>
        </div>

        <div v-else>
          <div class="field">
            <label>Продукт</label>
            <ProductSearch @select="onProductSelect" />
            <div v-if="selectedProduct" class="selected-prod">{{ selectedProduct.name }}</div>
          </div>
          <div class="field">
            <label>{{ selectedProduct?.unit === 'pcs' ? 'Количество (шт)' : 'Вес (г)' }}</label>
            <input class="input" type="number" min="1" step="1" v-model.number="addForm.amount" />
          </div>
          <div class="field">
            <label>Термообработка</label>
            <CookingMethodSelect v-model="addForm.cooking_method_id" />
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn btn-outline" @click="addOpen = false">Отмена</button>
          <button class="btn btn-primary" @click="submitAdd" :disabled="submitting">
            {{ submitting ? 'Сохраняю...' : 'Добавить' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/api'
import ProductSearch from '@/components/ProductSearch.vue'
import CookingMethodSelect from '@/components/CookingMethodSelect.vue'

const TARGET_KEY = 'nutricale_target'
const FORM_KEY = 'nutricale_bmi_form'

const tab = ref('diary')

const mealTypes = [
  { key: 'breakfast', label: 'Завтрак' },
  { key: 'lunch', label: 'Обед' },
  { key: 'dinner', label: 'Ужин' },
  { key: 'snack', label: 'Перекусы' },
]

const currentDate = ref(todayStr())
const meals = ref([])
const totals = reactive({ calories: 0, protein: 0, fat: 0, carbs: 0 })
const userDishes = ref([])

const addOpen = ref(false)
const addType = ref('snack')
const src = ref('dish')
const submitting = ref(false)
const addForm = reactive({ dish_id: '', product_id: '', amount: 100, cooking_method_id: '' })
const selectedProduct = ref(null)

const form = reactive(loadForm())
const bmiResult = ref(null)
const target = ref(loadTarget())

function todayStr() {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

function loadForm() {
  try {
    const raw = localStorage.getItem(FORM_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return { weight_kg: 60, height_cm: 170, age: 25, sex: 'female', activity: 1.375, goal: 'maintain' }
}

function loadTarget() {
  try {
    const raw = localStorage.getItem(TARGET_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return null
}

function setToday() { currentDate.value = todayStr(); load() }

function shiftDate(days) {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + days)
  currentDate.value = d.toISOString().slice(0, 10)
  load()
}

async function load() {
  try {
    const { data } = await api.get('/diary/', { params: { date: currentDate.value } })
    meals.value = data.meals
    totals.calories = data.totals.calories
    totals.protein = data.totals.protein
    totals.fat = data.totals.fat
    totals.carbs = data.totals.carbs
  } catch {}
}

async function loadDishes() {
  try {
    const { data } = await api.get('/dishes/')
    userDishes.value = data
  } catch {}
}

function mealsByType(key) {
  return meals.value.filter(m => m.meal_type === key)
}

function formatAmount(m) {
  if (m.dish_id) return `${m.amount} порц.`
  return `${m.amount} г/шт`
}

function mealTypeLabel(k) {
  return mealTypes.find(t => t.key === k)?.label || ''
}

function openAdd(type) {
  addType.value = type
  src.value = 'dish'
  addForm.dish_id = ''
  addForm.product_id = ''
  addForm.amount = 1
  addForm.cooking_method_id = ''
  selectedProduct.value = null
  addOpen.value = true
}

function onProductSelect(p) {
  selectedProduct.value = p
  addForm.product_id = p.id
  addForm.amount = p.unit === 'pcs' ? 1 : 100
}

async function submitAdd() {
  submitting.value = true
  try {
    const payload = {
      date: currentDate.value,
      meal_type: addType.value,
      amount: addForm.amount,
    }
    if (src.value === 'dish') {
      if (!addForm.dish_id) { alert('Выберите блюдо'); submitting.value = false; return }
      payload.dish_id = addForm.dish_id
    } else {
      if (!addForm.product_id) { alert('Выберите продукт'); submitting.value = false; return }
      payload.product_id = addForm.product_id
      if (addForm.cooking_method_id) payload.cooking_method_id = addForm.cooking_method_id
    }
    await api.post('/diary/', payload)
    addOpen.value = false
    await load()
  } catch (e) {
    alert(e.response?.data?.error || 'Ошибка')
  } finally {
    submitting.value = false
  }
}

async function removeMeal(id) {
  if (!confirm('Удалить запись?')) return
  await api.delete(`/diary/${id}`)
  await load()
}

async function calcBmi() {
  try {
    const { data } = await api.post('/diary/bmi', form)
    bmiResult.value = data
    target.value = data.target
    localStorage.setItem(TARGET_KEY, JSON.stringify(data.target))
    localStorage.setItem(FORM_KEY, JSON.stringify(form))
  } catch (e) {
    alert(e.response?.data?.error || 'Ошибка расчёта')
  }
}

function goalLabel(g) {
  return { lose: 'Похудение', gain: 'Набор массы', maintain: 'Поддержание веса' }[g] || g
}

function pct(v, max) {
  if (!max) return 0
  return Math.min(100, Math.round((v / max) * 100))
}

onMounted(() => {
  load()
  loadDishes()
})
</script>

<style scoped>
.diary-wrap { max-width: 820px; margin: 0 auto; }

.tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.tab {
  flex: 1; padding: 10px 0;
  border: 1.5px solid var(--border); border-radius: 8px;
  background: var(--bg-soft); color: var(--text-dark);
  font-size: 14px; font-weight: 500; cursor: pointer; transition: all .15s;
}
.tab.active { background: var(--primary); color: #fff; border-color: var(--primary); }

.date-row { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; }
.date-input { max-width: 180px; }
.nav-btn {
  background: var(--bg-soft); border: 1px solid var(--border); border-radius: 8px;
  width: 36px; height: 36px; cursor: pointer; font-size: 14px;
}
.nav-btn:hover { background: var(--bg-accent); }

.totals { margin-bottom: 20px; }
.totals-title { font-size: 16px; color: var(--text-dark); margin-bottom: 12px; }
.totals-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.ring {
  background: var(--bg-accent); border-radius: 10px; padding: 12px; text-align: center;
  display: flex; flex-direction: column; gap: 4px;
}
.ring-val { font-size: 20px; font-weight: 700; color: var(--primary); }
.ring-label { font-size: 12px; color: #777; }
.ring-of { font-size: 11px; color: #999; }
.progress {
  width: 100%; height: 6px; background: rgba(0,0,0,.07);
  border-radius: 3px; margin-top: 4px; overflow: hidden;
}
.progress-bar { height: 100%; background: var(--primary); transition: width .3s; }
.progress-bar.p { background: #e67e22; }
.progress-bar.f { background: #f1c40f; }
.progress-bar.c { background: #3498db; }

.simple-totals { display: flex; gap: 20px; flex-wrap: wrap; font-size: 14px; color: var(--text-dark); }
.simple-totals b { color: var(--primary); font-size: 17px; }
.hint { font-size: 12px; color: #999; margin-top: 8px; }

.meal-block { margin-bottom: 14px; }
.meal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.meal-title { font-size: 15px; font-weight: 700; color: var(--text-dark); }
.meal-empty { font-size: 13px; color: #aaa; padding: 4px 0; }
.meal-list { display: flex; flex-direction: column; gap: 6px; }
.meal-row {
  display: flex; align-items: center; gap: 12px;
  padding: 8px 10px; border-radius: 8px; background: var(--bg-soft);
}
.meal-info { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.meal-name { font-size: 14px; font-weight: 600; color: var(--text-dark); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.meal-amt { font-size: 11px; color: #888; }
.meal-nutr { display: flex; gap: 10px; font-size: 12px; color: #666; flex-wrap: wrap; }
.meal-nutr span:first-child { color: var(--primary); font-weight: 600; }
.btn-del {
  background: transparent; border: none; cursor: pointer;
  color: #c0392b; font-size: 20px; width: 28px; height: 28px;
  border-radius: 6px;
}
.btn-del:hover { background: rgba(192, 57, 43, .1); }

/* BMI */
.bmi-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 8px;
}
.field label { display: block; font-size: 13px; color: #555; margin-bottom: 5px; }
.bmi-result { margin-top: 16px; }
.bmi-summary { display: flex; gap: 24px; flex-wrap: wrap; margin-bottom: 16px; }
.bmi-main {
  background: var(--bg-accent); padding: 16px 20px; border-radius: 10px;
  text-align: center; min-width: 140px;
}
.bmi-val { font-size: 32px; font-weight: 700; color: var(--primary); }
.bmi-cls { font-size: 13px; color: var(--text-dark); font-weight: 600; margin-top: 2px; }
.bmi-extra { display: flex; flex-direction: column; gap: 6px; font-size: 14px; justify-content: center; }
.muted { color: #999; }
.subhead { font-size: 14px; font-weight: 700; color: var(--text-dark); margin-bottom: 10px; }
.target-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.t-card {
  background: var(--bg-accent); border-radius: 10px; padding: 14px;
  text-align: center;
}
.t-val { font-size: 22px; font-weight: 700; color: var(--primary); }
.t-lab { font-size: 12px; color: #777; margin-top: 2px; }

/* Modal */
.modal-bg {
  position: fixed; inset: 0; background: rgba(0,0,0,.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 16px;
}
.modal {
  background: var(--bg-soft); border-radius: 12px; padding: 20px;
  max-width: 460px; width: 100%; max-height: 90vh; overflow: auto;
}
.modal-title { font-size: 17px; font-weight: 700; color: var(--text-dark); margin-bottom: 14px; }
.src-tabs { display: flex; gap: 6px; margin-bottom: 12px; }
.src-tab {
  flex: 1; padding: 8px 0; border: 1.5px solid var(--border); border-radius: 8px;
  background: transparent; color: var(--text-dark); font-size: 13px; cursor: pointer;
}
.src-tab.active { background: var(--primary); color: #fff; border-color: var(--primary); }
.selected-prod {
  background: var(--bg-accent); padding: 6px 10px; border-radius: 6px;
  font-size: 13px; margin-top: 6px;
}
.empty-hint { font-size: 13px; color: #888; padding: 12px 0; text-align: center; }
.empty-hint a { color: var(--primary); font-weight: 600; }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 16px; }

@media (max-width: 640px) {
  .totals-grid { grid-template-columns: repeat(2, 1fr); }
  .target-grid { grid-template-columns: repeat(2, 1fr); }
  .bmi-grid { grid-template-columns: 1fr; }
  .meal-row { flex-wrap: wrap; }
  .meal-nutr { width: 100%; }
}
</style>
