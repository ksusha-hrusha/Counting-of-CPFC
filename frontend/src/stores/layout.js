import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useLayoutStore = defineStore('layout', () => {
  // 'auto' | 'mobile' | 'desktop'
  const mode = ref(localStorage.getItem('layoutMode') || 'auto')

  watch(mode, (val) => {
    localStorage.setItem('layoutMode', val)
    applyMode(val)
  }, { immediate: true })

  function applyMode(val) {
    const html = document.documentElement
    html.classList.remove('force-mobile', 'force-desktop')
    if (val === 'mobile') html.classList.add('force-mobile')
    if (val === 'desktop') html.classList.add('force-desktop')
  }

  function setMode(val) { mode.value = val }

  return { mode, setMode }
})
