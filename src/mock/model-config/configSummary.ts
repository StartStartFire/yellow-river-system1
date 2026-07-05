/**
 * Step 6: 配置汇总 Mock 数据
 */
import type { ConfigPlan, DistributionItem, ConfigSummaryState } from '@/types/model'

export const configSummaryState = {
  code: 200,
  message: 'success',
  data: {
    currentStep: 5,
    selectedPlanIds: ['plan-001', 'plan-002', 'plan-003'],
    total: 24,
    pageSize: 10,
    currentPage: 1,
    estimatedTime: '02:18:45',
    planCount: 24,
  } as ConfigSummaryState,
}

const allPlans: ConfigPlan[] = [
  { id: 'plan-001', index: 1, name: '防洪调度方案_20250516_A', model: '联动水库优化调度模型（LRO）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_主汛期', selected: true },
  { id: 'plan-002', index: 2, name: '防洪调度方案_20250515_B', model: '联动水库优化调度模型（LRO）', algorithm: '改进粒子群算法（PSO）', scenario: '极端场景_设计洪水', selected: true },
  { id: 'plan-003', index: 3, name: '兴利调度方案_20250514_C', model: '来水预报模型（LSTM）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_平水年', selected: true },
  { id: 'plan-004', index: 4, name: '生态调度方案_20250513_D', model: '水库调蓄模型（MIKE11）', algorithm: 'Pareto最优解集算法', scenario: '生态场景_生态流量保障', selected: false },
  { id: 'plan-005', index: 5, name: '防洪调度方案_20250512_E', model: '联动水库优化调度模型（LRO）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_主汛期', selected: false },
  { id: 'plan-006', index: 6, name: '兴利调度方案_20250511_F', model: '来水预报模型（LSTM）', algorithm: '差分进化算法', scenario: '典型场景_枯水年', selected: false },
  { id: 'plan-007', index: 7, name: '生态调度方案_20250510_G', model: '水库调蓄模型（MIKE11）', algorithm: 'Pareto最优解集算法', scenario: '生态场景_生态流量保障', selected: false },
  { id: 'plan-008', index: 8, name: '防洪调度方案_20250509_H', model: '联动水库优化调度模型（LRO）', algorithm: '改进粒子群算法（PSO）', scenario: '极端场景_设计洪水', selected: false },
  { id: 'plan-009', index: 9, name: '兴利调度方案_20250508_I', model: '来水预报模型（LSTM）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_平水年', selected: false },
  { id: 'plan-010', index: 10, name: '生态调度方案_20250507_J', model: '水库调蓄模型（MIKE11）', algorithm: '差分进化算法', scenario: '典型场景_枯水年', selected: false },
  { id: 'plan-011', index: 11, name: '防洪调度方案_20250506_K', model: '联动水库优化调度模型（LRO）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_主汛期', selected: false },
  { id: 'plan-012', index: 12, name: '兴利调度方案_20250505_L', model: '来水预报模型（LSTM）', algorithm: '改进粒子群算法（PSO）', scenario: '典型场景_平水年', selected: false },
  { id: 'plan-013', index: 13, name: '生态调度方案_20250504_M', model: '水库调蓄模型（MIKE11）', algorithm: 'Pareto最优解集算法', scenario: '生态场景_生态流量保障', selected: false },
  { id: 'plan-014', index: 14, name: '防洪调度方案_20250503_N', model: '联动水库优化调度模型（LRO）', algorithm: '改进粒子群算法（PSO）', scenario: '极端场景_设计洪水', selected: false },
  { id: 'plan-015', index: 15, name: '兴利调度方案_20250502_O', model: '来水预报模型（LSTM）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_枯水年', selected: false },
  { id: 'plan-016', index: 16, name: '生态调度方案_20250501_P', model: '水库调蓄模型（MIKE11）', algorithm: '差分进化算法', scenario: '典型场景_平水年', selected: false },
  { id: 'plan-017', index: 17, name: '防洪调度方案_20250430_Q', model: '联动水库优化调度模型（LRO）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_主汛期', selected: false },
  { id: 'plan-018', index: 18, name: '兴利调度方案_20250429_R', model: '来水预报模型（LSTM）', algorithm: '改进粒子群算法（PSO）', scenario: '典型场景_平水年', selected: false },
  { id: 'plan-019', index: 19, name: '生态调度方案_20250428_S', model: '水库调蓄模型（MIKE11）', algorithm: 'Pareto最优解集算法', scenario: '生态场景_生态流量保障', selected: false },
  { id: 'plan-020', index: 20, name: '防洪调度方案_20250427_T', model: '联动水库优化调度模型（LRO）', algorithm: '差分进化算法', scenario: '典型场景_主汛期', selected: false },
  { id: 'plan-021', index: 21, name: '兴利调度方案_20250426_U', model: '来水预报模型（LSTM）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '极端场景_设计洪水', selected: false },
  { id: 'plan-022', index: 22, name: '生态调度方案_20250425_V', model: '水库调蓄模型（MIKE11）', algorithm: '改进粒子群算法（PSO）', scenario: '典型场景_枯水年', selected: false },
  { id: 'plan-023', index: 23, name: '防洪调度方案_20250424_W', model: '联动水库优化调度模型（LRO）', algorithm: 'Pareto最优解集算法', scenario: '生态场景_生态流量保障', selected: false },
  { id: 'plan-024', index: 24, name: '兴利调度方案_20250423_X', model: '来水预报模型（LSTM）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_平水年', selected: false },
]

export const configPlanList = {
  code: 200,
  message: 'success',
  data: allPlans,
}

export const modelDistribution = {
  code: 200,
  message: 'success',
  data: [
    { name: 'LRO模型', value: 10, percent: 41.7 },
    { name: 'LSTM模型', value: 6, percent: 25.0 },
    { name: 'MIKE11模型', value: 8, percent: 33.3 },
  ] as DistributionItem[],
}

export const algorithmDistribution = {
  code: 200,
  message: 'success',
  data: [
    { name: 'NSGA-II', value: 10, percent: 41.7 },
    { name: '改进PSO', value: 7, percent: 29.2 },
    { name: 'Pareto算法', value: 4, percent: 16.7 },
    { name: '差分进化', value: 3, percent: 12.5 },
  ] as DistributionItem[],
}
