import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/home/HomeView.vue')
  },
  {
    path: '/basic-data',
    name: 'BasicData',
    component: () => import('@/views/basic-data/BasicDataView.vue')
  },
  {
    path: '/water-condition',
    name: 'WaterCondition',
    component: () => import('@/views/water-condition/WaterConditionView.vue')
  },
  {
    path: '/model-config',
    redirect: '/model-config/model-data'
  },
  {
    path: '/model-config/model-data',
    name: 'ModelData',
    component: () => import('@/views/model-config/model-data/ModelDataView.vue')
  },
  {
    path: '/process-transparent',
    name: 'ProcessTransparent',
    component: () => import('@/views/process-transparent/ProcessTransparentView.vue')
  },
  {
    path: '/evaluation-decision',
    name: 'EvaluationDecision',
    component: () => import('@/views/evaluation-decision/EvaluationDecisionView.vue')
  },
  {
    path: '/case-library',
    name: 'CaseLibrary',
    component: () => import('@/views/case-library/CaseLibraryView.vue')
  },
  {
    path: '/report-statistics',
    name: 'ReportStatistics',
    component: () => import('@/views/report-statistics/ReportStatisticsView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
