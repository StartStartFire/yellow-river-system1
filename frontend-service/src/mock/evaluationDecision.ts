// ==================== 评价决策页面 Mock 数据 ====================
import type { ApiResponse, OptionItem } from '@/types/common'
import type { DistributionItem } from '@/types/model'
import type {
  EvaluationDecisionState,
  ConvergenceData,
  RankingItem,
  DecisionTarget,
  DecisionWaterLevelData,
  DecisionFlowData,
  DecisionPowerData,
  DecisionPlanDataBundle,
  PlanLabelMap,
} from '@/types/evaluation'

// ── 页面状态 ──
export const evaluationDecisionState: ApiResponse<EvaluationDecisionState> = {
  code: 200,
  message: 'success',
  data: {
    evaluationExpanded: true,
    decisionExpanded: false,
    selectedComparePlans: ['plan-1', 'plan-2', 'plan-3'],
    currentDecisionPlan: 'plan-2',
  },
}

// ── 方案选项（排名前 10） ──
const PLAN_LABELS_10 = Array.from({ length: 10 }, (_, i) => `方案${i + 1}`)

export const planOptions: ApiResponse<OptionItem[]> = {
  code: 200,
  message: 'success',
  data: PLAN_LABELS_10.map((label, i) => ({ label, value: `plan-${i + 1}` })),
}

export const planLabelMap: PlanLabelMap = Object.fromEntries(
  PLAN_LABELS_10.map((label, i) => [`plan-${i + 1}`, label]),
)
// ── 算法收敛曲线数据（NMF / PP 的 cost_history，模拟 500 代） ──
function generateCostHistory(start: number, end: number, steps: number, noise: number): number[] {
  const result: number[] = []
  for (let i = 0; i < steps; i++) {
    const t = i / steps
    const trend = start + (end - start) * Math.pow(t, 0.6)
    const n = (Math.random() - 0.5) * noise * (1 - t * 0.8)
    result.push(Math.max(0, trend + n))
  }
  return result
}

export const convergenceData: ApiResponse<ConvergenceData> = {
  code: 200,
  message: 'success',
  data: {
    iteration_count: 500,
    algorithms: [
      {
        name: 'NMF',
        cost_history: generateCostHistory(120000, 96500, 200, 8000),
        color: '#00afff',
      },
      {
        name: 'PP',
        cost_history: generateCostHistory(0.008, 0.00048, 200, 0.002),
        color: '#00e5a0',
      },
    ],
  },
}

// ── 评价算法排名数据（NMF / PP / AHP_FUZZY + ALL 整合排名，前 10 方案） ──
function generateRankScores(count: number, base: number, spread: number): number[] {
  const arr: number[] = []
  for (let i = 0; i < count; i++) {
    arr.push(parseFloat((base - i * spread + (Math.random() - 0.5) * spread * 0.3).toFixed(3)))
  }
  return arr
}

const PLAN_COUNT = 10

export const rankingData: ApiResponse<RankingItem[]> = {
  code: 200,
  message: 'success',
  data: [
    {
      rank: 1,
      algorithm: 'NMF 非负矩阵分解',
      scores: generateRankScores(PLAN_COUNT, 0.892, 0.012).map((v, i) => ({
        plan: PLAN_LABELS_10[i],
        value: v,
      })),
    },
    {
      rank: 2,
      algorithm: 'PP 投影寻踪',
      scores: generateRankScores(PLAN_COUNT, 0.875, 0.015).map((v, i) => ({
        plan: PLAN_LABELS_10[i],
        value: v,
      })),
    },
    {
      rank: 3,
      algorithm: 'AHP-Fuzzy 模糊综合',
      scores: generateRankScores(PLAN_COUNT, 0.856, 0.014).map((v, i) => ({
        plan: PLAN_LABELS_10[i],
        value: v,
      })),
    },
    {
      rank: -1,
      algorithm: 'ALL 序号总和整合',
      scores: PLAN_LABELS_10.map((_, i) => ({
        plan: PLAN_LABELS_10[i],
        value: i + 1,
      })),
    },
  ],
}

// ── 决策分析-目标满足情况 ──
export const decisionTargets: ApiResponse<DecisionTarget[]> = {
  code: 200,
  message: 'success',
  data: [
    { name: '发电目标', status: '已满足', rate: 96.5 },
    { name: '生态目标', status: '已满足', rate: 93.2 },
    { name: '灌溉目标', status: '基本满足', rate: 82.4 },
    { name: '生活供水目标', status: '已满足', rate: 98.1 },
    { name: '弃水控制', status: '已满足', rate: 97.8 },
    { name: '冲沙目标', status: '基本满足', rate: 75.6 },
  ],
}

// ── 决策分析-过程曲线（水位） ──
export const processWaterLevelData: ApiResponse<DecisionWaterLevelData> = {
  code: 200,
  message: 'success',
  data: {
    dates: Array.from({ length: 11 }, (_, i) => `05-${String(16 + i).padStart(2, '0')}`),
    longyang: (() => {
      const arr: number[] = []
      for (let i = 0; i < 11; i++) arr.push(parseFloat((2575 + Math.sin(i * 0.5) * 1.5 + Math.random() * 0.3).toFixed(2)))
      return arr
    })(),
    liujia: (() => {
      const arr: number[] = []
      for (let i = 0; i < 11; i++) arr.push(parseFloat((1730 + Math.sin(i * 0.5 + 1) * 1.2 + Math.random() * 0.3).toFixed(2)))
      return arr
    })(),
    floodLimit: 2578.5,
    normalLevel: 2575.0,
  },
}

// ── 决策分析-过程曲线（流量） ──
export const processFlowData: ApiResponse<DecisionFlowData> = {
  code: 200,
  message: 'success',
  data: {
    dates: Array.from({ length: 11 }, (_, i) => `05-${String(16 + i).padStart(2, '0')}`),
    longyang: (() => {
      const arr: number[] = []
      for (let i = 0; i < 11; i++) arr.push(parseFloat((800 + Math.sin(i * 0.6) * 200 + Math.random() * 50).toFixed(0)))
      return arr
    })(),
    liujia: (() => {
      const arr: number[] = []
      for (let i = 0; i < 11; i++) arr.push(parseFloat((900 + Math.sin(i * 0.6 + 1) * 220 + Math.random() * 50).toFixed(0)))
      return arr
    })(),
  },
}

// ── 决策分析-过程曲线（出力） ──
export const processPowerData: ApiResponse<DecisionPowerData> = {
  code: 200,
  message: 'success',
  data: {
    dates: Array.from({ length: 11 }, (_, i) => `05-${String(16 + i).padStart(2, '0')}`),
    longyang: (() => {
      const arr: number[] = []
      for (let i = 0; i < 11; i++) arr.push(parseFloat((1200 + Math.sin(i * 0.5) * 300 + Math.random() * 50).toFixed(0)))
      return arr
    })(),
    liujia: (() => {
      const arr: number[] = []
      for (let i = 0; i < 11; i++) arr.push(parseFloat((1300 + Math.sin(i * 0.5 + 1) * 320 + Math.random() * 50).toFixed(0)))
      return arr
    })(),
    longyangCapacity: 1600,
    liujiaCapacity: 1800,
  },
}

// ── 水量使用流向图 ──
export const waterUsageFlow: ApiResponse<DistributionItem[]> = {
  code: 200,
  message: 'success',
  data: [
    { name: '发电', value: 45.8, percent: 45.8 },
    { name: '生态', value: 18.6, percent: 18.6 },
    { name: '灌溉', value: 15.2, percent: 15.2 },
    { name: '生活', value: 6.0, percent: 6.0 },
    { name: '弃水', value: 8.4, percent: 8.4 },
    { name: '冲沙', value: 6.0, percent: 6.0 },
  ],
}

// ── 各方案数据映射（方案切换时图表联动，覆盖前 10 方案） ──
export const decisionPlanDataMap: Record<string, DecisionPlanDataBundle> = Object.fromEntries(
  PLAN_LABELS_10.map((_, i) => {
    const planId = `plan-${i + 1}`
    const seed = i * 0.3
    return [
      planId,
      {
        targets: decisionTargets.data.map((t) => ({
          ...t,
          rate: parseFloat(Math.min(100, Math.max(50, t.rate + Math.sin(seed + Math.random() * 0.5) * 12)).toFixed(1)),
        })),
        waterLevel: processWaterLevelData.data,
        flow: processFlowData.data,
        power: processPowerData.data,
        waterUsage: waterUsageFlow.data.map((u) => ({
          ...u,
          value: parseFloat((u.value + Math.sin(seed + Math.random() * 0.5) * 3).toFixed(1)),
          percent: parseFloat((u.percent + Math.sin(seed + Math.random() * 0.5) * 3).toFixed(1)),
        })),
      },
    ]
  }),
)

export function getDecisionPlanData(planId: string): DecisionPlanDataBundle {
  return decisionPlanDataMap[planId] || decisionPlanDataMap['plan-1']
}
