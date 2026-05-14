import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref(localStorage.getItem('theme') || 'green')

  watch(theme, (val) => {
    localStorage.setItem('theme', val)
    document.documentElement.setAttribute('data-theme', val)
  }, { immediate: true })

  function toggle() {
    theme.value = theme.value === 'green' ? 'pink' : 'green'
  }

  return { theme, toggle }
})
