<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import {
  reservoirOptions,
  waterConditionTabs,
  getProcessData,
} from '@/mock/waterCondition'

// ==================== 筛选状态 ====================
const reservoirs = reservoirOptions.data
const tabs = waterConditionTabs.data

const dateRange = ref<[string, string]>(['2026-05-15 00:00', '2026-05-16 14:30'])
const selectedReservoir = ref('longyangxia')
const activeTabKey = ref('inflow')
// 当前页签信息
const activeTabInfo = computed(() => {
  return tabs.find(t => t.key === activeTabKey.value) || tabs[0]
})

// 当前图表数据
const chartData = computed(() => {
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

  // 构建系列数据
  const seriesData = data.series.map((s, index) => {
    const baseSeries: any = {
      name: s.name,
      type: 'line',
      data: s.data,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 2.5,
        color: s.color,
        type: s.type === 'dashed' ? 'dashed' : s.type === 'dotted' ? 'dotted' : 'solid',
      },
      itemStyle: { color: s.color },
    }

    // 添加面积渐变（仅第一个实线系列）
    if (index === 0 && s.type === 'solid') {
      baseSeries.areaStyle = {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: s.color + '25' },
          { offset: 1, color: s.color + '05' },
        ]),
      }
    }

    // 添加标记线
    if (data.updateIndex !== undefined && data.updateIndex >= 0 && index === 0) {
      baseSeries.markLine = {
        silent: true,
        symbol: 'none',
        data: [
          {
            xAxis: data.xAxis[data.updateIndex],
            lineStyle: {
              color: data.markLineStyle?.color || 'rgba(0, 175, 255, 0.5)',
              type: 'dashed',
              width: 1.5,
            },
            label: {
              formatter: `{b}\n${data.markLineStyle?.label || '更新节点'}`,
              color: '#7a8fa3',
              fontSize: 11,
              position: 'insideEndTop',
            },
          },
        ],
      }
    }

    // 添加末端标签
    const lastValue = s.data[s.data.length - 1]
    if (lastValue !== null && lastValue !== undefined) {
      baseSeries.markPoint = {
        symbol: 'none',
        data: [
          {
            coord: [data.xAxis.length - 1, lastValue],
            value: lastValue,
            label: {
              formatter: `{a} ${lastValue.toFixed(1)}`,
              color: s.color,
              fontSize: 11,
              fontWeight: 600,
              position: 'right',
            },
          },
        ],
      }
    }

    return baseSeries
  })

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(8, 28, 58, 0.95)',
      borderColor: 'rgba(0, 175, 255, 0.3)',
      borderWidth: 1,
      textStyle: { color: '#e0e6ed', fontSize: 12 },
      axisPointer: {
        type: 'cross',
        crossStyle: { color: '#7a8fa3' },
      },
    },
    legend: {
      data: data.legend,
      textStyle: { color: '#7a8fa3', fontSize: 12 },
      bottom: 0,
      itemGap: 24,
    },
    grid: {
      left: 65,
      right: 80,
      top: 20,
      bottom: 45,
    },
    xAxis: {
      type: 'category',
      data: data.xAxis,
      axisLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.2)' } },
      axisLabel: { color: '#7a8fa3', fontSize: 11 },
      splitLine: { show: false },
      boundaryGap: false,
    },
    yAxis: {
      type: 'value',
      name: data.unit,
      min: data.yAxisMin,
      max: data.yAxisMax,
      nameTextStyle: { color: '#7a8fa3', fontSize: 11 },
      axisLine: { show: false },
      axisLabel: { color: '#7a8fa3', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.08)', type: 'dashed' } },
    },
    series: seriesData,
  }

  chart.setOption(option, true)
  chart.resize()
}

// ==================== 交互 ====================
const handleReservoirChange = () => {
  renderChart()
}

const handleTabChange = (key: string) => {
  activeTabKey.value = key
}

const handleDownload = () => {
  ElMessage.info('当前为前端原型，暂不支持真实下载')
}

const handleFullscreen = () => {
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
    <!-- 顶部筛选区 -->
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
            style="width: 160px"
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

      </div>

      <!-- 指标页签 -->
      <div class="tabs-inline">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTabKey === tab.key }"
          @click="handleTabChange(tab.key)"
        >
          <svg v-if="tab.key === 'inflow'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 19V5M5 12l7-7 7 7"/>
          </svg>
          <svg v-else-if="tab.key === 'water-level'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2.69l5.66 5.66a8 8 0 11-11.31 0z"/>
          </svg>
          <svg v-else-if="tab.key === 'output'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12l7 7 7-7"/>
          </svg>
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- 图表卡片 -->
    <div class="chart-card">
      <div class="chart-header">
        <div class="header-left">
          <span class="chart-title">{{ chartTitle }}</span>
        </div>
        <div class="chart-tools">
          <button class="tool-btn" title="下载" @click="handleDownload">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </button>
          <button class="tool-btn" title="全屏" @click="handleFullscreen">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3m0 18h3a2 2 0 002-2v-3M3 16v3a2 2 0 002 2h3"/>
            </svg>
          </button>
        </div>
      </div>
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
  gap: 12px;
  overflow: hidden;
}

/* 筛选区 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  padding: 12px 16px;
  background: rgba(6, 30, 70, 0.45);
  border: 1px solid rgba(50, 150, 255, 0.10);
  backdrop-filter: blur(14px);
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
}

/* 页签 */
.tabs-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: 1px solid rgba(50, 150, 255, 0.15);
  color: #7a8fa3;
  font-size: 13px;
  padding: 8px 20px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s;
  white-space: nowrap;
}

.tab-btn:hover {
  color: #c0c8d4;
  border-color: rgba(50, 150, 255, 0.3);
  background: rgba(50, 150, 255, 0.05);
}

.tab-btn.active {
  color: #00d4ff;
  border-color: rgba(0, 175, 255, 0.5);
  background: rgba(0, 175, 255, 0.1);
  font-weight: 500;
}

.tab-btn svg {
  flex-shrink: 0;
}

/* 图表卡片 */
.chart-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: rgba(6, 30, 70, 0.45);
  border: 1px solid rgba(50, 150, 255, 0.10);
  backdrop-filter: blur(14px);
  border-radius: 12px;
  overflow: hidden;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.08);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-title {
  font-size: 15px;
  font-weight: 600;
  color: #e0e6ed;
}

.chart-tools {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-btn {
  background: none;
  border: 1px solid rgba(50, 150, 255, 0.15);
  color: #7a8fa3;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.tool-btn:hover {
  color: #00d4ff;
  border-color: rgba(0, 175, 255, 0.4);
  background: rgba(0, 175, 255, 0.08);
}

.chart-container {
  flex: 1;
  min-height: 0;
  padding: 12px;
}

/* Element Plus 深色主题覆盖 */
:deep(.dark-date-picker .el-input__wrapper),
:deep(.dark-select .el-input__wrapper) {
  background: transparent;
  border: 1px solid rgba(50, 150, 255, 0.25);
  box-shadow: none;
}

:deep(.dark-date-picker .el-input__inner),
:deep(.dark-select .el-input__inner) {
  color: #e0e6ed;
}

:deep(.el-range-input) {
  color: #e0e6ed;
}

:deep(.el-range-separator) {
  color: #7a8fa3;
}

:deep(.el-popper) {
  background: #112536;
  border-color: rgba(50, 150, 255, 0.25);
}

:deep(.el-popper__arrow::before) {
  background: #112536;
  border-color: rgba(50, 150, 255, 0.25);
}
</style>
