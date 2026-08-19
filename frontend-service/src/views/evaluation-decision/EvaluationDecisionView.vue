<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import EvalTabNav from '@/components/evaluation-decision/EvalTabNav.vue'
import PlanSelectorBar from '@/components/evaluation-decision/PlanSelectorBar.vue'
import EvaluationPanel from '@/components/evaluation-decision/EvaluationPanel.vue'
import DecisionPanel from '@/components/evaluation-decision/DecisionPanel.vue'
import {
  buildRadarOption,
  buildSankeyOptionFromRaw,
  buildParetoOption,
  buildProcessOption,
  buildWaterFlowOption,
} from '@/utils/evaluationCharts'
import { getEvaluateResult, postEvaluate, getDecisionPlans } from '@/api'
import type { EvaluateDetails, DecisionPlanDetail } from '@/api'
import { useEvaluationData, ALGO_DISPLAY_NAMES } from '@/composables/useEvaluationData'
import type { DecisionPlanDataBundle } from '@/types/evaluation'
import {
  evaluationDecisionState as pageState,
  planOptions,
  planLabelMap,
} from '@/mock/evaluationDecision'

const route = useRoute()

// ── job_id（来自 URL query，从过程透明页面传入） ──
const jobId = ref((route.query.job_id as string) || '')

// ── 评价真实数据状态 ──
const evalStatus = ref<'not_requested' | 'loading' | 'evaluated' | 'error'>('not_requested')
const evalError = ref('')
const evalCache = ref<EvaluateDetails | null>(null)

// 是否使用真实数据
const hasRealData = computed(() => evalStatus.value === 'evaluated' && evalCache.value)

// ── 使用 composable 处理数据转换 ──
const { realPlanCount, radarData, convergenceData, rankingData } =
  useEvaluationData(evalCache)

// ── 方案选择列表（排名前 10 个个体，来自评价算法排名） ──
const PLAN_LABELS = Array.from({ length: 10 }, (_, i) => `方案${i + 1}`)

const plans = computed(() => {
  if (hasRealData.value) {
    return PLAN_LABELS.map((label, i) => ({
      label,
      value: `plan-${i + 1}`,
    }))
  }
  return planOptions.data
})

const currentPlanLabels = computed(() => {
  if (hasRealData.value) {
    return Object.fromEntries(
      PLAN_LABELS.map((label, i) => [`plan-${i + 1}`, label]),
    )
  }
  return planLabelMap
})

// ── 选中方案（默认选中排名前 3） ──
const selectedComparePlans = ref<string[]>(['plan-1', 'plan-2', 'plan-3'])

const selectedPlanLabels = computed(() => {
  const labels = currentPlanLabels.value
  return selectedComparePlans.value.map((v) => (labels as Record<string, string>)[v] || '').filter(Boolean)
})

/** 选中的方案索引（0~9），传给雷达图按位置索引过滤 */
const selectedPlanIndices = computed(() =>
  selectedComparePlans.value
    .map((v) => parseInt(v.replace('plan-', '')) - 1)
    .filter((i) => i >= 0),
)


// ── 真实方案选择默认值 ──
// Tab 切换
const activeTab = ref('evaluation')

// 决策分析当前方案
const currentDecisionPlan = ref(pageState.data.currentDecisionPlan)

// ── 决策分析真实数据状态（GET /decision/{job_id}） ──
const decisionPlans = ref<DecisionPlanDetail[] | null>(null)
const decisionYears = ref<{ start: number | null; end: number | null }>({ start: null, end: null })

/** 真实方案数据可用（有 job_id 且后端返回了 plan_details） */
const hasRealDecisionData = computed(() => !!decisionPlans.value && decisionPlans.value.length > 0)

// 目标项元数据（后端 key → 中文名）
const TARGET_META: { key: keyof DecisionPlanDetail['targets']; name: string }[] = [
  { key: 'power', name: '发电目标' },
  { key: 'ecology', name: '生态目标' },
  { key: 'irrigation', name: '灌溉目标' },
  { key: 'domestic', name: '生活供水目标' },
  { key: 'spill', name: '弃水控制' },
  { key: 'sediment', name: '冲沙目标' },
]

// 水量分配元数据（后端 key → 中文名）
const USAGE_META: { key: keyof DecisionPlanDetail['water_usage']; name: string }[] = [
  { key: 'power', name: '发电' },
  { key: 'ecology', name: '生态' },
  { key: 'irrigation', name: '灌溉' },
  { key: 'domestic', name: '生活' },
  { key: 'spill', name: '弃水' },
  { key: 'sediment', name: '冲沙' },
]

/** 目标满足状态：≥90 已满足，≥70 基本满足，否则未满足 */
const targetStatus = (rate: number): string =>
  rate >= 90 ? '已满足' : rate >= 70 ? '基本满足' : '未满足'

/** 构造时间轴标签（每时段 = 1 旬，每年 20 时段；无年份信息时退化为序号） */
const buildDecisionDates = (n: number, years: { start: number | null; end: number | null }): string[] => {
  const labels: string[] = []
  for (let k = 0; k < n; k++) {
    const period = (k % 20) + 1
    const year = years.start != null ? years.start + Math.floor(k / 20) : null
    labels.push(year != null ? `${year}-${String(period).padStart(2, '0')}` : `T${k + 1}`)
  }
  return labels
}

/** 将后端方案明细转换为 DecisionPanel 所需的数据包 */
const buildRealDecisionBundle = (p: DecisionPlanDetail): DecisionPlanDataBundle => {
  const n = Math.max(p.level_long?.length || 0, p.qout_long?.length || 0, p.power_long?.length || 0)
  const dates = buildDecisionDates(n, decisionYears.value)

  const targets = TARGET_META.map(({ key, name }) => {
    const rate = Number(p.targets?.[key] ?? 0)
    return { name, status: targetStatus(rate), rate }
  })

  const usageItems = USAGE_META.map(({ key, name }) => ({
    name,
    value: Number(p.water_usage?.[key] ?? 0),
  }))
  const totalUsage = usageItems.reduce((s, u) => s + u.value, 0) || 1
  const waterUsage = usageItems.map((u) => ({
    ...u,
    percent: parseFloat(((u.value / totalUsage) * 100).toFixed(1)),
  }))

  // 出力：模型单位为万kW（龙羊峡装机钳位 128、刘家峡 122.5），转为 MW 统一坐标轴
  const toMW = (arr: number[]) => (arr || []).map((v) => v * 10)

  return {
    targets,
    waterLevel: {
      dates,
      longyang: p.level_long || [],
      liujia: p.level_liu || [],
      floodLimit: 2594,   // 龙羊峡汛限水位（m）
      normalLevel: 2600,  // 龙羊峡正常蓄水位（m）
    },
    flow: {
      dates,
      longyang: p.qout_long || [],
      liujia: p.qout_liu || [],
    },
    power: {
      dates,
      longyang: toMW(p.power_long),
      liujia: toMW(p.power_liu),
      longyangCapacity: 1280,  // 龙羊峡装机容量（MW）
      liujiaCapacity: 1225,    // 刘家峡装机容量（MW）
    },
    waterUsage,
  }
}

// 决策分析空数据包（无 job_id / 无真实数据时使用，展示为空）
const EMPTY_DECISION_BUNDLE: DecisionPlanDataBundle = {
  targets: [],
  waterLevel: { dates: [], longyang: [], liujia: [], floodLimit: 0, normalLevel: 0 },
  flow: { dates: [], longyang: [], liujia: [] },
  power: { dates: [], longyang: [], liujia: [], longyangCapacity: 0, liujiaCapacity: 0 },
  waterUsage: [],
}

// 决策分析数据包：仅有真实数据时填充，否则为空（与评价分析展示一致）
const decisionPlanData = computed<DecisionPlanDataBundle>(() => {
  if (hasRealDecisionData.value) {
    const k = parseInt(currentDecisionPlan.value.replace('plan-', '')) - 1
    const plans = decisionPlans.value!
    const p = (k >= 0 && k < plans.length) ? plans[k] : plans[0]
    return buildRealDecisionBundle(p)
  }
  return EMPTY_DECISION_BUNDLE
})
const targets = computed(() => decisionPlanData.value.targets)

// 过程曲线页签
const processTabOptions = [
  { key: 'water', label: '水位变化' },
  { key: 'flow', label: '流量变化' },
  { key: 'power', label: '出力变化' },
]
const activeProcessTab = ref('water')

// ── 子组件 refs ──
const evaluationPanelRef = ref<InstanceType<typeof EvaluationPanel> | null>(null)
const decisionPanelRef = ref<InstanceType<typeof DecisionPanel> | null>(null)

// ── 图表 option ──
const radarOption = computed<echarts.EChartsOption>(() =>
  buildRadarOption(radarData.value, selectedPlanIndices.value),
)
const sankeyOption = computed<echarts.EChartsOption>(() =>
  buildSankeyOptionFromRaw(hasRealData.value ? (evalCache.value?.raw_indicators || null) : null),
)
const paretoOption = computed<echarts.EChartsOption>(() =>
  buildParetoOption(convergenceData.value, selectedPlanLabels.value),
)
const processOption = computed<echarts.EChartsOption>(() =>
  buildProcessOption(decisionPlanData.value, activeProcessTab.value),
)
const waterFlowOption = computed<echarts.EChartsOption>(() =>
  buildWaterFlowOption(decisionPlanData.value.waterUsage),
)

// ── 获取缓存的评价结果 ──
const fetchEvalCache = async () => {
  if (!jobId.value) return
  try {
    const cached = await getEvaluateResult(jobId.value)
    console.log('[fetchEvalCache] status:', cached.status, 'has rankings:', !!cached.rankings, 'has convergence:', !!cached.convergence)
    if (cached.status === 'evaluated' && cached.rankings) {
      evalCache.value = cached as unknown as EvaluateDetails
      evalStatus.value = 'evaluated'
      console.log('[fetchEvalCache] evalCache set, hasData:', hasRealData.value)
    }
  } catch (e) {
    console.error('[fetchEvalCache] error:', e)
  }
}

// ── 运行评价 ──
const runEvaluation = async () => {
  if (!jobId.value) return
  evalStatus.value = 'loading'
  evalError.value = ''
  try {
    const result = await postEvaluate({ job_id: jobId.value, method: 'ALL' })
    if (result.status === 'error') {
      evalStatus.value = 'error'
      evalError.value = result.message || '评价失败'
      ElMessage.error(evalError.value)
      return
    }
    // 从 details 中提取缓存数据（POST /evaluate 会把缓存结构放在 details 里）
    console.log('[runEvaluation] details keys:', Object.keys(result.details || {}))
    evalCache.value = result.details as EvaluateDetails | null
    evalStatus.value = 'evaluated'
    console.log('[runEvaluation] evalCache set, has conv:', !!evalCache.value?.convergence, 'has rankings:', !!evalCache.value?.rankings)
    // 评价完成后方案排序变化，重新拉取决策方案（按整合排名重排）
    fetchDecisionPlans()
    ElMessage.success('评价完成')
  } catch (e: any) {
    evalStatus.value = 'error'
    evalError.value = e.message || '评价请求失败'
    ElMessage.error(evalError.value)
  }
}

// ── 获取决策分析方案明细（真实数据） ──
const fetchDecisionPlans = async () => {
  if (!jobId.value) return
  try {
    const res = await getDecisionPlans(jobId.value)
    if (res.plans && res.plans.length > 0) {
      decisionPlans.value = res.plans
      decisionYears.value = { start: res.year_start, end: res.year_end }
      console.log('[fetchDecisionPlans] loaded', res.plans.length, 'plans, evaluated:', res.evaluated)
    }
  } catch (e) {
    console.error('[fetchDecisionPlans] error:', e)
  }
}

// ── onMounted ──
onMounted(() => {
  if (jobId.value) {
    fetchEvalCache()
    fetchDecisionPlans()
  }
})

// ── 交互事件 ──
const handleTabSwitch = (tab: string) => {
  activeTab.value = tab
  setTimeout(() => {
    evaluationPanelRef.value?.resize()
    decisionPanelRef.value?.resize()
  }, 200)
  setTimeout(() => {
    evaluationPanelRef.value?.resize()
    decisionPanelRef.value?.resize()
  }, 400)
}

const handleExportPlan = () => {
  ElMessage.info('当前为前端原型，暂不支持真实导出')
}

watch(selectedComparePlans, (val, oldVal) => {
  if (val.length === 0 && oldVal && oldVal.length > 0) {
    nextTick(() => {
      selectedComparePlans.value = ['plan-1']
    })
  }
})

watch(activeTab, () => {
  setTimeout(() => {
    evaluationPanelRef.value?.resize()
    decisionPanelRef.value?.resize()
  }, 300)
})
</script>

<template>
  <div class="evaluation-decision-view">
    <!-- ===== Tab 导航栏 ===== -->
    <EvalTabNav :active-tab="activeTab" @switch="handleTabSwitch" />

    <!-- ===== 评价分析内容 ===== -->
    <div v-show="activeTab === 'evaluation'" class="tab-content">
      <!-- 评价状态提示栏（有 job_id 时显示） -->
      <div v-if="jobId" class="eval-status-bar" :class="'eval-' + evalStatus">
        <span class="eval-status-label">
          <template v-if="evalStatus === 'not_requested'">📋 任务 {{ jobId.slice(0, 8) }}… — 尚未评价</template>
          <template v-else-if="evalStatus === 'loading'">⏳ 正在运行评价算法（NMF + PP + AHP-Fuzzy）…</template>
          <template v-else-if="evalStatus === 'evaluated'">✅ 评价已完成 — 排名前 10 个方案，3 种算法 + 整合排名</template>
          <template v-else-if="evalStatus === 'error'">❌ 评价失败：{{ evalError }}</template>
        </span>
        <el-button
          v-if="evalStatus === 'not_requested' || evalStatus === 'error'"
          type="primary"
          size="small"
          :loading="evalStatus === 'loading'"
          @click="runEvaluation"
        >
          {{ evalStatus === 'error' ? '重新评价' : '开始评价' }}
        </el-button>
      </div>

      <!-- 顶部：多方案对比选择 -->
      <PlanSelectorBar
        :plans="plans"
        v-model:selected-plans="selectedComparePlans"
      />

      <!-- 评价分析面板（雷达图 + 桑基图 + 收敛曲线 + 排名表格） -->
      <EvaluationPanel
        ref="evaluationPanelRef"
        :radar-option="radarOption"
        :sankey-option="sankeyOption"
        :pareto-option="paretoOption"
        :ranking-data="rankingData"
        :selected-plan-labels="selectedPlanLabels"
      />
    </div>

    <!-- ===== 决策分析内容 ===== -->
    <div v-show="activeTab === 'decision'" class="tab-content tab-content-decision">
      <DecisionPanel
        ref="decisionPanelRef"
        :plans="plans"
        v-model:current-plan="currentDecisionPlan"
        :targets="targets"
        :process-option="processOption"
        :process-tab-options="processTabOptions"
        v-model:active-process-tab="activeProcessTab"
        :water-flow-option="waterFlowOption"
        @export-plan="handleExportPlan"
      />
    </div>
  </div>
</template>

<style scoped>
.evaluation-decision-view {
  display: flex;
  flex-direction: column;
  padding: 0;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  position: relative;
  background: rgba(var(--tech-bg-rgb), 0.92);
}

/* ===== 评价状态栏 ===== */
.eval-status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  border-radius: 6px;
  margin-bottom: 6px;
  flex-shrink: 0;
  font-size: 12px;
}
.eval-status-bar.eval-not_requested {
  background: rgba(var(--tech-blue-rgb), 0.08);
  border: 1px solid rgba(var(--tech-blue-rgb), 0.15);
}
.eval-status-bar.eval-loading {
  background: rgba(255, 170, 0, 0.08);
  border: 1px solid rgba(255, 170, 0, 0.2);
}
.eval-status-bar.eval-evaluated {
  background: rgba(0, 229, 160, 0.08);
  border: 1px solid rgba(0, 229, 160, 0.15);
}
.eval-status-bar.eval-error {
  background: rgba(255, 77, 79, 0.08);
  border: 1px solid rgba(255, 77, 79, 0.15);
}
.eval-status-label {
  color: var(--tech-text-regular);
}

/* ===== Tab 内容区 ===== */
.tab-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
  padding: 0;
}

.tab-content-decision {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
