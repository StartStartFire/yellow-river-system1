<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import EvalTabNav from '@/components/evaluation-decision/EvalTabNav.vue'
import PlanSelectorBar from '@/components/evaluation-decision/PlanSelectorBar.vue'
import EvaluationPanel from '@/components/evaluation-decision/EvaluationPanel.vue'
import DecisionPanel from '@/components/evaluation-decision/DecisionPanel.vue'
import {
  buildRadarOption,
  buildSankeyOption,
  buildParetoOption,
  buildProcessOption,
  buildWaterFlowOption,
} from '@/utils/evaluationCharts'
import {
  evaluationDecisionState as pageState,
  planOptions,
  planLabelMap,
  radarData,
  evaluationSankeyData,
  paretoData,
  rankingData,
  getDecisionPlanData,
} from '@/mock/evaluationDecision'

// ========== 页面状态 ==========
const plans = planOptions.data

// 默认选中方案一、二、三
const selectedComparePlans = ref<string[]>([...pageState.data.selectedComparePlans])

// Tab 切换（默认评价分析）
const activeTab = ref('evaluation')

// 决策分析当前方案（默认方案二）
const currentDecisionPlan = ref(pageState.data.currentDecisionPlan)

// 决策分析方案数据
const decisionPlanData = computed(() => getDecisionPlanData(currentDecisionPlan.value))

// 决策分析目标满足情况
const targets = computed(() => decisionPlanData.value.targets)

// 过程曲线页签
const processTabOptions = [
  { key: 'water', label: '水位变化' },
  { key: 'flow', label: '流量变化' },
  { key: 'power', label: '出力变化' },
]
const activeProcessTab = ref('water')

// 被选中的方案标签集合（用于图表过滤）
const selectedPlanLabels = computed(() => {
  return selectedComparePlans.value.map(v => planLabelMap[v]).filter(Boolean)
})

// ========== 子组件 refs（用于 Tab 切换后统一 resize） ==========
const evaluationPanelRef = ref<InstanceType<typeof EvaluationPanel> | null>(null)
const decisionPanelRef = ref<InstanceType<typeof DecisionPanel> | null>(null)

// ========== 图表 option（调用 utils 中的纯函数构建） ==========
const radarOption = computed<echarts.EChartsOption>(() => {
  return buildRadarOption(radarData.data, selectedPlanLabels.value)
})

const sankeyOption = computed<echarts.EChartsOption>(() => {
  return buildSankeyOption(evaluationSankeyData.data)
})

const paretoOption = computed<echarts.EChartsOption>(() => {
  return buildParetoOption(paretoData.data, selectedPlanLabels.value)
})

const processOption = computed<echarts.EChartsOption>(() => {
  return buildProcessOption(decisionPlanData.value, activeProcessTab.value)
})

const waterFlowOption = computed<echarts.EChartsOption>(() => {
  return buildWaterFlowOption(decisionPlanData.value.waterUsage)
})

// ========== 交互事件 ==========

const handleTabSwitch = (tab: string) => {
  activeTab.value = tab
  // 二次 resize 确保 display 变化后 ECharts 获取正确尺寸
  setTimeout(() => {
    evaluationPanelRef.value?.resize()
    decisionPanelRef.value?.resize()
  }, 200)
  setTimeout(() => {
    evaluationPanelRef.value?.resize()
    decisionPanelRef.value?.resize()
  }, 400)
}

// 导出方案
const handleExportPlan = () => {
  ElMessage.info('当前为前端原型，暂不支持真实导出')
}

// ========== watch ==========
watch(selectedComparePlans, (val, oldVal) => {
  if (val.length === 0 && oldVal && oldVal.length > 0) {
    // 避免无限循环：用 nextTick 重置
    nextTick(() => { selectedComparePlans.value = ['plan-1'] })
    return
  }
  // BaseChart 自动响应 computed option 变化，无需手动 renderCharts
})

// activeTab 变化时需要手动 resize（v-show display 切换后容器尺寸变化）
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
      <!-- 顶部：多方案对比选择 -->
      <PlanSelectorBar
        :plans="plans"
        v-model:selected-plans="selectedComparePlans"
      />

      <!-- 评价分析面板（雷达图 + 桑基图 + 帕累托曲线 + 排名表格） -->
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
