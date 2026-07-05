/**
 * 步骤间联动数据
 *
 * 这些数据跨步骤使用，被 store 和多个页面引用：
 * - 模型/算法的中文显示名
 * - 水库组合、场景、子选项与模型的兼容关系
 * - 时间步长建议、目标关联参数
 */

/** 水库组合 → 兼容的模型ID列表 */
export const reservoirGroupModelMap: Record<string, string[]> = {
  'long-liu': ['lro', 'multi_objective_stress'],
  'long-liu-hei': ['lro', 'multi_objective_dispatch', 'water_sediment_realtime'],
}

/** 调度场景大类 → 兼容的模型ID列表 */
export const scenarioModelMap: Record<string, string[]> = {
  'multi-year': ['lro', 'multi_objective_stress', 'multi_objective_dispatch'],
  'critical-period': ['multi_objective_stress', 'multi_objective_dispatch'],
  'realtime': ['water_sediment_realtime'],
}

/** 调度场景子选项 → 推荐的模型ID */
export const scenarioSubOptionModelMap: Record<string, string> = {
  'multi-objective': 'multi_objective_dispatch',
  'flood': 'multi_objective_stress',
  'ice': 'multi_objective_stress',
  'supply': 'lro',
  'sediment-period': 'multi_objective_dispatch',
  'ice-sediment': 'water_sediment_realtime',
  'cross-section': 'water_sediment_realtime',
  'reach': 'water_sediment_realtime',
  'multi-energy': 'multi_objective_dispatch',
}

/** 时间步长 → 建议的算法参数 */
export const timeStepParamSuggestions: Record<string, Partial<Record<string, number>>> = {
  '每日': { iterationCount: 500, populationSize: 200 },
  '每旬': { iterationCount: 300, populationSize: 150 },
  '每月': { iterationCount: 200, populationSize: 100 },
}

/** 调度目标 → 关联的场景参数ID */
export const objectiveRelevantParams: Record<string, string[]> = {
  'flood-control': [],
  'power-generation': [],
  'ecology': ['ecologicalFlow', 'sedimentRequirement'],
  'sediment': ['sedimentFlow', 'sedimentRequirement'],
  'multi-energy': [],
}

/** 模型ID → 中文显示名称 */
export const modelLabelMap: Record<string, string> = {
  lro: '水库群优化调度模型（LRO）',
  multi_objective_stress: '多目标协同胁迫模型',
  multi_objective_dispatch: '多目标优化调度模型',
  water_sediment_realtime: '水沙实时调度模型（WSS）',
}

/** 算法ID → 中文显示名称 */
export const algorithmLabelMap: Record<string, string> = {
  nsga2: 'NSGA-II 多目标遗传算法',
  pso: 'PSO 粒子群优化算法',
  paem: 'PAEM 逐步逼近评价方法',
  nsga3: 'NSGA-III 多目标遗传算法',
}
