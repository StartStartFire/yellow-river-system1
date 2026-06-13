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
          { id: 'long-liu-inflow', name: '龙刘区间来水', icon: 'inflow' },
        ],
      },
      {
        groupName: '原始表格',
        children: [
          { id: 'raw-inflow-level', name: '入库与水位', icon: 'table' },
          { id: 'raw-west-route', name: '西线调水数据', icon: 'table' },
          { id: 'raw-level-boundary', name: '水位上下限', icon: 'table' },
          { id: 'raw-lanzhou-demand', name: '兰州断面需水数据', icon: 'table' },
          { id: 'raw-long-liu-demand', name: '龙刘区间用水数据', icon: 'table' },
          { id: 'raw-long-liu-inflow', name: '龙刘区间来水', icon: 'table' },
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
      'long-liu-inflow': {
        type: 'chart',
        chartData: {
          title: '输入数据概览（龙刘区间来水）',
          xAxis: ['05-19', '05-20', '05-21', '05-22', '05-23', '05-24', '05-25'],
          series: {
            inflow: [320, 380, 410, 360, 340, 395, 370],
            level: [1865, 1868, 1870, 1867, 1866, 1869, 1867],
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
      'raw-inflow-level': {
        type: 'table',
        tableData: {
          title: '入库与水位原始数据',
          columns: [
            { key: 'date', label: '日期' },
            { key: 'inflow', label: '入库流量', unit: 'm³/s' },
            { key: 'level', label: '水位', unit: 'm' },
          ],
          rows: [
            { date: '2025-05-19', inflow: 430, level: 2486 },
            { date: '2025-05-20', inflow: 560, level: 2484 },
            { date: '2025-05-21', inflow: 820, level: 2488 },
            { date: '2025-05-22', inflow: 620, level: 2486 },
            { date: '2025-05-23', inflow: 420, level: 2484 },
            { date: '2025-05-24', inflow: 340, level: 2481 },
            { date: '2025-05-25', inflow: 460, level: 2485 },
          ],
        },
      },
      'raw-long-liu-inflow': {
        type: 'table',
        tableData: {
          title: '龙刘区间来水原始数据',
          columns: [
            { key: 'date', label: '日期' },
            { key: 'inflow', label: '来水流量', unit: 'm³/s' },
            { key: 'level', label: '水位', unit: 'm' },
          ],
          rows: [
            { date: '2025-05-19', inflow: 320, level: 1865 },
            { date: '2025-05-20', inflow: 380, level: 1868 },
            { date: '2025-05-21', inflow: 410, level: 1870 },
            { date: '2025-05-22', inflow: 360, level: 1867 },
            { date: '2025-05-23', inflow: 340, level: 1866 },
            { date: '2025-05-24', inflow: 395, level: 1869 },
            { date: '2025-05-25', inflow: 370, level: 1867 },
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

// ==================== Step 2: 基础配置 Mock 数据 ====================

export interface ReservoirGroup {
  id: string
  name: string
  reservoirs: string[]
}

export interface DispatchObjective {
  id: string
  name: string
  description: string
  icon: string
}

export interface BasicConfigState {
  currentStep: number
  startTime: string
  endTime: string
  timeStep: string
  scheduleFrequency: string
  totalPeriods: number
  schemeName: string
  selectedReservoirGroup: string
  selectedObjectives: string[]
  constraintCount: number
}

export interface ConstraintSummaryData {
  count: number
  description: string
  constraints: string[]
}

export const basicConfigState = {
  code: 200,
  message: 'success',
  data: {
    currentStep: 2,
    startTime: '2025-05-16',
    endTime: '2025-05-26',
    timeStep: '每日',
    scheduleFrequency: '每月一次',
    totalPeriods: 11,
    schemeName: '',
    selectedReservoirGroup: 'long-liu',
    selectedObjectives: ['flood-control'],
    constraintCount: 12,
  } as BasicConfigState,
}

export const reservoirGroups = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'long-liu',
      name: '龙刘组合',
      reservoirs: ['龙羊峡水库', '刘家峡水库'],
    },
    {
      id: 'long-liu-hei',
      name: '龙刘黑组合',
      reservoirs: ['龙羊峡水库', '刘家峡水库', '黑山峡水库'],
    },
    {
      id: 'long-liu-qing',
      name: '龙刘青组合',
      reservoirs: ['龙羊峡水库', '刘家峡水库', '青铜峡水库'],
    },
    {
      id: 'long-liu-gong',
      name: '龙刘公组合',
      reservoirs: ['龙羊峡水库', '刘家峡水库', '公伯峡水库'],
    },
    {
      id: 'all',
      name: '全部水库组合',
      reservoirs: ['龙羊峡水库', '刘家峡水库', '公伯峡水库', '积石峡水库', '青铜峡水库'],
    },
  ] as ReservoirGroup[],
}

export const dispatchObjectives = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'flood-control',
      name: '防洪安全',
      description: '保障水库防洪安全，控制水位与下泄流量',
      icon: 'shield',
    },
    {
      id: 'power-generation',
      name: '兴利发电',
      description: '优化发电出力，提高综合经济效益',
      icon: 'flash',
    },
    {
      id: 'ecology',
      name: '生态保护',
      description: '保障生态流量，维护下游生态环境',
      icon: 'leaf',
    },
  ] as DispatchObjective[],
}

export const constraintSummary = {
  code: 200,
  message: 'success',
  data: {
    count: 12,
    description: '约束条件将影响调度方案的可行性与优化结果',
    constraints: [
      '水位上限约束',
      '水位下限约束',
      '汛限水位约束',
      '最小生态流量约束',
      '最大发电出力约束',
      '最小下泄流量约束',
      '冲沙流量约束',
      '库容边界约束',
      '入库流量边界约束',
      '出库流量边界约束',
      '水量平衡约束',
      '梯级协同约束',
    ],
  } as ConstraintSummaryData,
}

// ==================== Step 3: 模型算法 Mock 数据 ====================

export interface DispatchModel {
  id: string
  name: string
  supportedAlgorithms: string[]
}

export interface OptimizationAlgorithm {
  id: string
  name: string
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

export const modelAlgorithmState = {
  code: 200,
  message: 'success',
  data: {
    currentStep: 3,
    selectedModel: 'lro',
    selectedAlgorithm: 'nsga2',
    parameters: {
      populationSize: 200,
      iterationCount: 500,
      crossoverRate: 0.9,
      mutationRate: 0.1,
      eliteRate: 0.05,
      crowdingFactor: 2.0,
    },
  } as ModelAlgorithmState,
}

export const dispatchModels = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'lro',
      name: '水库群优化调度模型',
      supportedAlgorithms: ['nsga2', 'pso'],
    },
    {
      id: 'multi_objective_stress',
      name: '多目标协同胁迫模型',
      supportedAlgorithms: ['nsga2', 'pso'],
    },
    {
      id: 'multi_objective_dispatch',
      name: '多目标优化调度模型',
      supportedAlgorithms: ['paem'],
    },
    {
      id: 'water_sediment_realtime',
      name: '水沙实时调度模型',
      supportedAlgorithms: ['nsga3'],
    },
  ] as DispatchModel[],
}

export const optimizationAlgorithms = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'nsga2',
      name: 'NSGA-II 多目标遗传算法',
    },
    {
      id: 'pso',
      name: 'PSO 粒子群优化算法',
    },
    {
      id: 'paem',
      name: 'PAEM 逐步逼近评价方法',
    },
    {
      id: 'nsga3',
      name: 'NSGA-III 多目标遗传算法',
    },
  ] as OptimizationAlgorithm[],
}

export const algorithmParameters = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'populationSize',
      name: '种群规模',
      value: 200,
      min: 50,
      max: 1000,
      step: 10,
      description: '种群规模越大，搜索更充分，结果更稳定，但计算耗时增加；种群规模越小，计算更快，但容易遗漏优良解。',
    },
    {
      id: 'iterationCount',
      name: '迭代次数',
      value: 500,
      min: 100,
      max: 2000,
      step: 50,
      description: '迭代次数越大，收敛更充分，但运行时间更长；迭代次数越小，运行更快，但可能未充分收敛。',
    },
    {
      id: 'crossoverRate',
      name: '交叉概率 Pc',
      value: 0.9,
      min: 0.5,
      max: 1.0,
      step: 0.01,
      description: '交叉概率越高，种群探索能力更强；交叉概率越低，解集变化较慢，可能影响搜索效率。',
    },
    {
      id: 'mutationRate',
      name: '变异概率 Pm',
      value: 0.1,
      min: 0.01,
      max: 0.3,
      step: 0.01,
      description: '变异概率越高，跳出局部最优能力更强，但过高会导致结果波动；变异概率越低，结果更稳定，但探索不足。',
    },
    {
      id: 'eliteRate',
      name: '精英保留比例',
      value: 0.05,
      min: 0.01,
      max: 0.2,
      step: 0.01,
      description: '精英保留比例越高，保留优良解更多，但可能降低种群多样性；精英保留比例越低，多样性更高，但优良解可能丢失。',
    },
    {
      id: 'crowdingFactor',
      name: '拥挤度因子',
      value: 2.0,
      min: 1.0,
      max: 3.0,
      step: 0.1,
      description: '拥挤度因子用于控制解集分布的均匀性，数值越大越强调解集分散性，数值越小越强调局部收敛效果。',
    },
  ] as AlgorithmParameter[],
}

// ==================== Step 4: 场景约束 Mock 数据 ====================

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

export const scenarioConstraintState = {
  code: 200,
  message: 'success',
  data: {
    currentStep: 4,
    scenarioType: 'typical',
    scenarioDescription:
      '典型场景基于历史调度经验与水文条件组合，用于评估不同调度策略下的系统响应。适用于常规调度方案的模拟与优化分析。',
    params: {
      westRoute: 'all',
      sedimentFlow: '1800',
      backboneStatus: 'normal',
      sedimentRequirement: 'min',
      ecologicalFlow: 'plan',
    },
  } as ScenarioConstraintState,
}

export const scenarioTypeOptions = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'typical',
      name: '典型场景',
      description: '基于历史调度经验与水文条件组合形成的预设场景',
    },
    {
      id: 'custom',
      name: '自定义场景',
      description: '由用户自行定义调度场景和约束参数',
    },
  ],
}

export const scenarioParams = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'westRoute',
      name: '西线调水',
      value: 'all',
      options: [
        { label: '无', value: 'none' },
        { label: '上线', value: 'upper' },
        { label: '下线', value: 'lower' },
        { label: '上下线同引', value: 'both' },
        { label: '全有', value: 'all' },
      ],
    },
    {
      id: 'sedimentFlow',
      name: '调沙流量',
      value: '1800',
      options: [
        { label: '1600 m³/s', value: '1600' },
        { label: '1800 m³/s', value: '1800' },
        { label: '2000 m³/s', value: '2000' },
        { label: '自定义', value: 'custom' },
      ],
    },
    {
      id: 'backboneStatus',
      name: '骨干工程运行状态',
      value: 'normal',
      options: [
        { label: '正常运行', value: 'normal' },
        { label: '限制运行', value: 'limited' },
        { label: '检修停运', value: 'maintenance' },
        { label: '应急运行', value: 'emergency' },
      ],
    },
    {
      id: 'sedimentRequirement',
      name: '冲沙流量要求',
      value: 'min',
      options: [
        { label: '不考虑', value: 'none' },
        { label: '满足最小冲沙流量', value: 'min' },
        { label: '满足推荐冲沙流量', value: 'recommended' },
        { label: '自定义冲沙流量', value: 'custom' },
      ],
    },
    {
      id: 'ecologicalFlow',
      name: '下游生态流量',
      value: 'plan',
      options: [
        { label: '不考虑', value: 'none' },
        { label: '按方案执行', value: 'plan' },
        { label: '最低生态需水', value: 'minimum' },
        { label: '强化生态保障', value: 'enhanced' },
        { label: '自定义', value: 'custom' },
      ],
    },
  ] as ScenarioParam[],
}

export const constraintList = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'level',
      name: '水库水位约束',
      description: '龙羊峡水库、刘家峡水库、青铜峡水库',
      status: 'configured',
    },
    {
      id: 'flow',
      name: '流量过程约束',
      description: '下游控制断面流量满足过程要求',
      status: 'configured',
    },
    {
      id: 'flood',
      name: '防洪安全约束',
      description: '水库汛限水位约束，洪水期防洪安全',
      status: 'configured',
    },
    {
      id: 'power',
      name: '发电约束',
      description: '满足发电任务要求，保证电站出力',
      status: 'configured',
    },
    {
      id: 'sediment',
      name: '泥沙冲淤约束',
      description: '满足最小冲沙流量要求',
      status: 'configured',
    },
    {
      id: 'ecology',
      name: '生态流量约束',
      description: '下游生态流量不低于最小生态需水',
      status: 'configured',
    },
    {
      id: 'engineering',
      name: '工程运行约束',
      description: '泵站、闸门等工程运行状态约束',
      status: 'configured',
    },
    {
      id: 'balance',
      name: '水量平衡约束',
      description: '系统水量平衡，满足水资源可利用量',
      status: 'configured',
    },
  ] as ConstraintItem[],
}

// ==================== Step 5: 配置汇总 Mock 数据 ====================

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

export const configSummaryState = {
  code: 200,
  message: 'success',
  data: {
    currentStep: 5,
    selectedPlanIds: ['plan-001', 'plan-002', 'plan-003'],
    total: 24,
    pageSize: 10,
    currentPage: 1,
    estimatedTime: '02:18:45',
    planCount: 24,
  } as ConfigSummaryState,
}

const allPlans: ConfigPlan[] = [
  { id: 'plan-001', index: 1, name: '防洪调度方案_20250516_A', model: '联动水库优化调度模型（LRO）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_主汛期', selected: true },
  { id: 'plan-002', index: 2, name: '防洪调度方案_20250515_B', model: '联动水库优化调度模型（LRO）', algorithm: '改进粒子群算法（PSO）', scenario: '极端场景_设计洪水', selected: true },
  { id: 'plan-003', index: 3, name: '兴利调度方案_20250514_C', model: '来水预报模型（LSTM）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_平水年', selected: true },
  { id: 'plan-004', index: 4, name: '生态调度方案_20250513_D', model: '水库调蓄模型（MIKE11）', algorithm: 'Pareto最优解集算法', scenario: '生态场景_生态流量保障', selected: false },
  { id: 'plan-005', index: 5, name: '防洪调度方案_20250512_E', model: '联动水库优化调度模型（LRO）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_主汛期', selected: false },
  { id: 'plan-006', index: 6, name: '兴利调度方案_20250511_F', model: '来水预报模型（LSTM）', algorithm: '差分进化算法', scenario: '典型场景_枯水年', selected: false },
  { id: 'plan-007', index: 7, name: '生态调度方案_20250510_G', model: '水库调蓄模型（MIKE11）', algorithm: 'Pareto最优解集算法', scenario: '生态场景_生态流量保障', selected: false },
  { id: 'plan-008', index: 8, name: '防洪调度方案_20250509_H', model: '联动水库优化调度模型（LRO）', algorithm: '改进粒子群算法（PSO）', scenario: '极端场景_设计洪水', selected: false },
  { id: 'plan-009', index: 9, name: '兴利调度方案_20250508_I', model: '来水预报模型（LSTM）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_平水年', selected: false },
  { id: 'plan-010', index: 10, name: '生态调度方案_20250507_J', model: '水库调蓄模型（MIKE11）', algorithm: '差分进化算法', scenario: '典型场景_枯水年', selected: false },
  { id: 'plan-011', index: 11, name: '防洪调度方案_20250506_K', model: '联动水库优化调度模型（LRO）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_主汛期', selected: false },
  { id: 'plan-012', index: 12, name: '兴利调度方案_20250505_L', model: '来水预报模型（LSTM）', algorithm: '改进粒子群算法（PSO）', scenario: '典型场景_平水年', selected: false },
  { id: 'plan-013', index: 13, name: '生态调度方案_20250504_M', model: '水库调蓄模型（MIKE11）', algorithm: 'Pareto最优解集算法', scenario: '生态场景_生态流量保障', selected: false },
  { id: 'plan-014', index: 14, name: '防洪调度方案_20250503_N', model: '联动水库优化调度模型（LRO）', algorithm: '改进粒子群算法（PSO）', scenario: '极端场景_设计洪水', selected: false },
  { id: 'plan-015', index: 15, name: '兴利调度方案_20250502_O', model: '来水预报模型（LSTM）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_枯水年', selected: false },
  { id: 'plan-016', index: 16, name: '生态调度方案_20250501_P', model: '水库调蓄模型（MIKE11）', algorithm: '差分进化算法', scenario: '典型场景_平水年', selected: false },
  { id: 'plan-017', index: 17, name: '防洪调度方案_20250430_Q', model: '联动水库优化调度模型（LRO）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_主汛期', selected: false },
  { id: 'plan-018', index: 18, name: '兴利调度方案_20250429_R', model: '来水预报模型（LSTM）', algorithm: '改进粒子群算法（PSO）', scenario: '典型场景_平水年', selected: false },
  { id: 'plan-019', index: 19, name: '生态调度方案_20250428_S', model: '水库调蓄模型（MIKE11）', algorithm: 'Pareto最优解集算法', scenario: '生态场景_生态流量保障', selected: false },
  { id: 'plan-020', index: 20, name: '防洪调度方案_20250427_T', model: '联动水库优化调度模型（LRO）', algorithm: '差分进化算法', scenario: '典型场景_主汛期', selected: false },
  { id: 'plan-021', index: 21, name: '兴利调度方案_20250426_U', model: '来水预报模型（LSTM）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '极端场景_设计洪水', selected: false },
  { id: 'plan-022', index: 22, name: '生态调度方案_20250425_V', model: '水库调蓄模型（MIKE11）', algorithm: '改进粒子群算法（PSO）', scenario: '典型场景_枯水年', selected: false },
  { id: 'plan-023', index: 23, name: '防洪调度方案_20250424_W', model: '联动水库优化调度模型（LRO）', algorithm: 'Pareto最优解集算法', scenario: '生态场景_生态流量保障', selected: false },
  { id: 'plan-024', index: 24, name: '兴利调度方案_20250423_X', model: '来水预报模型（LSTM）', algorithm: 'NSGA-II 多目标遗传算法', scenario: '典型场景_平水年', selected: false },
]

export const configPlanList = {
  code: 200,
  message: 'success',
  data: allPlans,
}

export const modelDistribution = {
  code: 200,
  message: 'success',
  data: [
    { name: 'LRO模型', value: 10, percent: 41.7 },
    { name: 'LSTM模型', value: 6, percent: 25.0 },
    { name: 'MIKE11模型', value: 8, percent: 33.3 },
  ] as DistributionItem[],
}

export const algorithmDistribution = {
  code: 200,
  message: 'success',
  data: [
    { name: 'NSGA-II', value: 10, percent: 41.7 },
    { name: '改进PSO', value: 7, percent: 29.2 },
    { name: 'Pareto算法', value: 4, percent: 16.7 },
    { name: '差分进化', value: 3, percent: 12.5 },
  ] as DistributionItem[],
}
