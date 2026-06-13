<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import ModelConfigFooter from '@/components/model-config/ModelConfigFooter.vue'
import { useModelConfigStore } from '@/stores/modelConfig'
import { modelDataMock } from '@/mock/modelConfig'
import type { MenuGroup, MenuContentMap, PageState } from '@/mock/modelConfig'

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

// 是否为图表类型
const isChartType = computed(() => currentContent.value?.type === 'chart')

// 是否为表格类型
const isTableType = computed(() => currentContent.value?.type === 'table')

// 图表标题
const chartTitle = computed(() => {
  if (isChartType.value && currentContent.value?.chartData) {
    return currentContent.value.chartData.title
  }
  if (isTableType.value && currentContent.value?.tableData) {
    return currentContent.value.tableData.title
  }
  return ''
})

// ==================== 左侧目录切换 ====================
const handleSelectMenu = (menuId: string) => {
  activeMenuId.value = menuId
  // 切换后重新渲染图表
  nextTickInitChart()
}

const handleToggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

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
  ElMessage.success('模型数据配置已保存')
}

const confirmCancel = () => {
  cancelDialogVisible.value = false
  ElMessage.info('已取消，未保存任何更改')
}

const handleNext = () => {
  // 同步当前数据到 Store（联动 Step 2）
  store.setModelData({
    activeMenuId: activeMenuId.value,
    dateRange: ['2025-05-19', '2025-05-25'],
    selectedDataIds: [],
  })
  router.push('/model-config/basic-config')
}

// ==================== ECharts ====================
const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const initChart = () => {
  if (!chartRef.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const chartData = currentContent.value?.chartData
  if (!chartData) return

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(6, 30, 70, 0.9)',
      borderColor: 'rgba(50, 150, 255, 0.4)',
      textStyle: { color: '#e0e6ed', fontSize: 12 },
    },
    legend: {
      data: ['入库流量 (m³/s)', '水位 (m)'],
      textStyle: { color: '#7a8fa3', fontSize: 12 },
      top: 0,
    },
    grid: {
      left: 60,
      right: 60,
      top: 40,
      bottom: 30,
    },
    xAxis: {
      type: 'category',
      data: chartData.xAxis,
      axisLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.3)' } },
      axisLabel: { color: '#7a8fa3', fontSize: 11 },
      splitLine: { show: false },
    },
    yAxis: [
      {
        type: 'value',
        name: '入库流量 (m³/s)',
        nameTextStyle: { color: '#7a8fa3', fontSize: 11 },
        axisLine: { show: false },
        axisLabel: { color: '#7a8fa3', fontSize: 11 },
        splitLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.1)', type: 'dashed' } },
      },
      {
        type: 'value',
        name: '水位 (m)',
        nameTextStyle: { color: '#7a8fa3', fontSize: 11 },
        axisLine: { show: false },
        axisLabel: { color: '#7a8fa3', fontSize: 11 },
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
        lineStyle: { width: 2, color: '#00afff' },
        itemStyle: { color: '#00afff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 175, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 175, 255, 0.02)' },
          ]),
        },
      },
      {
        name: '水位 (m)',
        type: 'line',
        yAxisIndex: 1,
        data: chartData.series.level,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, color: '#00e5a0' },
        itemStyle: { color: '#00e5a0' },
      },
    ],
  }

  chartInstance.setOption(option, true)
  chartInstance.resize()
}

const nextTickInitChart = () => {
  setTimeout(() => {
    if (isChartType.value) {
      initChart()
    } else {
      // 切换为表格时销毁图表实例（v-if 会移除 DOM，旧实例无法复用）
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
    }
  }, 50)
}

// 监听 activeMenuId 切换
watch(activeMenuId, () => {
  nextTickInitChart()
})

onMounted(() => {
  setTimeout(() => {
    if (isChartType.value) {
      initChart()
    }
    if (chartRef.value) {
      resizeObserver = new ResizeObserver(() => chartInstance?.resize())
      resizeObserver.observe(chartRef.value)
    }
  }, 300)
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
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
</script>

<template>
  <div class="model-data-view">
    <!-- 步骤条 -->
    <ModelConfigStepBar :current-step="1" />

    <!-- 主体：左侧目录 + 右侧内容区 -->
    <div class="main-content">
      <!-- 左侧数据目录 -->
      <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-inner">
          <div class="sidebar-title-row">
            <svg v-if="!sidebarCollapsed" width="16" height="16" viewBox="0 0 16 16" fill="none" class="shrink-0">
              <rect x="2" y="3" width="5" height="4" rx="1" stroke="#7a8fa3" stroke-width="1.3"/>
              <rect x="9" y="3" width="5" height="4" rx="1" stroke="#7a8fa3" stroke-width="1.3"/>
              <rect x="2" y="9.5" width="5" height="4" rx="1" stroke="#7a8fa3" stroke-width="1.3"/>
              <rect x="9" y="9.5" width="5" height="4" rx="1" stroke="#7a8fa3" stroke-width="1.3"/>
            </svg>
            <span v-if="!sidebarCollapsed" class="sidebar-title">数据目录</span>
          </div>

          <div class="menu-scroll-area">
            <div v-for="(group, gIdx) in menus" :key="gIdx" class="menu-group">
              <div v-if="!sidebarCollapsed" class="group-header">{{ group.groupName }}</div>
              <div
                v-for="item in group.children"
                :key="item.id"
                class="menu-item"
                :class="{ active: item.id === activeMenuId }"
                @click="handleSelectMenu(item.id)"
              >
                <span class="menu-icon" v-html="iconMap[item.icon] || iconMap.database"></span>
                <span v-if="!sidebarCollapsed" class="menu-name">{{ item.name }}</span>
              </div>
            </div>
          </div>

          <!-- 收起按钮 -->
          <div class="collapse-footer" @click="handleToggleSidebar">
            <svg v-if="!sidebarCollapsed" width="14" height="14" viewBox="0 0 16 16" fill="none">
              <path d="M10 3L5 8L10 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else width="14" height="14" viewBox="0 0 16 16" fill="none">
              <path d="M6 3L11 8L6 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span v-if="!sidebarCollapsed" class="collapse-text">收起</span>
          </div>
        </div>
      </div>

      <!-- 右侧内容区 -->
      <div class="content-area">
        <!-- 顶部操作栏 -->
        <div class="toolbar">
          <div class="toolbar-left">
            <div class="current-info">
              <span class="info-label">{{ activeGroupName }}</span>
              <span class="info-divider">/</span>
              <span class="info-value">{{ activeMenuItem.name }}</span>
            </div>
          </div>
          <div class="toolbar-right">
            <el-button type="primary" size="small" @click="handleUpload" class="toolbar-btn-custom">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
                <path d="M8 2v9M4 6l4-4 4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12v2h12v-2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              上传数据
            </el-button>
            <el-button size="small" @click="handleDownload" class="toolbar-btn-custom">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
                <path d="M8 11V2M4 7l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12v2h12v-2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              下载模板
            </el-button>
          </div>
        </div>

        <!-- 图表/表格区 -->
        <div class="content-panel"
          style="background: rgba(6, 30, 70, 0.85); border: 1px solid rgba(50, 150, 255, 0.35); border-radius: 12px;"
        >
          <!-- 标题 -->
          <div class="content-header">
            <span class="content-title">{{ chartTitle }}</span>
          </div>

          <!-- 图表区 -->
          <div v-if="isChartType && currentContent?.chartData" class="chart-wrapper">
            <div ref="chartRef" class="chart-container"></div>
          </div>

          <!-- 表格区 -->
          <div v-if="isTableType && currentContent?.tableData" class="table-wrapper">
            <el-table
              :data="currentContent.tableData.rows"
              stripe
              size="small"
              class="data-table"
              style="width: 100%"
            >
              <el-table-column
                v-for="col in currentContent.tableData.columns"
                :key="col.key"
                :prop="col.key"
                :label="col.unit ? `${col.label}（${col.unit}）` : col.label"
                min-width="120"
              />
            </el-table>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <ModelConfigFooter
      :step="1"
      @cancel="handleCancel"
      @save="handleSave"
      @next="handleNext"
    />
  </div>

    <!-- 保存确认弹窗 -->
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
          <span class="dialog-title-main">确认保存当前模型数据配置？</span>
          <span class="dialog-desc">保存后当前目录选择和时间范围将保留。</span>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="saveDialogVisible = false">取消</el-button>
          <el-button type="primary" size="small" @click="confirmSave">确认保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 取消确认弹窗 -->
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
</template>

<style scoped>
.model-data-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 8px 12px;
  gap: 8px;
  overflow: hidden;
}

/* ===== 主体区域 ===== */
.main-content {
  display: flex;
  flex: 1;
  min-height: 0;
  gap: 8px;
}

/* ===== 左侧目录 ===== */
.sidebar {
  width: 200px;
  min-width: 200px;
  transition: width 0.25s ease, min-width 0.25s ease;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 48px;
  min-width: 48px;
}

.sidebar-inner {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(6, 30, 70, 0.85);
  border: 1px solid rgba(50, 150, 255, 0.35);
  border-radius: 12px;
  overflow: hidden;
}

.menu-scroll-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
}

.menu-scroll-area::-webkit-scrollbar {
  width: 4px;
}

.menu-scroll-area::-webkit-scrollbar-track {
  background: transparent;
}

.menu-scroll-area::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.25);
  border-radius: 2px;
}

.menu-scroll-area::-webkit-scrollbar-thumb:hover {
  background: rgba(50, 150, 255, 0.45);
}

.sidebar-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 13px;
  font-weight: 600;
  color: #e0e6ed;
  white-space: nowrap;
}

.menu-group {
  padding: 6px 0;
  border-bottom: 1px solid rgba(50, 150, 255, 0.08);
}

/* 调度输入和原始表格组均固定显示6项高度，超出滚动 */
.menu-group {
  max-height: 230px;
  overflow-y: auto;
}

.menu-group::-webkit-scrollbar {
  width: 4px;
}

.menu-group::-webkit-scrollbar-track {
  background: transparent;
}

.menu-group::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.25);
  border-radius: 2px;
}

.menu-group::-webkit-scrollbar-thumb:hover {
  background: rgba(50, 150, 255, 0.45);
}

.group-header {
  font-size: 11px;
  font-weight: 500;
  color: #5a6f83;
  padding: 6px 14px 8px;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  margin: 0 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  color: #7a8fa3;
}

.menu-item:hover {
  background: rgba(0, 175, 255, 0.08);
  color: #c0c8d4;
}

.menu-item.active {
  background: rgba(0, 175, 255, 0.15);
  border: 1px solid rgba(0, 175, 255, 0.4);
  color: #00d4ff;
  margin: 0 5px;
  padding: 7px 13px;
}

.menu-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: inherit;
}

.menu-name {
  font-size: 12px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collapse-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border-top: 1px solid rgba(50, 150, 255, 0.15);
  cursor: pointer;
  color: #5a6f83;
  font-size: 12px;
  transition: all 0.2s;
  margin-top: auto;
  flex-shrink: 0;
}

.collapse-footer:hover {
  color: #c0c8d4;
  background: rgba(0, 175, 255, 0.05);
}

.collapse-text {
  white-space: nowrap;
}

/* 收起时 */
.collapsed .menu-item {
  justify-content: center;
  padding: 10px 0;
  margin: 0 4px;
}

.collapsed .menu-item.active {
  padding: 9px 0;
  margin: 0 3px;
}

.collapsed .collapse-footer {
  justify-content: center;
  padding: 10px 0;
}

/* ===== 右侧内容区 ===== */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

/* ===== 操作栏 ===== */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: rgba(6, 30, 70, 0.85);
  border: 1px solid rgba(50, 150, 255, 0.35);
  border-radius: 12px;
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.current-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.info-label {
  color: #5a6f83;
}

.info-divider {
  color: rgba(50, 150, 255, 0.3);
}

.info-value {
  color: #00d4ff;
  font-weight: 500;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-btn-custom {
  font-size: 12px !important;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-icon {
  flex-shrink: 0;
}

/* ===== 内容面板 ===== */
.content-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.content-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}

.content-title {
  font-size: 14px;
  font-weight: 600;
  color: #e0e6ed;
}

/* ===== 图表 ===== */
.chart-wrapper {
  flex: 1;
  padding: 8px 16px 16px;
  min-height: 0;
}

.chart-container {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

/* ===== 表格 ===== */
.table-wrapper {
  flex: 1;
  padding: 8px 16px 16px;
  overflow: auto;
}

.data-table {
  width: 100%;
}

.data-table :deep(.el-table__header th) {
  background: rgba(2, 27, 63, 0.8) !important;
  color: #7a8fa3 !important;
  font-size: 12px;
  font-weight: 500;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2) !important;
}

.data-table :deep(.el-table__body td) {
  background: transparent !important;
  color: #c0c8d4 !important;
  font-size: 12px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.08) !important;
}

.data-table :deep(.el-table__row--striped td) {
  background: rgba(0, 175, 255, 0.03) !important;
}

.data-table :deep(.el-table__body tr:hover td) {
  background: rgba(0, 175, 255, 0.08) !important;
}

.data-table :deep(.el-table__body tr.el-table__row--striped:hover td) {
  background: rgba(0, 175, 255, 0.1) !important;
}

.data-table :deep(.el-table__inner-wrapper) {
  background: transparent !important;
}

.data-table :deep(.el-table__body-wrapper) {
  background: transparent !important;
}



/* ===== Element Plus 按钮深色覆盖 ===== */
:deep(.el-button) {
  --el-button-bg-color: transparent;
  --el-button-border-color: rgba(50, 150, 255, 0.3);
  --el-button-text-color: #c0c8d4;
  --el-button-hover-bg-color: rgba(0, 175, 255, 0.1);
  --el-button-hover-border-color: rgba(50, 150, 255, 0.5);
  --el-button-hover-text-color: #e0e6ed;
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
  color: #7a8fa3;
  font-size: 12px;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

:deep(.el-button--primary) {
  --el-button-bg-color: rgba(0, 175, 255, 0.2);
  --el-button-border-color: rgba(0, 175, 255, 0.5);
  --el-button-text-color: #00d4ff;
  --el-button-hover-bg-color: rgba(0, 175, 255, 0.3);
  --el-button-hover-border-color: rgba(0, 175, 255, 0.7);
  --el-button-hover-text-color: #00e5ff;
}
</style>
