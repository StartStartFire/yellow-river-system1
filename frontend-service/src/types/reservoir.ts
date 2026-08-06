/**
 * 水库相关类型定义
 * 来源：home.ts / basicData.ts / waterCondition.ts / caseLibrary.ts / reportStatistics.ts
 */
import type { ApiResponse } from './common'

// ==================== 基础 ====================

export type ReservoirStatus = 'normal' | 'warning' | 'abnormal'

export interface ReservoirBrief {
  id: string
  name: string
  status: ReservoirStatus
}

/** 水库简选项（仅 id + name，用于纯展示列表） */
export interface ReservoirIdName {
  id: string
  name: string
}

export interface ReservoirGroup {
  name: string
  items: ReservoirBrief[]
}

// ==================== 首页监控 ====================

/** 水库监控数据（首页卡片） */
export interface ReservoirMonitor {
  id: string
  name: string
  status: ReservoirStatus
  inflow: number // 入库流量 m³/s
  outflow: number // 出库流量 m³/s
  forebayLevel: number // 坝前水位 m
  tailwaterLevel: number // 尾水位 m
  storage: number // 库容 亿m³
  turbineFlow: number // 机组过流流量 m³/s
}

/** 水库地图点位 */
export interface ReservoirPoint {
  id: string
  name: string
  lat: number
  lng: number
  status: ReservoirStatus
  waterLevel: number // 坝前水位 m
  tailwaterLevel: number // 尾水位 m
  storage: number // 库容 亿m³
  storageRate: number // 库容率 %
  inflow: number // 入库流量 m³/s
  outflow: number // 出库流量 m³/s
  turbineFlow: number // 机组过流流量 m³/s
  updateTime: string // 更新时间
}

/** 发电统计 */
export interface PowerStatistic {
  reservoirName: string
  dailyPower: number // 日发电量 万kW·h
  monthlyPower: number // 月发电量 万kW·h
  yearlyPower: number // 年发电量 万kW·h
}

/** 水位过程线数据 */
export interface WaterLevelSeries {
  xAxis: string[]
  series: {
    name: string
    data: number[]
  }[]
}

/** 负荷过程线数据 */
export interface LoadSeries {
  xAxis: string[]
  activePower: { name: string; data: number[] }[]
  reactivePower: { name: string; data: number[] }[]
}

/** 预警信息 */
export interface WarningItem {
  id: string
  time: string
  type: string
  content: string
  target: string
  level: 1 | 2 | 3 | 4
}

/** 通知公告 */
export interface Announcement {
  content: string
}

/** 天气信息 */
export interface WeatherInfo {
  city: string
  weather: string
  temperature: string
  wind: string
}

/** 地图图层 */
export interface MapLayer {
  id: string
  name: string
  visible: boolean
}

// ==================== 基础数据 ====================

/** 指标卡片数据 */
export interface MetricCardData {
  label: string
  value: number
  unit: string
  change: number
  isUpBad?: boolean
}

/** 特征水位线 */
export interface FeatureWaterLevel {
  name: string
  value: number
  color: string
  dashed?: boolean
}

/** 大坝信息 */
export interface DamInfo {
  type: string
  crestElevation: number
  crestLength: number
  maxHeight: number
}

/** 水库断面示意图 */
export interface ReservoirSection {
  title: string
  elevationAxis: number[]
  levels: FeatureWaterLevel[]
  currentLevel: number
  inflow: number
  outflow: number
  dam: DamInfo
}

/** 基础信息分组 */
export interface BaseInfoGroup {
  title: string
  items: { key: string; value: string }[]
}

/** 机组信息 */
export interface TurbineItem {
  id: string
  name: string
  status: 'running' | 'stop' | 'maintenance'
  output: number // kW
  flow: number // m³/s
  gateOpen: number // 闸门开度 %
}

/** 闸门信息 */
export interface GateItem {
  id: string
  name: string
  openPercentage: number
  dischargeFlow: number
}

/** 工情摘要 */
export interface EngineeringSummary {
  turbineTotal: number
  turbineRunning: number
  gateTotal: number
  gateOpen: number
  totalOutput: number
}

/** 工情信息 */
export interface EngineeringInfo {
  summary: EngineeringSummary
  turbines: TurbineItem[]
  gates: GateItem[]
}

/** 关键曲线数据 */
export interface KeyCurvesData {
  storageCurve: { levels: number[]; storage: number[] }
  turbineCurve: { head: number[]; power: number[] }
  gateCurve: { opening: number[]; flow: number[] }
}

/** 水情过程数据 */
export interface ReservoirProcessData {
  dates: string[]
  levels: number[]
  inflows: number[]
  outflows: number[]
}

// ==================== 水调水情 ====================

export interface ReservoirOption {
  label: string
  value: string
}

export interface ConditionTab {
  key: string
  label: string
  unit: string
  icon: string
}

export interface ProcessSeries {
  title: string
  unit: string
  legend: string[]
  xAxis: string[]
  series: { name: string; data: number[]; color: string; type: 'solid' | 'dashed' | 'dotted' }[]
  updateIndex?: number
  markLineStyle?: { color: string; label: string }
  yAxisMin?: number
  yAxisMax?: number
}

// ==================== 水调水情页面状态 ====================

export interface WaterConditionState {
  activeTab: string
  reservoir: string
  dateRange: [string, string]
  updateTime: string
}

// ==================== 水库 ID 映射 ====================

/** 水库 ID → 显示名称 */
export type ReservoirNameMap = Record<string, string>
