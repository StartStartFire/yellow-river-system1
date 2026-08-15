/**
 * 案例库相关类型定义
 * 来源：caseLibrary.ts
 */
import type { OptionItem } from './common'

// ==================== 页面状态 ====================

/** 案例库筛选条件 */
export interface CaseFilters {
  dateRange: string[]
  caseType: string
  reservoir: string
  keyword: string
}

/** 案例库页面状态 */
export interface CaseLibraryPageState {
  selectedCaseId: string
  activeTab: string
  filters: CaseFilters
}

// ==================== 案例列表 ====================

/** 案例列表项 */
export interface CaseItem {
  id: string
  title: string
  tag: string
  tagColor: string
  iconType: string
  reservoirs: string[]
  caseType: string[]
  createdAt: string
  summary: string
  status: string
  statusColor: string
  score: number
  cover: string
}

// ==================== 案例详情 ====================

/** 案例配置摘要 */
export interface CaseConfigSummary {
  period: string
  reservoirs: string
  objective: string
  constraints: string
  modelType: string
  algorithm: string
  population: string
  iterations: string
  modelVersion: string
}

/** 案例指标项 */
export interface CaseMetric {
  name: string
  value: string
  change: string
  changeType: 'up' | 'down' | 'success' | 'excellent' | string
  baseline: string
}

/** 图表系列定义（用于多系列对比图表） */
export interface ChartSeries {
  name: string
  data: number[]
  color: string
  dashed?: boolean
}

/** 案例过程图（水位/下泄流量/出力 共用同一结构）
 *
 * 支持单系列、双系列对比、或多系列（多条线）展示。
 * - 单系列：使用 data
 * - 双系列（优化 vs 实际对比）：同时使用 data + compareData
 * - 多系列（如龙羊峡+刘家峡的优化vs实际共4条线）：使用 series[]
 */
export interface CaseProcessChart {
  title: string
  unit: string
  times: string[]
  data: number[]
  /** 对比系列数据（可选，用于优化 vs 实际对比展示） */
  compareData?: number[]
  /** 主系列名称（如 "优化调度"） */
  legendName?: string
  /** 对比系列名称（如 "实际调度"） */
  compareName?: string
  /** 多系列数据（优先于单系列/双系列） */
  series?: ChartSeries[]
}

/** 案例过程图集合 */
export interface CaseProcessCharts {
  waterLevel: CaseProcessChart
  outflow: CaseProcessChart
  power: CaseProcessChart
}

/** 关键发现表格行（优化 vs 实际对比） */
export interface CaseFindingTableRow {
  /** 维度分类：发电 / 供水 / 输沙 / 生态 */
  dimension: string
  /** 具体指标名称 */
  indicator: string
  /** 优化调度值 */
  optValue: string
  /** 实际调度值（可选，无对比时可省略） */
  actValue?: string
}

/** 历史结果 */
export interface CaseHistoryResult {
  summary: string
  keyFindings: string[]
  /** 关键发现对比表格（可选，优先于 keyFindings 列表展示） */
  findingsTable?: CaseFindingTableRow[]
}

/** 评价维度 */
export interface CaseEvaluationDimension {
  name: string
  score: number
  weight: number
}

/** 案例评价 */
export interface CaseEvaluation {
  overall: number
  dimensions: CaseEvaluationDimension[]
}

/** 案例详情 */
export interface CaseDetail {
  id: string
  title: string
  tag: string
  tagColor: string
  status: string
  statusColor: string
  score: number
  scoreLevel: string
  createdAt: string
  creator: string
  /** 方案编号（如 SC-YI-003-2），仅部分案例有 */
  caseCode?: string
  reservoirs: string[]
  caseType: string[]
  configSummary: CaseConfigSummary
  metrics: CaseMetric[]
  processCharts: CaseProcessCharts
  historyResult: CaseHistoryResult
  evaluation: CaseEvaluation
}
