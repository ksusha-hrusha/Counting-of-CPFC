<template>
  <header class="header">
    <div class="container header-inner">
      <RouterLink to="/" class="logo">NutriCalc</RouterLink>

      <!-- Desktop nav -->
      <nav class="nav desktop-nav">
        <RouterLink to="/calculator">Калькулятор</RouterLink>
        <RouterLink v-if="auth.isLoggedIn" to="/diary">Дневник</RouterLink>
        <RouterLink to="/feed">Лента</RouterLink>
        <RouterLink to="/catalog">Каталог</RouterLink>
        <RouterLink v-if="auth.isLoggedIn" to="/profile">Профиль</RouterLink>
      </nav>

      <div class="header-actions">
        <button class="theme-btn" @click="themeStore.toggle()" :title="themeStore.theme === 'green' ? 'Розовая тема' : 'Зелёная тема'">
          <SparklesIcon v-if="themeStore.theme === 'green'" class="theme-icon" />
          <svg v-else class="theme-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 8C8 10 5.9 16.17 3.82 19.34M21 3C21 3 15 3 12 6c-3 3-3 9-3 9s6 0 9-3c3-3 3-9 3-9z"/>
          </svg>
        </button>
        <button class="layout-btn" @click="cycleLayout()" :title="`Режим: ${layoutLabels[layoutStore.mode]}`">
          <ComputerDesktopIcon v-if="layoutStore.mode === 'desktop'" class="theme-icon" />
          <DevicePhoneMobileIcon v-else-if="layoutStore.mode === 'mobile'" class="theme-icon" />
          <span v-else class="layout-auto">A</span>
        </button>
        <template v-if="auth.isLoggedIn">
          <span class="username desktop-only">{{ auth.user?.username }}</span>
          <button class="btn btn-outline btn-sm desktop-only" @click="auth.logout(); $router.push('/')">Выйти</button>
        </template>
        <template v-else>
          <RouterLink to="/auth" class="btn btn-primary btn-sm desktop-only">Войти</RouterLink>
        </template>
        <!-- Burger -->
        <button class="burger" @click="menuOpen = !menuOpen">
          <Bars3Icon v-if="!menuOpen" class="burger-icon" />
          <XMarkIcon v-else class="burger-icon" />
        </button>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-if="menuOpen" class="mobile-menu" @click.self="menuOpen = false">
      <nav class="mobile-nav">
        <RouterLink to="/" @click="menuOpen = false">Главная</RouterLink>
        <RouterLink to="/calculator" @click="menuOpen = false">Калькулятор</RouterLink>
        <RouterLink v-if="auth.isLoggedIn" to="/diary" @click="menuOpen = false">Дневник</RouterLink>
        <RouterLink to="/feed" @click="menuOpen = false">Лента</RouterLink>
        <RouterLink to="/catalog" @click="menuOpen = false">Каталог</RouterLink>
        <RouterLink v-if="auth.isLoggedIn" to="/profile" @click="menuOpen = false">Профиль</RouterLink>
        <hr class="mobile-divider" />
        <template v-if="auth.isLoggedIn">
          <span class="mobile-username">{{ auth.user?.username }}</span>
          <button class="btn btn-outline btn-sm" @click="auth.logout(); $router.push('/'); menuOpen = false">Выйти</button>
        </template>
        <template v-else>
          <RouterLink to="/auth" class="btn btn-primary" @click="menuOpen = false">Войти</RouterLink>
        </template>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { SparklesIcon, MoonIcon, Bars3Icon, XMarkIcon, ComputerDesktopIcon, DevicePhoneMobileIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useLayoutStore } from '@/stores/layout'

const auth = useAuthStore()
const themeStore = useThemeStore()
const layoutStore = useLayoutStore()
const menuOpen = ref(false)

function cycleLayout() {
  const modes = ['auto', 'desktop', 'mobile']
  const next = modes[(modes.indexOf(layoutStore.mode) + 1) % modes.length]
  layoutStore.setMode(next)
}

const layoutLabels = { auto: 'Авто', desktop: 'ПК', mobile: 'Моб.' }
</script>

<style scoped>
.header {
  background: var(--primary);
  position: sticky; top: 0; z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,.15);
}
.header-inner {
  display: flex; align-items: center; gap: 16px;
  height: 60px;
}
.logo { font-size: 22px; font-weight: 700; color: #fff; flex-shrink: 0; }
.nav { display: flex; gap: 16px; flex: 1; }
.nav a { color: rgba(255,255,255,.85); font-size: 14px; font-weight: 500; padding: 4px 8px; border-radius: 6px; transition: background .15s; }
.nav a:hover, .nav a.router-link-active { background: rgba(255,255,255,.15); color: #fff; }
.header-actions { display: flex; align-items: center; gap: 10px; margin-left: auto; }
.username { color: rgba(255,255,255,.9); font-size: 14px; }
.theme-btn {
  background: rgba(255,255,255,.15);
  border: none; border-radius: 8px;
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background .15s;
}
.theme-btn:hover { background: rgba(255,255,255,.25); }
.theme-icon { width: 20px; height: 20px; color: white; }
.layout-btn {
  background: rgba(255,255,255,.15);
  border: none; border-radius: 8px;
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background .15s;
}
.layout-btn:hover { background: rgba(255,255,255,.25); }
.layout-auto { color: white; font-size: 15px; font-weight: 700; }

/* Burger */
.burger {
  display: none;
  background: rgba(255,255,255,.15);
  border: none; border-radius: 8px;
  width: 36px; height: 36px;
  align-items: center; justify-content: center;
  cursor: pointer;
}
.burger-icon { width: 20px; height: 20px; color: white; }

/* Mobile menu */
.mobile-menu {
  background: var(--primary);
  border-top: 1px solid rgba(255,255,255,.15);
  padding: 12px 0;
}
.mobile-nav {
  display: flex; flex-direction: column; gap: 4px;
  padding: 0 20px;
}
.mobile-nav a {
  color: rgba(255,255,255,.9); font-size: 15px; font-weight: 500;
  padding: 10px 12px; border-radius: 8px;
  transition: background .15s;
}
.mobile-nav a:hover, .mobile-nav a.router-link-active {
  background: rgba(255,255,255,.15);
}
.mobile-divider { border: none; border-top: 1px solid rgba(255,255,255,.2); margin: 8px 0; }
.mobile-username { color: rgba(255,255,255,.7); font-size: 13px; padding: 4px 12px; }

@media (max-width: 640px) {
  .desktop-nav { display: none; }
  .desktop-only { display: none; }
  .burger { display: flex; }
}
</style>
