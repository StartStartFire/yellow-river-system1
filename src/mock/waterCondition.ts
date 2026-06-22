// ==================== 统一 API 响应结构 ====================
interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// ==================== 页面状态 ====================
export interface WaterConditionState {
  activeTab: string
  reservoir: string
  dateRange: [string, string]
  updateTime: string
}

export const waterConditionPageState: ApiResponse<WaterConditionState> = {
  code: 200,
  message: 'success',
  data: {
    activeTab: 'water-level',
    reservoir: 'longyangxia',
    dateRange: ['2026-05-15 00:00', '2026-05-16 14:30'],
    updateTime: '2026-05-16 00:00',
  },
}

// ==================== 水库选项 ====================
export interface ReservoirOption {
  label: string
  value: string
}

export const reservoirOptions: ApiResponse<ReservoirOption[]> = {
  code: 200,
  message: 'success',
  data: [
    { label: '龙羊峡水库', value: 'longyangxia' },
    { label: '刘家峡水库', value: 'liujiaxia' },
  ],
}

// ==================== 指标页签 ====================
export interface ConditionTab {
  key: string
  label: string
  unit: string
}

export const waterConditionTabs: ApiResponse<ConditionTab[]> = {
  code: 200,
  message: 'success',
  data: [
    { key: 'water-level', label: '水位', unit: 'm' },
    { key: 'flow', label: '流量', unit: 'm³/s' },
    { key: 'output', label: '出力', unit: 'MW' },
  ],
}

// ==================== 过程数据 ====================
export interface ProcessSeries {
  title: string
  unit: string
  legend: [string, string]
  xAxis: string[]
  target: number[]
  actual: number[]
  updateIndex: number
  targetLastValue: number
  actualLastValue: number
}

type TabKey = 'water-level' | 'flow' | 'output'
type ReservoirDataMap = Record<TabKey, ProcessSeries>

const longyangxiaData: Record<TabKey, ProcessSeries> = {
  'water-level': {
    title: '龙羊峡水库调令执行对比 - 水位过程',
    unit: 'm',
    legend: ['调令目标水位', '实际水位'],
    xAxis: [
      '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
      '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
      '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
      '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
      '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
    ],
    target: [2445, 2445, 2446, 2448, 2450, 2452, 2454, 2456, 2458, 2460, 2462, 2463, 2464, 2464.5, 2465, 2466, 2467, 2467.5, 2468, 2467.5],
    actual: [2442, 2442, 2443, 2445, 2447, 2448, 2450, 2451, 2453, 2455, 2457, 2459, 2460, 2460.5, 2461, 2461.5, 2462, 2463.5, 2464.5, 2467.35],
    updateIndex: 12,
    targetLastValue: 2467.5,
    actualLastValue: 2467.35,
  },
  flow: {
    title: '龙羊峡水库调令执行对比 - 流量过程',
    unit: 'm³/s',
    legend: ['调令目标流量', '实际流量'],
    xAxis: [
      '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
      '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
      '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
      '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
      '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
    ],
    target: [1180, 1180, 1180, 1200, 1200, 1200, 1220, 1220, 1220, 1240, 1240, 1240, 1240, 1240, 1240, 1240, 1260, 1260, 1260, 1260],
    actual: [1150, 1160, 1170, 1180, 1190, 1195, 1205, 1210, 1215, 1225, 1230, 1235, 1238, 1240, 1242, 1245, 1250, 1255, 1258, 1262],
    updateIndex: 12,
    targetLastValue: 1260,
    actualLastValue: 1262,
  },
  output: {
    title: '龙羊峡水库调令执行对比 - 出力过程',
    unit: 'MW',
    legend: ['调令目标出力', '实际出力'],
    xAxis: [
      '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
      '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
      '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
      '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
      '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
    ],
    target: [320, 320, 325, 325, 330, 330, 335, 335, 340, 340, 345, 345, 345, 345, 350, 350, 355, 355, 360, 360],
    actual: [310, 312, 318, 320, 325, 328, 330, 332, 335, 338, 340, 342, 343, 345, 347, 348, 350, 352, 355, 358],
    updateIndex: 12,
    targetLastValue: 360,
    actualLastValue: 358,
  },
}

const liujiaxiaData: Record<TabKey, ProcessSeries> = {
  'water-level': {
    title: '刘家峡水库调令执行对比 - 水位过程',
    unit: 'm',
    legend: ['调令目标水位', '实际水位'],
    xAxis: [
      '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
      '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
      '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
      '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
      '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
    ],
    target: [1735, 1735, 1736, 1737, 1738, 1738, 1739, 1739, 1740, 1740, 1741, 1741, 1741, 1741, 1742, 1742, 1743, 1743, 1743, 1743],
    actual: [1732, 1733, 1734, 1735, 1736, 1737, 1737, 1738, 1738, 1739, 1739, 1740, 1740, 1740, 1741, 1741, 1742, 1742, 1742.5, 1742.8],
    updateIndex: 12,
    targetLastValue: 1743,
    actualLastValue: 1742.8,
  },
  flow: {
    title: '刘家峡水库调令执行对比 - 流量过程',
    unit: 'm³/s',
    legend: ['调令目标流量', '实际流量'],
    xAxis: [
      '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
      '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
      '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
      '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
      '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
    ],
    target: [980, 980, 1000, 1000, 1020, 1020, 1020, 1040, 1040, 1040, 1060, 1060, 1060, 1060, 1060, 1080, 1080, 1080, 1080, 1080],
    actual: [950, 960, 975, 985, 995, 1005, 1010, 1015, 1025, 1030, 1035, 1045, 1050, 1055, 1058, 1060, 1065, 1070, 1075, 1078],
    updateIndex: 12,
    targetLastValue: 1080,
    actualLastValue: 1078,
  },
  output: {
    title: '刘家峡水库调令执行对比 - 出力过程',
    unit: 'MW',
    legend: ['调令目标出力', '实际出力'],
    xAxis: [
      '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
      '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
      '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
      '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
      '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
    ],
    target: [480, 480, 485, 485, 490, 490, 495, 495, 500, 500, 505, 505, 505, 505, 510, 510, 515, 515, 520, 520],
    actual: [465, 470, 475, 478, 482, 485, 488, 490, 493, 496, 498, 500, 502, 504, 506, 508, 510, 512, 515, 517],
    updateIndex: 12,
    targetLastValue: 520,
    actualLastValue: 517,
  },
}

// 水库数据映射表
const reservoirProcessMap: Record<string, Record<TabKey, ProcessSeries>> = {
  longyangxia: longyangxiaData,
  liujiaxia: liujiaxiaData,
}

/** 根据水库ID和页签获取对应的过程数据 */
export function getProcessData(reservoirId: string, tabKey: string): ApiResponse<ProcessSeries> {
  const data = reservoirProcessMap[reservoirId]?.[tabKey as TabKey]
  if (data) {
    return { code: 200, message: 'success', data }
  }
  // 默认返回龙羊峡水位数据
  return { code: 200, message: 'success', data: longyangxiaData['water-level'] }
}
