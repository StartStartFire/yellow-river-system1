/**
 * useEvaluationData — 评价数据转换与状态管理
 *
 * 从 API 返回的 EvaluateDetails 中提取：
 * - 子系统得分雷达图数据
 * - 收敛曲线数据
 * - 排名表格数据
 * - 方案标签列表
 */
import { computed, ref, watch } from 'vue'
import type { RankingAlgorithm } from '@/api'

/** NMF / PP 算法固定配色 */
export const ALGO_COLORS: Record<string, string> = { NMF: '#00afff', PP: '#00e5a0' }

export const ALGO_DISPLAY_NAMES: Record<string, string> = {
  NMF: 'NMF 非负矩阵分解',
  PP: 'PP 投影寻踪',
  AHP_FUZZY: 'AHP-Fuzzy 模糊综合',
  ALL: 'ALL 序号总和整合',
}

/** 标签格式：方案1～方案10 */
const PLAN_LABELS = Array.from({ length: 10 }, (_, i) => `方案${i + 1}`)

export function useEvaluationData(evalCache: ReturnType<typeof ref>) {
  // 方案数量
  const realPlanCount = computed(() => {
    const rankings = evalCache.value?.rankings
    if (!rankings || rankings.length === 0) return 0
    return rankings[0].ranks.length
  })

  const realPlanLabels = computed(() =>
    Array.from({ length: realPlanCount.value }, (_, i) => PLAN_LABELS[i] || `方案${i + 1}`),
  )

  const realPlanValueMap = computed(() =>
    Array.from({ length: realPlanCount.value }, (_, i) => `plan-${i + 1}`),
  )

  /** 算法得分雷达图数据（NMF H / PP z / AHP-Fuzzy final_scores） */
  const radarData = computed(() => {
    const radar = evalCache.value?.radar
    if (!radar || !radar.plans || radar.plans.length === 0) {
      return {
        indicators: [] as { name: string; max: number }[],
        plans: [] as { plan: string; values: number[] }[],
      }
    }
    // 后端已按排名排序，前端按位置规范方案名
    // 确保 plan 字段与 PLAN_COLORS 匹配（方案1~方案10）
    const count = Math.min(radar.plans.length, 10)
    const plans = Array.from({ length: count }, (_, i) => {
      const p = radar.plans[i]
      return {
        plan: PLAN_LABELS[i],
        values: p?.values || [],
      }
    })
    return { indicators: radar.indicators || [], plans }
  })

  /** 收敛曲线数据 */
  const convergenceData = computed(() => {
    const conv = evalCache.value?.convergence
    console.log('[evalData] conv:', !!evalCache.value, 'keys:', conv ? Object.keys(conv) : 'empty')
    if (!conv) return { algorithms: [] as any[], iteration_count: 0 }
    const algorithms = Object.entries(conv)
      .filter(([, ch]) => ch && ch.length > 0)
      .map(([name, ch]) => ({
        name,
        cost_history: (ch as number[]).slice(0, 200),
        color: ALGO_COLORS[name] || '#00afff',
      }))
    return {
      iteration_count: algorithms.length > 0 ? algorithms[0].cost_history.length : 500,
      algorithms,
    }
  })

  /** 排名表格数据 */
  const rankingData = computed(() => {
    const rankings = evalCache.value?.rankings
    console.log('[evalData] rankings:', !!evalCache.value, 'len:', rankings?.length)
    if (!rankings || rankings.length === 0) return { code: 200, message: 'success', data: [] as any[] }

    // 从 ALL 行提取整合排名，确定每个种群个体的位置（按排名排序）
    const allRanking = rankings.find((r) => r.algorithm === 'ALL')
    // sortOrder[i] = 整合排名第 i+1 的个体在原始 scores/ranks 数组中的索引
    const sortOrder: number[] = allRanking
      ? allRanking.ranks
          .map((rank, idx) => ({ rank, idx }))
          .sort((a, b) => a.rank - b.rank)
          .slice(0, 10)            // 只取前 10 名
          .map((item) => item.idx)
      : Array.from({ length: (rankings[0]?.scores || rankings[0]?.ranks || []).length }, (_, i) => i)

    const count = Math.min(sortOrder.length, 10)
    const labels = Array.from({ length: count }, (_, i) => PLAN_LABELS[i])

    return {
      code: 200,
      message: 'success',
      data: rankings.map((algo: RankingAlgorithm, algoIdx: number) => {
        const isAll = algo.algorithm === 'ALL'
        return {
          rank: isAll ? -1 : algoIdx + 1,
          algorithm: ALGO_DISPLAY_NAMES[algo.algorithm] || algo.algorithm,
          scores: labels.map((plan, planIdx) => {
            const srcIdx = sortOrder[planIdx]
            return {
              plan,
              value: isAll
                ? (algo.ranks[srcIdx] ?? 0) + 1
                : (algo.scores?.[srcIdx] ?? 0),
            }
          }),
        }
      }),
    }
  })

  // 方案选择默认值
  watch(realPlanCount, (n) => {
    if (n > 0) {
      // 由 view 负责设置 selectedComparePlans
    }
  })

  return { realPlanCount, realPlanLabels, realPlanValueMap, radarData, convergenceData, rankingData }
}
