<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import ConfigPlanTable from '@/components/model-config/config-summary/ConfigPlanTable.vue'
import ConfigInfoPanel from '@/components/model-config/config-summary/ConfigInfoPanel.vue'
import ConfigDetailDialog from '@/components/model-config/config-summary/ConfigDetailDialog.vue'
import ConfigConfirmDialog from '@/components/model-config/config-summary/ConfigConfirmDialog.vue'
import { TEXT_PRIMARY, baseItemTooltip, SERIES_COLORS } from '@/utils/chart'
import { useModelConfigStore } from '@/stores/modelConfig'
import { modelLabelMap, algorithmLabelMap } from '@/mock/model-config/linkage'
import { postRun } from '@/api'
import type { ConfigPlan } from '@/types/model'

const store = useModelConfigStore()
const router = useRouter()

// ==================== 方案名称 & 描述 ====================

const currentPlanName = computed(() => {
  const name = store.dispatchScenario.scenarioName?.trim()
  if (name) return name
  const objectives = store.modelAlgorithm.selectedObjectives
  const objNames: Record<string, string> = { 'water-shortage': '缺水', 'power-generation': '发电', 'coordination': '协同' }
  const tag = objectives.map(o => objNames[o] || o).join('')
  return `${tag}调度方案_${store.dispatchSubject.startTime || 'today'}`
})

const currentScenarioDesc = computed(() => {
  const type = store.scenarioConstraint.scenarioType === 'typical' ? '典型场景' : '自定义场景'
  const westRoute = store.scenarioConstraint.params.westRoute
  const westRouteLabels: Record<string, string> = { none: '无', upper: '有上无下', lower: '有下无上', all: '上线+下线' }
  return `${type}_西线${westRouteLabels[westRoute] || westRoute}`
})

// ==================== 状态管理 ====================

const currentPage = ref(1)
const pageSize = ref(13)
const searchQuery = ref('')

/** 所有方案列表 */
const plansList = ref<ConfigPlan[]>([])

/** 选中的行 ID（独立跟踪，不与 plansList.selected 绑定，避免循环） */
const selectedRowIds = ref<Set<string>>(new Set())

/** 当前页展示的数据（稳定 ref，不触发 el-table 重渲染） */
const currentPagePlans = ref<ConfigPlan[]>([])

/** 选中方案数 */
const selectedCount = computed(() => selectedRowIds.value.size)

/** 总条数 */
const totalCount = computed(() => plansList.value.length)

/** 总页数 */
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value) || 1)

/** 预估运行时间（基于种群大小 × 迭代次数） */
const estimatedTime = computed(() => {
  const pop = store.modelAlgorithm.parameters.populationSize || 15
  const iter = store.modelAlgorithm.parameters.iterationCount || 30
  // 基准：pop=15, iter=30 → 约 4 秒
  const basePop = 15
  const baseIter = 30
  const baseSeconds = 4
  const sec = Math.round(baseSeconds * (pop / basePop) * (iter / baseIter))
  if (sec < 60) return `${sec} 秒`
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m} 分 ${s} 秒`
})

function buildPlanList(): ConfigPlan[] {
  const current: ConfigPlan = {
    id: 'current-plan',
    index: 1,
    name: currentPlanName.value,
    model: modelLabelMap[store.modelAlgorithm.selectedModel] || store.modelAlgorithm.selectedModel,
    algorithm: algorithmLabelMap[store.modelAlgorithm.selectedAlgorithm] || store.modelAlgorithm.selectedAlgorithm,
    scenario: currentScenarioDesc.value,
    selected: true,
  }
  return [current]
}

function updatePageData() {
  const q = searchQuery.value.trim().toLowerCase()
  const filtered = !q ? plansList.value : plansList.value.filter(
    p => p.name.toLowerCase().includes(q) ||
      p.model.toLowerCase().includes(q) ||
      p.algorithm.toLowerCase().includes(q) ||
      p.scenario.toLowerCase().includes(q)
  )
  const start = (currentPage.value - 1) * pageSize.value
  currentPagePlans.value = filtered.slice(start, start + pageSize.value)
}

watch([plansList, currentPage, pageSize, searchQuery], updatePageData, { immediate: true, deep: true })

// ==================== 图表 ====================


const modelChartOption = computed(() => ({
  tooltip: {
    ...baseItemTooltip,
    confine: true,
    formatter: (p: any) => `${p.name}<br/>数量: ${p.value}个`,
  },
  series: [{
    type: 'pie',
    radius: ['55%', '82%'],
    center: ['40%', '50%'],
    padAngle: 2,
    itemStyle: { borderRadius: 4 },
    label: {
      show: true,
      position: 'outside',
      formatter: (p) => p.name + ' ' + p.percent + '%',
      color: '#8aa0b8',
      fontSize: 10,
      lineHeight: 15,
    },
    labelLine: {
      show: true,
      length: 6,
      length2: 6,
    },
    emphasis: {
      label: { show: true, fontSize: 12, fontWeight: 'bold', color: TEXT_PRIMARY },
      scale: false,
      itemStyle: { color: SERIES_COLORS[0] },
    },
    data: [{
      value: selectedCount.value || 1,
      name: modelLabelMap[store.modelAlgorithm.selectedModel] || store.modelAlgorithm.selectedModel,
      itemStyle: { color: SERIES_COLORS[0] },
    }],
  }],
}))

const algoChartOption = computed(() => ({
  tooltip: {
    ...baseItemTooltip,
    confine: true,
    formatter: (p: any) => `${p.name}<br/>数量: ${p.value}个`,
  },
  series: [{
    type: 'pie',
    radius: ['55%', '82%'],
    center: ['40%', '50%'],
    padAngle: 2,
    itemStyle: { borderRadius: 4 },
    label: {
      show: true,
      position: 'outside',
      formatter: (p) => p.name + ' ' + p.percent + '%',
      color: '#8aa0b8',
      fontSize: 10,
      lineHeight: 15,
    },
    labelLine: {
      show: true,
      length: 6,
      length2: 6,
    },
    emphasis: {
      label: { show: true, fontSize: 12, fontWeight: 'bold', color: TEXT_PRIMARY },
      scale: false,
      itemStyle: { color: SERIES_COLORS[1] },
    },
    data: [{
      value: selectedCount.value || 1,
      name: algorithmLabelMap[store.modelAlgorithm.selectedAlgorithm] || store.modelAlgorithm.selectedAlgorithm,
      itemStyle: { color: SERIES_COLORS[1] },
    }],
  }],
}))

// ==================== 初始化 ====================

onMounted(() => {
  plansList.value = buildPlanList()
  selectedRowIds.value = new Set(['current-plan'])
})

watch(searchQuery, () => { currentPage.value = 1 })

// ==================== 表格事件 ====================

/** 多选框变化时只更新 selectedRowIds，不修改 plansList */
const onSelectionChange = (rows: ConfigPlan[]) => {
  selectedRowIds.value = new Set(rows.map(r => r.id))
}

/** 给表格的 tableSelected：当前页中选中了的行 */
const tableSelected = computed({
  get: () => currentPagePlans.value.filter(p => selectedRowIds.value.has(p.id)),
  set: (val: ConfigPlan[]) => {
    const ids = new Set(val.map(v => v.id))
    // 合并当前页选中状态到全局
    const pageIds = new Set(currentPagePlans.value.map(p => p.id))
    for (const id of pageIds) {
      if (ids.has(id)) selectedRowIds.value.add(id)
      else selectedRowIds.value.delete(id)
    }
    selectedRowIds.value = new Set(selectedRowIds.value)
  },
})

// ==================== 操作 ====================

const handleCancel = () => { cancelDialogVisible.value = true }
const handleSave = () => { saveDialogVisible.value = true }
const handlePrev = () => { router.push('/model-config/scenario-constraint') }

const westRouteMap: Record<string, string> = {
  none: '全无', upper: '有上无下', lower: '有下无上', all: '全有',
}

function assembleRunRequest() {
  // 从日期字符串中提取年份（"YYYY-MM-DD" 或 "YYYY-MM" → YYYY）
  const startDate = store.dispatchSubject.startTime
  const endDate = store.dispatchSubject.endTime
  const year_start = startDate ? parseInt(startDate.split('-')[0]) : undefined
  const year_end = endDate ? parseInt(endDate.split('-')[0]) : undefined

  return {
    algorithm: store.modelAlgorithm.selectedAlgorithm,
    pop: store.modelAlgorithm.parameters.populationSize,
    iterate: store.modelAlgorithm.parameters.iterationCount,
    M: store.computedMValue,
    Q_sediment: parseFloat(store.scenarioConstraint.params.sedimentFlow) || 1800,
    crossover_rate: store.modelAlgorithm.parameters.crossoverRate,
    flag_xixian: westRouteMap[store.scenarioConstraint.params.westRoute] || '全无',
    year_start,
    year_end,
    ...(store.modelAlgorithm.selectedAlgorithm === 'paem'
      ? { K_mut: store.modelAlgorithm.parameters.kMut }
      : {}),
  }
}

const handleRunAll = async () => {
  if (selectedRowIds.value.size === 0) {
    ElMessage.warning('请至少选择一个配置方案')
    return
  }
  try {
    const payload = assembleRunRequest()
    const result = await postRun(payload)
    ElMessage.success('任务已提交，正在跳转至过程透明页面...')
    setTimeout(() => router.push(`/process-transparent?job_id=${result.job_id}`), 500)
  } catch (err: any) {
    ElMessage.error('提交失败: ' + (err.message || '未知错误'))
  }
}

const handleRunSingle = async (plan: ConfigPlan) => {
  try {
    const payload = assembleRunRequest()
    const result = await postRun(payload)
    ElMessage.success(`方案「${plan.name}」已启动`)
    setTimeout(() => router.push(`/process-transparent?job_id=${result.job_id}`), 500)
  } catch (err: any) {
    ElMessage.error('提交失败: ' + (err.message || '未知错误'))
  }
}

const handleAdd = () => {
  const newPlan: ConfigPlan = {
    id: `plan-new-${Date.now()}`,
    index: 1,
    name: currentPlanName.value,
    model: modelLabelMap[store.modelAlgorithm.selectedModel] || store.modelAlgorithm.selectedModel,
    algorithm: algorithmLabelMap[store.modelAlgorithm.selectedAlgorithm] || store.modelAlgorithm.selectedAlgorithm,
    scenario: currentScenarioDesc.value,
    selected: true,
  }
  plansList.value.forEach((p, i) => { p.index = i + 2 })
  plansList.value.unshift(newPlan)
  selectedRowIds.value.add(newPlan.id)
  selectedRowIds.value = new Set(selectedRowIds.value)
  updatePageData()
  ElMessage.success(`已新增方案「${newPlan.name}」`)
}

const handleFilter = () => { ElMessage.info('筛选功能开发中') }
const handleDetail = () => { detailDialogVisible.value = true }
const handleEdit = () => { ElMessage.info('编辑功能开发中') }

const handleCopy = (plan: ConfigPlan) => {
  const newPlan: ConfigPlan = { ...plan, id: `plan-copy-${Date.now()}`, index: plansList.value.length + 1, name: `${plan.name}_副本`, selected: false }
  plansList.value.unshift(newPlan)
  selectedRowIds.value = new Set(selectedRowIds.value)
  updatePageData()
  ElMessage.success(`已复制方案「${plan.name}」`)
}

const handleDelete = (plan: ConfigPlan) => { detailPlan.value = plan; deleteDialogVisible.value = true }

const confirmDelete = () => {
  if (detailPlan.value) {
    plansList.value = plansList.value.filter(p => p.id !== detailPlan.value!.id)
    selectedRowIds.value.delete(detailPlan.value.id)
    selectedRowIds.value = new Set(selectedRowIds.value)
    ElMessage.success(`已删除方案「${detailPlan.value.name}」`)
  }
  deleteDialogVisible.value = false; detailPlan.value = null
}

const handleStepClick = (step: number) => {
  const paths: Record<number, string> = {
    1: '/model-config/dispatch-scenario', 2: '/model-config/dispatch-subject',
    3: '/model-config/model-data', 4: '/model-config/model-algorithm',
    5: '/model-config/scenario-constraint',
  }
  if (paths[step]) router.push(paths[step])
}

const handleExport = () => { ElMessage.info('导出功能开发中') }

// 弹窗
const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const detailPlan = ref<ConfigPlan | null>(null)

const confirmSave = () => { saveDialogVisible.value = false; ElMessage.success('配置汇总已保存') }
const confirmCancel = () => { cancelDialogVisible.value = false; ElMessage.info('已取消，未保存任何更改') }
void handleCancel
void handleSave
</script>

<template>
  <div class="config-summary-view">
    <ModelConfigStepBar :current-step="6" version="new" @step-click="handleStepClick" />

    <div class="main-content">
      <ConfigPlanTable
        :plans="currentPagePlans"
        v-model:current-page="currentPage"
        v-model:search-query="searchQuery"
        :page-size="pageSize"
        :selected-count="selectedCount"
        :total-count="totalCount"
        :total-pages="totalPages"
        :table-selected="tableSelected"
        @add="handleAdd"
        @filter="handleFilter"
        @selection-change="onSelectionChange"
        @detail="handleDetail"
        @edit="handleEdit"
        @copy="handleCopy"
        @delete="handleDelete"
        @run-single="handleRunSingle"
      />

      <ConfigInfoPanel
        :estimated-time="estimatedTime"
        :total-count="totalCount"
        :plan-count="totalCount"
        :model-chart-option="modelChartOption"
        :algo-chart-option="algoChartOption"
        :model-dist="[]"
        :algo-dist="[]"
      />
    </div>

    <div class="footer-bar">
      <div class="footer-center">
        <el-button size="default" @click="handlePrev" class="footer-btn footer-btn-prev">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon"><path d="M10 13L5 8l5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          上一步
        </el-button>
        <div class="footer-divider" />
        <el-button type="primary" size="default" class="footer-btn footer-btn-run" @click="handleRunAll">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon"><path d="M4 2v12l10-6L4 2z" fill="currentColor"/></svg>
          一键运行
        </el-button>
        <el-button size="default" class="footer-btn footer-btn-export" @click="handleExport">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon"><path d="M8 2v9M4 7l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 12v2h12v-2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          导出配置
        </el-button>
      </div>
    </div>

    <ConfigConfirmDialog v-model:visible="saveDialogVisible" title="保存确认" icon="save" message="确认保存当前配置？" confirm-text="确认保存" cancel-text="取消" confirm-color="primary" @confirm="confirmSave" @cancel="saveDialogVisible = false" />
    <ConfigConfirmDialog v-model:visible="cancelDialogVisible" title="取消确认" icon="cancel" message="确认取消当前操作？" confirm-text="确认取消" cancel-text="继续编辑" confirm-color="warning" @confirm="confirmCancel" @cancel="cancelDialogVisible = false" />
    <ConfigDetailDialog v-model:visible="detailDialogVisible" :detail-plan="detailPlan" :store="store" />
    <ConfigConfirmDialog v-model:visible="deleteDialogVisible" title="删除确认" icon="delete" :message="`确认删除方案「${detailPlan?.name}」？`" confirm-text="确认删除" cancel-text="取消" confirm-color="danger" @confirm="confirmDelete" @cancel="deleteDialogVisible = false" />
  </div>
</template>

<style scoped>
.config-summary-view {
  display: flex; flex-direction: column; height: 100%; box-sizing: border-box;
  padding: 0; gap: 0; overflow: hidden; background: rgba(var(--tech-bg-rgb), 0.92);
}
.main-content { flex: 1; display: flex; gap: 0; min-height: 0; overflow: hidden; }
.footer-bar {
  display: flex; align-items: center; justify-content: center;
  padding: 10px 16px; border-top: 1px solid rgba(var(--tech-blue-rgb), 0.1); flex-shrink: 0;
}
.footer-center { display: flex; align-items: center; gap: 8px; }
.footer-divider { width: 1px; height: 20px; background: rgba(50, 150, 255, 0.15); flex-shrink: 0; }
.footer-btn { font-size: 12px !important; display: inline-flex !important; align-items: center; gap: 4px; }
.footer-btn-run { font-size: 13px !important; padding: 8px 24px !important; display: inline-flex; align-items: center; gap: 6px; }
.footer-btn-export { display: inline-flex; align-items: center; gap: 4px; }
.btn-icon { flex-shrink: 0; }
</style>
