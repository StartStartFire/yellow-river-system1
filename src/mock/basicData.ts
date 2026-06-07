// ==================== 类型定义 ====================

export interface ReservoirBrief {
  id: string
  name: string
  status: 'normal' | 'warning' | 'abnormal'
}

export interface MetricCardData {
  label: string
  value: number
  unit: string
  change: number // 较昨日变化值，正为上升，负为下降
  isUpBad?: boolean // true: 上升代表不好（如水位上升），false: 上升代表好
}

export interface FeatureWaterLevel {
  name: string
  value: number
  color: string
  dashed?: boolean
}

export interface DamInfo {
  type: string
  crestElevation: number // 坝顶高程 m
  crestLength: number // 坝顶长度 m
  maxHeight: number // 最大坝高 m
}

export interface ReservoirSection {
  title: string
  elevationAxis: number[] // 高程刻度
  levels: FeatureWaterLevel[] // 特征水位线
  currentLevel: number // 当前水位
  inflow: number // 入库流量 m³/s
  outflow: number // 出库流量 m³/s
  dam: DamInfo
}

export interface BaseInfoGroup {
  title: string
  items: { key: string; value: string }[]
}

export interface TurbineItem {
  id: string
  name: string
  status: 'running' | 'stop' | 'maintenance'
  output: number // kW
  flow: number // m³/s
  gateOpen: number // 闸门开度 %
}

export interface GateItem {
  id: string
  name: string
  openPercentage: number // 开度 %
  dischargeFlow: number // 泄洪流量 m³/s
}

export interface EngineeringSummary {
  turbineTotal: number // 机组总数
  turbineRunning: number // 运行中
  gateTotal: number // 闸门总数
  gateOpen: number // 开启数
  totalOutput: number // 当前总出力 kW
}

// ==================== Mock 数据 ====================

// 水库列表（左侧列表用）
export const reservoirList: ReservoirBrief[] = [
  { id: 'longyangxia', name: '龙羊峡', status: 'normal' },
  { id: 'liujiaxia', name: '刘家峡', status: 'normal' },
  { id: 'gongboxia', name: '公伯峡', status: 'warning' },
  { id: 'jishixia', name: '积石峡', status: 'normal' },
  { id: 'qingtongxia', name: '青铜峡', status: 'normal' },
]

// 各水库核心指标
const metricsMap: Record<string, Record<string, MetricCardData>> = {
  longyangxia: {
    waterLevel:   { label: '当前水位',   value: 2472.35, unit: 'm',     change: -0.12, isUpBad: true },
    inflow:       { label: '入库流量',   value: 1250,   unit: 'm³/s',  change: 83,   isUpBad: true },
    outflow:      { label: '出库流量',   value: 1180,   unit: 'm³/s',  change: 60,   isUpBad: false },
    storage:      { label: '蓄水量',     value: 247.58, unit: '亿m³',  change: -1.8, isUpBad: true },
  },
  liujiaxia: {
    waterLevel:   { label: '当前水位',   value: 1738.62, unit: 'm',     change: -0.08, isUpBad: true },
    inflow:       { label: '入库流量',   value: 1060,   unit: 'm³/s',  change: 56,   isUpBad: true },
    outflow:      { label: '出库流量',   value: 1020,   unit: 'm³/s',  change: 42,   isUpBad: false },
    storage:      { label: '蓄水量',     value: 57.32,  unit: '亿m³',  change: -1.1, isUpBad: true },
  },
  gongboxia: {
    waterLevel:   { label: '当前水位',   value: 1986.78, unit: 'm',     change: 0.35, isUpBad: true },
    inflow:       { label: '入库流量',   value: 1100,   unit: 'm³/s',  change: 95,   isUpBad: true },
    outflow:      { label: '出库流量',   value: 1050,   unit: 'm³/s',  change: 40,   isUpBad: false },
    storage:      { label: '蓄水量',     value: 15.62,  unit: '亿m³',  change: 0.42, isUpBad: true },
  },
  jishixia: {
    waterLevel:   { label: '当前水位',   value: 1856.32, unit: 'm',     change: -0.15, isUpBad: true },
    inflow:       { label: '入库流量',   value: 1040,   unit: 'm³/s',  change: 68,   isUpBad: true },
    outflow:      { label: '出库流量',   value: 1010,   unit: 'm³/s',  change: 35,   isUpBad: false },
    storage:      { label: '蓄水量',     value: 12.45,  unit: '亿m³',  change: -0.28, isUpBad: true },
  },
  qingtongxia: {
    waterLevel:   { label: '当前水位',   value: 1156.45, unit: 'm',     change: 0.05, isUpBad: true },
    inflow:       { label: '入库流量',   value: 980,    unit: 'm³/s',  change: 45,   isUpBad: true },
    outflow:      { label: '出库流量',   value: 950,    unit: 'm³/s',  change: 20,   isUpBad: false },
    storage:      { label: '蓄水量',     value: 6.18,   unit: '亿m³',  change: 0.12, isUpBad: true },
  },
}

// 各水库断面数据
const sectionsMap: Record<string, ReservoirSection> = {
  longyangxia: {
    title: '龙羊峡水库断面示意图',
    elevationAxis: [2520, 2500, 2480, 2460, 2440, 2420, 2400],
    levels: [
      { name: '校核洪水位', value: 2505.0, color: '#C084FC' },
      { name: '设计洪水位', value: 2497.0, color: '#F97316' },
      { name: '正常蓄水位', value: 2480.0, color: '#38BDF8' },
      { name: '汛限水位',   value: 2470.0, color: '#EAB308' },
      { name: '死水位',     value: 2410.0, color: '#94A3B8' },
    ],
    currentLevel: 2472.35,
    inflow: 1250,
    outflow: 1180,
    dam: {
      type: '混凝土重力坝',
      crestElevation: 2510.0,
      crestLength: 393.0,
      maxHeight: 178.0,
    },
  },
  liujiaxia: {
    title: '刘家峡水库断面示意图',
    elevationAxis: [1760, 1740, 1720, 1700, 1680, 1660],
    levels: [
      { name: '校核洪水位', value: 1750.0, color: '#C084FC' },
      { name: '设计洪水位', value: 1742.0, color: '#F97316' },
      { name: '正常蓄水位', value: 1738.0, color: '#38BDF8' },
      { name: '汛限水位',   value: 1735.0, color: '#EAB308' },
      { name: '死水位',     value: 1685.0, color: '#94A3B8' },
    ],
    currentLevel: 1738.62,
    inflow: 1060,
    outflow: 1020,
    dam: {
      type: '混凝土双曲拱坝',
      crestElevation: 1754.0,
      crestLength: 240.0,
      maxHeight: 147.0,
    },
  },
  gongboxia: {
    title: '公伯峡水库断面示意图',
    elevationAxis: [2020, 2000, 1980, 1960, 1940, 1920],
    levels: [
      { name: '校核洪水位', value: 2005.0, color: '#C084FC' },
      { name: '设计洪水位', value: 1997.0, color: '#F97316' },
      { name: '正常蓄水位', value: 1988.0, color: '#38BDF8' },
      { name: '汛限水位',   value: 1985.0, color: '#EAB308' },
      { name: '死水位',     value: 1950.0, color: '#94A3B8' },
    ],
    currentLevel: 1986.78,
    inflow: 1100,
    outflow: 1050,
    dam: {
      type: '混凝土双曲拱坝',
      crestElevation: 2002.0,
      crestLength: 260.0,
      maxHeight: 155.0,
    },
  },
  jishixia: {
    title: '积石峡水库断面示意图',
    elevationAxis: [1880, 1860, 1840, 1820, 1800, 1780],
    levels: [
      { name: '校核洪水位', value: 1870.0, color: '#C084FC' },
      { name: '设计洪水位', value: 1862.0, color: '#F97316' },
      { name: '正常蓄水位', value: 1858.0, color: '#38BDF8' },
      { name: '汛限水位',   value: 1855.0, color: '#EAB308' },
      { name: '死水位',     value: 1820.0, color: '#94A3B8' },
    ],
    currentLevel: 1856.32,
    inflow: 1040,
    outflow: 1010,
    dam: {
      type: '混凝土重力坝',
      crestElevation: 1868.0,
      crestLength: 210.0,
      maxHeight: 138.0,
    },
  },
  qingtongxia: {
    title: '青铜峡水库断面示意图',
    elevationAxis: [1180, 1160, 1140, 1120, 1100, 1080],
    levels: [
      { name: '校核洪水位', value: 1168.0, color: '#C084FC' },
      { name: '设计洪水位', value: 1160.0, color: '#F97316' },
      { name: '正常蓄水位', value: 1157.0, color: '#38BDF8' },
      { name: '汛限水位',   value: 1155.0, color: '#EAB308' },
      { name: '死水位',     value: 1130.0, color: '#94A3B8' },
    ],
    currentLevel: 1156.45,
    inflow: 980,
    outflow: 950,
    dam: {
      type: '碾压混凝土重力坝',
      crestElevation: 1162.0,
      crestLength: 365.0,
      maxHeight: 52.0,
    },
  },
}

// 各水库基础信息
const baseInfoMap: Record<string, BaseInfoGroup[]> = {
  longyangxia: [
    {
      title: '工程属性',
      items: [
        { key: '水库名称', value: '龙羊峡水库' },
        { key: '水库编码', value: 'B61021010' },
        { key: '所属流域', value: '黄河上游' },
        { key: '所在水系', value: '龙羊峡－刘家村河段' },
        { key: '水库类型', value: '多年调节水库' },
        { key: '坝型', value: '混凝土重力坝' },
        { key: '坝顶高程', value: '2510.00 m' },
        { key: '坝顶长度', value: '393.00 m' },
        { key: '最大坝高', value: '178.00 m' },
        { key: '装机容量', value: '1280 MW' },
        { key: '机组台数', value: '4 台' },
      ],
    },
    {
      title: '特征水位',
      items: [
        { key: '正常蓄水位', value: '2480.00 m' },
        { key: '汛限水位', value: '2470.00 m' },
        { key: '死水位', value: '2410.00 m' },
        { key: '设计洪水位（P=2%）', value: '2497.00 m' },
        { key: '校核洪水位（P=0.2%）', value: '2505.00 m' },
      ],
    },
    {
      title: '调度规则',
      items: [
        { key: '调度目标', value: '发电为主，兼顾防洪、灌溉' },
        { key: '汛期时段', value: '6月1日 — 10月31日' },
        { key: '生态下泄流量', value: '≥ 80 m³/s' },
      ],
    },
  ],
  liujiaxia: [
    {
      title: '工程属性',
      items: [
        { key: '水库名称', value: '刘家峡水库' },
        { key: '水库编码', value: 'B61031010' },
        { key: '所属流域', value: '黄河上游' },
        { key: '所在水系', value: '大通河汇入处' },
        { key: '水库类型', value: '多年调节水库' },
        { key: '坝型', value: '混凝土双曲拱坝' },
        { key: '坝顶高程', value: '1754.00 m' },
        { key: '坝顶长度', value: '240.00 m' },
        { key: '最大坝高', value: '147.00 m' },
        { key: '装机容量', value: '1225 MW' },
        { key: '机组台数', value: '6 台' },
      ],
    },
    {
      title: '特征水位',
      items: [
        { key: '正常蓄水位', value: '1738.00 m' },
        { key: '汛限水位', value: '1735.00 m' },
        { key: '死水位', value: '1685.00 m' },
        { key: '设计洪水位（P=2%）', value: '1742.00 m' },
        { key: '校核洪水位（P=0.2%）', value: '1750.00 m' },
      ],
    },
    {
      title: '调度规则',
      items: [
        { key: '调度目标', value: '发电、防洪、防凌综合调度' },
        { key: '汛期时段', value: '6月1日 — 9月30日' },
        { key: '生态下泄流量', value: '≥ 60 m³/s' },
      ],
    },
  ],
  gongboxia: [
    {
      title: '工程属性',
      items: [
        { key: '水库名称', value: '公伯峡水库' },
        { key: '水库编码', value: 'B61041010' },
        { key: '所属流域', value: '黄河上游' },
        { key: '所在水系', value: '公伯峡峡谷段' },
        { key: '水库类型', value: '年调节水库' },
        { key: '坝型', value: '混凝土双曲拱坝' },
        { key: '坝顶高程', value: '2002.00 m' },
        { key: '坝顶长度', value: '260.00 m' },
        { key: '最大坝高', value: '155.00 m' },
        { key: '装机容量', value: '750 MW' },
        { key: '机组台数', value: '5 台' },
      ],
    },
    {
      title: '特征水位',
      items: [
        { key: '正常蓄水位', value: '1988.00 m' },
        { key: '汛限水位', value: '1985.00 m' },
        { key: '死水位', value: '1950.00 m' },
        { key: '设计洪水位（P=2%）', value: '1997.00 m' },
        { key: '校核洪水位（P=0.2%）', value: '2005.00 m' },
      ],
    },
    {
      title: '调度规则',
      items: [
        { key: '调度目标', value: '发电为主，兼顾防洪' },
        { key: '汛期时段', value: '6月1日 — 9月30日' },
        { key: '生态下泄流量', value: '≥ 50 m³/s' },
      ],
    },
  ],
  jishixia: [
    {
      title: '工程属性',
      items: [
        { key: '水库名称', value: '积石峡水库' },
        { key: '水库编码', value: 'B61051010' },
        { key: '所属流域', value: '黄河上游' },
        { key: '所在水系', value: '积石峡峡谷段' },
        { key: '水库类型', value: '年调节水库' },
        { key: '坝型', value: '混凝土重力坝' },
        { key: '坝顶高程', value: '1868.00 m' },
        { key: '坝顶长度', value: '210.00 m' },
        { key: '最大坝高', value: '138.00 m' },
        { key: '装机容量', value: '1020 MW' },
        { key: '机组台数', value: '3 台' },
      ],
    },
    {
      title: '特征水位',
      items: [
        { key: '正常蓄水位', value: '1858.00 m' },
        { key: '汛限水位', value: '1855.00 m' },
        { key: '死水位', value: '1820.00 m' },
        { key: '设计洪水位（P=2%）', value: '1862.00 m' },
        { key: '校核洪水位（P=0.2%）', value: '1870.00 m' },
      ],
    },
    {
      title: '调度规则',
      items: [
        { key: '调度目标', value: '发电为主，兼顾防洪、防凌' },
        { key: '汛期时段', value: '6月1日 — 9月30日' },
        { key: '生态下泄流量', value: '≥ 45 m³/s' },
      ],
    },
  ],
  qingtongxia: [
    {
      title: '工程属性',
      items: [
        { key: '水库名称', value: '青铜峡水库' },
        { key: '水库编码', value: 'B61061010' },
        { key: '所属流域', value: '黄河上游' },
        { key: '所在水系', value: '青铜峡峡谷段' },
        { key: '水库类型', value: '日调节水库' },
        { key: '坝型', value: '碾压混凝土重力坝' },
        { key: '坝顶高程', value: '1162.00 m' },
        { key: '坝顶长度', value: '365.00 m' },
        { key: '最大坝高', value: '52.00 m' },
        { key: '装机容量', value: '272 MW' },
        { key: '机组台数', value: '8 台' },
      ],
    },
    {
      title: '特征水位',
      items: [
        { key: '正常蓄水位', value: '1157.00 m' },
        { key: '汛限水位', value: '1155.00 m' },
        { key: '死水位', value: '1130.00 m' },
        { key: '设计洪水位（P=2%）', value: '1160.00 m' },
        { key: '校核洪水位（P=0.2%）', value: '1168.00 m' },
      ],
    },
    {
      title: '调度规则',
      items: [
        { key: '调度目标', value: '灌溉为主，兼顾发电、防洪' },
        { key: '汛期时段', value: '6月15日 — 9月15日' },
        { key: '生态下泄流量', value: '≥ 35 m³/s' },
      ],
    },
  ],
}

// 各水库水情过程数据
const processDataMap: Record<string, { dates: string[]; levels: number[]; inflows: number[]; outflows: number[] }> = {
  longyangxia: {
    dates: ['05-10', '05-11', '05-12', '05-13', '05-14', '05-15', '05-16'],
    levels: [2470.15, 2470.82, 2471.20, 2471.58, 2471.95, 2472.10, 2472.35],
    inflows: [835, 920, 1050, 1100, 1180, 1220, 1250],
    outflows: [720, 800, 900, 980, 1050, 1120, 1180],
  },
  liujiaxia: {
    dates: ['05-10', '05-11', '05-12', '05-13', '05-14', '05-15', '05-16'],
    levels: [1736.80, 1737.10, 1737.45, 1737.80, 1738.15, 1738.38, 1738.62],
    inflows: [680, 750, 860, 920, 980, 1030, 1060],
    outflows: [620, 680, 760, 840, 920, 980, 1020],
  },
  gongboxia: {
    dates: ['05-10', '05-11', '05-12', '05-13', '05-14', '05-15', '05-16'],
    levels: [1985.10, 1985.45, 1985.80, 1986.10, 1986.40, 1986.60, 1986.78],
    inflows: [720, 810, 900, 960, 1020, 1070, 1100],
    outflows: [680, 740, 820, 880, 940, 1000, 1050],
  },
  jishixia: {
    dates: ['05-10', '05-11', '05-12', '05-13', '05-14', '05-15', '05-16'],
    levels: [1854.80, 1855.10, 1855.40, 1855.70, 1856.00, 1856.15, 1856.32],
    inflows: [650, 730, 820, 890, 960, 1010, 1040],
    outflows: [600, 680, 760, 830, 900, 960, 1010],
  },
  qingtongxia: {
    dates: ['05-10', '05-11', '05-12', '05-13', '05-14', '05-15', '05-16'],
    levels: [1155.20, 1155.45, 1155.68, 1155.90, 1156.10, 1156.28, 1156.45],
    inflows: [580, 650, 730, 810, 880, 940, 980],
    outflows: [550, 620, 700, 770, 840, 900, 950],
  },
}

// 各水库工情信息
const engineeringMap: Record<string, { summary: EngineeringSummary; turbines: TurbineItem[]; gates: GateItem[] }> = {
  longyangxia: {
    summary: { turbineTotal: 4, turbineRunning: 3, gateTotal: 6, gateOpen: 2, totalOutput: 960000 },
    turbines: [
      { id: 'L-1', name: '1号机组', status: 'running', output: 320, flow: 340, gateOpen: 85 },
      { id: 'L-2', name: '2号机组', status: 'running', output: 310, flow: 330, gateOpen: 82 },
      { id: 'L-3', name: '3号机组', status: 'running', output: 315, flow: 335, gateOpen: 84 },
      { id: 'L-4', name: '4号机组', status: 'maintenance', output: 0, flow: 0, gateOpen: 0 },
    ],
    gates: [
      { id: 'L-G1', name: '1号泄洪闸', openPercentage: 30, dischargeFlow: 280 },
      { id: 'L-G2', name: '2号泄洪闸', openPercentage: 25, dischargeFlow: 240 },
      { id: 'L-G3', name: '3号泄洪闸', openPercentage: 0, dischargeFlow: 0 },
      { id: 'L-G4', name: '4号泄洪闸', openPercentage: 0, dischargeFlow: 0 },
      { id: 'L-G5', name: '5号泄洪闸', openPercentage: 0, dischargeFlow: 0 },
      { id: 'L-G6', name: '6号泄洪闸', openPercentage: 0, dischargeFlow: 0 },
    ],
  },
  liujiaxia: {
    summary: { turbineTotal: 6, turbineRunning: 5, gateTotal: 8, gateOpen: 3, totalOutput: 882000 },
    turbines: [
      { id: 'J-1', name: '1号机组', status: 'running', output: 180, flow: 200, gateOpen: 80 },
      { id: 'J-2', name: '2号机组', status: 'running', output: 175, flow: 195, gateOpen: 78 },
      { id: 'J-3', name: '3号机组', status: 'running', output: 178, flow: 198, gateOpen: 81 },
      { id: 'J-4', name: '4号机组', status: 'running', output: 170, flow: 190, gateOpen: 76 },
      { id: 'J-5', name: '5号机组', status: 'running', output: 172, flow: 192, gateOpen: 77 },
      { id: 'J-6', name: '6号机组', status: 'stop', output: 0, flow: 0, gateOpen: 0 },
    ],
    gates: [
      { id: 'J-G1', name: '1号泄洪闸', openPercentage: 35, dischargeFlow: 320 },
      { id: 'J-G2', name: '2号泄洪闸', openPercentage: 28, dischargeFlow: 260 },
      { id: 'J-G3', name: '3号泄洪闸', openPercentage: 22, dischargeFlow: 200 },
      { id: 'J-G4', name: '4号泄洪闸', openPercentage: 0, dischargeFlow: 0 },
      { id: 'J-G5', name: '5号泄洪闸', openPercentage: 0, dischargeFlow: 0 },
      { id: 'J-G6', name: '6号泄洪闸', openPercentage: 0, dischargeFlow: 0 },
      { id: 'J-G7', name: '7号泄洪闸', openPercentage: 0, dischargeFlow: 0 },
      { id: 'J-G8', name: '8号泄洪闸', openPercentage: 0, dischargeFlow: 0 },
    ],
  },
}

// 导出统一方法
export function getMetrics(reservoirId: string): MetricCardData[] {
  return Object.values(metricsMap[reservoirId] || metricsMap.longyangxia)
}

export function getSection(reservoirId: string): ReservoirSection {
  return sectionsMap[reservoirId] || sectionsMap.longyangxia
}

export function getBaseInfo(reservoirId: string): BaseInfoGroup[] {
  return baseInfoMap[reservoirId] || baseInfoMap.longyangxia
}

export function getProcessData(reservoirId: string) {
  return processDataMap[reservoirId] || processDataMap.longyangxia
}

export function getEngineeringInfo(reservoirId: string) {
  return engineeringMap[reservoirId] || engineeringMap.longyangxia
}
