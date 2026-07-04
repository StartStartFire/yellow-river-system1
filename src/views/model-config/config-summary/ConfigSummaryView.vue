<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import { useModelConfigStore } from '@/stores/modelConfig'
import {
  configPlanList,
  modelDistribution,
  algorithmDistribution,
  modelLabelMap,
  algorithmLabelMap,
} from '@/mock/modelConfig'
import type { ConfigPlan, DistributionItem } from '@/mock/modelConfig'

// ==================== Store ====================
const store = useModelConfigStore()

// ==================== 辅助函数 ====================
const reservoirGroupName = computed(() => {
  const map: Record<string, string> = {
    'long-liu': '龙刘组合',
    'long-liu-hei': '龙刘黑组合',
    'long-liu-qing': '龙刘青组合',
    'long-liu-gong': '龙刘公组合',
    all: '全部水库组合',
  }
  return map[store.basicConfig.selectedReservoirGroup] || store.basicConfig.selectedReservoirGroup
})

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

// ==================== 图表 ref ====================
const modelChartRef = ref<HTMLDivElement | null>(null)
const algoChartRef = ref<HTMLDivElement | null>(null)
let modelChart: echarts.ECharts | null = null
let algoChart: echarts.ECharts | null = null
let modelResizeObserver: ResizeObserver | null = null
let algoResizeObserver: ResizeObserver | null = null

const DONUT_COLORS = ['#00afff', '#00e5a0', '#f0a020', '#ff6b6b']
const DONUT_COLORS_ALGO = ['#00d4ff', '#00ff88', '#ffaa00', '#a855f7']

// ==================== 图表初始化 ====================
const initDonutChart = (
  el: HTMLDivElement,
  data: DistributionItem[],
  colors: string[]
): echarts.ECharts => {
  const chart = echarts.init(el)
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(6, 30, 70, 0.9)',
      borderColor: 'rgba(50, 150, 255, 0.4)',
      textStyle: { color: '#e0e6ed', fontSize: 12 },
      formatter: (params: any) => {
        return `${params.name}<br/>数量: ${params.value}个 (${params.percent}%)`
      },
    },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        padAngle: 2,
        itemStyle: {
          borderRadius: 4,
        },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 13, fontWeight: 'bold', color: '#e0e6ed' },
        },
        data: data.map((d, i) => ({
          value: d.value,
          name: d.name,
          itemStyle: { color: colors[i % colors.length] },
        })),
      },
    ],
  }
  chart.setOption(option, true)
  return chart
}

const initAllCharts = () => {
  if (modelChartRef.value) {
    if (modelChart) modelChart.dispose()
    modelChart = initDonutChart(modelChartRef.value, modelDist, DONUT_COLORS)
    modelResizeObserver = new ResizeObserver(() => modelChart?.resize())
    modelResizeObserver.observe(modelChartRef.value)
  }
  if (algoChartRef.value) {
    if (algoChart) algoChart.dispose()
    algoChart = initDonutChart(algoChartRef.value, algoDist, DONUT_COLORS_ALGO)
    algoResizeObserver = new ResizeObserver(() => algoChart?.resize())
    algoResizeObserver.observe(algoChartRef.value)
  }
}

onMounted(() => {
  // 从 Store 当前配置重建方案列表，确保前四步最新配置已同步
  plansList.value = buildPlanList()
  setTimeout(initAllCharts, 300)
})

onUnmounted(() => {
  modelResizeObserver?.disconnect()
  algoResizeObserver?.disconnect()
  modelChart?.dispose()
  algoChart?.dispose()
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

// 分页跳转
const goPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 分页数字
const pageNumbers = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const pages: (number | string)[] = []
  if (total <= 5) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})
</script>

<template>
  <div class="config-summary-view">
    <!-- 步骤条 -->
    <ModelConfigStepBar :current-step="6" version="new" @step-click="handleStepClick" />

    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 左侧：配置方案表格 -->
      <div class="table-section">
        <div class="card table-card">
          <!-- 标题 + 操作栏 -->
          <div class="card-header">
            <div class="header-title-row">
              <div class="header-accent-line"></div>
              <span class="header-title">配置汇总</span>
            </div>
            <div class="toolbar-actions">
              <el-button size="small" type="primary" class="toolbar-btn" @click="handleAdd">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none" class="btn-icon-sm">
                  <path d="M6 2v8M2 6h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                新增
              </el-button>
              <el-button size="small" class="toolbar-btn" @click="handleFilter">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none" class="btn-icon-sm">
                  <path d="M1 2h10L7 6.5V10L5 11V6.5L1 2z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
                </svg>
                筛选
              </el-button>
              <el-input
                v-model="searchQuery"
                placeholder="搜索方案名、模型、算法或场景"
                size="small"
                clearable
                class="search-input"
              >
                <template #prefix>
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="search-icon">
                    <circle cx="6" cy="6" r="4" stroke="#6e8a9e" stroke-width="1.3"/>
                    <path d="M9.5 9.5L13 13" stroke="#6e8a9e" stroke-width="1.3" stroke-linecap="round"/>
                  </svg>
                </template>
              </el-input>
            </div>
          </div>

          <!-- 表格 -->
          <div class="table-wrapper">
            <el-table
              :data="currentPagePlans"
              height="100%"
              style="width: 100%"
              size="small"
              stripe
              class="dark-table"
              @selection-change="onSelectionChange"
              row-key="id"
            >
              <el-table-column type="selection" width="40" />
              <el-table-column label="序号" width="50" prop="index" />
              <el-table-column label="方案名" min-width="160" prop="name" />
              <el-table-column label="模型" min-width="150" prop="model" />
              <el-table-column label="算法" min-width="140" prop="algorithm" />
              <el-table-column label="场景" min-width="130" prop="scenario" />
              <el-table-column label="功能操作" width="240" fixed="right">
                <template #default="{ row }">
                  <div class="action-btns">
                    <el-button size="small" text class="action-btn action-detail" @click="handleDetail">详情</el-button>
                    <el-button size="small" text class="action-btn action-edit" @click="handleEdit">编辑</el-button>
                    <el-button size="small" text class="action-btn action-copy" @click="handleCopy(row)">复制</el-button>
                    <el-button size="small" text class="action-btn action-delete" @click="handleDelete(row)">删除</el-button>
                    <el-button size="small" text class="action-btn action-run" @click="handleRunSingle(row)">运行</el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 分页 -->
          <div class="pagination-bar">
            <div class="pagination-info">
              共 <span class="pagination-num">{{ totalCount }}</span> 条
            </div>
            <div class="pagination-controls">
              <button class="page-btn" :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">‹</button>
              <template v-for="pg in pageNumbers" :key="pg">
                <button
                  v-if="pg === '...'"
                  class="page-btn page-ellipsis"
                  disabled
                >…</button>
                <button
                  v-else
                  class="page-btn"
                  :class="{ 'page-active': pg === currentPage }"
                  @click="goPage(pg as number)"
                >{{ pg }}</button>
              </template>
              <button class="page-btn" :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)">›</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：预计计算信息 -->
      <div class="info-section">
        <!-- 时间预估 -->
        <div class="card info-card">
          <div class="card-header info-card-header">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
              <circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.3"/>
              <path d="M8 5v3.5H11" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            <span class="card-title">时间预估</span>
          </div>
          <div class="card-body info-card-body">
            <div class="time-display">02:18:45</div>
            <div class="time-label">预计总运行时间</div>
          </div>
        </div>

        <!-- 方案数量 -->
        <div class="card info-card">
          <div class="card-header info-card-header">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
              <rect x="2" y="3" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.3"/>
              <rect x="9" y="3" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.3"/>
              <rect x="2" y="10" width="5" height="3" rx="1" stroke="currentColor" stroke-width="1.3"/>
              <rect x="9" y="10" width="5" height="3" rx="1" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            <span class="card-title">方案数量</span>
          </div>
          <div class="card-body info-card-body">
            <div class="plan-count-display">
              <span class="plan-count-num">{{ totalCount }}</span>
              <span class="plan-count-unit"> 个</span>
            </div>
            <div class="plan-count-label">已配置方案总数</div>
          </div>
        </div>

        <!-- 模型分布 -->
        <div class="card info-card chart-card">
          <div class="card-header info-card-header">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
              <rect x="2" y="10" width="3" height="4" rx="0.5" fill="currentColor"/>
              <rect x="6.5" y="6" width="3" height="8" rx="0.5" fill="currentColor"/>
              <rect x="11" y="3" width="3" height="11" rx="0.5" fill="currentColor"/>
            </svg>
            <span class="card-title">模型分布</span>
          </div>
          <div class="card-body">
            <div class="chart-legend-row">
              <div ref="modelChartRef" class="mini-donut"></div>
              <div class="legend-list">
                <div v-for="(item, i) in modelDist" :key="item.name" class="legend-item">
                  <span class="legend-dot" :style="{ background: DONUT_COLORS[i] }"></span>
                  <span class="legend-name">{{ item.name }}</span>
                  <span class="legend-detail">{{ item.value }}个（{{ item.percent }}%）</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 算法分布 -->
        <div class="card info-card chart-card">
          <div class="card-header info-card-header">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
              <path d="M2 12l4-6 3 3 5-5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="3" cy="13" r="1" fill="currentColor"/>
              <circle cx="7" cy="7" r="1" fill="currentColor"/>
              <circle cx="13" cy="4" r="1" fill="currentColor"/>
            </svg>
            <span class="card-title">算法分布</span>
          </div>
          <div class="card-body">
            <div class="chart-legend-row">
              <div ref="algoChartRef" class="mini-donut"></div>
              <div class="legend-list">
                <div v-for="(item, i) in algoDist" :key="item.name" class="legend-item">
                  <span class="legend-dot" :style="{ background: DONUT_COLORS_ALGO[i] }"></span>
                  <span class="legend-name">{{ item.name }}</span>
                  <span class="legend-detail">{{ item.value }}个（{{ item.percent }}%）</span>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
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

    <!-- ===== 保存确认弹窗 ===== -->
    <el-dialog
      v-model="saveDialogVisible"
      title="保存确认"
      width="400px"
      :close-on-click-modal="false"
      class="confirm-dialog"
    >
      <div class="dialog-body">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
          <circle cx="24" cy="24" r="22" stroke="#00afff" stroke-width="2" fill="rgba(0,175,255,0.1)"/>
          <path d="M16 24l6 6 10-10" stroke="#00afff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <div class="dialog-text">
          <span class="dialog-title-main">确认保存当前配置？</span>
          <span class="dialog-desc">保存后当前配置汇总状态将保留。</span>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="saveDialogVisible = false">取消</el-button>
          <el-button type="primary" size="small" @click="confirmSave">确认保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- ===== 取消确认弹窗 ===== -->
    <el-dialog
      v-model="cancelDialogVisible"
      title="取消确认"
      width="400px"
      :close-on-click-modal="false"
      class="confirm-dialog"
    >
      <div class="dialog-body">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
          <circle cx="24" cy="24" r="22" stroke="#f0a020" stroke-width="2" fill="rgba(240,160,32,0.1)"/>
          <path d="M16 16l16 16M32 16l-16 16" stroke="#f0a020" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <div class="dialog-text">
          <span class="dialog-title-main">确认取消当前操作？</span>
          <span class="dialog-desc">取消后当前页面的更改将不会保存。</span>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="cancelDialogVisible = false">继续编辑</el-button>
          <el-button type="warning" size="small" @click="confirmCancel">确认取消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- ===== 方案详情弹窗 ===== -->
    <el-dialog
      v-model="detailDialogVisible"
      title="当前配置摘要"
      width="640px"
      :close-on-click-modal="false"
      class="confirm-dialog detail-dialog"
    >
      <div class="summary-body">

        <!-- Step 1: 调度数据 -->
        <div class="summary-section">
          <div class="summary-section-header">
            <div class="step-badge">1</div>
            <span class="summary-section-title">调度数据</span>
          </div>
          <div class="summary-fields">
            <el-descriptions :column="2" size="small" border class="dark-descriptions">
              <el-descriptions-item label="时间范围">
                {{ store.modelData.dateRange[0] }} ~ {{ store.modelData.dateRange[1] }}
              </el-descriptions-item>
              <el-descriptions-item label="数据项数">
                {{ store.modelData.selectedDataIds.length || 7 }} 项
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <!-- Step 2: 基础配置 -->
        <div class="summary-section">
          <div class="summary-section-header">
            <div class="step-badge">2</div>
            <span class="summary-section-title">基础配置</span>
          </div>
          <div class="summary-fields">
            <el-descriptions :column="2" size="small" border class="dark-descriptions">
              <el-descriptions-item label="方案名称">
                {{ store.basicConfig.schemeName || '（未命名）' }}
              </el-descriptions-item>
              <el-descriptions-item label="水库组合">
                {{ reservoirGroupName }}
              </el-descriptions-item>
              <el-descriptions-item label="调度周期">
                {{ store.basicConfig.timeStep }}
              </el-descriptions-item>
              <el-descriptions-item label="调度频率">
                {{ store.basicConfig.scheduleFrequency }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <!-- Step 3: 模型算法 -->
        <div class="summary-section">
          <div class="summary-section-header">
            <div class="step-badge">3</div>
            <span class="summary-section-title">模型算法</span>
          </div>
          <div class="summary-fields">
            <el-descriptions :column="2" size="small" border class="dark-descriptions">
              <el-descriptions-item label="调度模型">
                {{ store.modelAlgorithm.selectedModel }}
              </el-descriptions-item>
              <el-descriptions-item label="优化算法">
                {{ store.modelAlgorithm.selectedAlgorithm }}
              </el-descriptions-item>
              <el-descriptions-item label="参数摘要" :span="2">
                种群: {{ store.modelAlgorithm.parameters.populationSize }} |
                迭代: {{ store.modelAlgorithm.parameters.iterationCount }} |
                交叉: {{ store.modelAlgorithm.parameters.crossoverRate }} |
                变异: {{ store.modelAlgorithm.parameters.mutationRate }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <!-- Step 4: 场景约束 -->
        <div class="summary-section">
          <div class="summary-section-header">
            <div class="step-badge">4</div>
            <span class="summary-section-title">场景约束</span>
          </div>
          <div class="summary-fields">
            <el-descriptions :column="2" size="small" border class="dark-descriptions">
              <el-descriptions-item label="场景类型">
                {{ store.scenarioConstraint.scenarioType === 'typical' ? '典型场景' : '自定义场景' }}
              </el-descriptions-item>
              <el-descriptions-item label="西线调水">
                {{ scenarioParamLabel('westRoute') }}
              </el-descriptions-item>
              <el-descriptions-item label="骨干工程">
                {{ scenarioParamLabel('backboneStatus') }}
              </el-descriptions-item>
              <el-descriptions-item label="生态流量">
                {{ scenarioParamLabel('ecologicalFlow') }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="detailDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- ===== 删除确认弹窗 ===== -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除确认"
      width="400px"
      :close-on-click-modal="false"
      class="confirm-dialog"
    >
      <div class="dialog-body">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
          <circle cx="24" cy="24" r="22" stroke="#ff4d4f" stroke-width="2" fill="rgba(255,77,79,0.1)"/>
          <path d="M16 16l16 16M32 16l-16 16" stroke="#ff4d4f" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <div class="dialog-text">
          <span class="dialog-title-main">确认删除方案「{{ detailPlan?.name }}」？</span>
          <span class="dialog-desc">删除后不可恢复，请谨慎操作。</span>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="danger" size="small" @click="confirmDelete">确认删除</el-button>
        </div>
      </template>
    </el-dialog>
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
  background: rgba(6, 20, 42, 0.92);
}

/* ===== 主体内容 ===== */
.main-content {
  flex: 1;
  display: flex;
  gap: 0;
  min-height: 0;
  overflow: hidden;
}

/* ===== 左侧表格区 ===== */
.table-section {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  border-right: 1px solid rgba(0, 175, 255, 0.08);
}

/* ===== 右侧信息区 ===== */
.info-section {
  width: 240px;
  min-width: 240px;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow-y: auto;
  padding-right: 2px;
}

.info-section::-webkit-scrollbar {
  width: 3px;
}

.info-section::-webkit-scrollbar-track {
  background: transparent;
}

.info-section::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.2);
  border-radius: 2px;
}

/* ===== 通用卡片 ===== */
.card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}

.card-icon {
  color: #00d4ff;
  flex-shrink: 0;
}

.card-title {
  font-size: 12px;
  font-weight: 600;
  color: #e0e6ed;
}

.card-body {
  padding: 12px 16px;
  flex: 1;
}

.info-card-header {
  padding: 8px 12px;
}

.info-card-body {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

/* ===== 表格标题行 ===== */
.table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-accent-line {
  width: 3px;
  height: 18px;
  background: linear-gradient(180deg, #00d4ff, rgba(0, 212, 255, 0.3));
  border-radius: 2px;
  flex-shrink: 0;
}

.header-title {
  font-size: 15px;
  font-weight: 700;
  color: #e0e6ed;
}

.toolbar-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
}

.toolbar-btn {
  font-size: 11px !important;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-icon-sm {
  flex-shrink: 0;
}

.search-input {
  width: 220px;
}

.search-icon {
  flex-shrink: 0;
}

/* ===== 表格 ===== */
.table-wrapper {
  flex: 1 1 auto;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.dark-table {
  width: 100%;
  height: 100%;
}

.dark-table :deep(.el-table__header th) {
  background: rgba(2, 27, 63, 0.8) !important;
  color: #8aa0b8 !important;
  font-size: 11px;
  font-weight: 500;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2) !important;
}

.dark-table :deep(.el-table__body td) {
  background: transparent !important;
  color: #c0c8d4 !important;
  font-size: 11px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.06) !important;
}

.dark-table :deep(.el-table__row--striped td) {
  background: rgba(0, 175, 255, 0.02) !important;
}

.dark-table :deep(.el-table__body tr:hover td) {
  background: rgba(0, 175, 255, 0.06) !important;
}

.dark-table :deep(.el-table__inner-wrapper) {
  height: 100%;
  background: transparent !important;
}

.dark-table :deep(.el-table__body-wrapper) {
  background: transparent !important;
  overflow-y: auto !important;
}

.dark-table :deep(.el-checkbox__inner) {
  background: rgba(2, 27, 63, 0.8) !important;
  border-color: rgba(50, 150, 255, 0.3) !important;
}

.dark-table :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: rgba(0, 175, 255, 0.5) !important;
  border-color: #00d4ff !important;
}

/* ===== 操作按钮行 ===== */
.action-btns {
  display: flex;
  gap: 2px;
  flex-wrap: nowrap;
}

.action-btn {
  font-size: 11px !important;
  padding: 2px 5px !important;
  min-width: 0 !important;
  height: auto !important;
}

.action-detail { color: #00d4ff !important; }
.action-edit { color: #c0c8d4 !important; }
.action-copy { color: #f0a020 !important; }
.action-delete { color: #ff6b6b !important; }
.action-run { color: #00ff88 !important; }

/* ===== 分页 ===== */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  border-top: 1px solid rgba(50, 150, 255, 0.1);
  flex-shrink: 0;
}

.pagination-info {
  font-size: 12px;
  color: #8aa0b8;
}

.pagination-num {
  color: #00d4ff;
  font-weight: 600;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 2px;
}

.page-btn {
  width: 28px;
  height: 28px;
  border: 1px solid rgba(50, 150, 255, 0.2);
  border-radius: 6px;
  background: transparent;
  color: #8aa0b8;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  border-color: rgba(50, 150, 255, 0.5);
  color: #c0c8d4;
  background: rgba(0, 175, 255, 0.05);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-btn.page-active {
  background: rgba(0, 175, 255, 0.2);
  border-color: rgba(0, 175, 255, 0.5);
  color: #00d4ff;
  font-weight: 600;
}

.page-ellipsis {
  border: none;
  cursor: default;
}

/* ===== 右侧信息卡片 ===== */
.info-card {
  flex-shrink: 0;
  border-bottom: 1px solid rgba(0, 175, 255, 0.1);
}

.info-card.chart-card {
  flex: 1;
  min-height: 0;
}

.info-card.chart-card .card-body {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 8px 12px;
}

/* 时间预估 */
.time-display {
  font-size: 22px;
  font-weight: 700;
  color: #e0e6ed;
  font-variant-numeric: tabular-nums;
  letter-spacing: 1px;
}

.time-label {
  font-size: 11px;
  color: #6e8a9e;
}

/* 方案数量 */
.plan-count-display {
  display: flex;
  align-items: baseline;
}

.plan-count-num {
  font-size: 28px;
  font-weight: 700;
  color: #e0e6ed;
}

.plan-count-unit {
  font-size: 14px;
  color: #8aa0b8;
}

.plan-count-label {
  font-size: 11px;
  color: #6e8a9e;
}

/* 图表 + 图例布局 */
.chart-legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 100%;
}

.mini-donut {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.legend-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
}

.legend-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-name {
  color: #c0c8d4;
  white-space: nowrap;
}

.legend-detail {
  color: #6e8a9e;
  white-space: nowrap;
  margin-left: auto;
}


/* ===== 底部操作栏 ===== */
.footer-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  border-top: 1px solid rgba(0, 175, 255, 0.1);
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

/* ===== 配置摘要弹窗 ===== */
.summary-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 480px;
  overflow-y: auto;
  padding-right: 4px;
}

.summary-body::-webkit-scrollbar {
  width: 4px;
}

.summary-body::-webkit-scrollbar-track {
  background: transparent;
}

.summary-body::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.25);
  border-radius: 2px;
}

.summary-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-badge {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 175, 255, 0.15);
  border: 1px solid rgba(0, 175, 255, 0.4);
  color: #00d4ff;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.summary-section-title {
  font-size: 13px;
  font-weight: 600;
  color: #e0e6ed;
}

.summary-fields {
  padding-left: 30px;
}

/* el-descriptions 深色适配 */
:deep(.dark-descriptions) {
  --el-descriptions-table-bg-color: transparent;
}

:deep(.dark-descriptions .el-descriptions__header) {
  display: none;
}

:deep(.dark-descriptions .el-descriptions__body) {
  background: transparent !important;
}

:deep(.dark-descriptions .el-descriptions__table) {
  border-collapse: collapse;
}

:deep(.dark-descriptions .el-descriptions__cell) {
  background: rgba(2, 27, 63, 0.6) !important;
  border-color: rgba(50, 150, 255, 0.15) !important;
  color: #c0c8d4 !important;
  font-size: 12px;
}

:deep(.dark-descriptions .el-descriptions__label.is-bordered-label) {
  background: rgba(2, 27, 63, 0.8) !important;
  color: #8aa0b8 !important;
  font-weight: 500;
}

:deep(.dark-descriptions .el-descriptions__content) {
  color: #c0c8d4 !important;
}

/* ===== Element Plus 深色覆盖 ===== */
:deep(.el-input__wrapper) {
  background: rgba(2, 27, 63, 0.8) !important;
  box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.25) inset !important;
}

:deep(.el-input__inner) {
  color: #c0c8d4 !important;
  font-size: 12px;
}

:deep(.el-input__inner::placeholder) {
  color: #6e8a9e;
}

:deep(.el-button) {
  --el-button-bg-color: transparent;
  --el-button-border-color: rgba(50, 150, 255, 0.3);
  --el-button-text-color: #c0c8d4;
  --el-button-hover-bg-color: rgba(0, 175, 255, 0.1);
  --el-button-hover-border-color: rgba(50, 150, 255, 0.5);
  --el-button-hover-text-color: #e0e6ed;
}

:deep(.el-button--primary) {
  --el-button-bg-color: rgba(0, 175, 255, 0.2);
  --el-button-border-color: rgba(0, 175, 255, 0.5);
  --el-button-text-color: #00d4ff;
  --el-button-hover-bg-color: rgba(0, 175, 255, 0.3);
  --el-button-hover-border-color: rgba(0, 175, 255, 0.7);
  --el-button-hover-text-color: #00e5ff;
}

/* ===== 弹窗样式 ===== */
.confirm-dialog :deep(.el-dialog) {
  background: rgba(6, 30, 70, 0.98) !important;
  border: 1px solid rgba(50, 150, 255, 0.4);
  border-radius: 12px;
}

.confirm-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  padding: 16px 20px;
  margin: 0;
}

.confirm-dialog :deep(.el-dialog__title) {
  color: #e0e6ed;
  font-size: 15px;
  font-weight: 600;
}

.confirm-dialog :deep(.el-dialog__body) {
  padding: 24px 20px;
}

.confirm-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid rgba(50, 150, 255, 0.1);
  padding: 12px 20px;
}

.dialog-body {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.dialog-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.dialog-text {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.dialog-title-main {
  color: #e0e6ed;
  font-size: 14px;
  font-weight: 500;
}

.dialog-desc {
  color: #8aa0b8;
  font-size: 12px;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
