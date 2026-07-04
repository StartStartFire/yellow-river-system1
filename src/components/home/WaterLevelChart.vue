<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'
import PanelCard from '@/components/common/PanelCard.vue'
import BaseChart from '@/components/chart/BaseChart.vue'
import { waterLevelSeries } from '@/mock/home'
import {
  baseTooltip,
  baseLegend,
  baseCategoryXAxis,
  baseValueYAxis,
  RESERVOIR_COLORS,
  TEXT_PRIMARY,
  TECH_BLUE,
  createGrid,
} from '@/utils/chart'

const seriesData = waterLevelSeries.data

// 只展示龙羊峡和刘家峡
const displaySeries = seriesData.series.filter(
  s => s.name === '龙羊峡水库' || s.name === '刘家峡水库'
)
const colorMap: Record<string, string> = {
  '龙羊峡水库': TECH_BLUE,
  '刘家峡水库': '#00e5ff',
}

const chartOption = computed<EChartsOption>(() => ({
  tooltip: {
    ...baseTooltip,
    textStyle: { color: TEXT_PRIMARY, fontSize: 12 },
  },
  legend: {
    ...baseLegend,
    data: displaySeries.map(s => s.name),
    top: 0,
  },
  grid: createGrid(36, 30, 50, 20),
  xAxis: {
    ...baseCategoryXAxis,
    data: seriesData.xAxis,
  },
  yAxis: {
    ...baseValueYAxis,
    name: 'm',
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
      color: colorMap[s.name] || RESERVOIR_COLORS[s.name] || TECH_BLUE,
    },
  })),
}))
</script>

<template>
  <PanelCard title="水位过程线" unit="单位：m">
    <BaseChart :option="chartOption" class="chart-container" />
  </PanelCard>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 120px;
}
</style>
