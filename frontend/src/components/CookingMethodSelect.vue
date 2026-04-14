<template>
  <select class="input" :value="modelValue" @change="$emit('update:modelValue', $event.target.value)">
    <option value="">— без обработки —</option>
    <option v-for="m in methods" :key="m.id" :value="m.id">
      {{ m.name }} (×{{ m.weight_coefficient }})
    </option>
  </select>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

defineProps({ modelValue: String })
defineEmits(['update:modelValue'])

const methods = ref([])
onMounted(async () => {
  const { data } = await api.get('/products/cooking-methods')
  methods.value = data
})
</script>
