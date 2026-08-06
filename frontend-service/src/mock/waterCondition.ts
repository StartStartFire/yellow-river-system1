import type { ApiResponse } from '@/types/common'
import type { ReservoirOption, ConditionTab, ProcessSeries, WaterConditionState } from '@/types/reservoir'

// ==================== 页面状态 ====================
export const waterConditionPageState: ApiResponse<WaterConditionState> = {
  code: 200,
  message: 'success',
  data: {
    activeTab: 'inflow',
    reservoir: 'longyangxia',
    dateRange: ['2026-05-15 00:00', '2026-05-16 14:30'],
    updateTime: '2026-05-16 00:00',
  },
}

// ==================== 水库选项 ====================
export const reservoirOptions: ApiResponse<ReservoirOption[]> = {
  code: 200,
  message: 'success',
  data: [
    { label: '龙羊峡水库', value: 'longyangxia' },
    { label: '刘家峡水库', value: 'liujiaxia' },
  ],
}

// ==================== 指标页签 ====================
export const waterConditionTabs: ApiResponse<ConditionTab[]> = {
  code: 200,
  message: 'success',
  data: [
    { key: 'inflow', label: '入流', unit: 'm³/s', icon: 'inflow' },
    { key: 'water-level', label: '水位', unit: 'm', icon: 'water-level' },
    { key: 'output', label: '出力', unit: 'MW', icon: 'output' },
    { key: 'outflow', label: '出流', unit: 'm³/s', icon: 'outflow' },
  ],
}

// ==================== 过程数据 ====================

// 入流数据：预报流量 + 历史流量
const longyangxiaInflow: ProcessSeries = {
  title: '龙羊峡水库入流过程',
  unit: 'm³/s',
  legend: ['历史入库流量', '预报入库流量'],
  xAxis: [
    '05-13 00:00', '05-13 06:00', '05-13 12:00', '05-13 18:00',
    '05-14 00:00', '05-14 06:00', '05-14 12:00', '05-14 18:00',
    '05-15 00:00', '05-15 06:00', '05-15 12:00', '05-15 18:00',
    '05-16 00:00', '05-16 06:00', '05-16 12:00', '05-16 14:30',
  ],
  series: [
    {
      name: '历史入库流量',
      data: [850, 920, 1050, 1120, 1180, 1250, 1320, 1380, 1420, 1480, 1520, 1560, 1580, 1600, 1620, 1625],
      color: '#00d4ff',
      type: 'solid',
    },
    {
      name: '预报入库流量',
      data: [null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, 1580, 1650, 1720, 1780],
      color: '#ffaa00',
      type: 'dashed',
    },
  ],
  updateIndex: 12,
  markLineStyle: { color: 'rgba(255, 170, 0, 0.5)', label: '预报起点' },
}

// 水位数据：调令目标水位 + 实际水位
const longyangxiaWaterLevel: ProcessSeries = {
  title: '龙羊峡水库水位过程',
  unit: 'm',
  legend: ['调令目标水位', '实际水位'],
  xAxis: [
    '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
    '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
    '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
    '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
    '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
  ],
  series: [
    {
      name: '调令目标水位',
      data: [2445, 2445, 2446, 2448, 2450, 2452, 2454, 2456, 2458, 2460, 2462, 2463, 2464, 2464.5, 2465, 2466, 2467, 2467.5, 2468, 2467.5],
      color: '#00afff',
      type: 'dashed',
    },
    {
      name: '实际水位',
      data: [2442, 2442, 2443, 2445, 2447, 2448, 2450, 2451, 2453, 2455, 2457, 2459, 2460, 2460.5, 2461, 2461.5, 2462, 2463.5, 2464.5, 2467.35],
      color: '#00e5a0',
      type: 'solid',
    },
  ],
  updateIndex: 12,
  markLineStyle: { color: 'rgba(0, 175, 255, 0.5)', label: '调度更新节点' },
  yAxisMin: 2430,
  yAxisMax: 2475,
}

// 出力数据：调令目标出力 + 实际出力
const longyangxiaOutput: ProcessSeries = {
  title: '龙羊峡水库出力过程',
  unit: 'MW',
  legend: ['调令目标出力', '实际出力'],
  xAxis: [
    '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
    '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
    '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
    '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
    '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
  ],
  series: [
    {
      name: '调令目标出力',
      data: [320, 320, 325, 325, 330, 330, 335, 335, 340, 340, 345, 345, 345, 345, 350, 350, 355, 355, 360, 360],
      color: '#00afff',
      type: 'dashed',
    },
    {
      name: '实际出力',
      data: [310, 312, 318, 320, 325, 328, 330, 332, 335, 338, 340, 342, 343, 345, 347, 348, 350, 352, 355, 358],
      color: '#00e5a0',
      type: 'solid',
    },
  ],
  updateIndex: 12,
  markLineStyle: { color: 'rgba(0, 175, 255, 0.5)', label: '调度更新节点' },
}

// 出流数据：历史调令 + 实际出流 + 未来调令
const longyangxiaOutflow: ProcessSeries = {
  title: '龙羊峡水库出流过程',
  unit: 'm³/s',
  legend: ['历史调令', '实际出流', '未来调令'],
  xAxis: [
    '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
    '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
    '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
    '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
    '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
  ],
  series: [
    {
      name: '历史调令',
      data: [1180, 1180, 1180, 1200, 1200, 1200, 1220, 1220, 1220, 1240, 1240, 1240, 1240, null as any, null as any, null as any, null as any, null as any, null as any, null as any],
      color: '#00afff',
      type: 'dashed',
    },
    {
      name: '实际出流',
      data: [1150, 1160, 1170, 1180, 1190, 1195, 1205, 1210, 1215, 1225, 1230, 1235, 1238, 1240, 1242, 1245, 1250, 1255, 1258, 1262],
      color: '#00e5a0',
      type: 'solid',
    },
    {
      name: '未来调令',
      data: [null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, 1240, 1260, 1280, 1300, 1320, 1340, 1360, 1380],
      color: '#b37feb',
      type: 'dotted',
    },
  ],
  updateIndex: 12,
  markLineStyle: { color: 'rgba(179, 127, 235, 0.5)', label: '当前时刻' },
  yAxisMin: 1000,
  yAxisMax: 1450,
}

// 刘家峡水库数据
const liujiaxiaInflow: ProcessSeries = {
  title: '刘家峡水库入流过程',
  unit: 'm³/s',
  legend: ['历史入库流量', '预报入库流量'],
  xAxis: [
    '05-13 00:00', '05-13 06:00', '05-13 12:00', '05-13 18:00',
    '05-14 00:00', '05-14 06:00', '05-14 12:00', '05-14 18:00',
    '05-15 00:00', '05-15 06:00', '05-15 12:00', '05-15 18:00',
    '05-16 00:00', '05-16 06:00', '05-16 12:00', '05-16 14:30',
  ],
  series: [
    {
      name: '历史入库流量',
      data: [680, 750, 860, 920, 980, 1030, 1060, 1100, 1150, 1200, 1250, 1300, 1350, 1380, 1400, 1420],
      color: '#00d4ff',
      type: 'solid',
    },
    {
      name: '预报入库流量',
      data: [null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, 1350, 1450, 1550, 1620],
      color: '#ffaa00',
      type: 'dashed',
    },
  ],
  updateIndex: 12,
  markLineStyle: { color: 'rgba(255, 170, 0, 0.5)', label: '预报起点' },
}

const liujiaxiaWaterLevel: ProcessSeries = {
  title: '刘家峡水库水位过程',
  unit: 'm',
  legend: ['调令目标水位', '实际水位'],
  xAxis: [
    '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
    '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
    '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
    '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
    '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
  ],
  series: [
    {
      name: '调令目标水位',
      data: [1735, 1735, 1736, 1737, 1738, 1738, 1739, 1739, 1740, 1740, 1741, 1741, 1741, 1741, 1742, 1742, 1743, 1743, 1743, 1743],
      color: '#00afff',
      type: 'dashed',
    },
    {
      name: '实际水位',
      data: [1732, 1733, 1734, 1735, 1736, 1737, 1737, 1738, 1738, 1739, 1739, 1740, 1740, 1740, 1741, 1741, 1742, 1742, 1742.5, 1742.8],
      color: '#00e5a0',
      type: 'solid',
    },
  ],
  updateIndex: 12,
  markLineStyle: { color: 'rgba(0, 175, 255, 0.5)', label: '调度更新节点' },
  yAxisMin: 1725,
  yAxisMax: 1750,
}

const liujiaxiaOutput: ProcessSeries = {
  title: '刘家峡水库出力过程',
  unit: 'MW',
  legend: ['调令目标出力', '实际出力'],
  xAxis: [
    '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
    '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
    '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
    '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
    '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
  ],
  series: [
    {
      name: '调令目标出力',
      data: [480, 480, 485, 485, 490, 490, 495, 495, 500, 500, 505, 505, 505, 505, 510, 510, 515, 515, 520, 520],
      color: '#00afff',
      type: 'dashed',
    },
    {
      name: '实际出力',
      data: [465, 470, 475, 478, 482, 485, 488, 490, 493, 496, 498, 500, 502, 504, 506, 508, 510, 512, 515, 517],
      color: '#00e5a0',
      type: 'solid',
    },
  ],
  updateIndex: 12,
  markLineStyle: { color: 'rgba(0, 175, 255, 0.5)', label: '调度更新节点' },
}

const liujiaxiaOutflow: ProcessSeries = {
  title: '刘家峡水库出流过程',
  unit: 'm³/s',
  legend: ['历史调令', '实际出流', '未来调令'],
  xAxis: [
    '05-15 00:00', '05-15 02:00', '05-15 04:00', '05-15 06:00',
    '05-15 08:00', '05-15 10:00', '05-15 12:00', '05-15 14:00',
    '05-15 16:00', '05-15 18:00', '05-15 20:00', '05-15 22:00',
    '05-16 00:00', '05-16 02:00', '05-16 04:00', '05-16 06:00',
    '05-16 08:00', '05-16 10:00', '05-16 12:00', '05-16 14:30',
  ],
  series: [
    {
      name: '历史调令',
      data: [980, 980, 1000, 1000, 1020, 1020, 1020, 1040, 1040, 1040, 1060, 1060, 1060, null as any, null as any, null as any, null as any, null as any, null as any, null as any],
      color: '#00afff',
      type: 'dashed',
    },
    {
      name: '实际出流',
      data: [950, 960, 975, 985, 995, 1005, 1010, 1015, 1025, 1030, 1035, 1045, 1050, 1055, 1058, 1060, 1065, 1070, 1075, 1078],
      color: '#00e5a0',
      type: 'solid',
    },
    {
      name: '未来调令',
      data: [null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, null as any, 1060, 1080, 1100, 1120, 1140, 1160, 1180, 1200],
      color: '#b37feb',
      type: 'dotted',
    },
  ],
  updateIndex: 12,
  markLineStyle: { color: 'rgba(179, 127, 235, 0.5)', label: '当前时刻' },
  yAxisMin: 800,
  yAxisMax: 1300,
}

// 水库数据映射表
type TabKey = 'inflow' | 'water-level' | 'output' | 'outflow'

const reservoirProcessMap: Record<string, Record<TabKey, ProcessSeries>> = {
  longyangxia: {
    'inflow': longyangxiaInflow,
    'water-level': longyangxiaWaterLevel,
    'output': longyangxiaOutput,
    'outflow': longyangxiaOutflow,
  },
  liujiaxia: {
    'inflow': liujiaxiaInflow,
    'water-level': liujiaxiaWaterLevel,
    'output': liujiaxiaOutput,
    'outflow': liujiaxiaOutflow,
  },
}

/** 根据水库ID和页签获取对应的过程数据 */
export function getProcessData(reservoirId: string, tabKey: string): ApiResponse<ProcessSeries> {
  const data = reservoirProcessMap[reservoirId]?.[tabKey as TabKey]
  if (data) {
    return { code: 200, message: 'success', data }
  }
  // 默认返回龙羊峡入流数据
  return { code: 200, message: 'success', data: longyangxiaInflow }
}
