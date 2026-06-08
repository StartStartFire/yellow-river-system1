// ==================== 类型定义 ====================

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

export interface MenuContentMap {
  [menuId: string]: {
    type: 'chart' | 'table'
    chartData?: ChartData
    tableData?: TableData
  }
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

// ==================== Mock 数据 ====================

export const modelDataMock = {
  code: 200,
  message: 'success',
  data: {
    menus: [
      {
        groupName: '调度输入',
        children: [
          { id: 'inflow-level', name: '入库与水位', icon: 'database' },
          { id: 'west-route', name: '西线调水数据', icon: 'water' },
          { id: 'level-boundary', name: '水位上下限', icon: 'level' },
          { id: 'lanzhou-demand', name: '兰州断面需水数据', icon: 'clock' },
          { id: 'long-liu-demand', name: '龙刘区间用水数据', icon: 'river' },
          { id: 'inflow-frequency', name: '来水频率', icon: 'bar' },
        ],
      },
      {
        groupName: '原始表格',
        children: [
          { id: 'raw-west-route', name: '西线调水数据', icon: 'table' },
          { id: 'raw-level-boundary', name: '水位上下限', icon: 'table' },
          { id: 'raw-lanzhou-demand', name: '兰州断面需水数据', icon: 'table' },
          { id: 'raw-long-liu-demand', name: '龙刘区间用水数据', icon: 'table' },
          { id: 'raw-inflow-frequency', name: '来水频率', icon: 'table' },
        ],
      },
    ] as MenuGroup[],

    menuContents: {
      // ===== 调度输入 =====
      'inflow-level': {
        type: 'chart',
        chartData: {
          title: '输入数据概览（近7日入库流量与水位）',
          xAxis: ['05-19', '05-20', '05-21', '05-22', '05-23', '05-24', '05-25'],
          series: {
            inflow: [430, 560, 820, 620, 420, 340, 460],
            level: [2486, 2484, 2488, 2486, 2484, 2481, 2485],
          },
        },
      },
      'west-route': {
        type: 'chart',
        chartData: {
          title: '输入数据概览（西线调水数据）',
          xAxis: ['05-19', '05-20', '05-21', '05-22', '05-23', '05-24', '05-25'],
          series: {
            inflow: [280, 300, 310, 290, 320, 305, 295],
            level: [2450, 2452, 2455, 2453, 2456, 2454, 2451],
          },
        },
      },
      'level-boundary': {
        type: 'chart',
        chartData: {
          title: '输入数据概览（水位上下限）',
          xAxis: ['05-19', '05-20', '05-21', '05-22', '05-23', '05-24', '05-25'],
          series: {
            inflow: [2460, 2458, 2462, 2459, 2461, 2460, 2457],
            level: [2470, 2472, 2471, 2473, 2470, 2469, 2471],
          },
        },
      },
      'lanzhou-demand': {
        type: 'chart',
        chartData: {
          title: '输入数据概览（兰州断面需水数据）',
          xAxis: ['05-19', '05-20', '05-21', '05-22', '05-23', '05-24', '05-25'],
          series: {
            inflow: [380, 390, 375, 385, 395, 370, 388],
            level: [1525, 1527, 1524, 1526, 1528, 1523, 1525],
          },
        },
      },
      'long-liu-demand': {
        type: 'chart',
        chartData: {
          title: '输入数据概览（龙刘区间用水数据）',
          xAxis: ['05-19', '05-20', '05-21', '05-22', '05-23', '05-24', '05-25'],
          series: {
            inflow: [120, 135, 128, 140, 132, 125, 138],
            level: [1850, 1852, 1851, 1853, 1850, 1849, 1851],
          },
        },
      },
      'inflow-frequency': {
        type: 'chart',
        chartData: {
          title: '输入数据概览（来水频率）',
          xAxis: ['05-19', '05-20', '05-21', '05-22', '05-23', '05-24', '05-25'],
          series: {
            inflow: [75, 82, 68, 79, 85, 72, 80],
            level: [25, 28, 22, 26, 30, 24, 27],
          },
        },
      },

      // ===== 原始表格 =====
      'raw-west-route': {
        type: 'table',
        tableData: {
          title: '西线调水数据',
          columns: [
            { key: 'date', label: '日期' },
            { key: 'designedFlow', label: '设计调水流量', unit: 'm³/s' },
            { key: 'actualFlow', label: '实际调水流量', unit: 'm³/s' },
            { key: 'dailyVolume', label: '日调水量', unit: '万m³' },
            { key: 'cumulativeVolume', label: '累计调水量', unit: '万m³' },
          ],
          rows: [
            { date: '2025-05-19', designedFlow: 300, actualFlow: 280, dailyVolume: 2419, cumulativeVolume: 2419 },
            { date: '2025-05-20', designedFlow: 300, actualFlow: 300, dailyVolume: 2592, cumulativeVolume: 5011 },
            { date: '2025-05-21', designedFlow: 300, actualFlow: 310, dailyVolume: 2678, cumulativeVolume: 7689 },
            { date: '2025-05-22', designedFlow: 300, actualFlow: 290, dailyVolume: 2506, cumulativeVolume: 10195 },
            { date: '2025-05-23', designedFlow: 300, actualFlow: 320, dailyVolume: 2765, cumulativeVolume: 12960 },
            { date: '2025-05-24', designedFlow: 300, actualFlow: 305, dailyVolume: 2635, cumulativeVolume: 15595 },
            { date: '2025-05-25', designedFlow: 300, actualFlow: 295, dailyVolume: 2549, cumulativeVolume: 18144 },
          ],
        },
      },
      'raw-level-boundary': {
        type: 'table',
        tableData: {
          title: '水位上下限',
          columns: [
            { key: 'date', label: '日期' },
            { key: 'upperLimit', label: '水位上限', unit: 'm' },
            { key: 'lowerLimit', label: '水位下限', unit: 'm' },
            { key: 'currentLevel', label: '当前水位', unit: 'm' },
          ],
          rows: [
            { date: '2025-05-19', upperLimit: 2475, lowerLimit: 2450, currentLevel: 2468 },
            { date: '2025-05-20', upperLimit: 2475, lowerLimit: 2450, currentLevel: 2466 },
            { date: '2025-05-21', upperLimit: 2475, lowerLimit: 2450, currentLevel: 2470 },
            { date: '2025-05-22', upperLimit: 2475, lowerLimit: 2450, currentLevel: 2467 },
            { date: '2025-05-23', upperLimit: 2475, lowerLimit: 2450, currentLevel: 2465 },
            { date: '2025-05-24', upperLimit: 2475, lowerLimit: 2450, currentLevel: 2463 },
            { date: '2025-05-25', upperLimit: 2475, lowerLimit: 2450, currentLevel: 2466 },
          ],
        },
      },
      'raw-lanzhou-demand': {
        type: 'table',
        tableData: {
          title: '兰州断面需水数据',
          columns: [
            { key: 'date', label: '日期' },
            { key: 'demandFlow', label: '需水流量', unit: 'm³/s' },
            { key: 'actualFlow', label: '实际流量', unit: 'm³/s' },
            { key: 'satisfaction', label: '满足率', unit: '%' },
          ],
          rows: [
            { date: '2025-05-19', demandFlow: 380, actualFlow: 380, satisfaction: 100 },
            { date: '2025-05-20', demandFlow: 380, actualFlow: 390, satisfaction: 100 },
            { date: '2025-05-21', demandFlow: 380, actualFlow: 375, satisfaction: 98.7 },
            { date: '2025-05-22', demandFlow: 380, actualFlow: 385, satisfaction: 100 },
            { date: '2025-05-23', demandFlow: 380, actualFlow: 395, satisfaction: 100 },
            { date: '2025-05-24', demandFlow: 380, actualFlow: 370, satisfaction: 97.4 },
            { date: '2025-05-25', demandFlow: 380, actualFlow: 388, satisfaction: 100 },
          ],
        },
      },
      'raw-long-liu-demand': {
        type: 'table',
        tableData: {
          title: '龙刘区间用水数据',
          columns: [
            { key: 'date', label: '日期' },
            { key: 'irrigation', label: '灌溉用水', unit: 'm³/s' },
            { key: 'domestic', label: '生活用水', unit: 'm³/s' },
            { key: 'industrial', label: '工业用水', unit: 'm³/s' },
            { key: 'total', label: '合计', unit: 'm³/s' },
          ],
          rows: [
            { date: '2025-05-19', irrigation: 60, domestic: 25, industrial: 35, total: 120 },
            { date: '2025-05-20', irrigation: 68, domestic: 27, industrial: 40, total: 135 },
            { date: '2025-05-21', irrigation: 62, domestic: 26, industrial: 40, total: 128 },
            { date: '2025-05-22', irrigation: 72, domestic: 28, industrial: 40, total: 140 },
            { date: '2025-05-23', irrigation: 65, domestic: 27, industrial: 40, total: 132 },
            { date: '2025-05-24', irrigation: 58, domestic: 25, industrial: 42, total: 125 },
            { date: '2025-05-25', irrigation: 70, domestic: 28, industrial: 40, total: 138 },
          ],
        },
      },
      'raw-inflow-frequency': {
        type: 'table',
        tableData: {
          title: '来水频率',
          columns: [
            { key: 'frequency', label: '频率', unit: '%' },
            { key: 'designedInflow', label: '设计来水', unit: 'm³/s' },
            { key: 'actualInflow', label: '实际来水', unit: 'm³/s' },
            { key: 'deviation', label: '偏差', unit: '%' },
          ],
          rows: [
            { frequency: '10% (丰水年)', designedInflow: 1200, actualInflow: 1250, deviation: 4.2 },
            { frequency: '25% (偏丰年)', designedInflow: 950, actualInflow: 980, deviation: 3.2 },
            { frequency: '50% (平水年)', designedInflow: 780, actualInflow: 800, deviation: 2.6 },
            { frequency: '75% (偏枯年)', designedInflow: 600, actualInflow: 580, deviation: -3.3 },
            { frequency: '90% (枯水年)', designedInflow: 450, actualInflow: 430, deviation: -4.4 },
          ],
        },
      },
    } as MenuContentMap,

    pageState: {
      currentStep: 1,
      activeMenuId: 'inflow-level',
      dateRange: ['2025-05-19', '2025-05-25'],
    } as PageState,
  } as ModelDataResponse,
}
