/**
 * 模型配置相关类型定义
 * 来源：modelConfig.ts
 */

// ==================== Step 1: 模型数据 ====================

export interface MenuItem {
  id: string
  name: string
  icon: string
}

export interface MenuGroup {
  groupName: string
  children: MenuItem[]
}

export interface ChartData {
  title: string
  xAxis: string[]
  series: {
    inflow: number[]
    level: number[]
  }
}

export interface TableColumn {
  key: string
  label: string
  unit?: string
}

export interface TableData {
  title: string
  columns: TableColumn[]
  rows: Record<string, string | number>[]
}

export interface MenuContent {
  type: 'chart' | 'table'
  chartData?: ChartData
  tableData?: TableData
}

export interface MenuContentMap {
  [menuId: string]: MenuContent
}

export interface PageState {
  currentStep: number
  activeMenuId: string
  dateRange: [string, string]
}

export interface ModelDataResponse {
  menus: MenuGroup[]
  menuContents: MenuContentMap
  pageState: PageState
}

// ==================== Step 1: 调度场景 ====================

export interface DispatchSubOption {
  id: string
  name: string
  description: string
  linkedObjectives: string[]
}

export interface DispatchScenarioCategory {
  id: string
  name: string
  icon: string
  description: string
  subOptions: DispatchSubOption[]
}

// ==================== Step 2: 基础配置 ====================

export interface DispatchObjective {
  id: string
  name: string
  description: string
  icon: string
}

export interface ConstraintDetail {
  name: string
  min: number
  max: number
  unit: string
}

export interface ConstraintSummaryData {
  count: number
  description: string
  constraints: ConstraintDetail[]
}

// ==================== Step 3: 模型算法 ====================

export interface DispatchModel {
  id: string
  name: string
  supportedAlgorithms: string[]
}

export interface OptimizationAlgorithm {
  id: string
  name: string
  paramIds: string[]
}

export interface AlgorithmParameter {
  id: string
  name: string
  value: number
  min: number
  max: number
  step: number
  description: string
}

export interface ModelAlgorithmState {
  currentStep: number
  selectedModel: string
  selectedAlgorithm: string
  parameters: Record<string, number>
}

// ==================== Step 4: 场景约束 ====================

export interface ScenarioParam {
  id: string
  name: string
  value: string
  options: { label: string; value: string }[]
}

export interface ConstraintItem {
  id: string
  name: string
  description: string
  status: string
}

export interface ScenarioConstraintState {
  currentStep: number
  scenarioType: string
  scenarioDescription: string
  params: Record<string, string>
}

// ==================== Step 5: 配置汇总 ====================

export interface ConfigPlan {
  id: string
  index: number
  name: string
  model: string
  algorithm: string
  scenario: string
  selected: boolean
}

export interface DistributionItem {
  name: string
  value: number
  percent: number
}

export interface ConfigSummaryState {
  currentStep: number
  selectedPlanIds: string[]
  total: number
  pageSize: number
  currentPage: number
  estimatedTime: string
  planCount: number
}

// ==================== 步骤间联动数据 ====================

export type ReservoirGroupModelMap = Record<string, string[]>
export type ScenarioModelMap = Record<string, string[]>
export type ScenarioSubOptionModelMap = Record<string, string>
export type TimeStepParamSuggestions = Record<string, Partial<Record<string, number>>>
export type ObjectiveRelevantParams = Record<string, string[]>
export type ModelLabelMap = Record<string, string>
export type AlgorithmLabelMap = Record<string, string>

/** 场景大类时间约束 */
export interface ScenarioCategoryConstraint {
  maxDays: number
  allowedTimeSteps: string[]
  defaultTimeStep: string
}

/** 场景 → 调度主体默认值 */
export interface ScenarioToSubjectDefault {
  startTime: string
  endTime: string
  timeStep: string
  scheduleFrequency: string
  reservoirIds: string[]
}

/** 水库组合 */
export interface SubjectReservoirGroup {
  id: string
  name: string
  reservoirIds: string[]
  description: string
}
