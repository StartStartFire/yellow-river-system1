<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import PanelCard from '@/components/common/PanelCard.vue'
import { loadSeries } from '@/mock/home'

const seriesData = loadSeries.data

const chartRef = ref<HTMLDivElement | null>(null)
const activeType = ref<'active' | 'reactive'>('active')
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

// 只展示龙羊峡和刘家峡
const colorMap: Record<string, string> = {
  '龙羊峡水库': '#00afff',
  '刘家峡水库': '#00e5ff',
}

const initChart = () => {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const rawData = activeType.value === 'active' ? seriesData.activePower : seriesData.reactivePower
  const displayData = rawData.filter(
    s => s.name === '龙羊峡水库' || s.name === '刘家峡水库'
  )
  const unit = activeType.value === 'active' ? '有功 (MW)' : '无功 (Mvar)'

  const option = {
    tooltip: {
      trigger: 'axis' as const,
      backgroundColor: 'rgba(6, 30, 70, 0.9)',
      borderColor: 'rgba(50, 150, 255, 0.4)',
      textStyle: { color: '#e0e6ed', fontSize: 12 },
    },
    legend: {
      data: displayData.map(s => s.name),
      textStyle: { color: '#7a8fa3', fontSize: 11 },
      top: 0,
    },
    grid: {
      left: 50,
      right: 20,
      top: 36,
      bottom: 30,
    },
    xAxis: {
      type: 'category' as const,
      data: seriesData.xAxis,
      axisLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.3)' } },
      axisLabel: { color: '#7a8fa3', fontSize: 11 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value' as const,
      name: unit,
      nameTextStyle: { color: '#7a8fa3', fontSize: 11 },
      axisLine: { show: false },
      axisLabel: { color: '#7a8fa3', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.1)' } },
    },
    series: displayData.map(s => ({
      name: s.name,
      type: 'line' as const,
      data: s.data,
      smooth: true,
      symbol: 'circle',
      symbolSize: 4,
      lineStyle: { width: 2 },
      itemStyle: {
        color: colorMap[s.name] || '#00afff',
      },
    })),
  }

  chart.setOption(option)
  chart.resize()
}

watch(activeType, () => {
  initChart()
})

onMounted(() => {
  setTimeout(() => {
    initChart()
    if (chartRef.value) {
      resizeObserver = new ResizeObserver(() => chart?.resize())
      resizeObserver.observe(chartRef.value)
    }
  }, 300)
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<template>
  <PanelCard title="负荷过程线">
    <template #header-extra>
      <div class="flex gap-2">
        <button
          @click="activeType = 'active'"
          class="toggle-btn"
          :class="{ active: activeType === 'active' }"
        >有功</button>
        <button
          @click="activeType = 'reactive'"
          class="toggle-btn"
          :class="{ active: activeType === 'reactive' }"
        >无功</button>
      </div>
    </template>
    <div ref="chartRef" class="chart-container"></div>
  </PanelCard>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 120px;
}

.toggle-btn {
  background: none;
  border: 1px solid rgba(50, 150, 255, 0.3);
  color: #7a8fa3;
  font-size: 11px;
  padding: 2px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: rgba(0, 175, 255, 0.2);
  border-color: rgba(0, 175, 255, 0.6);
  color: #00d4ff;
}
</style>