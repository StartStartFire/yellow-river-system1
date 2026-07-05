/**
 * 评价决策相关类型定义
 * 来源：evaluationDecision.ts
 */
import type { DistributionItem } from './model'

// ==================== 雷达图 ====================

/** 雷达图指标 */
export interface RadarIndicator {
  name: string
  max: number
}

/** 雷达图方案 */
export interface RadarPlan {
  plan: string
  values: number[]
}

/** 雷达图数据 */
export interface RadarData {
  indicators: RadarIndicator[]
  plans: RadarPlan[]
}

// ==================== 桑基图 ====================

/** 桑基图节点 */
export interface SankeyNode {
  name: string
  category: number
}

/** 桑基图连线 */
export interface SankeyLink {
  source: string
  target: string
  value: number
}

/** 桑基图数据 */
export interface EvaluationSankeyData {
  nodes: SankeyNode[]
  links: SankeyLink[]
}

// ==================== 帕累托 ====================

/** 帕累托散点（通用） */
export interface ParetoPoint {
  name: string
  value: number[]
}

/** 帕累托数据（通用结构） */
export interface ParetoData {
  xLabel: string
  yLabel: string
  xUnit: string
  yUnit: string
  points: ParetoPoint[]
  frontierIndices: number[]
}

/** 帕累托散点（评价决策页面专用：projection/index 对） */
export interface ParetoPlanPoint {
  projection: number
  index: number
}

/** 帕累托方案数据（评价决策页面专用） */
export interface ParetoPlanItem {
  plan: string
  points: ParetoPlanPoint[]
}

// ==================== 排名 ====================

/** 评价算法排名项 */
export interface RankingScoreItem {
  plan: string
  value: number
}

/** 评价算法排名项 */
export interface RankingItem {
  rank: number
  algorithm: string
  scores: RankingScoreItem[]
}

// ==================== 过程曲线 ====================

/** 过程曲线数据（通用） */
export interface EvaluationProcessData {
  title: string
  xAxis: string[]
  series: { name: string; data: (number | null)[] }[]
}

/** 决策分析-水位过程曲线 */
export interface DecisionWaterLevelData {
  dates: string[]
  longyang: number[]
  liujia: number[]
  floodLimit: number
  normalLevel: number
}

/** 决策分析-流量过程曲线 */
export interface DecisionFlowData {
  dates: string[]
  longyang: number[]
  liujia: number[]
}

/** 决策分析-出力过程曲线 */
export interface DecisionPowerData {
  dates: string[]
  longyang: number[]
  liujia: number[]
  longyangCapacity: number
  liujiaCapacity: number
}

// ==================== 水量流向 ====================

/** 水量流向数据（复用 DistributionItem 保持一致） */
export type WaterFlowData = DistributionItem[]

// ==================== 方案排名与目标满足 ====================

/** 方案排名 */
export interface PlanRanking {
  rank: number
  plan: string
  score: number
  indicator: string
  status: 'optimal' | 'suboptimal' | 'feasible'
}

/** 目标满足情况（通用结构） */
export interface ObjectiveSatisfaction {
  name: string
  target: string
  actual: string
  satisfied: boolean
}

/** 决策分析-目标满足项（评价决策页面专用） */
export interface DecisionTarget {
  name: string
  status: string
  rate: number
}

// ==================== 页面状态 ====================

/** 评价决策页面状态 */
export interface EvaluationDecisionState {
  evaluationExpanded: boolean
  decisionExpanded: boolean
  selectedComparePlans: string[]
  currentDecisionPlan: string
}

// ==================== 方案数据聚合 ====================

/** 单个方案的数据包（decisionPlanDataMap 的值类型） */
export interface DecisionPlanDataBundle {
  targets: DecisionTarget[]
  waterLevel: DecisionWaterLevelData
  flow: DecisionFlowData
  power: DecisionPowerData
  waterUsage: DistributionItem[]
}

/** 方案ID → 中文显示名称 */
export type PlanLabelMap = Record<string, string>
