/**
 * 评价决策页面图表 option 构建函数
 *
 * 将 EvaluationDecisionView.vue 中的 5 个图表 option 构建逻辑提取为纯函数，
 * 接收 mock 数据返回 EChartsOption，方便组件层直接调用。
 */
import * as echarts from 'echarts'
import {
  PLAN_COLORS,
  SANKEY_NODE_COLORS,
  WATER_FLOW_COLORS,
  TEXT_PRIMARY,
  TEXT_REGULAR,
  TEXT_SECONDARY,
  TECH_BLUE,
  TECH_GREEN,
  TECH_ORANGE,
  AXIS_LINE_COLOR,
  SPLIT_LINE_COLOR,
  baseTooltip,
  baseItemTooltip,
  baseLegend,
  baseCategoryXAxis,
  baseValueYAxis,
  baseValueXAxis,
  createGrid,
} from '@/utils/chart'

// ==================== 雷达图 ====================

/** 构建多方案评价雷达图 option */
export function buildRadarOption(data: any, selectedPlanLabels: string[]): echarts.EChartsOption {
  const filteredPlans = data.plans.filter((p: any) => selectedPlanLabels.includes(p.plan))

  return {
    title: {
      text: '多方案评价雷达图',
      right: 12,
      top: 4,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    tooltip: {
      ...baseItemTooltip,
    },
    legend: {
      ...baseLegend,
      data: filteredPlans.map((p: any) => p.plan),
      bottom: 2,
    },
    radar: {
      indicator: data.indicators.map((ind: any) => ({
        name: ind.name,
        max: ind.max,
      })),
      center: ['50%', '52%'],
      radius: '56%',
      axisName: {
        color: TEXT_REGULAR,
        fontSize: 11,
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(0, 175, 255, 0.02)', 'rgba(0, 175, 255, 0.05)'],
        },
      },
      axisLine: {
        lineStyle: {
          color: AXIS_LINE_COLOR,
        },
      },
      splitLine: {
        lineStyle: {
          color: SPLIT_LINE_COLOR,
        },
      },
    },
    series: [{
      type: 'radar',
      data: filteredPlans.map((p: any) => ({
        name: p.plan,
        value: p.values,
        lineStyle: { width: 2, color: PLAN_COLORS[p.plan] },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: PLAN_COLORS[p.plan] + '30' },
            { offset: 1, color: PLAN_COLORS[p.plan] + '05' },
          ]),
        },
        itemStyle: { color: PLAN_COLORS[p.plan] },
      })),
    }],
  }
}

// ==================== 评价指标桑基图 ====================

/** 构建多方案评价指标桑基图 option */
export function buildSankeyOption(data: any): echarts.EChartsOption {
  return {
    title: {
      text: '多方案评价指标',
      right: 12,
      top: 6,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    tooltip: {
      ...baseItemTooltip,
      triggerOn: 'mousemove' as const,
    },
    series: [{
      type: 'sankey',
      emphasis: {
        focus: 'adjacency' as const,
      },
      nodeAlign: 'left' as const,
      nodeGap: 4,
      nodeWidth: 28,
      left: 50,
      right: 36,
      top: 36,
      bottom: 20,
      data: data.nodes.map((n: any, i: number) => ({
        ...n,
        itemStyle: {
          color: SANKEY_NODE_COLORS[i % SANKEY_NODE_COLORS.length],
          borderColor: 'rgba(255,255,255,0.15)',
          borderWidth: 1,
        },
        label: {
          show: true,
          color: '#ffffff',
          fontSize: 9,
          fontWeight: 600,
          // R编号和分类名称均在色块内部，右侧结果在色块外
          position: n.category === 2 ? 'right' : 'inside',
        },
      })),
      links: data.links.map((l: any) => ({
        source: l.source,
        target: l.target,
        value: l.value,
        lineStyle: {
          color: 'gradient',
          opacity: 0.35,
          curveness: 0.5,
        },
      })),
      lineStyle: {
        color: 'gradient',
        opacity: 0.35,
        curveness: 0.5,
      },
    }],
  }
}

// ==================== 帕累托曲线 ====================

/** 构建帕累托曲线 option */
export function buildParetoOption(data: any, selectedPlanLabels: string[]): echarts.EChartsOption {
  const filteredData = data.filter((d: any) => selectedPlanLabels.includes(d.plan))

  return {
    title: {
      text: '帕累托曲线',
      right: 12,
      top: 4,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    tooltip: {
      ...baseTooltip,
    },
    legend: {
      ...baseLegend,
      data: filteredData.map((d: any) => d.plan),
      top: 22,
    },
    grid: createGrid(48, 22, 50, 16),
    xAxis: {
      ...baseValueXAxis,
      name: '最优投影值',
      nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
      axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
    },
    yAxis: {
      ...baseValueYAxis,
      name: '综合优选指数',
      nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
      axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
    },
    series: filteredData.map((d: any) => ({
      name: d.plan,
      type: 'line',
      data: d.points.map((p: any) => [p.projection, p.index]),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 2, color: PLAN_COLORS[d.plan] },
      itemStyle: { color: PLAN_COLORS[d.plan] },
      connectNulls: false,
    })),
  }
}

// ==================== 决策分析-过程曲线 ====================

/** 构建决策分析过程曲线 option（根据 tab 切换水位/流量/出力） */
export function buildProcessOption(data: any, tab: string): echarts.EChartsOption {
  if (tab === 'water') {
    const d = data.waterLevel
    return {
      title: {
        text: '水位变化过程线',
        right: 12,
        top: 2,
        textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
      },
      tooltip: { ...baseTooltip },
      legend: {
        ...baseLegend,
        data: ['龙羊峡水库', '刘家峡水库', '汛限水位', '正常蓄水位'],
        textStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        top: 18,
      },
      grid: createGrid(46, 16, 42, 8),
      xAxis: {
        ...baseCategoryXAxis,
        data: d.dates,
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      yAxis: {
        ...baseValueYAxis,
        name: '水位（m）',
        nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      series: [
        {
          name: '龙羊峡水库',
          type: 'line',
          data: d.longyang,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_BLUE },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0, 175, 255, 0.2)' },
              { offset: 1, color: 'rgba(0, 175, 255, 0.02)' },
            ]),
          },
        },
        {
          name: '刘家峡水库',
          type: 'line',
          data: d.liujia,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_GREEN },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0, 229, 160, 0.2)' },
              { offset: 1, color: 'rgba(0, 229, 160, 0.02)' },
            ]),
          },
        },
        {
          name: '汛限水位',
          type: 'line',
          data: d.dates.map(() => d.floodLimit),
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 1.5, color: '#ff6b6b', type: 'dashed' },
        },
        {
          name: '正常蓄水位',
          type: 'line',
          data: d.dates.map(() => d.normalLevel),
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 1.5, color: TECH_ORANGE, type: 'dashed' },
        },
      ],
    }
  } else if (tab === 'flow') {
    const d = data.flow
    return {
      title: {
        text: '流量变化过程线',
        right: 12,
        top: 2,
        textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
      },
      tooltip: { ...baseTooltip },
      legend: {
        ...baseLegend,
        data: ['龙羊峡水库', '刘家峡水库'],
        textStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        top: 18,
      },
      grid: createGrid(46, 16, 42, 8),
      xAxis: {
        ...baseCategoryXAxis,
        data: d.dates,
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      yAxis: {
        ...baseValueYAxis,
        name: '流量（m³/s）',
        nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      series: [
        {
          name: '龙羊峡水库',
          type: 'line',
          data: d.longyang,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_BLUE },
        },
        {
          name: '刘家峡水库',
          type: 'line',
          data: d.liujia,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_GREEN },
        },
      ],
    }
  } else {
    const d = data.power
    return {
      title: {
        text: '出力变化过程线',
        right: 12,
        top: 2,
        textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
      },
      tooltip: { ...baseTooltip },
      legend: {
        ...baseLegend,
        data: ['龙羊峡水库', '刘家峡水库', '龙羊峡装机容量', '刘家峡装机容量'],
        textStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        top: 18,
      },
      grid: createGrid(46, 16, 42, 8),
      xAxis: {
        ...baseCategoryXAxis,
        data: d.dates,
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      yAxis: {
        ...baseValueYAxis,
        name: '出力（MW）',
        nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      series: [
        {
          name: '龙羊峡水库',
          type: 'line',
          data: d.longyang,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_BLUE },
        },
        {
          name: '刘家峡水库',
          type: 'line',
          data: d.liujia,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_GREEN },
        },
        {
          name: '龙羊峡装机容量',
          type: 'line',
          data: d.dates.map(() => d.longyangCapacity),
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 1.5, color: '#ff6b6b', type: 'dashed' },
        },
        {
          name: '刘家峡装机容量',
          type: 'line',
          data: d.dates.map(() => d.liujiaCapacity),
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 1.5, color: TECH_ORANGE, type: 'dashed' },
        },
      ],
    }
  }
}

// ==================== 水量使用流向图 ====================

/** 构建水量使用流向图 option */
export function buildWaterFlowOption(data: any): echarts.EChartsOption {
  const totalValue = data.reduce((sum: number, d: any) => sum + d.value, 0)
  const sourceName = `最终来水量\n${totalValue.toFixed(2)} 亿m³`

  const nodes = [
    { name: sourceName, itemStyle: { color: '#0088cc' } },
    ...data.map((d: any, i: number) => ({
      name: `${d.name}\n${d.value} 亿m³（${d.percent}%）`,
      itemStyle: { color: WATER_FLOW_COLORS[i % WATER_FLOW_COLORS.length] },
    })),
  ]

  const links = data.map((d: any) => ({
    source: sourceName,
    target: `${d.name}\n${d.value} 亿m³（${d.percent}%）`,
    value: d.value,
  }))

  return {
    title: {
      text: '水量使用流向图',
      right: 12,
      top: 6,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    tooltip: {
      ...baseItemTooltip,
      triggerOn: 'mousemove' as const,
      formatter: (params: any) => {
        if (params.dataType === 'edge') {
          return `${params.data.source} → ${params.data.target}<br/>水量：${params.data.value} 亿m³`
        }
        return params.name
      },
    },
    series: [{
      type: 'sankey',
      layout: 'none',
      layoutIterations: 0,
      emphasis: {
        focus: 'adjacency' as const,
      },
      nodeAlign: 'left' as const,
      nodeGap: 10,
      nodeWidth: 18,
      left: 20,
      right: 40,
      top: 36,
      bottom: 20,
      data: nodes,
      links: links,
      lineStyle: {
        color: 'gradient',
        opacity: 0.4,
        curveness: 0.5,
      },
      label: {
        show: true,
        color: TEXT_PRIMARY,
        fontSize: 10,
        position: 'right',
      },
    }],
  }
}
