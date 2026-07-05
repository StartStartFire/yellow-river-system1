/**
 * 过程透明相关类型定义
 * 来源：processTransparent.ts
 */

// ==================== 基础数据 ====================

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

// ==================== 页面状态 ====================

/** 页面状态 */
export interface ProcessPageState {
  activeScenarioId: string
  status: string
  progress: number
  elapsedTime: string
  remainingTime: string
  period: string
  autoPopupResult: boolean
}

// ==================== 算法过程曲线 ====================

/** 算法收敛曲线 */
export interface ConvergenceData {
  iterations: number[]
  fitness: number[]
}

/** 最优目标值变化趋势 */
export interface ObjectiveTrendData {
  iterations: number[]
  total: number[]
  flood: number[]
  power: number[]
  ecology: number[]
}

/** 种群多样性变化 */
export interface DiversityData {
  generations: number[]
  diversity: number[]
}

// ==================== 水库运行响应曲线 ====================

/** 水位过程线（单水库） */
export interface ReservoirLevelSeries {
  optimal: number[]
  forecast: number[]
  history: number[]
}

/** 水位过程线（整体） */
export interface WaterLevelProcessData {
  dates: string[]
  longyang: ReservoirLevelSeries
  liujia: ReservoirLevelSeries
}

/** 下泄流量过程线（单水库） */
export interface ReservoirDischargeSeries {
  optimal: number[]
  schedule: number[]
  minDischarge: number[]
}

/** 下泄流量过程线（整体） */
export interface DischargeProcessData {
  dates: string[]
  longyang: ReservoirDischargeSeries
  liujia: ReservoirDischargeSeries
}

/** 出力过程线（单水库） */
export interface ReservoirPowerSeries {
  optimal: number[]
  schedule: number[]
  capacity: number
}

/** 出力过程线（整体） */
export interface PowerOutputProcessData {
  dates: string[]
  longyang: ReservoirPowerSeries
  liujia: ReservoirPowerSeries
}

// ==================== 方案数据聚合 ====================

/** 单个方案的完整数据包（scenarioDataMap 的值类型） */
export interface ScenarioDataBundle {
  convergenceData: ConvergenceData
  objectiveTrendData: ObjectiveTrendData
  diversityData: DiversityData
  waterLevelData: WaterLevelProcessData
  dischargeData: DischargeProcessData
  powerOutputData: PowerOutputProcessData
  summary: ProcessSummary
  logs: ProcessLog[]
}
