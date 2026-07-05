// ==================== 评价决策页面 Mock 数据 ====================
import type { ApiResponse, OptionItem } from '@/types/common'
import type { DistributionItem } from '@/types/model'
import type {
  EvaluationDecisionState,
  RadarData,
  EvaluationSankeyData,
  ParetoPlanItem,
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

// ── 方案选项 ──
export const planOptions: ApiResponse<OptionItem[]> = {
  code: 200,
  message: 'success',
  data: [
    { label: '方案一', value: 'plan-1' },
    { label: '方案二', value: 'plan-2' },
    { label: '方案三', value: 'plan-3' },
    { label: '方案四', value: 'plan-4' },
  ],
}

export const planLabelMap: PlanLabelMap = {
  'plan-1': '方案一',
  'plan-2': '方案二',
  'plan-3': '方案三',
  'plan-4': '方案四',
}

// ── 雷达图数据 ──
export const radarData: ApiResponse<RadarData> = {
  code: 200,
  message: 'success',
  data: {
    indicators: [
      { name: '综合优选指数', max: 1.0 },
      { name: '最优投影值', max: 1.0 },
      { name: '综合隶属度', max: 1.0 },
    ],
    plans: [
      { plan: '方案一', values: [0.88, 0.82, 0.79] },
      { plan: '方案二', values: [0.76, 0.91, 0.84] },
      { plan: '方案三', values: [0.63, 0.78, 0.86] },
      { plan: '方案四', values: [0.52, 0.69, 0.74] },
    ],
  },
}

// ── 评价指标桑基图数据 ──
export const evaluationSankeyData: ApiResponse<EvaluationSankeyData> = {
  code: 200,
  message: 'success',
  data: {
    nodes: [
      // Left: indicator codes
      { name: 'R7', category: 0 },
      { name: 'R8', category: 0 },
      { name: 'R3', category: 0 },
      { name: 'R4', category: 0 },
      { name: 'R2', category: 0 },
      { name: 'R5', category: 0 },
      { name: 'R10', category: 0 },
      { name: 'R9', category: 0 },
      { name: 'R11', category: 0 },
      { name: 'R12', category: 0 },
      { name: 'R14', category: 0 },
      { name: 'R15', category: 0 },
      { name: 'R16', category: 0 },
      { name: 'R17', category: 0 },
      { name: 'R18', category: 0 },
      { name: 'R20', category: 0 },
      { name: 'R21', category: 0 },
      { name: 'R22', category: 0 },
      // Middle: categories
      { name: '沙', category: 1 },
      { name: '水', category: 1 },
      { name: '能', category: 1 },
      { name: '灾', category: 1 },
      { name: '生', category: 1 },
      // Right: results
      { name: '优', category: 2 },
      { name: '劣', category: 2 },
      { name: '不变', category: 2 },
    ],
    links: [
      // R → 沙
      { source: 'R7', target: '沙', value: 8 },
      { source: 'R8', target: '沙', value: 6 },
      { source: 'R3', target: '沙', value: 4 },
      // R → 水
      { source: 'R4', target: '水', value: 7 },
      { source: 'R2', target: '水', value: 5 },
      { source: 'R5', target: '水', value: 6 },
      // R → 能
      { source: 'R10', target: '能', value: 9 },
      { source: 'R9', target: '能', value: 7 },
      { source: 'R12', target: '能', value: 3 },
      // R → 灾
      { source: 'R11', target: '灾', value: 5 },
      { source: 'R14', target: '灾', value: 6 },
      { source: 'R15', target: '灾', value: 5 },
      { source: 'R16', target: '灾', value: 3 },
      // R → 生
      { source: 'R17', target: '生', value: 8 },
      { source: 'R18', target: '生', value: 6 },
      { source: 'R20', target: '生', value: 7 },
      { source: 'R21', target: '生', value: 5 },
      { source: 'R22', target: '生', value: 4 },
      // Category → Result
      { source: '沙', target: '优', value: 10 },
      { source: '沙', target: '劣', value: 5 },
      { source: '沙', target: '不变', value: 3 },
      { source: '水', target: '优', value: 12 },
      { source: '水', target: '劣', value: 4 },
      { source: '水', target: '不变', value: 2 },
      { source: '能', target: '优', value: 14 },
      { source: '能', target: '劣', value: 2 },
      { source: '灾', target: '优', value: 8 },
      { source: '灾', target: '劣', value: 10 },
      { source: '灾', target: '不变', value: 5 },
      { source: '生', target: '优', value: 18 },
      { source: '生', target: '劣', value: 4 },
      { source: '生', target: '不变', value: 8 },
    ],
  },
}

// ── 帕累托曲线数据 ──
export const paretoData: ApiResponse<ParetoPlanItem[]> = {
  code: 200,
  message: 'success',
  data: [
    {
      plan: '方案一',
      points: [
        { projection: 0.52, index: 0.88 },
        { projection: 0.55, index: 0.85 },
        { projection: 0.58, index: 0.82 },
        { projection: 0.62, index: 0.78 },
        { projection: 0.65, index: 0.75 },
        { projection: 0.68, index: 0.71 },
        { projection: 0.72, index: 0.68 },
        { projection: 0.75, index: 0.64 },
        { projection: 0.78, index: 0.60 },
        { projection: 0.82, index: 0.55 },
      ],
    },
    {
      plan: '方案二',
      points: [
        { projection: 0.60, index: 0.76 },
        { projection: 0.63, index: 0.78 },
        { projection: 0.67, index: 0.80 },
        { projection: 0.71, index: 0.82 },
        { projection: 0.75, index: 0.84 },
        { projection: 0.79, index: 0.86 },
        { projection: 0.83, index: 0.88 },
        { projection: 0.87, index: 0.90 },
        { projection: 0.91, index: 0.88 },
      ],
    },
    {
      plan: '方案三',
      points: [
        { projection: 0.50, index: 0.63 },
        { projection: 0.54, index: 0.66 },
        { projection: 0.58, index: 0.69 },
        { projection: 0.62, index: 0.72 },
        { projection: 0.66, index: 0.75 },
        { projection: 0.70, index: 0.78 },
        { projection: 0.74, index: 0.81 },
        { projection: 0.78, index: 0.84 },
        { projection: 0.82, index: 0.86 },
        { projection: 0.86, index: 0.83 },
      ],
    },
    {
      plan: '方案四',
      points: [
        { projection: 0.45, index: 0.52 },
        { projection: 0.49, index: 0.55 },
        { projection: 0.53, index: 0.58 },
        { projection: 0.57, index: 0.61 },
        { projection: 0.61, index: 0.64 },
        { projection: 0.65, index: 0.67 },
        { projection: 0.69, index: 0.70 },
        { projection: 0.73, index: 0.69 },
      ],
    },
  ],
}

// ── 评价算法排名数据 ──
export const rankingData: ApiResponse<RankingItem[]> = {
  code: 200,
  message: 'success',
  data: [
    {
      rank: 1,
      algorithm: '熵权-TOPSIS法',
      scores: [
        { plan: '方案一', value: 0.856 },
        { plan: '方案二', value: 0.892 },
        { plan: '方案三', value: 0.768 },
      ],
    },
    {
      rank: 2,
      algorithm: '改进模糊综合评价',
      scores: [
        { plan: '方案一', value: 0.823 },
        { plan: '方案二', value: 0.875 },
        { plan: '方案三', value: 0.745 },
      ],
    },
    {
      rank: 3,
      algorithm: '灰色关联分析',
      scores: [
        { plan: '方案一', value: 0.791 },
        { plan: '方案二', value: 0.856 },
        { plan: '方案三', value: 0.723 },
      ],
    },
    {
      rank: 4,
      algorithm: '加权求积法',
      scores: [
        { plan: '方案一', value: 0.758 },
        { plan: '方案二', value: 0.832 },
        { plan: '方案三', value: 0.698 },
      ],
    },
    {
      rank: 5,
      algorithm: '层次分析法（AHP）',
      scores: [
        { plan: '方案一', value: 0.725 },
        { plan: '方案二', value: 0.798 },
        { plan: '方案三', value: 0.672 },
      ],
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

// ── 各方案数据映射（方案切换时图表联动） ──
export const decisionPlanDataMap: Record<string, DecisionPlanDataBundle> = {
  'plan-1': {
    targets: decisionTargets.data,
    waterLevel: processWaterLevelData.data,
    flow: processFlowData.data,
    power: processPowerData.data,
    waterUsage: waterUsageFlow.data,
  },
  'plan-2': {
    targets: decisionTargets.data.map((t) => ({
      ...t,
      rate: t.rate + (Math.random() * 4 - 2),
    })),
    waterLevel: processWaterLevelData.data,
    flow: processFlowData.data,
    power: processPowerData.data,
    waterUsage: waterUsageFlow.data,
  },
  'plan-3': {
    targets: decisionTargets.data.map((t) => ({
      ...t,
      rate: t.rate + (Math.random() * 6 - 3),
    })),
    waterLevel: processWaterLevelData.data,
    flow: processFlowData.data,
    power: processPowerData.data,
    waterUsage: waterUsageFlow.data.map((u) => ({
      ...u,
      value: parseFloat((u.value + Math.random() * 4 - 2).toFixed(1)),
      percent: parseFloat((u.percent + Math.random() * 4 - 2).toFixed(1)),
    })),
  },
  'plan-4': {
    targets: decisionTargets.data.map((t) => ({
      ...t,
      rate: t.rate + (Math.random() * 8 - 4),
    })),
    waterLevel: processWaterLevelData.data,
    flow: processFlowData.data,
    power: processPowerData.data,
    waterUsage: waterUsageFlow.data.map((u) => ({
      ...u,
      value: parseFloat((u.value + Math.random() * 6 - 3).toFixed(1)),
      percent: parseFloat((u.percent + Math.random() * 6 - 3).toFixed(1)),
    })),
  },
}

export function getDecisionPlanData(planId: string): DecisionPlanDataBundle {
  return decisionPlanDataMap[planId] || decisionPlanDataMap['plan-2']
}
