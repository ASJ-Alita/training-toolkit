import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '仪表盘' } },
  { path: '/students', name: 'Students', component: () => import('../views/Students.vue'), meta: { title: '学员管理' } },
  { path: '/trainings', name: 'Trainings', component: () => import('../views/Trainings.vue'), meta: { title: '培训管理' } },
  { path: '/records', name: 'Records', component: () => import('../views/Records.vue'), meta: { title: '测评记录' } },
  { path: '/evaluation', name: 'Evaluation', component: () => import('../views/Evaluation.vue'), meta: { title: '柯氏评估' } },
  { path: '/knowledge-base', name: 'KnowledgeBase', component: () => import('../views/KnowledgeBase.vue'), meta: { title: '知识库问答' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || 'Training Toolkit'} - Training Toolkit`
})

export default router
