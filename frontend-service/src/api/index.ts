/**
 * API 客户端
 *
 * 封装 HTTP 请求，base URL 指向后端 FastAPI 服务。
 * 系统集成阶段使用 fetch，后续可替换为 axios。
 */
import type { RadarData } from '@/types/evaluation'

const API_BASE = `http://${window.location.hostname}:18080`

/** POST /run 请求体 */
export interface RunRequestPayload {
  algorithm: string
  pop: number
  iterate: number
  M: number
  Q_sediment: number
  crossover_rate: number
  flag_xixian: string
  K_mut?: number  // PAEM 算法时传送
  initial_water_level_longyangxia?: number  // 龙羊峡起调水位(m)
  initial_water_level_liujiaxia?: number    // 刘家峡起调水位(m)
  ice_prevention_flows?: number[]           // 防凌流量 [11月,12月,1月,2月,3月](m³/s)
  year_start?: number                        // 调度起始年份（从日期中提取）
  year_end?: number                          // 调度结束年份（从日期中提取）
}

/** POST /run 响应体 */
export interface RunResponse {
  job_id: string
  status: string
  progress_percent: number | null
  created_at: string | null
  message: string | null
}

/**
 * 提交优化任务
 * POST /run
 */
export async function postRun(config: RunRequestPayload): Promise<RunResponse> {
  const res = await fetch(`${API_BASE}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `提交失败 (${res.status})`)
  }
  return res.json()
}

// ─── 评价系统 ────────────────────────────────────────────

/** POST /evaluate 请求体 */
export interface EvaluateRequestPayload {
  job_id: string
  method: 'NMF' | 'PP' | 'AHP_FUZZY' | 'ALL'
}

/** POST /evaluate 响应体 */
export interface EvaluateResponse {
  job_id: string
  method: string
  status: 'success' | 'error'
  ranking: number[] | null
  scores: number[] | null
  best_scheme_index: number | null
  message: string | null
  details: EvaluateDetails | null
}

/** 评价详情（缓存结构） */
export interface EvaluateDetails {
  method: string
  status: string
  rankings?: RankingAlgorithm[]
  convergence?: Record<string, number[]>
  radar?: RadarData
  raw_indicators?: RawIndicators
}

export interface RawIndicatorScheme {
  plan: string
  values: number[]
}

export interface RawIndicatorSubsystem {
  name: string
  indices: number[]
}

export interface RawIndicators {
  subsystems: RawIndicatorSubsystem[]
  schemes: RawIndicatorScheme[]
}

export interface RankingAlgorithm {
  algorithm: string
  ranks: number[]
  scores: number[] | null
  execution_time: number | null
}

/** GET /evaluate/{job_id} 响应 */
export interface EvaluateCacheResponse {
  job_id: string
  status: 'evaluated' | 'not_evaluated'
  message?: string
  method?: string
  rankings?: RankingAlgorithm[]
  convergence?: Record<string, number[]>
  radar?: RadarData
}

/**
 * 运行评价
 * POST /evaluate
 */
export async function postEvaluate(config: EvaluateRequestPayload): Promise<EvaluateResponse> {
  const res = await fetch(`${API_BASE}/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `评价失败 (${res.status})`)
  }
  return res.json()
}

/**
 * 获取已缓存的评价结果
 * GET /evaluate/{job_id}
 */
export async function getEvaluateResult(jobId: string): Promise<EvaluateCacheResponse> {
  const res = await fetch(`${API_BASE}/evaluate/${jobId}`)
  if (!res.ok) throw new Error(`获取评价结果失败 (${res.status})`)
  return res.json()
}

// ─── 决策分析方案明细 ────────────────────────────────────

/** 目标满足度（0~100） */
export interface DecisionPlanTargets {
  power: number
  ecology: number
  irrigation: number
  domestic: number
  spill: number
  sediment: number
}

/** 水量分配（亿m³） */
export interface DecisionPlanWaterUsage {
  power: number
  ecology: number
  irrigation: number
  domestic: number
  spill: number
  sediment: number
}

/** 单个方案的决策明细 */
export interface DecisionPlanDetail {
  /** 种群个体索引（1 起） */
  index: number
  /** 展示名（方案N，与评价排名一致） */
  label?: string
  /** 目标函数值（缺水量/发电量/协同度） */
  objectives: number[]
  /** 龙羊峡水位过程（20Y 时段） */
  level_long: number[]
  /** 刘家峡水位过程 */
  level_liu: number[]
  /** 龙羊峡出库流量过程（m³/s） */
  qout_long: number[]
  /** 刘家峡出库流量过程 */
  qout_liu: number[]
  /** 龙羊峡出力过程（万kW） */
  power_long: number[]
  /** 刘家峡出力过程（万kW） */
  power_liu: number[]
  targets: DecisionPlanTargets
  water_usage: DecisionPlanWaterUsage
  coordination?: Record<string, number>
}

/** GET /decision/{job_id} 响应 */
export interface DecisionPlansResponse {
  job_id: string
  status: string
  algorithm: string
  evaluated: boolean
  year_start: number | null
  year_end: number | null
  plans: DecisionPlanDetail[]
  message: string | null
}

/**
 * 获取决策分析方案明细
 * GET /decision/{job_id}
 */
export async function getDecisionPlans(jobId: string): Promise<DecisionPlansResponse> {
  const res = await fetch(`${API_BASE}/decision/${jobId}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `获取决策方案失败 (${res.status})`)
  }
  return res.json()
}
