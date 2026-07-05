// ==================== 过程透明页面 Mock 数据 ====================
import type { ApiResponse } from '@/types/common'
import type {
  ProcessPageState,
  ScenarioOption,
  ProcessSummary,
  ProcessLog,
  ConvergenceData,
  ObjectiveTrendData,
  DiversityData,
  WaterLevelProcessData,
  DischargeProcessData,
  PowerOutputProcessData,
  ScenarioDataBundle,
} from '@/types/process'

// ── 页面状态 ──
export const processPageState: ApiResponse<ProcessPageState> = {
  code: 200,
  message: 'success',
  data: {
    activeScenarioId: 'flood-priority',
    status: 'running',
    progress: 26.2,
    elapsedTime: '00:08:24',
    remainingTime: '00:22:36',
    period: '2025-05-16 08:00 ~ 2025-05-26 08:00（241时段）',
    autoPopupResult: true,
  },
}

// ── 方案情景 ──
export const scenarioOptions: ApiResponse<ScenarioOption[]> = {
  code: 200,
  message: 'success',
  data: [
    { id: 'flood-priority', name: '方案一：防洪优先', taskId: 'TASK_20250516_102415' },
    { id: 'power-priority', name: '方案二：发电优先', taskId: 'TASK_20250516_102416' },
    { id: 'ecology-priority', name: '方案三：生态优先', taskId: 'TASK_20250516_102417' },
  ],
}

// ── 底部摘要 ──
export const processSummary: ApiResponse<ProcessSummary> = {
  code: 200,
  message: 'success',
  data: {
    bestSolution: {
      totalObjective: 873.56,
      floodObjective: 312.45,
      powerObjective: 428.71,
      ecologyObjective: 132.4,
    },
    constraintStatus: [
      { name: '防洪约束', status: '满足' },
      { name: '水位约束', status: '满足' },
      { name: '下泄生态流量', status: '满足' },
      { name: '机组出力约束', status: '满足' },
    ],
    estimatedResult: {
      peakReduction: '23.6%',
      totalPower: '2985.6 万kWh',
      avgOutflow: '1152 m³/s',
      minOutflow: '300 m³/s',
    },
  },
}

// ── 运行日志 ──
export const processLogs: ApiResponse<ProcessLog[]> = {
  code: 200,
  message: 'success',
  data: [
    { time: '10:24:33', level: 'INFO', message: '迭代 402/2000，当前最优适应度：1.5235E-03，平均适应度：2.1357E-02' },
    { time: '10:24:33', level: 'INFO', message: '龙羊峡水位约束满足率：100%，刘家峡水位约束满足率：100%' },
    { time: '10:24:33', level: 'INFO', message: '防洪目标满足，生态下泄满足，发电目标优化中...' },
  ],
}

// ── 算法收敛曲线 ──
export const convergenceData: ApiResponse<ConvergenceData> = {
  code: 200,
  message: 'success',
  data: {
    iterations: Array.from({ length: 50 }, (_, i) => i * 10),
    fitness: (() => {
      const arr: number[] = []
      for (let i = 0; i < 50; i++) {
        const v = 0.15 * Math.exp(-i * 0.08) + 0.005 + Math.random() * 0.008
        arr.push(parseFloat(v.toFixed(6)))
      }
      return arr
    })(),
  },
}

// ── 最优目标值变化趋势 ──
export const objectiveTrendData: ApiResponse<ObjectiveTrendData> = {
  code: 200,
  message: 'success',
  data: {
    iterations: Array.from({ length: 50 }, (_, i) => i * 10),
    total: (() => {
      const arr: number[] = []
      for (let i = 0; i < 50; i++) {
        arr.push(parseFloat((950 - i * 3.5 + Math.random() * 20).toFixed(1)))
      }
      return arr
    })(),
    flood: (() => {
      const arr: number[] = []
      for (let i = 0; i < 50; i++) {
        arr.push(parseFloat((380 - i * 1.8 + Math.random() * 12).toFixed(1)))
      }
      return arr
    })(),
    power: (() => {
      const arr: number[] = []
      for (let i = 0; i < 50; i++) {
        arr.push(parseFloat((460 - i * 1.2 + Math.random() * 15).toFixed(1)))
      }
      return arr
    })(),
    ecology: (() => {
      const arr: number[] = []
      for (let i = 0; i < 50; i++) {
        arr.push(parseFloat((180 - i * 1.0 + Math.random() * 8).toFixed(1)))
      }
      return arr
    })(),
  },
}

// ── 种群多样性变化 ──
export const diversityData: ApiResponse<DiversityData> = {
  code: 200,
  message: 'success',
  data: {
    generations: Array.from({ length: 50 }, (_, i) => i * 10),
    diversity: (() => {
      const arr: number[] = []
      for (let i = 0; i < 50; i++) {
        arr.push(parseFloat((0.85 * Math.exp(-i * 0.04) + 0.05 + Math.random() * 0.03).toFixed(4)))
      }
      return arr
    })(),
  },
}

// ── 水位过程线 ──
export const waterLevelData: ApiResponse<WaterLevelProcessData> = {
  code: 200,
  message: 'success',
  data: {
    dates: Array.from({ length: 11 }, (_, i) => `05-${String(16 + i).padStart(2, '0')}`),
    longyang: {
      optimal: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((2575 + Math.sin(i * 0.5) * 1.5 + Math.random() * 0.3).toFixed(2)))
        return arr
      })(),
      forecast: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((2574 + Math.sin(i * 0.5 + 0.3) * 1.8 + Math.random() * 0.4).toFixed(2)))
        return arr
      })(),
      history: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((2573 + Math.sin(i * 0.5 - 0.2) * 1.2 + Math.random() * 0.3).toFixed(2)))
        return arr
      })(),
    },
    liujia: {
      optimal: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((1730 + Math.sin(i * 0.5 + 1) * 1.2 + Math.random() * 0.3).toFixed(2)))
        return arr
      })(),
      forecast: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((1729 + Math.sin(i * 0.5 + 1.3) * 1.5 + Math.random() * 0.4).toFixed(2)))
        return arr
      })(),
      history: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((1728 + Math.sin(i * 0.5 + 0.8) * 0.9 + Math.random() * 0.3).toFixed(2)))
        return arr
      })(),
    },
  },
}

// ── 下泄流量过程线 ──
export const dischargeData: ApiResponse<DischargeProcessData> = {
  code: 200,
  message: 'success',
  data: {
    dates: Array.from({ length: 11 }, (_, i) => `05-${String(16 + i).padStart(2, '0')}`),
    longyang: {
      optimal: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((800 + Math.sin(i * 0.6) * 200 + Math.random() * 50).toFixed(0)))
        return arr
      })(),
      schedule: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((750 + Math.sin(i * 0.6 + 0.5) * 180 + Math.random() * 40).toFixed(0)))
        return arr
      })(),
      minDischarge: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((350 + Math.random() * 20).toFixed(0)))
        return arr
      })(),
    },
    liujia: {
      optimal: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((900 + Math.sin(i * 0.6 + 1) * 220 + Math.random() * 50).toFixed(0)))
        return arr
      })(),
      schedule: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((850 + Math.sin(i * 0.6 + 1.5) * 200 + Math.random() * 40).toFixed(0)))
        return arr
      })(),
      minDischarge: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((400 + Math.random() * 20).toFixed(0)))
        return arr
      })(),
    },
  },
}

// ── 出力过程线 ──
export const powerOutputData: ApiResponse<PowerOutputProcessData> = {
  code: 200,
  message: 'success',
  data: {
    dates: Array.from({ length: 11 }, (_, i) => `05-${String(16 + i).padStart(2, '0')}`),
    longyang: {
      optimal: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((1200 + Math.sin(i * 0.5) * 300 + Math.random() * 50).toFixed(0)))
        return arr
      })(),
      schedule: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((1100 + Math.sin(i * 0.5 + 0.3) * 280 + Math.random() * 40).toFixed(0)))
        return arr
      })(),
      capacity: 1600,
    },
    liujia: {
      optimal: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((1300 + Math.sin(i * 0.5 + 1) * 320 + Math.random() * 50).toFixed(0)))
        return arr
      })(),
      schedule: (() => {
        const arr: number[] = []
        for (let i = 0; i < 11; i++) arr.push(parseFloat((1200 + Math.sin(i * 0.5 + 1.3) * 300 + Math.random() * 40).toFixed(0)))
        return arr
      })(),
      capacity: 1800,
    },
  },
}

// ── 各方案的过程摘要映射（方案切换时图表数据同步切换） ──
export const scenarioDataMap: Record<string, ScenarioDataBundle> = {
  'flood-priority': {
    convergenceData: convergenceData.data,
    objectiveTrendData: objectiveTrendData.data,
    diversityData: diversityData.data,
    waterLevelData: waterLevelData.data,
    dischargeData: dischargeData.data,
    powerOutputData: powerOutputData.data,
    summary: processSummary.data,
    logs: processLogs.data,
  },
  'power-priority': {
    convergenceData: { ...convergenceData.data, fitness: convergenceData.data.fitness.map((v: number) => v * 1.1) },
    objectiveTrendData: {
      ...objectiveTrendData.data,
      total: objectiveTrendData.data.total.map((v: number) => v * 0.95),
      power: objectiveTrendData.data.power.map((v: number) => v * 0.85),
    },
    diversityData: { ...diversityData.data, diversity: diversityData.data.diversity.map((v: number) => v * 0.9) },
    waterLevelData: waterLevelData.data,
    dischargeData: dischargeData.data,
    powerOutputData: powerOutputData.data,
    summary: {
      bestSolution: { totalObjective: 812.34, floodObjective: 285.67, powerObjective: 365.22, ecologyObjective: 161.45 },
      constraintStatus: [
        { name: '防洪约束', status: '满足' },
        { name: '水位约束', status: '满足' },
        { name: '下泄生态流量', status: '满足' },
        { name: '机组出力约束', status: '满足' },
      ],
      estimatedResult: { peakReduction: '18.2%', totalPower: '3256.8 万kWh', avgOutflow: '1280 m³/s', minOutflow: '350 m³/s' },
    },
    logs: [
      { time: '10:25:12', level: 'INFO', message: '迭代 356/2000，当前最优适应度：1.8235E-03，平均适应度：2.4357E-02' },
      { time: '10:25:12', level: 'INFO', message: '发电目标优化中，当前发电量：3256.8 万kWh' },
      { time: '10:25:12', level: 'INFO', message: '防洪约束满足，生态下泄满足' },
    ],
  },
  'ecology-priority': {
    convergenceData: { ...convergenceData.data, fitness: convergenceData.data.fitness.map((v: number) => v * 1.2) },
    objectiveTrendData: {
      ...objectiveTrendData.data,
      total: objectiveTrendData.data.total.map((v: number) => v * 0.92),
      ecology: objectiveTrendData.data.ecology.map((v: number) => v * 0.75),
    },
    diversityData: { ...diversityData.data, diversity: diversityData.data.diversity.map((v: number) => v * 0.85) },
    waterLevelData: waterLevelData.data,
    dischargeData: dischargeData.data,
    powerOutputData: powerOutputData.data,
    summary: {
      bestSolution: { totalObjective: 756.78, floodObjective: 258.34, powerObjective: 285.56, ecologyObjective: 212.88 },
      constraintStatus: [
        { name: '防洪约束', status: '满足' },
        { name: '水位约束', status: '满足' },
        { name: '下泄生态流量', status: '满足' },
        { name: '机组出力约束', status: '满足' },
      ],
      estimatedResult: { peakReduction: '15.6%', totalPower: '2850.2 万kWh', avgOutflow: '980 m³/s', minOutflow: '420 m³/s' },
    },
    logs: [
      { time: '10:26:05', level: 'INFO', message: '迭代 312/2000，当前最优适应度：2.1356E-03，平均适应度：2.8357E-02' },
      { time: '10:26:05', level: 'INFO', message: '生态下泄流量满足要求，当前下泄：980 m³/s' },
      { time: '10:26:05', level: 'INFO', message: '防洪约束满足，发电目标优化中...' },
    ],
  },
}

export function getScenarioData(scenarioId: string): ScenarioDataBundle {
  return scenarioDataMap[scenarioId] || scenarioDataMap['flood-priority']
}
