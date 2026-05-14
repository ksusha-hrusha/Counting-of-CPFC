import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', component: () => import('@/views/HomeView.vue') },
  { path: '/auth', component: () => import('@/views/AuthView.vue') },
  { path: '/calculator', component: () => import('@/views/CalculatorView.vue') },
  { path: '/dishes/new', component: () => import('@/views/DishFormView.vue'), meta: { auth: true } },
  { path: '/dishes/:id/edit', component: () => import('@/views/DishFormView.vue'), meta: { auth: true } },
  { path: '/diary', component: () => import('@/views/DiaryView.vue'), meta: { auth: true } },
  { path: '/profile', component: () => import('@/views/ProfileView.vue'), meta: { auth: true } },
  { path: '/catalog', component: () => import('@/views/CatalogView.vue') },
  { path: '/feed', component: () => import('@/views/FeedView.vue') },
  { path: '/forgot-password', component: () => import('@/views/ForgotPasswordView.vue') },
  { path: '/reset-password', component: () => import('@/views/ResetPasswordView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.token) return '/auth'
})

export default router
