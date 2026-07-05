/**
 * 数值格式化工具
 *
 * 统一处理数字精度、空值回退、千分位等格式化逻辑。
 * 用于表格、卡片、图表等场景的数值展示。
 */

/**
 * 格式化数字到指定小数位数，空值返回 fallback
 *
 * @example
 *   formatNumber(12.3456, 2)           // '12.35'
 *   formatNumber(null, 2)              // '-'
 *   formatNumber(undefined, 2, '--')   // '--'
 */
export function formatNumber(
  value: number | null | undefined,
  digits: number = 2,
  fallback: string = '-',
): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return fallback
  }
  return value.toFixed(digits)
}

/**
 * 格式化数字为千分位分隔字符串
 *
 * @example
 *   formatThousands(1234567.89, 2)   // '1,234,567.89'
 *   formatThousands(null, 0)         // '-'
 */
export function formatThousands(
  value: number | null | undefined,
  digits: number = 0,
  fallback: string = '-',
): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return fallback
  }
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })
}

/**
 * 格式化为百分比字符串
 *
 * @example
 *   formatPercent(0.875, 1)   // '87.5%'
 *   formatPercent(87.5, 1)    // '87.5%'
 */
export function formatPercent(
  value: number | null | undefined,
  digits: number = 1,
  fallback: string = '-',
): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return fallback
  }
  // 当值 ≤ 1 时视为 0-1 比例值；> 1 时视为已乘 100 的百分比值
  const percent = value <= 1 ? value * 100 : value
  return `${percent.toFixed(digits)}%`
}

/**
 * 带单位的格式化
 *
 * @example
 *   formatWithUnit(2486.35, 'm', 2)   // '2486.35 m'
 *   formatWithUnit(null, 'm')         // '-'
 */
export function formatWithUnit(
  value: number | null | undefined,
  unit: string,
  digits: number = 2,
  fallback: string = '-',
): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return fallback
  }
  return `${value.toFixed(digits)} ${unit}`
}

// ==================== 业务领域专用快捷函数 ====================

/** 水位格式化（保留 2 位小数，单位 m） */
export const formatLevel = (value: number | null | undefined): string =>
  formatNumber(value, 2)

/** 流量格式化（保留 1 位小数，单位 m³/s） */
export const formatFlow = (value: number | null | undefined): string =>
  formatNumber(value, 1)

/** 库容格式化（保留 2 位小数，单位 亿m³） */
export const formatStorage = (value: number | null | undefined): string =>
  formatNumber(value, 2)

/** 发电量格式化（千分位整数，单位 kWh） */
export const formatPower = (value: number | null | undefined): string =>
  formatThousands(value, 0)

/** 评价得分格式化（保留 3 位小数） */
export const formatScore = (value: number | null | undefined): string =>
  formatNumber(value, 3)
