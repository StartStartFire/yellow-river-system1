/**
 * 报表统计相关类型定义
 * 来源：reportStatistics.ts
 */
import type { OptionItem } from './common'

// ==================== 页面状态 ====================

/** 报表统计页面状态 */
export interface ReportStatisticsPageState {
  reportType: 'monthly' | 'yearly' | string
  year: string
  month: string
  reservoir: string
}

// ==================== 月度报表 ====================

/** 月度运行情况行（合计行 level 字段为 null） */
export interface MonthlyOperationItem {
  reservoirName: string
  initialLevel: number | null
  finalLevel: number | null
  maxLevel: number | null
  minLevel: number | null
  initialStorage: number
  finalStorage: number
  maxStorage: number
  minStorage: number
  inflowMonth: number
  inflowYear: number
  totalOutflowMonth: number
  totalOutflowYear: number
  powerReleaseMonth: number
  powerReleaseYear: number
  ecologicalReleaseMonth: number
  ecologicalReleaseYear: number
  abandonedWaterMonth: number
  abandonedWaterYear: number
}

/** 月度主要经济指标行 */
export interface MonthlyEconomicItem {
  reservoirName: string
  installedCapacityTotal: number
  installedCapacityInService: number
  installedCapacityNew: number
  annualDesignPower: number
  averageRunoff: number
  currentYearRunoff: number
  waterUseMonth: number
  waterUseYear: number
  utilizationRateMonth: number
  utilizationRateYear: number
  waterSupplyMonth: number
  waterSupplyYear: number
  floodStorageDesign: number
  floodStorageCurrent: number
  floodStandard: number
}

/** 月度发电量及考核情况行 */
export interface MonthlyPowerItem {
  reservoirName: string
  powerMonth: number
  powerYear: number
  planCompletionRate: number
  waterConsumptionMonth: number
  waterConsumptionYear: number
  waterConsumptionAssessment: number
  assessmentResult: string
  gridPowerMonth: number
  gridPowerYear: number
  utilizationHoursMonth: number
  utilizationHoursYear: number
  remark: string
}

// ==================== 年度报表 ====================

/** 年度汇总行 */
export interface YearlySummaryItem {
  reservoirName: string
  initialYearLevel: number
  finalYearLevel: number
  averageYearLevel: number
  maxYearLevel: number
  minYearLevel: number
  totalYearInflow: number
  totalYearOutflow: number
  yearPowerWater: number
  yearAbandonedWater: number
  yearWaterSupply: number
  yearPower: number
  yearAverageConsumption: number
  yearAverageOutput: number
  yearUtilizationHours: number
  assessmentResult: string
}

// ==================== 选项 ====================

export type YearOption = OptionItem
export type MonthOption = OptionItem
export type ReportReservoirOption = OptionItem
