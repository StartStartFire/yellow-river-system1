<script setup lang="ts">
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import type { KeyCurvesData } from '@/mock/basicData'

const props = defineProps<{
  curves: KeyCurvesData
}>()

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const activeTab = ref('storage')

const tabList = [
  { key: 'storage', label: '库容曲线' },
  { key: 'turbine', label: '机组出力曲线' },
  { key: 'gate', label: '泄洪闸过流曲线' },
]

const currentCurve = computed(() => {
  switch (activeTab.value) {
    case 'storage':
      return {
        title: '库容曲线',
        subtitle: '水位 — 库容关系',
        xName: '水位 (m)',
        yName: '库容 (亿m³)',
        xData: props.curves.storageCurve.levels.map(v => v.toString()),
        yData: props.curves.storageCurve.storage,
        color: '#00d4ff',
        gradientStart: 'rgba(0, 212, 255, 0.4)',
        gradientEnd: 'rgba(0, 212, 255, 0.08)',
      }
    case 'turbine':
      return {
        title: '机组出力曲线',
        subtitle: '水头 — 出力关系',
        xName: '水头 (m)',
        yName: '出力 (MW)',
        xData: props.curves.turbineCurve.head.map(v => v.toString()),
        yData: props.curves.turbineCurve.power,
        color: '#00ff88',
        gradientStart: 'rgba(0, 255, 136, 0.4)',
        gradientEnd: 'rgba(0, 255, 136, 0.08)',
      }
    case 'gate':
      return {
        title: '泄洪闸过流曲线',
        subtitle: '开度 — 流量关系',
        xName: '开度 (%)',
        yName: '流量 (m³/s)',
        xData: props.curves.gateCurve.opening.map(v => v.toString()),
        yData: props.curves.gateCurve.flow,
        color: '#b37feb',
        gradientStart: 'rgba(179, 127, 235, 0.4)',
        gradientEnd: 'rgba(179, 127, 235, 0.08)',
      }
  }
})

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
      fontSize: 16,
      fontWeight: 600,
      fontFamily: 'Microsoft YaHei',
    },
    subtextStyle: {
      color: '#7a8fa3',
      fontSize: 12,
      lineHeight: 18,
    },
    left: 24,
    top: 12,
  },
  grid: {
    top: 80,
    right: 32,
    bottom: 50,
    left: 72,
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
    nameGap: 28,
    nameTextStyle: {
      color: '#7a8fa3',
      fontSize: 12,
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
      fontSize: 11,
      interval: Math.floor(config.xData.length / 6),
    },
    splitLine: { show: false },
  },
  yAxis: {
    type: 'value',
    name: config.yName,
    nameLocation: 'center',
    nameGap: 50,
    nameTextStyle: {
      color: '#7a8fa3',
      fontSize: 12,
      fontFamily: 'Microsoft YaHei',
    },
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: {
      color: '#7a8fa3',
      fontSize: 11,
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

const renderChart = async () => {
  await nextTick()
  if (!chartRef.value) return

  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption(getChartOption(currentCurve.value))
}

watch(() => props.curves, () => {
  renderChart()
}, { deep: true })

watch(activeTab, () => {
  renderChart()
})

onMounted(() => {
  renderChart()
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
})
</script>

<template>
  <div class="key-curves-panel">
    <div class="tabs-bar">
      <button
        v-for="tab in tabList"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>
    <div class="chart-area">
      <div ref="chartRef" class="chart-container"></div>
    </div>
  </div>
</template>

<style scoped>
.key-curves-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 12px 12px;
}

.tabs-bar {
  display: flex;
  gap: 2px;
  flex-shrink: 0;
}

.tab-btn {
  background: none;
  border: 1px solid rgba(50, 150, 255, 0.2);
  color: #7a8fa3;
  font-size: 13px;
  padding: 6px 20px;
  cursor: pointer;
  border-radius: 6px 6px 0 0;
  transition: all 0.2s;
  position: relative;
}

.tab-btn:hover {
  color: #c0c8d4;
  border-color: rgba(50, 150, 255, 0.35);
}

.tab-btn.active {
  color: #00d4ff;
  border-color: rgba(0, 175, 255, 0.5);
  background: rgba(0, 175, 255, 0.08);
  font-weight: 500;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 1px;
  background: rgba(0, 175, 255, 0.08);
}

.chart-area {
  flex: 1;
  min-height: 0;
  background: rgba(6, 30, 70, 0.5);
  border: 1px solid rgba(50, 150, 255, 0.12);
  backdrop-filter: blur(16px);
  border-radius: 14px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chart-container {
  flex: 1;
  min-height: 300px;
  width: 100%;
}
</style>
