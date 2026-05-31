// 水库监控数据
export interface ReservoirMonitor {
  id: string
  name: string
  status: 'normal' | 'warning' | 'abnormal'
  inflow: number // 入库流量 m³/s
  outflow: number // 出库流量 m³/s
  forebayLevel: number // 坝前水位 m
  tailwaterLevel: number // 尾水位 m
  storage: number // 库容 亿m³
  turbineFlow: number // 机组过流流量 m³/s
}

// 水库地图点位
export interface ReservoirPoint {
  id: string
  name: string
  lat: number
  lng: number
  status: 'normal' | 'warning' | 'abnormal'
  waterLevel: number // 坝前水位 m
  tailwaterLevel: number // 尾水位 m
  storage: number // 库容 亿m³
  storageRate: number // 库容率 %
  inflow: number // 入库流量 m³/s
  outflow: number // 出库流量 m³/s
  turbineFlow: number // 机组过流流量 m³/s
  updateTime: string // 更新时间
}

// 发电统计
export interface PowerStatistic {
  reservoirName: string
  dailyPower: number // 日发电量 万kW·h
  monthlyPower: number // 月发电量 万kW·h
  yearlyPower: number // 年发电量 万kW·h
}

// 水位过程线数据
export interface WaterLevelSeries {
  xAxis: string[] // 日期
  series: {
    name: string
    data: number[]
  }[]
}

// 负荷过程线数据
export interface LoadSeries {
  xAxis: string[]
  activePower: {
    name: string
    data: number[]
  }[]
  reactivePower: {
    name: string
    data: number[]
  }[]
}

// 预警信息
export interface WarningItem {
  id: string
  time: string // 预警时间
  type: string // 预警类型
  content: string // 预警内容
  target: string // 影响对象
  level: 1 | 2 | 3 | 4 // 预警级别
}

// 通知公告
export interface Announcement {
  content: string
}

// 天气信息
export interface WeatherInfo {
  city: string
  weather: string
  temperature: string
  wind: string
}

// 图层控制
export interface MapLayer {
  id: string
  name: string
  visible: boolean
}

// ==================== Mock 数据 ====================

// 水情监控数据
export const homeReservoirMonitor: ReservoirMonitor[] = [
  {
    id: 'longyangxia',
    name: '龙羊峡水库',
    status: 'normal',
    inflow: 1250,
    outflow: 1180,
    forebayLevel: 2472.35,
    tailwaterLevel: 2058.45,
    storage: 247.58,
    turbineFlow: 1180,
  },
  {
    id: 'liujiaxia',
    name: '刘家峡水库',
    status: 'normal',
    inflow: 1060,
    outflow: 1020,
    forebayLevel: 1738.62,
    tailwaterLevel: 1694.22,
    storage: 57.32,
    turbineFlow: 1020,
  },
]

// 水库地图点位数据
export const reservoirPoints: ReservoirPoint[] = [
  {
    id: 'longyangxia',
    name: '龙羊峡水库',
    lat: 36.12,
    lng: 100.92,
    status: 'normal',
    waterLevel: 2472.35,
    tailwaterLevel: 2058.45,
    storage: 247.58,
    storageRate: 86.2,
    inflow: 1250,
    outflow: 1180,
    turbineFlow: 1180,
    updateTime: '2025-05-16 10:20',
  },
  {
    id: 'liujiaxia',
    name: '刘家峡水库',
    lat: 35.95,
    lng: 103.32,
    status: 'normal',
    waterLevel: 1738.62,
    tailwaterLevel: 1694.22,
    storage: 57.32,
    storageRate: 78.5,
    inflow: 1060,
    outflow: 1020,
    turbineFlow: 1020,
    updateTime: '2025-05-16 10:20',
  },
  {
    id: 'qingtongxia',
    name: '青铜峡水库',
    lat: 37.88,
    lng: 105.98,
    status: 'normal',
    waterLevel: 1156.45,
    tailwaterLevel: 1138.20,
    storage: 6.18,
    storageRate: 65.3,
    inflow: 980,
    outflow: 950,
    turbineFlow: 950,
    updateTime: '2025-05-16 10:20',
  },
  {
    id: 'gongboxia',
    name: '公伯峡水库',
    lat: 35.75,
    lng: 102.12,
    status: 'warning',
    waterLevel: 1986.78,
    tailwaterLevel: 1945.30,
    storage: 15.62,
    storageRate: 72.1,
    inflow: 1100,
    outflow: 1050,
    turbineFlow: 1050,
    updateTime: '2025-05-16 10:20',
  },
  {
    id: 'jishixia',
    name: '积石峡水库',
    lat: 35.72,
    lng: 102.58,
    status: 'normal',
    waterLevel: 1856.32,
    tailwaterLevel: 1818.50,
    storage: 12.45,
    storageRate: 68.9,
    inflow: 1040,
    outflow: 1010,
    turbineFlow: 1010,
    updateTime: '2025-05-16 10:20',
  },
]

// 发电统计数据
export const powerStatistics: PowerStatistic[] = [
  {
    reservoirName: '龙羊峡水库',
    dailyPower: 2450.8,
    monthlyPower: 61320.5,
    yearlyPower: 512430.6,
  },
  {
    reservoirName: '刘家峡水库',
    dailyPower: 1820.5,
    monthlyPower: 45680.2,
    yearlyPower: 385620.4,
  },
  {
    reservoirName: '青铜峡水库',
    dailyPower: 680.3,
    monthlyPower: 17250.8,
    yearlyPower: 145680.2,
  },
  {
    reservoirName: '公伯峡水库',
    dailyPower: 1250.6,
    monthlyPower: 31580.3,
    yearlyPower: 265420.8,
  },
  {
    reservoirName: '积石峡水库',
    dailyPower: 980.2,
    monthlyPower: 24680.5,
    yearlyPower: 208560.5,
  },
  {
    reservoirName: '合计',
    dailyPower: 7182.4,
    monthlyPower: 180512.3,
    yearlyPower: 1517712.5,
  },
]

// 水位过程线数据
export const waterLevelSeries: WaterLevelSeries = {
  xAxis: ['05-10', '05-11', '05-12', '05-13', '05-14', '05-15', '05-16'],
  series: [
    {
      name: '龙羊峡水库',
      data: [2470.15, 2470.82, 2471.20, 2471.58, 2471.95, 2472.10, 2472.35],
    },
    {
      name: '刘家峡水库',
      data: [1736.80, 1737.10, 1737.45, 1737.80, 1738.15, 1738.38, 1738.62],
    },
    {
      name: '青铜峡水库',
      data: [1155.20, 1155.45, 1155.68, 1155.90, 1156.10, 1156.28, 1156.45],
    },
    {
      name: '公伯峡水库',
      data: [1985.10, 1985.45, 1985.80, 1986.10, 1986.40, 1986.60, 1986.78],
    },
    {
      name: '积石峡水库',
      data: [1854.80, 1855.10, 1855.40, 1855.70, 1856.00, 1856.15, 1856.32],
    },
  ],
}

// 负荷过程线数据
export const loadSeries: LoadSeries = {
  xAxis: ['05-10', '05-11', '05-12', '05-13', '05-14', '05-15', '05-16'],
  activePower: [
    { name: '龙羊峡水库', data: [820, 850, 880, 900, 870, 860, 890] },
    { name: '刘家峡水库', data: [620, 640, 660, 680, 650, 630, 670] },
    { name: '青铜峡水库', data: [220, 230, 240, 250, 235, 225, 245] },
    { name: '公伯峡水库', data: [420, 440, 460, 480, 450, 430, 470] },
    { name: '积石峡水库', data: [320, 335, 350, 365, 340, 325, 355] },
  ],
  reactivePower: [
    { name: '龙羊峡水库', data: [180, 190, 200, 210, 195, 185, 205] },
    { name: '刘家峡水库', data: [140, 150, 160, 170, 155, 145, 165] },
    { name: '青铜峡水库', data: [60, 65, 70, 75, 68, 62, 72] },
    { name: '公伯峡水库', data: [100, 110, 120, 130, 115, 105, 125] },
    { name: '积石峡水库', data: [80, 88, 95, 102, 90, 82, 98] },
  ],
}

// 预警信息数据
export const warningList: WarningItem[] = [
  {
    id: 'w1',
    time: '05-16 09:50',
    type: '水位超警',
    content: '龙羊峡水库坝前水位接近汛限水位，需加强监测',
    target: '龙羊峡水库',
    level: 1,
  },
  {
    id: 'w2',
    time: '05-16 09:30',
    type: '流量超警',
    content: '刘家峡水库入库流量超过阈值，注意调度安全',
    target: '刘家峡水库',
    level: 3,
  },
  {
    id: 'w3',
    time: '05-16 08:45',
    type: '设备异常',
    content: '公伯峡水库2号机组振动值偏高，建议检查',
    target: '公伯峡水库',
    level: 2,
  },
  {
    id: 'w4',
    time: '05-16 08:15',
    type: '降雨预警',
    content: '黄河上游流域预计未来24小时有中到大雨',
    target: '全流域',
    level: 4,
  },
  {
    id: 'w5',
    time: '05-16 07:30',
    type: '水位超警',
    content: '积石峡水库水位持续上涨，接近警戒水位',
    target: '积石峡水库',
    level: 3,
  },
  {
    id: 'w6',
    time: '05-15 22:00',
    type: '调度通知',
    content: '青铜峡水库按计划执行防洪调度，出库流量调整',
    target: '青铜峡水库',
    level: 4,
  },
]

// 通知公告
export const announcement: Announcement = {
  content:
    '黄委发布调度指令：5月16日10时起，龙羊峡水库出库流量增至1200m³/s，刘家峡水库出库流量增至1050m³/s。',
}

// 天气信息
export const weatherInfo: WeatherInfo = {
  city: '兰州市',
  weather: '阴',
  temperature: '18~26℃',
  wind: '西北风 2级',
}

// 地图图层
export const mapLayers: MapLayer[] = [
  { id: 'reservoir', name: '水库', visible: true },
  { id: 'hydroStation', name: '水文站', visible: false },
  { id: 'rainStation', name: '雨量站', visible: false },
  { id: 'river', name: '河道', visible: true },
  { id: 'admin', name: '行政区划', visible: true },
  { id: 'satellite', name: '卫星影像', visible: false },
  { id: 'terrain', name: '地形影像', visible: false },
]
