/**
 * 评价决策相关类型定义
 * 来源：evaluationDecision.ts
 */

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

/** 帕累托散点 */
export interface ParetoPoint {
  name: string
  value: number[]
}

/** 帕累托数据 */
export interface ParetoData {
  xLabel: string
  yLabel: string
  xUnit: string
  yUnit: string
  points: ParetoPoint[]
  frontierIndices: number[]
}

/** 过程曲线数据 */
export interface EvaluationProcessData {
  title: string
  xAxis: string[]
  series: { name: string; data: (number | null)[] }[]
}

/** 水量流向数据 */
export interface WaterFlowData {
  nodes: { name: string }[]
  links: { source: string; target: string; value: number }[]
}

/** 方案排名 */
export interface PlanRanking {
  rank: number
  plan: string
  score: number
  indicator: string
  status: 'optimal' | 'suboptimal' | 'feasible'
}

/** 目标满足情况 */
export interface ObjectiveSatisfaction {
  name: string
  target: string
  actual: string
  satisfied: boolean
}
