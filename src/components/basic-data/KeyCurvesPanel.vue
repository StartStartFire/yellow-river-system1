<script setup lang="ts">
import { ref, computed } from 'vue'
import type { EChartsOption } from 'echarts'
import BaseChart from '@/components/chart/BaseChart.vue'
import {
  TEXT_PRIMARY,
  TEXT_SECONDARY,
  baseTooltip,
  baseCategoryXAxis,
  baseValueYAxis,
  createGrid,
  createAreaGradient,
} from '@/utils/chart'
import type { KeyCurvesData } from '@/mock/basicData'

const props = defineProps<{
  curves: KeyCurvesData
}>()

const activeTab = ref('storage')

const tabList = [
  { key: 'storage', label: '库容曲线' },
  { key: 'turbine', label: '机组出力曲线' },
  { key: 'gate', label: '泄洪闸过流曲线' },
]

const chartOption = computed<EChartsOption>(() => {
  const configs = {
    storage: {
      title: '库容曲线',
      subtitle: '水位 — 库容关系',
      xName: '水位 (m)',
      yName: '库容 (亿m³)',
      xData: props.curves.storageCurve.levels.map(v => v.toString()),
      yData: props.curves.storageCurve.storage,
      color: '#00d4ff',
    },
    turbine: {
      title: '机组出力曲线',
      subtitle: '水头 — 出力关系',
      xName: '水头 (m)',
      yName: '出力 (MW)',
      xData: props.curves.turbineCurve.head.map(v => v.toString()),
      yData: props.curves.turbineCurve.power,
      color: '#00ff88',
    },
    gate: {
      title: '泄洪闸过流曲线',
      subtitle: '开度 — 流量关系',
      xName: '开度 (%)',
      yName: '流量 (m³/s)',
      xData: props.curves.gateCurve.opening.map(v => v.toString()),
      yData: props.curves.gateCurve.flow,
      color: '#b37feb',
    },
  }
  const config = configs[activeTab.value as keyof typeof configs]

  return {
    backgroundColor: 'transparent',
    title: {
      text: config.title,
      subtext: config.subtitle,
      textStyle: {
        color: TEXT_PRIMARY,
        fontSize: 16,
        fontWeight: 600,
        fontFamily: 'Microsoft YaHei',
      },
      subtextStyle: {
        color: TEXT_SECONDARY,
        fontSize: 12,
        lineHeight: 18,
      },
      left: 24,
      top: 12,
    },
    grid: createGrid(80, 50, 72, 32),
    tooltip: {
      ...baseTooltip,
      borderColor: config.color + '60',
      axisPointer: {
        type: 'cross',
        crossStyle: { color: TEXT_SECONDARY },
        lineStyle: { color: config.color + '40', type: 'dashed' },
      },
      formatter: (params: any) => {
        const data = params[0]
        return `<div style="font-size:12px">
          <div style="color:${config.color};font-weight:600;margin-bottom:6px">${config.title}</div>
          <div style="display:flex;justify-content:space-between;gap:20px">
            <span style="color:${TEXT_SECONDARY}">${config.xName}</span>
            <span style="color:${TEXT_PRIMARY};font-weight:500">${data.name}</span>
          </div>
          <div style="display:flex;justify-content:space-between;gap:20px;margin-top:4px">
            <span style="color:${TEXT_SECONDARY}">${config.yName}</span>
            <span style="color:${config.color};font-weight:600;font-size:14px">${data.value}</span>
          </div>
        </div>`
      },
    },
    xAxis: {
      ...baseCategoryXAxis,
      name: config.xName,
      nameLocation: 'center',
      nameGap: 28,
      nameTextStyle: {
        color: TEXT_SECONDARY,
        fontSize: 12,
        fontFamily: 'Microsoft YaHei',
      },
      data: config.xData,
      axisTick: { show: false },
      axisLabel: {
        color: TEXT_SECONDARY,
        fontSize: 11,
        interval: Math.floor(config.xData.length / 6),
      },
    },
    yAxis: {
      ...baseValueYAxis,
      name: config.yName,
      nameLocation: 'center',
      nameGap: 50,
      nameTextStyle: {
        color: TEXT_SECONDARY,
        fontSize: 12,
        fontFamily: 'Microsoft YaHei',
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
      areaStyle: createAreaGradient(config.color, 0.4, 0.08),
    }],
  }
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
      <div class="chart-container">
        <BaseChart :option="chartOption" />
      </div>
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
  color: #8aa0b8;
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
  background: transparent;
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
