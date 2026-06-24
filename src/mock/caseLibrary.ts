export const caseLibraryPageState = {
  code: 200,
  message: 'success',
  data: {
    selectedCaseId: 'case-2024-flood-001',
    activeTab: 'config-summary',
    filters: {
      dateRange: ['2020-01-01', '2025-05-16'],
      caseType: 'all',
      reservoir: 'all',
      keyword: '',
    },
  },
}

export const caseList = {
  code: 200,
  message: 'success',
  data: [
    {
      id: 'case-2024-flood-001',
      title: '2024年黄河上游典型连丰兴利调度案例',
      tag: '连丰',
      tagColor: '#00ff88',
      iconType: 'benefit',
      reservoirs: ['龙羊峡水库', '刘家峡水库', '青铜峡水库'],
      caseType: ['连丰', '兴利调度'],
      createdAt: '2024-11-20 15:30:22',
      summary: '2024年上游来水偏丰，本案例在保障防洪安全的前提下，最大化用丰水资源，提高发电量。',
      status: '已验证',
      statusColor: '#00ff88',
      score: 92.6,
      cover: 'flood-control',
    },
    {
      id: 'case-2022-drought-001',
      title: '2022年黄河上游典型连枯保供水调度案例',
      tag: '保供水',
      tagColor: '#faad14',
      iconType: 'supply',
      reservoirs: ['龙羊峡水库', '刘家峡水库'],
      caseType: ['连枯', '保供水'],
      createdAt: '2023-01-18 09:15:44',
      summary: '2022年上游来水持续偏枯，通过优化调度保障下游供水及生态用水安全。',
      status: '已归档',
      statusColor: '#00afff',
      score: 88.3,
      cover: 'drought',
    },
    {
      id: 'case-2024-realtime-001',
      title: '2024年7月上游实时防洪调度案例',
      tag: '实时',
      tagColor: '#ff7a45',
      iconType: 'realtime',
      reservoirs: ['龙羊峡水库', '刘家峡水库', '公伯峡水库', '积石峡水库'],
      caseType: ['实时', '防洪调度'],
      createdAt: '2024-07-15 08:42:18',
      summary: '2024年7月汛期突发暴雨，实时调度确保下游防洪安全。',
      status: '已验证',
      statusColor: '#00ff88',
      score: 95.2,
      cover: 'realtime',
    },
    {
      id: 'case-2023-drought-001',
      title: '2023年黄河上游典型连枯调度案例',
      tag: '连枯',
      tagColor: '#d4b106',
      iconType: 'drought',
      reservoirs: ['龙羊峡水库', '刘家峡水库', '青铜峡水库'],
      caseType: ['连枯', '兴利调度'],
      createdAt: '2023-12-05 10:25:18',
      summary: '2023年上游来水持续偏枯，通过科学调度平衡发电与供水需求。',
      status: '已验证',
      statusColor: '#00ff88',
      score: 89.5,
      cover: 'drought',
    },
  ],
}

export const caseDetail = {
  code: 200,
  message: 'success',
  data: {
    'case-2024-flood-001': {
      id: 'case-2024-flood-001',
      title: '2024年黄河上游典型连丰兴利调度案例',
      tag: '连丰',
      tagColor: '#00ff88',
      status: '已验证',
      statusColor: '#00ff88',
      score: 92.6,
      scoreLevel: '优秀',
      createdAt: '2024-11-20 15:30:22',
      creator: '系统管理员',
      reservoirs: ['龙羊峡水库', '刘家峡水库', '青铜峡水库'],
      caseType: ['连丰', '兴利调度'],

      configSummary: {
        period: '2024-06-01 08:00 ~ 2024-09-30 08:00（122天）',
        reservoirs: '龙羊峡水库、刘家峡水库、青铜峡水库',
        objective: '最大发电量，兼顾防洪安全与生态用水',
        constraints: '防洪约束、下泄生态流量约束、库容约束等',
        modelType: '联动水库优化调度模型（LRO）',
        algorithm: 'NSGA-II 多目标遗传算法',
        population: '200',
        iterations: '500',
        modelVersion: 'v2.3.1',
      },

      metrics: [
        { name: '总发电量（万kWh）', value: '3215.8', change: '↑ 8.76%', changeType: 'up', baseline: '较基准' },
        { name: '防洪最大风险值', value: '0.218', change: '↓ 21.36%', changeType: 'down', baseline: '较基准' },
        { name: '冲沙总量（万m³）', value: '1248.6', change: '↑ 6.12%', changeType: 'up', baseline: '较基准' },
        { name: '生态流量达标率', value: '100%', change: '达标', changeType: 'success', baseline: '' },
        { name: '综合满意度（分）', value: '92.6', change: '优秀', changeType: 'excellent', baseline: '' },
      ],

      processCharts: {
        waterLevel: {
          title: '龙羊峡水位过程线',
          unit: 'm',
          times: ['06-01', '06-15', '07-01', '07-15', '08-01', '08-15', '09-01', '09-15', '09-30'],
          data: [2468.5, 2470.2, 2472.8, 2474.1, 2475.6, 2474.3, 2472.1, 2470.8, 2469.2],
        },
        outflow: {
          title: '刘家峡下泄流量过程线',
          unit: 'm³/s',
          times: ['06-01', '06-15', '07-01', '07-15', '08-01', '08-15', '09-01', '09-15', '09-30'],
          data: [850, 920, 1180, 1350, 1420, 1280, 1050, 960, 880],
        },
        power: {
          title: '总出力过程线',
          unit: 'MW',
          times: ['06-01', '06-15', '07-01', '07-15', '08-01', '08-15', '09-01', '09-15', '09-30'],
          data: [1850, 1920, 2150, 2280, 2350, 2200, 2050, 1980, 1890],
        },
      },

      historyResult: {
        summary: '本案例在2024年丰水期通过优化调度，在保障防洪安全的前提下最大化发电量。',
        keyFindings: [
          '总发电量较基准方案提升8.76%',
          '防洪风险降低21.36%',
          '生态流量100%达标',
          '冲沙效率提升6.12%',
        ],
      },

      evaluation: {
        overall: 92.6,
        dimensions: [
          { name: '发电效益', score: 95, weight: 0.3 },
          { name: '防洪安全', score: 88, weight: 0.25 },
          { name: '生态保障', score: 94, weight: 0.2 },
          { name: '冲沙效果', score: 91, weight: 0.15 },
          { name: '经济性', score: 93, weight: 0.1 },
        ],
      },
    },

    'case-2022-drought-001': {
      id: 'case-2022-drought-001',
      title: '2022年黄河上游典型连枯保供水调度案例',
      tag: '连枯',
      tagColor: '#ffaa00',
      status: '已归档',
      statusColor: '#00afff',
      score: 88.3,
      scoreLevel: '良好',
      createdAt: '2023-01-18 09:15:44',
      creator: '调度专家',
      reservoirs: ['龙羊峡水库', '刘家峡水库'],
      caseType: ['连枯', '保供水'],

      configSummary: {
        period: '2022-01-01 08:00 ~ 2022-12-31 08:00（365天）',
        reservoirs: '龙羊峡水库、刘家峡水库',
        objective: '保障下游供水及生态用水安全',
        constraints: '供水约束、生态流量约束、库容下限约束',
        modelType: '水库群联合调度模型（RJOS）',
        algorithm: 'SCE-UA 全局优化算法',
        population: '500',
        iterations: '1000',
        modelVersion: 'v2.1.0',
      },

      metrics: [
        { name: '供水保障率', value: '98.5%', change: '↑ 2.3%', changeType: 'up', baseline: '较基准' },
        { name: '生态流量达标率', value: '96.2%', change: '↑ 8.5%', changeType: 'up', baseline: '较基准' },
        { name: '总发电量（万kWh）', value: '2180.5', change: '↓ 12.3%', changeType: 'down', baseline: '较基准' },
        { name: '库容消落深度（m）', value: '18.5', change: '正常', changeType: 'success', baseline: '' },
        { name: '综合满意度（分）', value: '88.3', change: '良好', changeType: 'excellent', baseline: '' },
      ],

      processCharts: {
        waterLevel: {
          title: '龙羊峡水位过程线',
          unit: 'm',
          times: ['01-01', '03-01', '05-01', '07-01', '09-01', '11-01', '12-31'],
          data: [2478.2, 2475.6, 2472.1, 2468.5, 2465.2, 2462.8, 2460.5],
        },
        outflow: {
          title: '刘家峡下泄流量过程线',
          unit: 'm³/s',
          times: ['01-01', '03-01', '05-01', '07-01', '09-01', '11-01', '12-31'],
          data: [650, 580, 520, 480, 450, 420, 400],
        },
        power: {
          title: '总出力过程线',
          unit: 'MW',
          times: ['01-01', '03-01', '05-01', '07-01', '09-01', '11-01', '12-31'],
          data: [1200, 1050, 920, 850, 800, 760, 720],
        },
      },

      historyResult: {
        summary: '本案例在2022年枯水期通过优化调度，在来水偏枯情况下保障了下游供水安全。',
        keyFindings: [
          '供水保障率达到98.5%',
          '生态流量达标率提升至96.2%',
          '库容合理消落，保障年度供水',
          '发电量较丰水年下降属正常范围',
        ],
      },

      evaluation: {
        overall: 88.3,
        dimensions: [
          { name: '供水保障', score: 96, weight: 0.35 },
          { name: '生态保障', score: 85, weight: 0.25 },
          { name: '发电效益', score: 78, weight: 0.2 },
          { name: '调度合理性', score: 92, weight: 0.2 },
        ],
      },
    },

    'case-2024-realtime-001': {
      id: 'case-2024-realtime-001',
      title: '2024年7月上游实时防洪调度案例',
      tag: '实时',
      tagColor: '#ff4d4f',
      status: '已验证',
      statusColor: '#00ff88',
      score: 95.2,
      scoreLevel: '优秀',
      createdAt: '2024-07-15 08:42:18',
      creator: '系统管理员',
      reservoirs: ['龙羊峡水库', '刘家峡水库', '公伯峡水库', '积石峡水库'],
      caseType: ['实时', '防洪调度'],

      configSummary: {
        period: '2024-07-10 08:00 ~ 2024-07-20 08:00（10天）',
        reservoirs: '龙羊峡水库、刘家峡水库、公伯峡水库、积石峡水库',
        objective: '最小化下游洪峰流量，确保防洪安全',
        constraints: '库容约束、泄流能力约束、下游防洪标准约束',
        modelType: '实时洪水调度模型（RTFD）',
        algorithm: '动态规划 + 实时优化',
        population: 'N/A',
        iterations: 'N/A',
        modelVersion: 'v3.0.1',
      },

      metrics: [
        { name: '洪峰削减率', value: '68.5%', change: '↑ 5.2%', changeType: 'up', baseline: '较基准' },
        { name: '最大下泄流量（m³/s）', value: '2850', change: '↓ 15.3%', changeType: 'down', baseline: '较基准' },
        { name: '调蓄水量（亿m³）', value: '8.6', change: '正常', changeType: 'success', baseline: '' },
        { name: '超警戒水位时长（h）', value: '0', change: '未超警', changeType: 'success', baseline: '' },
        { name: '综合满意度（分）', value: '95.2', change: '优秀', changeType: 'excellent', baseline: '' },
      ],

      processCharts: {
        waterLevel: {
          title: '龙羊峡水位过程线',
          unit: 'm',
          times: ['07-10', '07-11', '07-12', '07-13', '07-14', '07-15', '07-16', '07-17', '07-18', '07-19', '07-20'],
          data: [2471.2, 2472.5, 2474.8, 2476.2, 2475.8, 2474.1, 2472.6, 2471.3, 2470.5, 2469.8, 2469.2],
        },
        outflow: {
          title: '刘家峡下泄流量过程线',
          unit: 'm³/s',
          times: ['07-10', '07-11', '07-12', '07-13', '07-14', '07-15', '07-16', '07-17', '07-18', '07-19', '07-20'],
          data: [1200, 1580, 2250, 2850, 2680, 2100, 1650, 1380, 1250, 1180, 1120],
        },
        power: {
          title: '总出力过程线',
          unit: 'MW',
          times: ['07-10', '07-11', '07-12', '07-13', '07-14', '07-15', '07-16', '07-17', '07-18', '07-19', '07-20'],
          data: [1650, 1820, 2150, 2450, 2380, 2050, 1780, 1620, 1550, 1500, 1480],
        },
      },

      historyResult: {
        summary: '本案例成功应对2024年7月汛期突发暴雨，通过实时调度确保下游防洪安全。',
        keyFindings: [
          '洪峰削减率达68.5%',
          '下游水位未超警戒',
          '水库调蓄作用显著',
          '实时调度响应及时',
        ],
      },

      evaluation: {
        overall: 95.2,
        dimensions: [
          { name: '防洪效果', score: 98, weight: 0.4 },
          { name: '响应速度', score: 96, weight: 0.25 },
          { name: '调度精度', score: 94, weight: 0.2 },
          { name: '安全性', score: 93, weight: 0.15 },
        ],
      },
    },

    'case-2023-drought-001': {
      id: 'case-2023-drought-001',
      title: '2023年黄河上游典型连枯调度案例',
      tag: '连枯',
      tagColor: '#d4b106',
      status: '已验证',
      statusColor: '#00ff88',
      score: 89.5,
      scoreLevel: '良好',
      createdAt: '2023-12-05 10:25:18',
      creator: '调度专家',
      reservoirs: ['龙羊峡水库', '刘家峡水库', '青铜峡水库'],
      caseType: ['连枯', '兴利调度'],

      configSummary: {
        period: '2023-01-01 08:00 ~ 2023-12-31 08:00（365天）',
        reservoirs: '龙羊峡水库、刘家峡水库、青铜峡水库',
        objective: '平衡发电与供水需求，保障枯水年综合效益',
        constraints: '供水约束、生态流量约束、最小出力约束',
        modelType: '多目标优化调度模型（MOOP）',
        algorithm: 'MOPSO 多目标粒子群算法',
        population: '300',
        iterations: '800',
        modelVersion: 'v2.2.0',
      },

      metrics: [
        { name: '发电完成率', value: '94.2%', change: '↑ 3.8%', changeType: 'up', baseline: '较基准' },
        { name: '供水保障率', value: '97.8%', change: '↑ 1.5%', changeType: 'up', baseline: '较基准' },
        { name: '总发电量（万kWh）', value: '2856.3', change: '↓ 8.5%', changeType: 'down', baseline: '较基准' },
        { name: '生态流量达标率', value: '98.6%', change: '达标', changeType: 'success', baseline: '' },
        { name: '综合满意度（分）', value: '89.5', change: '良好', changeType: 'excellent', baseline: '' },
      ],

      processCharts: {
        waterLevel: {
          title: '龙羊峡水位过程线',
          unit: 'm',
          times: ['01-01', '03-01', '05-01', '07-01', '09-01', '11-01', '12-31'],
          data: [2475.8, 2472.3, 2468.6, 2465.2, 2462.5, 2460.8, 2458.9],
        },
        outflow: {
          title: '刘家峡下泄流量过程线',
          unit: 'm³/s',
          times: ['01-01', '03-01', '05-01', '07-01', '09-01', '11-01', '12-31'],
          data: [620, 560, 510, 485, 460, 435, 415],
        },
        power: {
          title: '总出力过程线',
          unit: 'MW',
          times: ['01-01', '03-01', '05-01', '07-01', '09-01', '11-01', '12-31'],
          data: [1150, 1020, 940, 880, 830, 790, 750],
        },
      },

      historyResult: {
        summary: '本案例在2023年枯水期通过科学调度，在来水偏枯情况下平衡了发电与供水需求。',
        keyFindings: [
          '发电完成率达到94.2%',
          '供水保障率达到97.8%',
          '生态流量98.6%达标',
          '库容合理消落，保障年度调度',
        ],
      },

      evaluation: {
        overall: 89.5,
        dimensions: [
          { name: '发电效益', score: 88, weight: 0.3 },
          { name: '供水保障', score: 95, weight: 0.3 },
          { name: '生态保障', score: 92, weight: 0.2 },
          { name: '调度合理性', score: 86, weight: 0.2 },
        ],
      },
    },
  },
}

export const caseTypeOptions = [
  { label: '全部', value: 'all' },
  { label: '连丰', value: '连丰' },
  { label: '连枯', value: '连枯' },
  { label: '实时', value: '实时' },
  { label: '多能互补', value: '多能互补' },
  { label: '防洪调度', value: '防洪调度' },
  { label: '保供水', value: '保供水' },
  { label: '兴利调度', value: '兴利调度' },
]

export const reservoirOptions = [
  { label: '全部', value: 'all' },
  { label: '龙羊峡水库', value: '龙羊峡水库' },
  { label: '刘家峡水库', value: '刘家峡水库' },
  { label: '青铜峡水库', value: '青铜峡水库' },
  { label: '公伯峡水库', value: '公伯峡水库' },
  { label: '积石峡水库', value: '积石峡水库' },
]
