/**
 * 步骤间联动数据
 *
 * 这些数据跨步骤使用，被 store 和多个页面引用：
 * - 模型/算法的中文显示名
 * - 水库组合、场景、子选项与模型的兼容关系
 * - 时间步长建议、目标关联参数
 */
import type {
  ReservoirGroupModelMap,
  ScenarioModelMap,
  ScenarioSubOptionModelMap,
  TimeStepParamSuggestions,
  ObjectiveRelevantParams,
  ModelLabelMap,
  AlgorithmLabelMap,
} from '@/types/model'

/** 水库组合 → 兼容的模型ID列表 */
export const reservoirGroupModelMap: ReservoirGroupModelMap = {
  'long-liu': ['stress'],
  'long-liu-hei': [],
  'all': [],
}

/** 调度场景大类 → 兼容的模型ID列表 */
export const scenarioModelMap: ScenarioModelMap = {
  'multi-year': ['stress'],
  'critical-period': [],
  'realtime': [],
}

/** 调度场景子选项 → 推荐的模型ID */
export const scenarioSubOptionModelMap: ScenarioSubOptionModelMap = {
  'multi-objective': 'stress',
}

/** 时间步长 → 建议的算法参数 */
export const timeStepParamSuggestions: TimeStepParamSuggestions = {
  '20时段/年': { iterationCount: 500, populationSize: 200 },
}

/** 调度目标 → 关联的场景参数ID */
export const objectiveRelevantParams: ObjectiveRelevantParams = {
  'water-shortage': [],
  'power-generation': [],
  'coordination': [],
}

/** 模型ID → 中文显示名称 */
export const modelLabelMap: ModelLabelMap = {
  stress: '多目标协同胁迫调度模型',
  lro: '水库群优化调度模型（LRO）',
  multi_objective_dispatch: '多目标优化调度模型',
  water_sediment_realtime: '水沙实时调度模型（WSS）',
}

/** 算法ID → 中文显示名称 */
export const algorithmLabelMap: AlgorithmLabelMap = {
  nsga2: 'NSGA-II 多目标遗传算法',
  paem: 'PAEM 逐步逼近评价方法',
  pso: 'PSO 粒子群优化算法',
  nsga3: 'NSGA-III 多目标遗传算法',
}
