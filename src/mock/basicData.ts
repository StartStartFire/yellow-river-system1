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

// ==================== API 统一响应类型 ====================
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// ==================== Mock 数据（统一 API 响应格式） ====================

// 水库列表（左侧列表用）
export const reservoirList: ApiResponse<ReservoirBrief[]> = {
  code: 200,
  message: 'success',
  data: [
    { id: 'longyangxia', name: '龙羊峡', status: 'normal' },
    { id: 'liujiaxia', name: '刘家峡', status: 'normal' },
    { id: 'gongboxia', name: '公伯峡', status: 'warning' },
    { id: 'jishixia', name: '积石峡', status: 'normal' },
    { id: 'qingtongxia', name: '青铜峡', status: 'normal' },
  ],
}

// 各水库核心指标
export const metricsMap: Record<string, Record<string, MetricCardData>> = {
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
      title: '调度规则',
      items: [
        { key: '防洪调度', value: '当入库流量Q≥2000m³/s时，启用防洪调度；汛限水位2470m，超限加大泄量' },
        { key: '发电调度', value: '当库水位≥2460m且电网需求≥800MW时，优先满发；水位＜2430m时减负荷运行' },
        { key: '生态调度', value: '非汛期下泄流量≥80m³/s；鱼类产卵期（4-6月）维持日变幅≤15%' },
        { key: '供水调度', value: '下游灌溉需水时，在保证生态基流前提下加大下泄；优先保障生活用水' },
        { key: '凌汛调度', value: '11月下旬至次年3月，控制下泄流量平稳过渡，防止冰塞冰坝' },
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
      title: '调度规则',
      items: [
        { key: '防洪调度', value: '入库流量Q≥1500m³/s时启动预泄；汛限水位1735m，超限按调度令执行' },
        { key: '发电调度', value: '来水偏丰年优先发电，水位≥1730m时满发；枯水年保电出力≥600MW' },
        { key: '生态调度', value: '全年下泄≥60m³/s；5-6月鱼类繁殖期加大至100m³/s并控制日变幅' },
        { key: '防凌调度', value: '12月至次年2月控制刘家峡至包头河段平稳封河，下泄流量波动≤5%' },
        { key: '供水调度', value: '兰州市生活取水口上游维持水位≥1728m，保障城市供水安全' },
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
      title: '调度规则',
      items: [
        { key: '防洪调度', value: '入库Q≥1200m³/s时加大泄量预泄；汛限水位1985m，超限按防汛指令执行' },
        { key: '发电调度', value: '水位≥1975m且电网需求≥500MW时满发；水位＜1960m时限负荷运行' },
        { key: '生态调度', value: '非汛期下泄≥50m³/s；春季融冰期维持流量平稳，日变幅≤10%' },
        { key: '联合调度', value: '服从龙羊峡、刘家峡水库统一调度指令，做好梯级衔接' },
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
      title: '调度规则',
      items: [
        { key: '防洪调度', value: '入库Q≥1000m³/s时启动防洪预案；汛限水位1855m，超限逐步加大泄量' },
        { key: '发电调度', value: '水位≥1845m时优先发电；水位＜1830m时减机运行保库容' },
        { key: '生态调度', value: '全年下泄≥45m³/s；关注下游河段生态敏感期用水需求' },
        { key: '防凌调度', value: '冬季控制下泄平稳，配合上游水库防凌调度，防止冰情发展' },
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
      title: '调度规则',
      items: [
        { key: '防洪调度', value: '入库Q≥2500m³/s时启用泄洪闸；汛限水位1155m，超限敞泄' },
        { key: '灌溉调度', value: '灌溉期（4-10月）优先保障下游灌区引水，引水量按灌溉计划执行' },
        { key: '发电调度', value: '利用灌溉尾水发电，来水不足时按灌溉优先、发电次之原则安排' },
        { key: '生态调度', value: '非灌溉期下泄≥35m³/s；宁蒙河段生态用水由上游水库统一调配' },
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

// 导出统一方法（返回 API 响应格式）
export function getMetrics(reservoirId: string): ApiResponse<MetricCardData[]> {
  return {
    code: 200,
    message: 'success',
    data: Object.values(metricsMap[reservoirId] || metricsMap.longyangxia),
  }
}

export function getSection(reservoirId: string): ApiResponse<ReservoirSection> {
  return {
    code: 200,
    message: 'success',
    data: sectionsMap[reservoirId] || sectionsMap.longyangxia,
  }
}

export function getBaseInfo(reservoirId: string): ApiResponse<BaseInfoGroup[]> {
  return {
    code: 200,
    message: 'success',
    data: baseInfoMap[reservoirId] || baseInfoMap.longyangxia,
  }
}

export function getProcessData(reservoirId: string): ApiResponse<{ dates: string[]; levels: number[]; inflows: number[]; outflows: number[] }> {
  return {
    code: 200,
    message: 'success',
    data: processDataMap[reservoirId] || processDataMap.longyangxia,
  }
}

export function getEngineeringInfo(reservoirId: string): ApiResponse<{ summary: EngineeringSummary; turbines: TurbineItem[]; gates: GateItem[] }> {
  return {
    code: 200,
    message: 'success',
    data: engineeringMap[reservoirId] || engineeringMap.longyangxia,
  }
}

// 关键曲线数据
export interface KeyCurvesData {
  storageCurve: { levels: number[]; storage: number[] }
  turbineCurve: { head: number[]; power: number[] }
  gateCurve: { opening: number[]; flow: number[] }
}

const keyCurvesMap: Record<string, KeyCurvesData> = {
  longyangxia: {
    storageCurve: {
      levels: [2410, 2420, 2430, 2440, 2450, 2460, 2470, 2480, 2490, 2500],
      storage: [50.2, 68.5, 92.3, 121.8, 156.2, 195.8, 241.5, 293.2, 351.6, 416.8],
    },
    turbineCurve: {
      head: [100, 120, 140, 160, 180, 200, 220, 240, 260, 280],
      power: [180, 225, 275, 328, 382, 435, 488, 540, 590, 635],
    },
    gateCurve: {
      opening: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
      flow: [0, 85, 180, 290, 415, 555, 710, 880, 1065, 1265, 1480],
    },
  },
  liujiaxia: {
    storageCurve: {
      levels: [1685, 1695, 1705, 1715, 1725, 1730, 1735, 1738, 1742, 1750],
      storage: [5.8, 12.5, 21.8, 33.2, 46.5, 53.8, 61.5, 66.2, 73.5, 88.6],
    },
    turbineCurve: {
      head: [60, 70, 80, 90, 100, 110, 120, 130, 140, 150],
      power: [95, 115, 138, 162, 188, 215, 242, 268, 292, 312],
    },
    gateCurve: {
      opening: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
      flow: [0, 72, 155, 250, 358, 478, 612, 760, 922, 1098, 1288],
    },
  },
  gongboxia: {
    storageCurve: {
      levels: [1950, 1960, 1970, 1975, 1980, 1985, 1988, 1992, 1997, 2005],
      storage: [2.1, 4.8, 8.5, 10.8, 13.5, 16.5, 18.6, 21.8, 26.2, 34.5],
    },
    turbineCurve: {
      head: [50, 60, 70, 80, 90, 100, 110, 120, 130, 140],
      power: [82, 102, 124, 148, 172, 198, 224, 250, 274, 295],
    },
    gateCurve: {
      opening: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
      flow: [0, 68, 148, 240, 345, 462, 595, 742, 905, 1082, 1275],
    },
  },
  jishixia: {
    storageCurve: {
      levels: [1820, 1830, 1840, 1845, 1850, 1855, 1858, 1862, 1870, 1878],
      storage: [1.8, 4.2, 7.8, 9.8, 12.2, 15.0, 16.8, 19.5, 24.2, 30.5],
    },
    turbineCurve: {
      head: [55, 65, 75, 85, 95, 105, 115, 125, 135, 145],
      power: [88, 108, 132, 158, 185, 212, 240, 268, 294, 318],
    },
    gateCurve: {
      opening: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
      flow: [0, 65, 142, 232, 335, 452, 582, 728, 890, 1068, 1260],
    },
  },
  qingtongxia: {
    storageCurve: {
      levels: [1130, 1135, 1140, 1145, 1150, 1155, 1157, 1160, 1168, 1175],
      storage: [0.08, 0.12, 0.17, 0.22, 0.28, 0.33, 0.36, 0.40, 0.52, 0.65],
    },
    turbineCurve: {
      head: [20, 25, 30, 35, 40, 45, 50, 55, 60, 65],
      power: [32, 42, 54, 68, 82, 98, 115, 132, 148, 162],
    },
    gateCurve: {
      opening: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
      flow: [0, 58, 128, 212, 308, 418, 542, 680, 832, 998, 1180],
    },
  },
}

export function getKeyCurves(reservoirId: string): ApiResponse<KeyCurvesData> {
  return {
    code: 200,
    message: 'success',
    data: keyCurvesMap[reservoirId] || keyCurvesMap.longyangxia,
  }
}
