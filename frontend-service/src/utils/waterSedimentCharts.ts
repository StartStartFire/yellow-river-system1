/**
 * 水沙耦合仿真模型 → ECharts option 适配
 *
 * 把后端 /results 的 result 字段（WaterSedimentResult）转换为 4 类图表：
 *  1. 断面洪水演进（多断面折线）
 *  2. 迭代收敛（刘家峡下泄 vs 兰州断面流量，迭代反馈）
 *  3. 龙羊峡调度过程（水位/出力/入库/出库）
 *  4. 河道冲淤（各段冲淤量柱状 + 合计）
 *
 * 复用 chart.ts 的通用配置工厂，保证与全系统图表风格一致。
 */
import * as echarts from 'echarts'
import type { WaterSedimentResult } from '@/api'
import {
  TEXT_PRIMARY,
  TEXT_SECONDARY,
  baseTooltip,
  baseItemTooltip,
  baseCategoryXAxis,
  baseValueYAxis,
  createGrid,
  createAreaGradient,
  SERIES_COLORS,
} from '@/utils/chart'

/** 8 个断面（自上游至下游） */
export const WATER_SEDIMENT_SECTIONS = ['兰州', '下河沿', '青铜峡', '石嘴山', '巴彦高勒', '三湖河口', '包头', '头道拐']

/** 生成统一的时间标签（1~N 时段） */
function buildTimeLabels(n: number): string[] {
  return Array.from({ length: n }, (_, i) => `${i + 1}`)
}

/** 生成断面洪水演进 option */
export function buildSectionFloodOption(data: WaterSedimentResult): echarts.EChartsOption {
  const sections = data.sections || {}
  const names = WATER_SEDIMENT_SECTIONS.filter(s => (sections[s] || []).length > 0)
  if (names.length === 0) return { title: { text: '无断面洪水数据' }, series: [] }

  const labels = buildTimeLabels((sections[names[0]] || []).length)

  return {
    tooltip: { ...baseTooltip, valueFormatter: (v: unknown) => `${Number(v).toFixed(0)} m³/s` },
    legend: {
      data: names,
      textStyle: { color: TEXT_SECONDARY, fontSize: 10 },
      top: 2,
      type: 'scroll',
    },
    grid: createGrid(36, 38, 50, 24),
    xAxis: { ...baseCategoryXAxis, data: labels, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
    yAxis: {
      ...baseValueYAxis,
      name: '流量（m³/s）',
      nameTextStyle: { color: TEXT_SECONDARY, fontSize: 9 },
      axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
    },
    dataZoom: [{ type: 'inside', start: 0, end: 100 }],
    series: names.map((s, i) => ({
      name: s,
      type: 'line' as const,
      data: sections[s],
      smooth: true,
      symbol: 'none' as const,
      lineStyle: { width: 1.8, color: SERIES_COLORS[i % SERIES_COLORS.length] },
      itemStyle: { color: SERIES_COLORS[i % SERIES_COLORS.length] },
    })),
  }
}

/** 生成迭代收敛 option（刘家峡下泄 vs 兰州断面流量） */
export function buildIterationOption(data: WaterSedimentResult): echarts.EChartsOption {
  const hist = data.iteration_history || {}
  const ljx = hist.liujiaxia || []
  const lanzhou = hist.lanzhou || []

  const series: any[] = []
  ljx.forEach((arr, idx) => {
    if (!Array.isArray(arr) || arr.length === 0) return
    series.push({
      name: `迭代${idx + 1}`,
      type: 'line' as const,
      data: arr,
      smooth: true,
      symbolSize: 3,
      lineStyle: { width: 1.4, color: SERIES_COLORS[idx % SERIES_COLORS.length] },
      itemStyle: { color: SERIES_COLORS[idx % SERIES_COLORS.length] },
    })
  })
  lanzhou.forEach((arr, idx) => {
    if (!Array.isArray(arr) || arr.length === 0) return
    series.push({
      name: `兰州-迭代${idx + 1}`,
      type: 'line' as const,
      data: arr,
      smooth: true,
      symbol: 'none' as const,
      lineStyle: { width: 1, type: 'dashed' as const, color: SERIES_COLORS[idx % SERIES_COLORS.length] },
      itemStyle: { color: SERIES_COLORS[idx % SERIES_COLORS.length] },
    })
  })

  if (series.length === 0) return { title: { text: '无迭代收敛数据' }, series: [] }

  return {
    tooltip: { ...baseTooltip },
    legend: {
      data: series.map(s => s.name),
      textStyle: { color: TEXT_SECONDARY, fontSize: 9 },
      top: 2,
      type: 'scroll',
    },
    grid: createGrid(42, 38, 50, 24),
    xAxis: { ...baseCategoryXAxis, data: [], axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
    yAxis: {
      ...baseValueYAxis,
      name: '流量（m³/s）',
      nameTextStyle: { color: TEXT_SECONDARY, fontSize: 9 },
      axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
    },
    series,
  }
}

/** 生成龙羊峡调度过程 option（水位/出力/入库/出库多指标） */
export function buildReservoirOption(data: WaterSedimentResult): echarts.EChartsOption {
  const res = data.reservoir?.longyangxia
  if (!res) return { title: { text: '无龙羊峡调度数据' }, series: [] }

  const labels = buildTimeLabels((res.level || []).length)
  const seriesDef = [
    { name: '水位（m）', data: res.level, color: SERIES_COLORS[0] },
    { name: '出力（兆瓦）', data: res.power, color: SERIES_COLORS[2] },
    { name: '入库流量（m³/s）', data: res.inflow, color: SERIES_COLORS[3] },
    { name: '出库流量（m³/s）', data: res.outflow, color: SERIES_COLORS[1] },
  ].filter(s => (s.data || []).length > 0)

  if (seriesDef.length === 0) return { title: { text: '无龙羊峡调度数据' }, series: [] }

  return {
    tooltip: { ...baseTooltip },
    legend: {
      data: seriesDef.map(s => s.name),
      textStyle: { color: TEXT_SECONDARY, fontSize: 10 },
      top: 2,
      type: 'scroll',
    },
    grid: createGrid(40, 38, 52, 24),
    xAxis: { ...baseCategoryXAxis, data: labels, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
    yAxis: {
      ...baseValueYAxis,
      name: '数值',
      nameTextStyle: { color: TEXT_SECONDARY, fontSize: 9 },
      axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
    },
    dataZoom: [{ type: 'inside', start: 0, end: 100 }],
    series: seriesDef.map(s => ({
      name: s.name,
      type: 'line' as const,
      data: s.data,
      smooth: true,
      symbol: 'none' as const,
      lineStyle: { width: 1.8, color: s.color },
      itemStyle: { color: s.color },
    })),
  }
}

/** 生成河道冲淤 option（各段冲淤量柱状） */
export function buildSedimentOption(data: WaterSedimentResult): echarts.EChartsOption {
  const sed = data.sediment
  const segments = sed?.segments || []
  if (segments.length === 0) {
    return {
      title: { text: '无河道冲淤数据' },
      series: [],
    }
  }

  const names = segments.map(s => s['段号'])
  const values = segments.map(s => s['总冲淤量(m³)'])
  const total = sed?.total ?? 0

  return {
    tooltip: {
      ...baseItemTooltip,
      formatter: (p: any) => {
        const seg = segments[p.dataIndex]
        return `${seg['段号']}<br/>段长: ${seg['段长(km)']} km<br/>总冲淤量: ${Number(seg['总冲淤量(m³)']).toFixed(0)} m³`
      },
    },
    title: {
      text: `全河段合计: ${Number(total).toFixed(0)} m³`,
      left: 'center',
      top: 0,
      textStyle: { color: TEXT_PRIMARY, fontSize: 11 },
    },
    grid: createGrid(28, 38, 64, 24),
    xAxis: { ...baseCategoryXAxis, data: names, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
    yAxis: {
      ...baseValueYAxis,
      name: '冲淤量（m³）',
      nameTextStyle: { color: TEXT_SECONDARY, fontSize: 9 },
      axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
    },
    series: [{
      name: '总冲淤量',
      type: 'bar' as const,
      data: values.map(v => ({
        value: v,
        itemStyle: { color: v >= 0 ? SERIES_COLORS[1] : SERIES_COLORS[4] },
      })),
      barWidth: '55%',
    }],
  }
}

/** 生成断面洪水面积图（带渐变，用于大图） */
export function buildSectionFloodAreaOption(data: WaterSedimentResult): echarts.EChartsOption {
  const base = buildSectionFloodOption(data)
  const series = (base.series as any[])?.map((s, i) => ({
    ...s,
    areaStyle: createAreaGradient(s.lineStyle?.color || SERIES_COLORS[i % SERIES_COLORS.length], 0.18, 0.02),
  })) || []
  return { ...base, series }
}
