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

/** 案例过程图（水位/下泄流量/出力 共用同一结构） */
export interface CaseProcessChart {
  title: string
  unit: string
  times: string[]
  data: number[]
}

/** 案例过程图集合 */
export interface CaseProcessCharts {
  waterLevel: CaseProcessChart
  outflow: CaseProcessChart
  power: CaseProcessChart
}

/** 历史结果 */
export interface CaseHistoryResult {
  summary: string
  keyFindings: string[]
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
  reservoirs: string[]
  caseType: string[]
  configSummary: CaseConfigSummary
  metrics: CaseMetric[]
  processCharts: CaseProcessCharts
  historyResult: CaseHistoryResult
  evaluation: CaseEvaluation
}

// ==================== 选项 ====================

export type CaseTypeOption = OptionItem
export type CaseReservoirOption = OptionItem
