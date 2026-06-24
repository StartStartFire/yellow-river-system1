<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import {
  reservoirOptions,
  waterConditionTabs,
  getProcessData,
} from '@/mock/waterCondition'
import { getProcessData as getBasicProcessData } from '@/mock/basicData'
import type { ConditionTab } from '@/mock/waterCondition'

// ==================== 筛选状态 ====================
const reservoirs = reservoirOptions.data
const tabs = [...waterConditionTabs.data, { key: 'basic-process', label: '水情过程', unit: '' }]

const dateRange = ref<[string, string]>(['2026-05-15 00:00', '2026-05-16 14:30'])
const selectedReservoir = ref('longyangxia')
const activeTabKey = ref('water-level')
const defaultRange: [string, string] = ['2026-05-15 00:00', '2026-05-16 14:30']
const defaultReservoir = 'longyangxia'

// 当前选中水库名称
const reservoirName = computed(() => {
  return reservoirs.find(r => r.value === selectedReservoir.value)?.label || '龙羊峡水库'
})

// 当前页签信息
const activeTabInfo = computed(() => {
  return tabs.find(t => t.key === activeTabKey.value) || tabs[0]
})

// 是否是水情过程页签
const isBasicProcess = computed(() => activeTabKey.value === 'basic-process')

// 当前图表数据
const chartData = computed(() => {
  if (isBasicProcess.value) {
    const data = getBasicProcessData(selectedReservoir.value).data
    return {
      title: `${reservoirName.value} - 水情过程`,
      unit: '',
      legend: ['入库流量', '出库流量'],
      xAxis: data.dates,
      inflow: data.inflows,
      outflow: data.outflows,
      updateIndex: -1,
    }
  }
  return getProcessData(selectedReservoir.value, activeTabKey.value).data
})

// 图表标题
const chartTitle = computed(() => chartData.value.title)

// ==================== ECharts ====================
const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const initChart = () => {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  renderChart()
}

const renderChart = () => {
  if (!chart) return
  const data = chartData.value

  if (isBasicProcess.value) {
    // 水情过程：双线（入库流量、出库流量）
    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(6, 30, 70, 0.9)',
        borderColor: 'rgba(50, 150, 255, 0.4)',
        textStyle: { color: '#e0e6ed', fontSize: 12 },
      },
      legend: {
        data: ['入库流量', '出库流量'],
        textStyle: { color: '#7a8fa3', fontSize: 12 },
        bottom: 0,
      },
      grid: {
        left: 60,
        right: 60,
        top: 20,
        bottom: 36,
      },
      xAxis: {
        type: 'category',
        data: data.xAxis,
        axisLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.3)' } },
        axisLabel: { color: '#7a8fa3', fontSize: 11 },
        splitLine: { show: false },
        boundaryGap: false,
      },
      yAxis: {
        type: 'value',
        name: '流量 (m³/s)',
        nameTextStyle: { color: '#7a8fa3', fontSize: 12 },
        axisLine: { show: false },
        axisLabel: { color: '#7a8fa3', fontSize: 11 },
        splitLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.1)', type: 'dashed' } },
      },
      series: [
        {
          name: '入库流量',
          type: 'line',
          data: (data as any).inflow,
          smooth: true,
          symbol: 'circle',
          symbolSize: 5,
          lineStyle: { width: 2, color: '#00e5a0' },
          itemStyle: { color: '#00e5a0' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0, 229, 160, 0.12)' },
              { offset: 1, color: 'rgba(0, 229, 160, 0.02)' },
            ]),
          },
        },
        {
          name: '出库流量',
          type: 'line',
          data: (data as any).outflow,
          smooth: true,
          symbol: 'circle',
          symbolSize: 5,
          lineStyle: { width: 2, color: '#b37feb' },
          itemStyle: { color: '#b37feb' },
        },
      ],
    }

    chart.setOption(option, true)
    chart.resize()
    return
  }

  // 调令执行对比：目标值 vs 实际值（原有逻辑）
  const updateLabel = data.xAxis[data.updateIndex]

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(6, 30, 70, 0.9)',
      borderColor: 'rgba(50, 150, 255, 0.4)',
      textStyle: { color: '#e0e6ed', fontSize: 12 },
    },
    legend: {
      data: data.legend,
      textStyle: { color: '#7a8fa3', fontSize: 12 },
      bottom: 0,
    },
    grid: {
      left: 60,
      right: 60,
      top: 20,
      bottom: 36,
    },
    xAxis: {
      type: 'category',
      data: data.xAxis,
      axisLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.3)' } },
      axisLabel: { color: '#7a8fa3', fontSize: 11 },
      splitLine: { show: false },
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      name: data.unit,
      nameTextStyle: { color: '#7a8fa3', fontSize: 12 },
      axisLine: { show: false },
      axisLabel: { color: '#7a8fa3', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.1)', type: 'dashed' } },
    },
    series: [
      {
        name: data.legend[0],
        type: 'line',
        data: data.target,
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        lineStyle: { width: 2, type: 'dashed', color: '#00afff' },
        itemStyle: { color: '#00afff' },
        markLine: {
          silent: true,
          symbol: 'none',
          data: [
            {
              xAxis: updateLabel,
              lineStyle: { color: 'rgba(0, 175, 255, 0.6)', type: 'dashed', width: 1.5 },
              label: {
                formatter: `{b}\n调度更新节点`,
                color: '#7a8fa3',
                fontSize: 11,
                position: 'start',
              },
            },
          ],
        },
        markPoint: {
          symbol: 'none',
          data: [
            {
              coord: [data.xAxis.length - 1, data.targetLastValue],
              value: data.targetLastValue,
              label: {
                formatter: `目标 {c}`,
                color: '#00afff',
                fontSize: 12,
                fontWeight: 600,
                position: 'right',
              },
            },
          ],
        },
      },
      {
        name: data.legend[1],
        type: 'line',
        data: data.actual,
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        lineStyle: { width: 2, color: '#00e5a0' },
        itemStyle: { color: '#00e5a0' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 229, 160, 0.15)' },
            { offset: 1, color: 'rgba(0, 229, 160, 0.02)' },
          ]),
        },
        markPoint: {
          symbol: 'none',
          data: [
            {
              coord: [data.xAxis.length - 1, data.actualLastValue],
              value: data.actualLastValue,
              label: {
                formatter: `实际 {c}`,
                color: '#00e5a0',
                fontSize: 12,
                fontWeight: 600,
                position: 'right',
              },
            },
          ],
        },
      },
    ],
  }

  chart.setOption(option, true)
  chart.resize()
}

// ==================== 交互 ====================
const handleQuery = () => {
  // 当前阶段只刷新图表渲染
  renderChart()
}

const handleReset = () => {
  dateRange.value = [...defaultRange] as [string, string]
  selectedReservoir.value = defaultReservoir
  activeTabKey.value = 'water-level'
}

const handleReservoirChange = () => {
  renderChart()
}

const handleTabChange = (key: string) => {
  activeTabKey.value = key
}

const handleDownload = () => {
  // 当前阶段只做 UI 提示
  const msg = '暂不支持真实下载'
  // 简单提示
  alert(msg)
}

const handleFullscreen = () => {
  // 简单浏览器全屏
  if (chartRef.value) {
    chartRef.value.requestFullscreen?.()
  }
}

// 全屏变化时重新渲染
const onFullscreenChange = () => {
  setTimeout(() => chart?.resize(), 200)
}

// ==================== 生命周期 ====================
onMounted(() => {
  setTimeout(() => {
    initChart()
    if (chartRef.value) {
      resizeObserver = new ResizeObserver(() => chart?.resize())
      resizeObserver.observe(chartRef.value)
    }
  }, 200)
  document.addEventListener('fullscreenchange', onFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (chart) {
    chart.dispose()
    chart = null
  }
})

// 页签切换时刷新图表
watch(activeTabKey, () => {
  setTimeout(() => renderChart(), 50)
})

// 水库切换时刷新图表
watch(selectedReservoir, () => {
  setTimeout(() => renderChart(), 50)
})
</script>

<template>
  <div class="water-condition-view">
    <!-- 顶部筛选区（含指标页签） -->
    <div class="filter-bar">
      <div class="filter-left">
        <div class="filter-item">
          <label class="filter-label">时间范围</label>
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="~"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            size="small"
            class="dark-date-picker"
            value-format="YYYY-MM-DD HH:mm"
            :clearable="false"
          />
        </div>

        <div class="filter-item">
          <label class="filter-label">水库</label>
          <el-select
            v-model="selectedReservoir"
            size="small"
            class="dark-select"
            @change="handleReservoirChange"
          >
            <el-option
              v-for="r in reservoirs"
              :key="r.value"
              :label="r.label"
              :value="r.value"
            />
          </el-select>
        </div>

        <div class="filter-actions">
          <el-button type="primary" size="small" class="filter-btn" @click="handleQuery">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="margin-right: 4px;">
              <circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.3"/>
              <path d="M9.5 9.5L13 13" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            查询
          </el-button>
          <el-button size="small" class="filter-btn" @click="handleReset">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="margin-right: 4px;">
              <path d="M3 7a4 4 0 016.5-3.1M11 7a4 4 0 01-6.5 3.1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              <path d="M9.5 2.5L12 4l-2.5 1.5M4.5 11.5L2 10l2.5-1.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            重置
          </el-button>
        </div>
      </div>

      <div class="filter-divider"></div>

      <!-- 指标页签（整合在筛选栏右侧） -->
      <div class="tabs-inline">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn-inline"
          :class="{ active: activeTabKey === tab.key }"
          @click="handleTabChange(tab.key)"
        >
          <svg v-if="tab.key === 'water-level'" width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1l5 6.5a4 4 0 01-10 0L7 1z" stroke="currentColor" stroke-width="1.3" fill="none"/>
            <circle cx="7" cy="7.5" r="1.5" fill="currentColor"/>
          </svg>
          <svg v-else-if="tab.key === 'flow'" width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M2 10c2-4 4-6 5-7M12 10c-2-4-4-6-5-7M7 3v8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
          <svg v-else-if="tab.key === 'output'" width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1v3M7 10v3M1 7h3M10 7h3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            <circle cx="7" cy="7" r="2.5" stroke="currentColor" stroke-width="1.3"/>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M2 3h10M2 7h10M2 11h10" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            <path d="M5 5v4M9 5v4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-dasharray="2 2"/>
          </svg>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- 核心图表卡片 -->
    <div class="chart-card">
      <!-- 图表标题栏 -->
      <div class="chart-header">
        <span class="chart-title">{{ chartTitle }}</span>
        <div class="chart-tools">
          <span v-if="!isBasicProcess" class="tool-unit">{{ activeTabInfo.unit }}</span>
          <button class="tool-btn" title="下载" @click="handleDownload">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1v8M4 6l3 3 3-3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 10v2h10v-2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
          </button>
          <button class="tool-btn" title="全屏" @click="handleFullscreen">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 5V2h3M12 5V2H9M2 9v3h3M12 9v3H9" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>
      <!-- 图表区 -->
      <div ref="chartRef" class="chart-container"></div>
    </div>
  </div>
</template>

<style scoped>
.water-condition-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 12px;
  gap: 8px;
  overflow: hidden;
}

/* ===== 筛选区 ===== */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  padding: 8px 16px;
  background: rgba(6, 30, 70, 0.85);
  border: 1px solid rgba(50, 150, 255, 0.35);
  border-radius: 12px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 12px;
  color: #7a8fa3;
  white-space: nowrap;
  font-weight: 500;
}

.filter-actions {
  display: flex;
  gap: 6px;
}

.filter-btn {
  font-size: 12px !important;
}

.filter-divider {
  width: 1px;
  height: 28px;
  background: rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}

/* ===== 筛选栏内联页签 ===== */
.tabs-inline {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.tab-btn-inline {
  display: flex;
  align-items: center;
  gap: 5px;
  background: transparent;
  border: 1px solid rgba(50, 150, 255, 0.2);
  color: #7a8fa3;
  font-size: 12px;
  padding: 5px 14px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab-btn-inline:hover {
  color: #c0c8d4;
  border-color: rgba(50, 150, 255, 0.35);
}

.tab-btn-inline.active {
  color: #00d4ff;
  border-color: rgba(0, 175, 255, 0.5);
  background: rgba(0, 175, 255, 0.08);
  font-weight: 500;
}

.tab-btn-inline svg {
  flex-shrink: 0;
}
:deep(.dark-date-picker .el-input__wrapper) {
  border: 1px solid rgba(50, 150, 255, 0.25) !important;
}

:deep(.dark-date-picker .el-input__inner) {
  color: #c0c8d4 !important;
  font-size: 12px;
}

:deep(.dark-select) {
  width: 160px;
}

:deep(.dark-select .el-input__wrapper) {
  border: 1px solid rgba(50, 150, 255, 0.25) !important;
}

:deep(.dark-select .el-input__inner) {
  color: #c0c8d4 !important;
  font-size: 12px;
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

/* ===== 图表卡片 ===== */
.chart-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: rgba(6, 30, 70, 0.85);
  border: 1px solid rgba(50, 150, 255, 0.35);
  border-radius: 12px;
  overflow: hidden;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #e0e6ed;
}

.chart-tools {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-unit {
  font-size: 12px;
  color: #7a8fa3;
  padding: 2px 10px;
  border: 1px solid rgba(50, 150, 255, 0.25);
  border-radius: 4px;
}

.tool-btn {
  background: none;
  border: 1px solid rgba(50, 150, 255, 0.25);
  color: #7a8fa3;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.tool-btn:hover {
  color: #00d4ff;
  border-color: rgba(0, 175, 255, 0.5);
  background: rgba(0, 175, 255, 0.08);
}

.chart-container {
  flex: 1;
  min-height: 0;
  padding: 8px;
}
</style>
