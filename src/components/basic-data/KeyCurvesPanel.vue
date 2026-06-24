<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { KeyCurvesData } from '@/mock/basicData'

const props = defineProps<{
  curves: KeyCurvesData
}>()

const storageChartRef = ref<HTMLElement>()
const turbineChartRef = ref<HTMLElement>()
const gateChartRef = ref<HTMLElement>()

let storageChart: echarts.ECharts | null = null
let turbineChart: echarts.ECharts | null = null
let gateChart: echarts.ECharts | null = null

const getChartOption = (config: {
  title: string
  subtitle: string
  xName: string
  yName: string
  xData: string[]
  yData: number[]
  color: string
  gradientStart: string
  gradientEnd: string
}) => ({
  backgroundColor: 'transparent',
  title: {
    text: config.title,
    subtext: config.subtitle,
    textStyle: {
      color: '#e0e6ed',
      fontSize: 14,
      fontWeight: 600,
      fontFamily: 'Microsoft YaHei',
    },
    subtextStyle: {
      color: '#7a8fa3',
      fontSize: 11,
      lineHeight: 16,
    },
    left: 16,
    top: 8,
  },
  grid: {
    top: 65,
    right: 24,
    bottom: 40,
    left: 60,
    containLabel: false,
  },
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(8, 28, 58, 0.95)',
    borderColor: config.color + '60',
    borderWidth: 1,
    padding: [12, 16],
    textStyle: {
      color: '#e0e6ed',
      fontSize: 12,
      fontFamily: 'Microsoft YaHei',
    },
    axisPointer: {
      type: 'cross',
      crossStyle: { color: '#7a8fa3' },
      lineStyle: { color: config.color + '40', type: 'dashed' },
    },
    formatter: (params: any) => {
      const data = params[0]
      return `<div style="font-size:12px">
        <div style="color:${config.color};font-weight:600;margin-bottom:6px">${config.title}</div>
        <div style="display:flex;justify-content:space-between;gap:20px">
          <span style="color:#7a8fa3">${config.xName}</span>
          <span style="color:#e0e6ed;font-weight:500">${data.name}</span>
        </div>
        <div style="display:flex;justify-content:space-between;gap:20px;margin-top:4px">
          <span style="color:#7a8fa3">${config.yName}</span>
          <span style="color:${config.color};font-weight:600;font-size:14px">${data.value}</span>
        </div>
      </div>`
    },
  },
  xAxis: {
    type: 'category',
    name: config.xName,
    nameLocation: 'center',
    nameGap: 25,
    nameTextStyle: {
      color: '#7a8fa3',
      fontSize: 11,
      fontFamily: 'Microsoft YaHei',
    },
    data: config.xData,
    axisLine: {
      lineStyle: {
        color: 'rgba(50, 150, 255, 0.15)',
      },
    },
    axisTick: { show: false },
    axisLabel: {
      color: '#7a8fa3',
      fontSize: 10,
      interval: Math.floor(config.xData.length / 6),
    },
    splitLine: { show: false },
  },
  yAxis: {
    type: 'value',
    name: config.yName,
    nameLocation: 'center',
    nameGap: 45,
    nameTextStyle: {
      color: '#7a8fa3',
      fontSize: 11,
      fontFamily: 'Microsoft YaHei',
    },
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: {
      color: '#7a8fa3',
      fontSize: 10,
    },
    splitLine: {
      lineStyle: {
        color: 'rgba(50, 150, 255, 0.06)',
        type: 'dashed',
      },
    },
  },
  series: [{
    type: 'line',
    smooth: 0.4,
    symbol: 'circle',
    symbolSize: 8,
    showSymbol: true,
    data: config.yData,
    lineStyle: {
      color: config.color,
      width: 2.5,
      shadowColor: config.color + '40',
      shadowBlur: 8,
      shadowOffsetY: 4,
    },
    itemStyle: {
      color: config.color,
      borderColor: '#0a1929',
      borderWidth: 2,
      shadowColor: config.color + '60',
      shadowBlur: 6,
    },
    emphasis: {
      itemStyle: {
        color: '#fff',
        borderColor: config.color,
        borderWidth: 3,
        shadowColor: config.color + '80',
        shadowBlur: 12,
      },
    },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: config.gradientStart },
        { offset: 0.5, color: config.gradientEnd },
        { offset: 1, color: 'rgba(0, 0, 0, 0)' },
      ]),
    },
  }],
})

const initCharts = async () => {
  await nextTick()

  // 库容曲线
  if (storageChartRef.value) {
    if (storageChart) storageChart.dispose()
    storageChart = echarts.init(storageChartRef.value)
    storageChart.setOption(getChartOption({
      title: '库容曲线',
      subtitle: '水位 — 库容关系',
      xName: '水位 (m)',
      yName: '库容 (亿m³)',
      xData: props.curves.storageCurve.levels.map(v => v.toString()),
      yData: props.curves.storageCurve.storage,
      color: '#00d4ff',
      gradientStart: 'rgba(0, 212, 255, 0.4)',
      gradientEnd: 'rgba(0, 212, 255, 0.08)',
    }))
  }

  // 机组出力曲线
  if (turbineChartRef.value) {
    if (turbineChart) turbineChart.dispose()
    turbineChart = echarts.init(turbineChartRef.value)
    turbineChart.setOption(getChartOption({
      title: '机组出力曲线',
      subtitle: '水头 — 出力关系',
      xName: '水头 (m)',
      yName: '出力 (MW)',
      xData: props.curves.turbineCurve.head.map(v => v.toString()),
      yData: props.curves.turbineCurve.power,
      color: '#00ff88',
      gradientStart: 'rgba(0, 255, 136, 0.4)',
      gradientEnd: 'rgba(0, 255, 136, 0.08)',
    }))
  }

  // 泄洪闸过流曲线
  if (gateChartRef.value) {
    if (gateChart) gateChart.dispose()
    gateChart = echarts.init(gateChartRef.value)
    gateChart.setOption(getChartOption({
      title: '泄洪闸过流曲线',
      subtitle: '开度 — 流量关系',
      xName: '开度 (%)',
      yName: '流量 (m³/s)',
      xData: props.curves.gateCurve.opening.map(v => v.toString()),
      yData: props.curves.gateCurve.flow,
      color: '#b37feb',
      gradientStart: 'rgba(179, 127, 235, 0.4)',
      gradientEnd: 'rgba(179, 127, 235, 0.08)',
    }))
  }
}

watch(() => props.curves, () => {
  initCharts()
}, { deep: true })

onMounted(() => {
  initCharts()
  window.addEventListener('resize', () => {
    storageChart?.resize()
    turbineChart?.resize()
    gateChart?.resize()
  })
})
</script>

<template>
  <div class="key-curves-panel">
    <div class="curves-grid">
      <div class="curve-card">
        <div ref="storageChartRef" class="chart-container"></div>
      </div>
      <div class="curve-card">
        <div ref="turbineChartRef" class="chart-container"></div>
      </div>
      <div class="curve-card">
        <div ref="gateChartRef" class="chart-container"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.key-curves-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 12px;
}

.curves-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  flex: 1;
  min-height: 0;
}

.curve-card {
  background: rgba(6, 30, 70, 0.5);
  border: 1px solid rgba(50, 150, 255, 0.12);
  backdrop-filter: blur(16px);
  border-radius: 14px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.3s ease;
}

.curve-card:hover {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.chart-container {
  flex: 1;
  min-height: 300px;
  width: 100%;
}
</style>
