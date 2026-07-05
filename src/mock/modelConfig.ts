/**
 * 模型配置 Mock 数据聚合导出
 *
 * 本文件仅作为聚合入口，所有实际数据已按步骤拆分到 model-config/ 子目录：
 *
 *   dispatchScenario.ts   — Step 1 调度场景
 *   dispatchSubject.ts    — Step 2 调度主体
 *   modelData.ts          — Step 3 调度数据
 *   modelAlgorithm.ts     — Step 4 模型算法
 *   scenarioConstraint.ts — Step 5 场景约束
 *   configSummary.ts      — Step 6 配置汇总
 *   linkage.ts            — 步骤间联动数据
 *
 * 现有 `from '@/mock/modelConfig'` 的 import 路径保持不变。
 * 新开发建议直接从子模块 import，例如：`from '@/mock/model-config/dispatchScenario'`。
 */

export { dispatchScenarioCategories } from './model-config/dispatchScenario'

export {
  reservoirNameMap,
  allReservoirs,
  subjectReservoirGroups,
  scenarioToSubjectDefaults,
  scenarioCategoryConstraints,
} from './model-config/dispatchSubject'

export { modelDataMock } from './model-config/modelData'

export {
  dispatchObjectives,
  constraintSummary,
  modelAlgorithmState,
  dispatchModels,
  optimizationAlgorithms,
  algorithmParameters,
} from './model-config/modelAlgorithm'

export {
  scenarioConstraintState,
  scenarioTypeOptions,
  scenarioParams,
  constraintList,
} from './model-config/scenarioConstraint'

export {
  configSummaryState,
  configPlanList,
  modelDistribution,
  algorithmDistribution,
} from './model-config/configSummary'

export {
  reservoirGroupModelMap,
  scenarioModelMap,
  scenarioSubOptionModelMap,
  timeStepParamSuggestions,
  objectiveRelevantParams,
  modelLabelMap,
  algorithmLabelMap,
} from './model-config/linkage'
