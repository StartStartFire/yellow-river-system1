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
  TEXT_PLACEHOLDER,
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
import { formatNumber, formatExponential } from '@/utils/format'

// ==================== 子系统得分雷达图 ====================

/** 构建 AHP-Fuzzy 子系统得分雷达图（5 子系统：水/沙/能/灾/生态） */
export function buildRadarOption(data: any, selectedIndices: number[]): echarts.EChartsOption {
  const filteredPlans = selectedIndices
    .filter((idx: number) => idx >= 0 && idx < (data.plans || []).length)
    .map((idx: number) => data.plans[idx])

  return {
    title: {
      text: '算法得分雷达图',
      right: 12,
      top: 4,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    tooltip: {
      ...baseItemTooltip,
      formatter: (params: any) => {
        if (!params.value) return ''
        const name = params.seriesName || ''
        const indicators = data.indicators || []
        let html = `<strong>${name}</strong><br/>`
        indicators.forEach((ind: any, i: number) => {
          html += `${ind.name}：${typeof params.value[i] === 'number' ? formatNumber(params.value[i], 1) : params.value[i]}<br/>`
        })
        return html
      },
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

/** 子系统配色 */
const SUBSYSTEM_COLORS: Record<string, string> = {
  '水子系统': '#00afff',
  '沙子系统': '#e88a3a',
  '能子系统': '#ffaa00',
  '灾子系统': '#ff6b6b',
  '生子系统': '#52c41a',
}

/** 构建评分指标流向桑基图 option（方案一的 R1~R22 原始指标至子系统） */
export function buildSankeyOptionFromRaw(data: any): echarts.EChartsOption {
  if (!data || !data.subsystems || !data.schemes || data.schemes.length === 0) {
    return buildSankeyEmptyOption()
  }

  const scheme = data.schemes[0]  // 方案一（排名第 1）
  const values = scheme.values || []
  const subsystems = data.subsystems

  // 节点构建
  const nodes: any[] = []
  const links: any[] = []

  // 第一层：R1~R22 指标节点
  for (let i = 0; i < values.length; i++) {
    const name = `R${i + 1}`
    nodes.push({ name, category: 0 })
  }

  // 第二层：子系统节点
  const subNodes: { name: string; rIndices: number[] }[] = []
  for (const sys of subsystems) {
    const color = SUBSYSTEM_COLORS[sys.name] || '#5a8ab8'
    nodes.push({ name: sys.name, category: 1, itemStyle: { color } })
    subNodes.push({ name: sys.name, rIndices: sys.indices })
  }

  // 第三层：综合得分
  nodes.push({ name: '综合得分', category: 2, itemStyle: { color: '#00e5a0' } })

  // 连线：R → 子系统（统一值 60，所有 R 节点方块等高）
  for (let i = 0; i < values.length; i++) {
    const sub = subNodes.find(s => s.rIndices.includes(i))
    if (sub) {
      links.push({
        source: `R${i + 1}`,
        target: sub.name,
        value: 600,
        realValue: values[i],
      })
    }
  }

  // 连线：子系统 → 综合得分（等于该子系统所有 R 流入之和，保持节点流量平衡）
  for (const sn of subNodes) {
    const rCount = sn.rIndices.length
    const total = rCount * 600
    links.push({ source: sn.name, target: '综合得分', value: total })
  }

  // 构建真实值查找映射（链接 → 实际指标值）
  const linkRealValues: Record<string, number> = {}
  for (let i = 0; i < values.length; i++) {
    linkRealValues[`R${i + 1}`] = values[i]
  }

  return {
    title: {
      text: '评分指标流向（方案一）',
      right: 12,
      top: 6,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    tooltip: {
      ...baseItemTooltip,
      triggerOn: 'mousemove' as const,
      formatter: (params: any) => {
        if (!params || !params.data) return ''
        const d = params.data
        // 连线 tooltip：显示实际指标值
        if (d.source && d.target) {
          const realVal = linkRealValues[d.source] ?? d.value
          return `<strong>${d.source} → ${d.target}</strong><br/>指标值：${typeof realVal === 'number' ? formatNumber(realVal, 4) : realVal}`
        }
        // 节点 tooltip
        if (d.name) {
          // 检查是否 R 节点
          const rMatch = d.name.match(/^R(\d+)$/)
          if (rMatch) {
            const idx = parseInt(rMatch[1]) - 1
            const realVal = values[idx]
            return `<strong>${d.name}</strong><br/>指标值：${typeof realVal === 'number' ? formatNumber(realVal, 4) : realVal}`
          }
          return `<strong>${d.name}</strong>`
        }
        return ''
      },
    },
    series: [{
      type: 'sankey',
      emphasis: { focus: 'adjacency' as const },
      nodeAlign: 'left' as const,
      nodeGap: 2,
      nodeWidth: 40,
      left: 80,
      right: 40,
      top: 40,
      bottom: 24,
      data: nodes.map((n: any) => ({
        ...n,
        itemStyle: {
          color: n.category === 0
            ? SANKEY_NODE_COLORS[parseInt(n.name.replace('R', '')) % SANKEY_NODE_COLORS.length]
            : (n.category === 1 ? SUBSYSTEM_COLORS[n.name] || '#5a8ab8' : '#00e5a0'),
          borderColor: 'rgba(255,255,255,0.15)',
          borderWidth: 1,
        },
        label: {
          show: true,
          color: '#ffffff',
          fontSize: n.category === 2 ? 12 : 11,
          fontWeight: 600,
          position: n.category === 2 ? 'right' : 'inside',
        },
      })),
      links: links.map((l: any) => ({
        ...l,
        lineStyle: {
          color: 'gradient',
          opacity: 0.45,
          curveness: 0.5,
        },
      })),
      lineStyle: {
        color: 'gradient',
        opacity: 0.45,
        curveness: 0.5,
      },
    }],
  }
}

/** 空桑基图（无数据时占位） */
function buildSankeyEmptyOption(): echarts.EChartsOption {
  return {
    title: {
      text: '评分指标流向',
      right: 12,
      top: 6,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    graphic: {
      type: 'text' as const,
      left: 'center',
      top: 'middle',
      style: {
        text: '暂无数据\n请先运行评价',
        fill: TEXT_PLACEHOLDER,
        fontSize: 13,
        textAlign: 'center' as const,
      },
    },
  }
}

// ==================== 算法收敛曲线（原帕累托曲线） ====================

/** 构建算法收敛曲线 option（NMF / PP 的 cost_history） */
export function buildParetoOption(data: any, _selectedPlanLabels: string[]): echarts.EChartsOption {
  const algos = data?.algorithms || []
  console.log('[buildParetoOption] algos count:', algos.length, 'data keys:', Object.keys(data || {}))

  return {
    title: {
      text: '算法收敛曲线',
      right: 12,
      top: 4,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    tooltip: {
      ...baseTooltip,
      formatter: (params: any) => {
        if (Array.isArray(params)) {
          const p = params[0]
          return `${p.seriesName}<br/>迭代次数：${p.data[0]}<br/>适应度：${typeof p.data[1] === 'number' ? formatExponential(p.data[1], 4) : p.data[1]}`
        }
        return ''
      },
    },
    legend: {
      ...baseLegend,
      data: algos.map((a: any) => a.name),
      top: 22,
    },
    grid: createGrid(48, 22, 50, 16),
    xAxis: {
      ...baseValueXAxis,
      name: '迭代次数',
      nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
      axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
    },
    yAxis: {
      ...baseValueYAxis,
      name: '适应度',
      nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
      axisLabel: {
        color: TEXT_SECONDARY,
        fontSize: 9,
        formatter: (v: number) => v >= 1000 ? formatExponential(v, 1) : formatNumber(v, 4),
      },
    },
    series: algos.map((a: any) => ({
      name: a.name,
      type: 'line',
      data: (a.cost_history || []).map((v: number, i: number) => [i + 1, v]),
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2, color: a.color || TECH_BLUE },
      itemStyle: { color: a.color || TECH_BLUE },
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
  const sourceName = `最终来水量\n${formatNumber(totalValue, 2)} 亿m³`

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
