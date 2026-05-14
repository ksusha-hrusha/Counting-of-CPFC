<template>
  <div class="search-wrap">
    <input
      class="input"
      ref="inputRef"
      :value="query"
      @input="onInput"
      :placeholder="placeholder"
      autocomplete="off"
    />
    <MagnifyingGlassIcon class="search-icon" />
    <div v-if="results.length" class="dropdown">
      <div
        v-for="p in results"
        :key="p.id"
        class="dropdown-item"
        @mousedown.prevent="select(p)"
      >
        <span class="name">{{ p.name }}</span>
        <span class="kcal">{{ p.calories }} ккал/100г</span>
      </div>
      <div class="dropdown-item add-custom" @mousedown.prevent="openModal">
        <PlusCircleIcon class="add-icon" />
        <span>Добавить свой продукт</span>
      </div>
    </div>
    <div v-if="loading" class="dropdown"><div class="dropdown-item muted">Поиск...</div></div>
    <div v-if="noResults" class="dropdown">
      <div class="dropdown-item muted">Ничего не найдено</div>
      <div class="dropdown-item add-custom" @mousedown.prevent="openModal">
        <PlusCircleIcon class="add-icon" />
        <span>Добавить свой продукт «{{ query }}»</span>
      </div>
    </div>

    <CustomProductModal
      v-if="showModal"
      :initialName="query"
      @close="showModal = false"
      @select="onCustomSelect"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { MagnifyingGlassIcon, PlusCircleIcon } from '@heroicons/vue/24/outline'
import api from '@/api'
import CustomProductModal from '@/components/CustomProductModal.vue'

const props = defineProps({
  placeholder: { default: 'Найти продукт...' },
})
const emit = defineEmits(['select'])

const query = ref('')
const results = ref([])
const loading = ref(false)
const noResults = ref(false)
const showModal = ref(false)
const inputRef = ref(null)
let timer = null

function onInput(e) {
  query.value = e.target.value
  clearTimeout(timer)
  results.value = []
  noResults.value = false
  if (query.value.length < 2) return
  loading.value = true
  timer = setTimeout(async () => {
    try {
      const { data } = await api.get('/products/', { params: { q: query.value } })
      results.value = data
      noResults.value = data.length === 0
    } finally {
      loading.value = false
    }
  }, 400)
}

function select(p) {
  results.value = []
  noResults.value = false
  emit('select', p)
}

function clear() {
  query.value = ''
  if (inputRef.value) inputRef.value.value = ''
  results.value = []
  noResults.value = false
}

function openModal() {
  results.value = []
  noResults.value = false
  showModal.value = true
}

function onCustomSelect(p) {
  emit('select', p)
}

defineExpose({ clear })
</script>

<style scoped>
.search-wrap { position: relative; }
.search-icon {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  width: 16px; height: 16px; color: #aaa; pointer-events: none;
}
.dropdown {
  position: absolute; top: 100%; left: 0; right: 0; z-index: 50;
  background: #fff; border: 1.5px solid var(--border);
  border-top: none; border-radius: 0 0 8px 8px;
  max-height: 280px; overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0,0,0,.1);
}
.dropdown-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 14px; cursor: pointer; font-size: 13px;
  transition: background .1s;
}
.dropdown-item:hover { background: var(--bg-soft); }
.kcal { color: var(--primary); font-weight: 600; font-size: 12px; }
.muted { color: #aaa; cursor: default; }
.add-custom {
  border-top: 1px solid var(--border);
  color: var(--primary); font-weight: 600;
  gap: 8px; justify-content: flex-start;
}
.add-custom:hover { background: var(--bg-accent); }
.add-icon { width: 16px; height: 16px; flex-shrink: 0; }
</style>
