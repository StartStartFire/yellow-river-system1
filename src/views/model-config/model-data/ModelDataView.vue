<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import ModelConfigFooter from '@/components/model-config/ModelConfigFooter.vue'
import DataMenuSidebar from '@/components/model-config/model-data/DataMenuSidebar.vue'
import DataContentToolbar from '@/components/model-config/model-data/DataContentToolbar.vue'
import DataContentPanel from '@/components/model-config/model-data/DataContentPanel.vue'
import ConfirmActionDialog from '@/components/model-config/common/ConfirmActionDialog.vue'
import {
  TEXT_SECONDARY, baseTooltip, baseCategoryXAxis, baseValueYAxis,
  createGrid, createAreaGradient, SERIES_COLORS,
} from '@/utils/chart'
import { useModelConfigStore } from '@/stores/modelConfig'
import { modelDataMock } from '@/mock/model-config/modelData'
import type { MenuGroup, MenuContentMap, PageState } from '@/types/model'

// ==================== 弹窗状态 ====================
const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)

// ==================== Store ====================
const store = useModelConfigStore()

// ==================== Mock 数据 ====================
const mockData = modelDataMock.data

const menus = mockData.menus as MenuGroup[]
const menuContents = mockData.menuContents as MenuContentMap
const pageState = mockData.pageState as PageState

// ==================== 状态 ====================
const router = useRouter()
const sidebarCollapsed = ref(false)
const activeMenuId = ref(pageState.activeMenuId)

// ==================== 计算属性 ====================

// 当前选中菜单项
const activeMenuItem = computed(() => {
  for (const group of menus) {
    const found = group.children.find(item => item.id === activeMenuId.value)
    if (found) return found
  }
  return menus[0].children[0]
})

// 当前菜单所在分组名称
const activeGroupName = computed(() => {
  for (const group of menus) {
    if (group.children.some(item => item.id === activeMenuId.value)) {
      return group.groupName
    }
  }
  return ''
})

// 当前内容
const currentContent = computed(() => {
  return menuContents[activeMenuId.value]
})

// 图表标题
const chartTitle = computed(() => {
  const c = currentContent.value
  if (!c) return ''
  if (c.type === 'chart' && c.chartData) return c.chartData.title
  if (c.type === 'table' && c.tableData) return c.tableData.title
  return ''
})

// ==================== 按钮交互 ====================
const handleUpload = () => {
  ElMessage.info('当前为前端原型，暂不支持真实上传')
}

const handleDownload = () => {
  ElMessage.info('当前为前端原型，暂不支持真实下载')
}

const handleSave = () => {
  saveDialogVisible.value = true
}

const handleCancel = () => {
  cancelDialogVisible.value = true
}

const confirmSave = () => {
  saveDialogVisible.value = false
  // 写入 Store（联动 Step 2 时间范围）
  store.setModelData({
    activeMenuId: activeMenuId.value,
    dateRange: ['2025-05-19', '2025-05-25'], // 当前为固定 mock，后续可从日历选择
    selectedDataIds: [],
  })
  ElMessage.success('调度数据配置已保存')
}

const confirmCancel = () => {
  cancelDialogVisible.value = false
  ElMessage.info('已取消，未保存任何更改')
}

const handlePrev = () => {
  router.push('/model-config/dispatch-subject')
}

const handleNext = () => {
  // 同步当前数据到 Store
  store.setModelData({
    activeMenuId: activeMenuId.value,
    dateRange: ['2025-05-19', '2025-05-25'],
    selectedDataIds: [],
  })
  store.markStepCompleted(3)
  router.push('/model-config/model-algorithm')
}

// ==================== ECharts ====================
const chartOption = computed(() => {
  const chartData = currentContent.value?.chartData
  if (!chartData) return {}

  return {
    tooltip: { ...baseTooltip },
    legend: {
      data: ['入库流量 (m³/s)', '水位 (m)'],
      textStyle: { color: TEXT_SECONDARY, fontSize: 12 },
      top: 0,
    },
    grid: createGrid(40, 30, 60, 60),
    xAxis: {
      ...baseCategoryXAxis,
      data: chartData.xAxis,
    },
    yAxis: [
      {
        ...baseValueYAxis,
        name: '入库流量 (m³/s)',
      },
      {
        ...baseValueYAxis,
        name: '水位 (m)',
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: '入库流量 (m³/s)',
        type: 'line',
        data: chartData.series.inflow,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, color: SERIES_COLORS[0] },
        itemStyle: { color: SERIES_COLORS[0] },
        areaStyle: createAreaGradient(SERIES_COLORS[0], 0.3, 0.02),
      },
      {
        name: '水位 (m)',
        type: 'line',
        yAxisIndex: 1,
        data: chartData.series.level,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, color: SERIES_COLORS[1] },
        itemStyle: { color: SERIES_COLORS[1] },
      },
    ],
  }
})

// ==================== SVG 图标映射 ====================
const iconMap: Record<string, string> = {
  database: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><ellipse cx="8" cy="4" rx="5" ry="2" stroke="currentColor" stroke-width="1.3"/><path d="M3 4v3c0 1.1 2.2 2 5 2s5-.9 5-2V4" stroke="currentColor" stroke-width="1.3"/><path d="M3 8v3c0 1.1 2.2 2 5 2s5-.9 5-2V8" stroke="currentColor" stroke-width="1.3"/></svg>',
  water: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2C8 2 4 6.5 4 9.5C4 11.7 5.8 13.5 8 13.5S12 11.7 12 9.5C12 6.5 8 2 8 2Z" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M6.5 9.5C6.5 10.3 7.2 11 8 11" stroke="currentColor" stroke-width="1.2"/></svg>',
  level: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2" y="7" width="12" height="2" rx="1" stroke="currentColor" stroke-width="1.3"/><path d="M4 7V4" stroke="currentColor" stroke-width="1.3"/><path d="M8 7V3" stroke="currentColor" stroke-width="1.3"/><path d="M12 7V5" stroke="currentColor" stroke-width="1.3"/></svg>',
  clock: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.3"/><path d="M8 5v3.5H11" stroke="currentColor" stroke-width="1.3"/></svg>',
  river: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 12C4 10 6 12 8 12S12 10 14 12" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M2 9C4 7 6 9 8 9S12 7 14 9" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M2 6C4 4 6 6 8 6S12 4 14 6" stroke="currentColor" stroke-width="1.3" fill="none"/></svg>',
  inflow: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 10h12M8 2v8M5 5l3-3 3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 12v1.5h12V12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>',
  bar: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2" y="10" width="3" height="4" rx="0.5" fill="currentColor"/><rect x="6.5" y="6" width="3" height="8" rx="0.5" fill="currentColor"/><rect x="11" y="3" width="3" height="11" rx="0.5" fill="currentColor"/></svg>',
  table: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2" y="3" width="12" height="10" rx="1" stroke="currentColor" stroke-width="1.3"/><path d="M2 7h12M7 3v10" stroke="currentColor" stroke-width="1.3"/></svg>',
}

// chartTitle 保留在父组件（内容由 DataContentPanel 内部渲染，此处保留供外部读取）
</script>

<template>
  <div class="model-data-view">
    <!-- 步骤条 -->
    <ModelConfigStepBar :current-step="3" version="new" />

    <!-- 主体：左侧目录 + 右侧内容区 -->
    <div class="main-content">
      <!-- 左侧数据目录 -->
      <DataMenuSidebar
        v-model:activeMenuId="activeMenuId"
        v-model:collapsed="sidebarCollapsed"
        :menus="menus"
        :icon-map="iconMap"
      />

      <!-- 右侧内容区 -->
      <div class="content-area">
        <!-- 顶部操作栏 -->
        <DataContentToolbar
          :group-name="activeGroupName"
          :menu-item-name="activeMenuItem.name"
          @upload="handleUpload"
          @download="handleDownload"
        />

        <!-- 图表/表格区 -->
        <DataContentPanel
          :content="currentContent"
          :chart-option="chartOption"
        />
      </div>
    </div>

    <!-- 底部操作栏 -->
    <ModelConfigFooter
      :step="3"
      @cancel="handleCancel"
      @save="handleSave"
      @prev="handlePrev"
      @next="handleNext"
    />
  </div>

  <!-- 保存确认弹窗 -->
  <ConfirmActionDialog
    v-model:visible="saveDialogVisible"
    title="保存确认"
    icon-type="success"
    main-text="确认保存当前调度数据配置？"
    desc-text="保存后当前目录选择和时间范围将保留。"
    confirm-text="确认保存"
    cancel-text="取消"
    confirm-type="primary"
    @confirm="confirmSave"
  />

  <!-- 取消确认弹窗 -->
  <ConfirmActionDialog
    v-model:visible="cancelDialogVisible"
    title="取消确认"
    icon-type="warning"
    main-text="确认取消当前操作？"
    desc-text="取消后当前页面的更改将不会保存。"
    confirm-text="确认取消"
    cancel-text="继续编辑"
    confirm-type="warning"
    @confirm="confirmCancel"
  />
</template>

<style scoped>
.model-data-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
  gap: 0;
  overflow: hidden;
  background: rgba(var(--tech-bg-rgb), 0.92);
}

/* ===== 主体区域 ===== */
.main-content {
  display: flex;
  flex: 1;
  min-height: 0;
  gap: 0;
}

/* ===== 右侧内容区 ===== */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
  min-width: 0;
}
</style>
