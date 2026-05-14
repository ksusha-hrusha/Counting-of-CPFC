<template>
  <div class="nutrition-box">
    <div style="text-align:center; margin-bottom:10px;">
      <span class="kcal">{{ n.calories }}</span>
      <span style="font-size:14px; color:#555;"> ккал</span>
      <div v-if="label" style="font-size:12px; color:#666; margin-top:2px;">{{ label }}</div>
    </div>
    <div class="nutrition-row"><span>Белки</span><span class="val">{{ n.protein }} г</span></div>
    <div class="nutrition-row"><span>Жиры</span><span class="val">{{ n.fat }} г</span></div>
    <div class="nutrition-row"><span>Углеводы</span><span class="val">{{ n.carbs }} г</span></div>
    <div v-if="n.weight_cooked !== undefined" class="nutrition-row">
      <span>Вес готового</span><span class="val">{{ n.weight_cooked }} г</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  n: { type: Object, required: true },
  label: { type: String, default: '' }
})
</script>
