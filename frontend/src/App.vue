<template>
  <AppHeader />
  <main class="container" style="padding-top:24px; padding-bottom:40px;">
    <RouterView />
  </main>
</template>

<script setup>
import AppHeader from '@/components/AppHeader.vue'
import { useThemeStore } from '@/stores/theme'
import { useLayoutStore } from '@/stores/layout'
useThemeStore()
useLayoutStore()
</script>
