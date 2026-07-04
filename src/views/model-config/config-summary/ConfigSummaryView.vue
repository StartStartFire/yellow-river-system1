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
import {
  configPlanList,
  modelDistribution,
  algorithmDistribution,
  modelLabelMap,
  algorithmLabelMap,
} from '@/mock/modelConfig'
import type { ConfigPlan, DistributionItem } from '@/types/model'

// ==================== Store ====================
const store = useModelConfigStore()

// ==================== 辅助函数 ====================
const scenarioParamLabels: Record<string, Record<string, string>> = {
  westRoute: { none: '无', upper: '上线', lower: '下线', both: '上下线同引', all: '上线+下线' },
  backboneStatus: { normal: '正常运行', limited: '限制运行', maintenance: '检修停运', emergency: '应急运行' },
  ecologicalFlow: { none: '不考虑', plan: '按方案执行', minimum: '最低生态需水', enhanced: '强化生态保障', custom: '自定义' },
}

const scenarioParamLabel = (key: string) => {
  const value = store.scenarioConstraint.params[key]
  return scenarioParamLabels[key]?.[value] || value
}

/** 根据 Store 当前配置生成方案名称（与 Step 2 逻辑一致） */
const currentPlanName = computed(() => {
  const name = store.basicConfig.schemeName?.trim()
  if (name) return name
  const objectives = store.basicConfig.selectedObjectives
  const objNames: Record<string, string> = { 'flood-control': '防洪', 'power-generation': '兴利', 'ecology': '生态' }
  const tag = objectives.map(o => objNames[o] || o).join('')
  return `${tag}调度方案_${store.basicConfig.startTime || 'today'}`
})

/** 根据 Store 当前配置生成场景描述 */
const currentScenarioDesc = computed(() => {
  const type = store.scenarioConstraint.scenarioType === 'typical' ? '典型场景' : '自定义场景'
  const eco = scenarioParamLabel('ecologicalFlow')
  return `${type}_${eco}`
})

// ==================== Mock 数据 ====================
const allPlans = configPlanList.data as ConfigPlan[]
const modelDist = modelDistribution.data as DistributionItem[]
const algoDist = algorithmDistribution.data as DistributionItem[]

// 预计总运行时间（前端原型静态展示）
const estimatedTime = '02:18:45'

// ==================== 响应式状态 ====================
const router = useRouter()

// 表格数据
const currentPage = ref(1)
const pageSize = ref(13)
const searchQuery = ref('')

// 本地可修改的方案列表（先插入当前方案）
const plansList = ref<ConfigPlan[]>(buildPlanList())

/** 构建方案列表：当前配置方案 + 历史 mock 方案 */
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
  const historical = JSON.parse(JSON.stringify(allPlans)) as ConfigPlan[]
  // 重新编号历史方案
  historical.forEach((p, i) => { p.index = i + 2 })
  return [current, ...historical]
}

// 过滤后的列表
const filteredPlans = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return plansList.value
  return plansList.value.filter(
    p =>
      p.name.toLowerCase().includes(q) ||
      p.model.toLowerCase().includes(q) ||
      p.algorithm.toLowerCase().includes(q) ||
      p.scenario.toLowerCase().includes(q)
  )
})

// 当前页数据
const currentPagePlans = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredPlans.value.slice(start, start + pageSize.value)
})

// 总条数
const totalCount = computed(() => filteredPlans.value.length)

// 总页数
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value) || 1)

// 选中方案数
const selectedCount = computed(() => plansList.value.filter(p => p.selected).length)

// 弹窗状态
const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const detailPlan = ref<ConfigPlan | null>(null)

// ==================== 图表 computed ====================
const modelChartOption = computed(() => ({
  tooltip: {
    ...baseItemTooltip,
    formatter: (params: any) => `${params.name}<br/>数量: ${params.value}个 (${params.percent}%)`,
  },
  series: [{
    type: 'pie',
    radius: ['45%', '70%'],
    center: ['35%', '50%'],
    avoidLabelOverlap: false,
    padAngle: 2,
    itemStyle: { borderRadius: 4 },
    label: { show: false },
    emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold', color: TEXT_PRIMARY } },
    data: modelDist.map((d, i) => ({
      value: d.value,
      name: d.name,
      itemStyle: { color: SERIES_COLORS[i % SERIES_COLORS.length] },
    })),
  }],
}))

const algoChartOption = computed(() => ({
  tooltip: {
    ...baseItemTooltip,
    formatter: (params: any) => `${params.name}<br/>数量: ${params.value}个 (${params.percent}%)`,
  },
  series: [{
    type: 'pie',
    radius: ['45%', '70%'],
    center: ['35%', '50%'],
    avoidLabelOverlap: false,
    padAngle: 2,
    itemStyle: { borderRadius: 4 },
    label: { show: false },
    emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold', color: TEXT_PRIMARY } },
    data: algoDist.map((d, i) => ({
      value: d.value,
      name: d.name,
      itemStyle: { color: SERIES_COLORS[i % SERIES_COLORS.length] },
    })),
  }],
}))

onMounted(() => {
  // 从 Store 当前配置重建方案列表，确保前四步最新配置已同步
  plansList.value = buildPlanList()
})

// 监听搜索，重置到第一页
watch(searchQuery, () => {
  currentPage.value = 1
})

// ==================== 步骤条点击 ====================
const handleStepClick = (step: number) => {
  const paths: Record<number, string> = {
    1: '/model-config/dispatch-scenario',
    2: '/model-config/dispatch-subject',
    3: '/model-config/model-data',
    4: '/model-config/model-algorithm',
    5: '/model-config/scenario-constraint',
  }
  if (paths[step]) router.push(paths[step])
}

// ==================== 表格操作 ====================
const handleSelectionChange = (rows: ConfigPlan[]) => {
  // 同步选中状态到 plansList
  const selectedIds = new Set(rows.map(r => r.id))
  plansList.value.forEach(p => {
    p.selected = selectedIds.has(p.id)
  })
}

// 兼容 el-table 的 selection-change：从当前页计划反向同步
const onSelectionChange = (val: ConfigPlan[]) => {
  const pageIds = new Set(currentPagePlans.value.map(p => p.id))
  const selectedIds = new Set(val.map(v => v.id))
  plansList.value.forEach(p => {
    if (pageIds.has(p.id)) {
      p.selected = selectedIds.has(p.id)
    }
  })
}

// 表格已选中项（用于 el-table 的 v-model）
const tableSelected = computed({
  get: () => currentPagePlans.value.filter(p => p.selected),
  set: (val: ConfigPlan[]) => {
    const pageIds = new Set(currentPagePlans.value.map(p => p.id))
    const selectedIds = new Set(val.map(v => v.id))
    plansList.value.forEach(p => {
      if (pageIds.has(p.id)) {
        p.selected = selectedIds.has(p.id)
      }
    })
  },
})

// ==================== 底部操作 ====================
const handleCancel = () => { cancelDialogVisible.value = true }
const handleSave = () => { saveDialogVisible.value = true }
const handlePrev = () => { router.push('/model-config/scenario-constraint') }

const handleRunAll = () => {
  if (selectedCount.value === 0) {
    ElMessage.warning('请至少选择一个配置方案')
    return
  }
  ElMessage.success('已生成计算任务，正在跳转至过程透明页面...')
  setTimeout(() => {
    router.push('/process-transparent')
  }, 800)
}

const handleExport = () => {
  ElMessage.info('当前为前端原型，暂不支持真实导出')
}

const handleAdd = () => {
  // 把当前配置作为新方案加入列表
  const newPlan: ConfigPlan = {
    id: `plan-new-${Date.now()}`,
    index: 1,
    name: currentPlanName.value,
    model: modelLabelMap[store.modelAlgorithm.selectedModel] || store.modelAlgorithm.selectedModel,
    algorithm: algorithmLabelMap[store.modelAlgorithm.selectedAlgorithm] || store.modelAlgorithm.selectedAlgorithm,
    scenario: currentScenarioDesc.value,
    selected: true,
  }
  // 重新编号现有方案
  plansList.value.forEach((p, i) => { p.index = i + 2 })
  plansList.value.unshift(newPlan)
  ElMessage.success(`已新增方案「${newPlan.name}」`)
}

const handleFilter = () => {
  ElMessage.info('筛选功能开发中')
}

// ==================== 行操作 ====================
const handleDetail = () => {
  detailDialogVisible.value = true
}

const handleEdit = () => {
  ElMessage.info('当前为前端原型，暂不支持真实编辑')
}

const handleCopy = (plan: ConfigPlan) => {
  const newPlan: ConfigPlan = {
    ...plan,
    id: `plan-copy-${Date.now()}`,
    index: plansList.value.length + 1,
    name: `${plan.name}_副本`,
    selected: false,
  }
  plansList.value.unshift(newPlan)
  ElMessage.success(`已复制方案「${plan.name}」`)
}

const handleDelete = (plan: ConfigPlan) => {
  detailPlan.value = plan
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (detailPlan.value) {
    plansList.value = plansList.value.filter(p => p.id !== detailPlan.value!.id)
    ElMessage.success(`已删除方案「${detailPlan.value.name}」`)
  }
  deleteDialogVisible.value = false
  detailPlan.value = null
}

const handleRunSingle = (plan: ConfigPlan) => {
  ElMessage.success(`方案「${plan.name}」已启动，正在跳转...`)
  setTimeout(() => {
    router.push('/process-transparent')
  }, 800)
}

// ==================== 弹窗确认 ====================
const confirmSave = () => {
  saveDialogVisible.value = false
  ElMessage.success('配置汇总已保存')
}

const confirmCancel = () => {
  cancelDialogVisible.value = false
  ElMessage.info('已取消，未保存任何更改')
}

// 保留 handleCancel / handleSave 以备底部操作栏扩展使用
void handleCancel
void handleSave
</script>

<template>
  <div class="config-summary-view">
    <!-- 步骤条 -->
    <ModelConfigStepBar :current-step="6" version="new" @step-click="handleStepClick" />

    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 左侧：配置方案表格 -->
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

      <!-- 右侧：预计计算信息 -->
      <ConfigInfoPanel
        :estimated-time="estimatedTime"
        :total-count="totalCount"
        :plan-count="totalCount"
        :model-chart-option="modelChartOption"
        :algo-chart-option="algoChartOption"
        :model-dist="modelDist"
        :algo-dist="algoDist"
      />
    </div>

    <!-- 底部操作栏 -->
    <div class="footer-bar">
      <div class="footer-center">
        <el-button size="default" @click="handlePrev" class="footer-btn footer-btn-prev">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
            <path d="M10 13L5 8l5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          上一步
        </el-button>
        <div class="footer-divider" />
        <el-button type="primary" size="default" class="footer-btn footer-btn-run" @click="handleRunAll">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
            <path d="M4 2v12l10-6L4 2z" fill="currentColor"/>
          </svg>
          一键运行
        </el-button>
        <el-button size="default" class="footer-btn footer-btn-export" @click="handleExport">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
            <path d="M8 2v9M4 7l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12v2h12v-2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          导出配置
        </el-button>
      </div>
    </div>

    <!-- 保存确认弹窗 -->
    <ConfigConfirmDialog
      v-model:visible="saveDialogVisible"
      title="保存确认"
      icon="save"
      message="确认保存当前配置？"
      confirm-text="确认保存"
      cancel-text="取消"
      confirm-color="primary"
      @confirm="confirmSave"
      @cancel="saveDialogVisible = false"
    />

    <!-- 取消确认弹窗 -->
    <ConfigConfirmDialog
      v-model:visible="cancelDialogVisible"
      title="取消确认"
      icon="cancel"
      message="确认取消当前操作？"
      confirm-text="确认取消"
      cancel-text="继续编辑"
      confirm-color="warning"
      @confirm="confirmCancel"
      @cancel="cancelDialogVisible = false"
    />

    <!-- 方案详情弹窗 -->
    <ConfigDetailDialog
      v-model:visible="detailDialogVisible"
      :detail-plan="detailPlan"
      :store="store"
    />

    <!-- 删除确认弹窗 -->
    <ConfigConfirmDialog
      v-model:visible="deleteDialogVisible"
      title="删除确认"
      icon="delete"
      :message="`确认删除方案「${detailPlan?.name}」？`"
      confirm-text="确认删除"
      cancel-text="取消"
      confirm-color="danger"
      @confirm="confirmDelete"
      @cancel="deleteDialogVisible = false"
    />
  </div>
</template>

<style scoped>
.config-summary-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
  padding: 0;
  gap: 0;
  overflow: hidden;
  background: rgba(var(--tech-bg-rgb), 0.92);
}

/* ===== 主体内容 ===== */
.main-content {
  flex: 1;
  display: flex;
  gap: 0;
  min-height: 0;
  overflow: hidden;
}

/* ===== 底部操作栏 ===== */
.footer-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  border-top: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  flex-shrink: 0;
}

.footer-center {
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-divider {
  width: 1px;
  height: 20px;
  background: rgba(50, 150, 255, 0.15);
  flex-shrink: 0;
}

.footer-btn {
  font-size: 12px !important;
  display: inline-flex !important;
  align-items: center;
  gap: 4px;
}

.footer-btn-run {
  font-size: 13px !important;
  padding: 8px 24px !important;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.footer-btn-export {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-icon {
  flex-shrink: 0;
}

/* ===== Element Plus 深色覆盖（底部按钮） ===== */
:deep(.el-button) {
  --el-button-bg-color: transparent;
  --el-button-border-color: rgba(50, 150, 255, 0.3);
  --el-button-text-color: var(--tech-text-regular);
  --el-button-hover-bg-color: rgba(var(--tech-blue-rgb), 0.1);
  --el-button-hover-border-color: rgba(50, 150, 255, 0.5);
  --el-button-hover-text-color: var(--tech-text-primary);
}

:deep(.el-button--primary) {
  --el-button-bg-color: rgba(var(--tech-blue-rgb), 0.2);
  --el-button-border-color: rgba(var(--tech-blue-rgb), 0.5);
  --el-button-text-color: var(--tech-cyan);
  --el-button-hover-bg-color: rgba(var(--tech-blue-rgb), 0.3);
  --el-button-hover-border-color: rgba(var(--tech-blue-rgb), 0.7);
  --el-button-hover-text-color: var(--tech-cyan-light);
}
</style>
