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
    redirect: '/model-config/dispatch-scenario'
  },
  {
    path: '/model-config/dispatch-scenario',
    name: 'DispatchScenario',
    component: () => import('@/views/model-config/dispatch-scenario/DispatchScenarioView.vue')
  },
  {
    path: '/model-config/dispatch-subject',
    name: 'DispatchSubject',
    component: () => import('@/views/model-config/dispatch-subject/DispatchSubjectView.vue')
  },
  {
    path: '/model-config/model-data',
    name: 'ModelData',
    component: () => import('@/views/model-config/model-data/ModelDataView.vue')
  },
  {
    path: '/model-config/model-algorithm',
    name: 'ModelAlgorithm',
    component: () => import('@/views/model-config/model-algorithm/ModelAlgorithmView.vue')
  },
  {
    path: '/model-config/scenario-constraint',
    name: 'ScenarioConstraint',
    component: () => import('@/views/model-config/scenario-constraint/ScenarioConstraintView.vue')
  },
  {
    path: '/model-config/config-summary',
    name: 'ConfigSummary',
    component: () => import('@/views/model-config/config-summary/ConfigSummaryView.vue')
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
