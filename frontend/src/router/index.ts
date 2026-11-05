import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', name: 'dashboard', component: () => import('@/views/dashboard/DashboardView.vue') },
        { path: 'projects', name: 'projects', component: () => import('@/views/projects/ProjectListView.vue') },
        { path: 'projects/new', name: 'project-create', component: () => import('@/views/projects/ProjectCreateView.vue') },
        { path: 'projects/:id', name: 'project-detail', component: () => import('@/views/projects/ProjectDetailView.vue') },
        { path: 'projects/:id/edit', name: 'project-edit', component: () => import('@/views/projects/ProjectEditView.vue') },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.public) {
    if (to.name === 'login' && auth.accessToken && !auth.user) {
      await auth.loadCurrentUser()
    }
    if (to.name === 'login' && auth.isAuthenticated) return { name: 'dashboard' }
    return true
  }
  if (!auth.isAuthenticated) {
    if (auth.accessToken) await auth.loadCurrentUser()
    if (!auth.isAuthenticated) return { name: 'login', query: { redirect: to.fullPath } }
  }
  return true
})

export default router

