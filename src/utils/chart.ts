/**
 * ECharts 主题色常量与通用配置
 *
 * 用途：统一管理项目中所有 ECharts 图表的颜色、tooltip、坐标轴等通用样式，
 * 避免在每个组件中硬编码颜色值，方便后期全局调整主题。
 */

// ==================== 主题色 ====================

/** 方案配色板（评价决策等需要区分多方案的图表） */
export const PLAN_COLORS: Record<string, string> = {
  '方案一': '#00afff',
  '方案二': '#00e5a0',
  '方案三': '#ffaa00',
  '方案四': '#b37feb',
}

/** 水库配色板（按水库名称映射） */
export const RESERVOIR_COLORS: Record<string, string> = {
  '龙羊峡水库': '#00afff',
  '刘家峡水库': '#00e5a0',
  '青铜峡水库': '#ffaa00',
  '拉西瓦水库': '#b37feb',
  '李家峡水库': '#ff6b6b',
  '公伯峡水库': '#52c41a',
  '积石峡水库': '#e88a3a',
  '玛尔挡水库': '#d45a7a',
  '黑山峡水库': '#3aa0c0',
  '盐锅峡水库': '#8ab84a',
  '八盘峡水库': '#c07040',
  '大峡水库': '#5a8ab8',
  '小峡水库': '#b070a0',
}

/** 桑基图节点色板 */
export const SANKEY_NODE_COLORS = [
  '#4a90d9', '#50b8a0', '#e88a3a', '#7a5cc0', '#d45a7a',
  '#3aa0c0', '#8ab84a', '#c07040', '#5a8ab8', '#b070a0',
  '#c05040', '#40a080', '#8a6ab0', '#d0a040', '#5090b0',
  '#b08060', '#60a0a0', '#a06080',
]

/** 水量流向色板 */
export const WATER_FLOW_COLORS = ['#00afff', '#00e5a0', '#ffaa00', '#b37feb', '#ff6b6b', '#52c41a']

/** 通用序列色板（无特定含义时循环使用） */
export const SERIES_COLORS = ['#00afff', '#00e5a0', '#ffaa00', '#b37feb', '#ff6b6b', '#52c41a', '#e88a3a', '#3aa0c0']

// ==================== 单色常量（用于 JS/ECharts 上下文） ====================

/** 主题蓝（CSS 变量在 ECharts 中不可用，JS 上下文用此常量） */
export const TECH_BLUE = '#00afff'
/** 主题青 */
export const TECH_CYAN = '#00d4ff'
/** 主题绿 */
export const TECH_GREEN = '#00e5a0'
/** 主题橙 */
export const TECH_ORANGE = '#ffaa00'

// ==================== 文字颜色 ====================

/** 主文字（标题、重要数值） */
export const TEXT_PRIMARY = '#e0e6ed'
/** 正文文字 */
export const TEXT_REGULAR = '#c0c8d4'
/** 辅助文字（图例、标签） */
export const TEXT_SECONDARY = '#8aa0b8'
/** 占位符/极淡文字 */
export const TEXT_PLACEHOLDER = '#6e8a9e'

// ==================== 线条/边框颜色 ====================

/** 坐标轴线 */
export const AXIS_LINE_COLOR = 'rgba(50, 150, 255, 0.3)'
/** 分割线 */
export const SPLIT_LINE_COLOR = 'rgba(50, 150, 255, 0.1)'
/** 边框线（tooltip 等） */
export const BORDER_COLOR = 'rgba(50, 150, 255, 0.4)'

// ==================== 背景色 ====================

/** Tooltip 背景 */
export const TOOLTIP_BG = 'rgba(6, 30, 70, 0.9)'

// ==================== 状态色 ====================

export const STATUS_COLORS = {
  normal: '#00ff88',
  warning: '#ffaa00',
  abnormal: '#ff4d4f',
  danger: '#ff4d4f',
  info: '#00afff',
} as const

// ==================== 通用配置片段 ====================

/** 通用 tooltip 配置（axis 触发） */
export const baseTooltip = {
  trigger: 'axis' as const,
  backgroundColor: TOOLTIP_BG,
  borderColor: BORDER_COLOR,
  borderWidth: 1,
  textStyle: { color: TEXT_PRIMARY, fontSize: 11 },
  axisPointer: {
    type: 'cross' as const,
    crossStyle: { color: TEXT_SECONDARY },
  },
}

/** 通用 tooltip 配置（item 触发） */
export const baseItemTooltip = {
  trigger: 'item' as const,
  backgroundColor: TOOLTIP_BG,
  borderColor: BORDER_COLOR,
  borderWidth: 1,
  textStyle: { color: TEXT_PRIMARY, fontSize: 11 },
}

/** 通用 legend 配置 */
export const baseLegend = {
  textStyle: { color: TEXT_SECONDARY, fontSize: 11 },
  bottom: 0,
  itemGap: 24,
}

/** 通用 category X 轴配置 */
export const baseCategoryXAxis = {
  type: 'category' as const,
  axisLine: { lineStyle: { color: AXIS_LINE_COLOR } },
  axisLabel: { color: TEXT_SECONDARY, fontSize: 11 },
  splitLine: { show: false },
  boundaryGap: false,
}

/** 通用 value Y 轴配置 */
export const baseValueYAxis = {
  type: 'value' as const,
  axisLine: { show: false },
  axisLabel: { color: TEXT_SECONDARY, fontSize: 11 },
  splitLine: { lineStyle: { color: SPLIT_LINE_COLOR, type: 'dashed' as const } },
  nameTextStyle: { color: TEXT_SECONDARY, fontSize: 11 },
}

/** 通用 value X 轴配置（散点图等） */
export const baseValueXAxis = {
  type: 'value' as const,
  axisLine: { lineStyle: { color: AXIS_LINE_COLOR } },
  axisLabel: { color: TEXT_SECONDARY, fontSize: 11 },
  splitLine: { lineStyle: { color: SPLIT_LINE_COLOR } },
  nameTextStyle: { color: TEXT_SECONDARY, fontSize: 11 },
}

// ==================== 工具函数 ====================

/** 创建面积渐变色 */
export function createAreaGradient(color: string, topOpacity = 0.2, bottomOpacity = 0.02) {
  return {
    color: {
      type: 'linear' as const,
      x: 0, y: 0, x2: 0, y2: 1,
      colorStops: [
        { offset: 0, color: color + Math.round(topOpacity * 255).toString(16).padStart(2, '0') },
        { offset: 1, color: color + Math.round(bottomOpacity * 255).toString(16).padStart(2, '0') },
      ],
    },
  }
}

/** 创建带标题的通用 grid 配置 */
export function createGrid(top = 20, bottom = 45, left = 65, right = 80) {
  return { top, bottom, left, right }
}
