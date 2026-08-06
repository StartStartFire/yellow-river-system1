/**
 * 案例库工具函数
 *
 * 集中管理案例库页面用到的图标、渐变背景、评分颜色等纯函数，
 * 方便在多个子组件中复用，避免重复定义。
 */
import { TECH_CYAN, TECH_ORANGE, TEXT_SECONDARY } from '@/utils/chart'

/** 按案例 iconType 返回对应的 SVG 字符串 */
export function getIconByType(type: string): string {
  const icons: Record<string, string> = {
    benefit: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    supply: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M12 2.69l5.66 5.66a8 8 0 11-11.31 0z" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    realtime: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <circle cx="12" cy="12" r="10"/>
      <path d="M12 6v6l4 2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    hybrid: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <circle cx="12" cy="12" r="4"/>
      <path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" stroke-linecap="round"/>
    </svg>`,
    flood: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M12 12v4m0 0l-2-2m2 2l2-2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    eco: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    drought: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M14 14.76V3.5a2.5 2.5 0 00-5 0v11.26a4.5 4.5 0 105 0z" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
  }
  return icons[type] || icons['benefit']
}

/** 按案例 cover 类型返回对应的 CSS 渐变背景 */
export function getCoverGradient(type: string): string {
  const gradients: Record<string, string> = {
    'flood-control': 'linear-gradient(135deg, rgba(0, 175, 255, 0.25) 0%, rgba(0, 229, 255, 0.08) 100%)',
    'drought': 'linear-gradient(135deg, rgba(255, 170, 0, 0.25) 0%, rgba(255, 200, 0, 0.08) 100%)',
    'realtime': 'linear-gradient(135deg, rgba(255, 77, 79, 0.25) 0%, rgba(255, 100, 100, 0.08) 100%)',
    'hybrid': 'linear-gradient(135deg, rgba(179, 127, 235, 0.25) 0%, rgba(180, 130, 240, 0.08) 100%)',
    'autumn-flood': 'linear-gradient(135deg, rgba(255, 120, 50, 0.25) 0%, rgba(255, 150, 80, 0.08) 100%)',
    'benefit': 'linear-gradient(135deg, rgba(0, 175, 255, 0.25) 0%, rgba(0, 229, 255, 0.08) 100%)',
    'eco': 'linear-gradient(135deg, rgba(82, 196, 26, 0.25) 0%, rgba(100, 200, 50, 0.08) 100%)',
  }
  return gradients[type] || gradients['flood-control']
}

/** 按评分返回对应颜色 */
export function getScoreColor(score: number): string {
  if (score >= 90) return '#00ff88'
  if (score >= 80) return TECH_CYAN
  if (score >= 70) return TECH_ORANGE
  return '#ff4d4f'
}

/** 按变化类型返回对应颜色 */
export function getChangeColor(type: string): string {
  if (type === 'up') return '#00ff88'
  if (type === 'down') return TECH_ORANGE
  if (type === 'success') return '#00ff88'
  if (type === 'excellent') return TECH_CYAN
  return TEXT_SECONDARY
}
