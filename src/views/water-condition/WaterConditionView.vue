<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import BaseChart from '@/components/chart/BaseChart.vue'
import {
  baseTooltip,
  baseLegend,
  baseCategoryXAxis,
  baseValueYAxis,
  TEXT_SECONDARY,
  createGrid,
} from '@/utils/chart'
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

// 当前图表数据
const chartData = computed(() => {
  return getProcessData(selectedReservoir.value, activeTabKey.value).data
})

// 图表标题
const chartTitle = computed(() => chartData.value.title)

// ==================== ECharts option（纯数据，BaseChart 负责渲染） ====================
const chartOption = computed<echarts.EChartsOption>(() => {
  const data = chartData.value

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

    if (index === 0 && s.type === 'solid') {
      baseSeries.areaStyle = {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: s.color + '25' },
          { offset: 1, color: s.color + '05' },
        ]),
      }
    }

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
              color: TEXT_SECONDARY,
              fontSize: 11,
              position: 'insideEndTop',
            },
          },
        ],
      }
    }

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

  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...baseTooltip,
      textStyle: { ...baseTooltip.textStyle, fontSize: 12 },
    },
    legend: {
      ...baseLegend,
      data: data.legend,
      textStyle: { ...baseLegend.textStyle, fontSize: 12 },
    },
    grid: createGrid(20, 45, 65, 80),
    xAxis: {
      ...baseCategoryXAxis,
      data: data.xAxis,
    },
    yAxis: {
      ...baseValueYAxis,
      name: data.unit,
      min: data.yAxisMin,
      max: data.yAxisMax,
    },
    series: seriesData,
  }
})

// ==================== 交互 ====================
const handleTabChange = (key: string) => {
  activeTabKey.value = key
}

const handleDownload = () => {
  ElMessage.info('当前为前端原型，暂不支持真实下载')
}

const baseChartRef = ref<InstanceType<typeof BaseChart> | null>(null)

const handleFullscreen = () => {
  const el = (baseChartRef.value?.$el as HTMLElement)?.parentElement
  el?.requestFullscreen?.()
}

const onFullscreenChange = () => {
  setTimeout(() => baseChartRef.value?.resize(), 200)
}

onMounted(() => {
  document.addEventListener('fullscreenchange', onFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', onFullscreenChange)
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
      <BaseChart ref="baseChartRef" :option="chartOption" class="chart-container" />
    </div>
  </div>
</template>

<style scoped>
.water-condition-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
  gap: 0;
  overflow: hidden;
  background: rgba(6, 20, 42, 0.92);
}

/* 筛选区 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(0, 175, 255, 0.12);
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
  color: #8aa0b8;
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
  border: none;
  border-bottom: 2px solid transparent;
  color: #8aa0b8;
  font-size: 13px;
  padding: 8px 20px;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.tab-btn:hover {
  color: #c0c8d4;
  border-bottom-color: rgba(50, 150, 255, 0.3);
  background: rgba(50, 150, 255, 0.05);
}

.tab-btn.active {
  color: #00d4ff;
  border-bottom-color: rgba(0, 212, 255, 0.6);
  background: transparent;
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
  background: transparent;
  border: none;
  overflow: hidden;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-bottom: 1px solid rgba(0, 175, 255, 0.08);
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
  border: none;
  color: #8aa0b8;
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
  color: #8aa0b8;
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
