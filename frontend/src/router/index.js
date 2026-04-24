import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { title: '登录', public: true } },
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '仪表盘', adminOnly: false } },
  { path: '/students', name: 'Students', component: () => import('../views/Students.vue'), meta: { title: '学员管理', adminOnly: true } },
  { path: '/trainings', name: 'Trainings', component: () => import('../views/Trainings.vue'), meta: { title: '培训管理', adminOnly: true } },
  { path: '/records', name: 'Records', component: () => import('../views/Records.vue'), meta: { title: '测评记录', adminOnly: false } },
  { path: '/evaluation', name: 'Evaluation', component: () => import('../views/Evaluation.vue'), meta: { title: '柯氏评估', adminOnly: false } },
  { path: '/knowledge-base', name: 'KnowledgeBase', component: () => import('../views/KnowledgeBase.vue'), meta: { title: '知识库问答', adminOnly: false } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to) => {
  document.title = `${to.meta.title || 'Training Toolkit'} - Training Toolkit`

  // 公开页面放行
  if (to.meta.public) {
    return true
  }

  const auth = useAuthStore()

  // 恢复登录状态（首次加载时）
  if (!auth.isLoggedIn) {
    await auth.restore()
  }

  // 未登录跳转
  if (!auth.isLoggedIn) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  // 管理员专属页面
  if (to.meta.adminOnly && !auth.isAdmin) {
    return { name: 'Dashboard' }
  }

  return true
})

export default router
