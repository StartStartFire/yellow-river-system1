/**
 * 过程透明相关类型定义
 * 来源：processTransparent.ts
 */

/** 方案选项 */
export interface ScenarioOption {
  id: string
  name: string
  taskId: string
}

/** 约束状态 */
export interface ConstraintStatus {
  name: string
  status: string
}

/** 最优解 */
export interface BestSolution {
  totalObjective: number
  floodObjective: number
  powerObjective: number
  ecologyObjective: number
}

/** 预估结果 */
export interface EstimatedResult {
  peakReduction: string
  totalPower: string
  avgOutflow: string
  minOutflow: string
}

/** 底部摘要 */
export interface ProcessSummary {
  bestSolution: BestSolution
  constraintStatus: ConstraintStatus[]
  estimatedResult: EstimatedResult
}

/** 运行日志 */
export interface ProcessLog {
  time: string
  level: string
  message: string
}
