<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import PanelCard from '@/components/common/PanelCard.vue'

interface ProcessSeries {
  name: string
  data: number[]
}

interface Props {
  xAxis: string[]
  series: ProcessSeries[]
}

const props = defineProps<Props>()

const chartRef = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const colorMap: Record<string, string> = {
  waterLevel: '#00AFFF',
  inflow: '#00E5FF',
  outflow: '#00ff88',
}

const initChart = () => {
  if (!chartRef.value) return
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis' as const,
      backgroundColor: 'rgba(6, 30, 70, 0.9)',
      borderColor: 'rgba(50, 150, 255, 0.4)',
      textStyle: { color: '#e0e6ed', fontSize: 12 },
    },
    legend: {
      data: props.series.map(s => s.name),
      textStyle: { color: '#7a8fa3', fontSize: 11 },
      top: 0,
    },
    grid: {
      left: 50,
      right: 20,
      top: 30,
      bottom: 30,
    },
    xAxis: {
      type: 'category' as const,
      data: props.xAxis,
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
    series: props.series.map(s => ({
      name: s.name,
      type: 'line' as const,
      data: s.data,
      smooth: true,
      symbol: 'circle',
      symbolSize: 4,
      lineStyle: { width: 2 },
      itemStyle: { color: colorMap[s.name] || '#00AFFF' },
    })),
  }

  chart.setOption(option)
  chart.resize()
}

onMounted(() => {
  setTimeout(() => {
    initChart()
    if (chartRef.value) {
      resizeObserver = new ResizeObserver(() => chart?.resize())
      resizeObserver.observe(chartRef.value)
    }
  }, 200)
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
  <PanelCard title="水情过程线">
    <div ref="chartRef" class="chart-container"></div>
  </PanelCard>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
