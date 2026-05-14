<template>
  <div class="avatar-wrap" :style="{ width: size + 'px', height: size + 'px' }">
    <img v-if="src && !failed" :src="src" class="avatar-img" :alt="username" @error="onError" />
    <div v-else class="avatar-initials" :style="{ fontSize: size * 0.35 + 'px' }">
      {{ initials }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  src: { type: String, default: null },
  username: { type: String, default: '' },
  size: { type: Number, default: 40 },
})

const failed = ref(false)
const initials = computed(() =>
  props.username.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || '?'
)
function onError() { failed.value = true }
</script>

<style scoped>
.avatar-wrap {
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid var(--border);
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-initials {
  width: 100%; height: 100%;
  background: var(--bg-accent);
  color: var(--primary);
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
</style>
