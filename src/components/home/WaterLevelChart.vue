<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import PanelCard from '@/components/common/PanelCard.vue'
import { waterLevelSeries } from '@/mock/home'

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

// 只展示龙羊峡和刘家峡
const displaySeries = waterLevelSeries.series.filter(
  s => s.name === '龙羊峡水库' || s.name === '刘家峡水库'
)
const colorMap: Record<string, string> = {
  '龙羊峡水库': '#00afff',
  '刘家峡水库': '#00e5ff',
}

const initChart = () => {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const option = {
    tooltip: {
      trigger: 'axis' as const,
      backgroundColor: 'rgba(6, 30, 70, 0.9)',
      borderColor: 'rgba(50, 150, 255, 0.4)',
      textStyle: { color: '#e0e6ed', fontSize: 12 },
    },
    legend: {
      data: displaySeries.map(s => s.name),
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
      data: waterLevelSeries.xAxis,
      axisLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.3)' } },
      axisLabel: { color: '#7a8fa3', fontSize: 11 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value' as const,
      name: 'm',
      nameTextStyle: { color: '#7a8fa3', fontSize: 11 },
      axisLine: { show: false },
      axisLabel: { color: '#7a8fa3', fontSize: 11 },
      splitLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.1)' } },
    },
    series: displaySeries.map(s => ({
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

onMounted(() => {
  // 延迟初始化确保 flex 布局完成
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
  <PanelCard title="水位过程线" unit="单位：m">
    <div ref="chartRef" class="chart-container"></div>
  </PanelCard>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 120px;
}
</style>