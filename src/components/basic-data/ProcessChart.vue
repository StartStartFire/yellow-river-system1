<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'
import PanelCard from '@/components/common/PanelCard.vue'
import BaseChart from '@/components/chart/BaseChart.vue'
import {
  TEXT_PRIMARY,
  TECH_BLUE,
  baseTooltip,
  baseLegend,
  baseCategoryXAxis,
  baseValueYAxis,
  SERIES_COLORS,
  createGrid,
} from '@/utils/chart'

interface ProcessSeries {
  name: string
  data: number[]
}

interface Props {
  xAxis: string[]
  series: ProcessSeries[]
}

const props = defineProps<Props>()

const colorMap: Record<string, string> = {
  waterLevel: TECH_BLUE,
  inflow: '#00E5FF',
  outflow: '#00ff88',
}

const chartOption = computed<EChartsOption>(() => ({
  tooltip: {
    ...baseTooltip,
    textStyle: { color: TEXT_PRIMARY, fontSize: 12 },
  },
  legend: {
    ...baseLegend,
    data: props.series.map(s => s.name),
    top: 0,
  },
  grid: createGrid(30, 30, 50, 20),
  xAxis: {
    ...baseCategoryXAxis,
    data: props.xAxis,
  },
  yAxis: {
    ...baseValueYAxis,
    name: 'm',
  },
  series: props.series.map((s, i) => ({
    name: s.name,
    type: 'line' as const,
    data: s.data,
    smooth: true,
    symbol: 'circle',
    symbolSize: 4,
    lineStyle: { width: 2 },
    itemStyle: { color: colorMap[s.name] || SERIES_COLORS[i % SERIES_COLORS.length] },
  })),
}))
</script>

<template>
  <PanelCard title="水情过程线">
    <BaseChart :option="chartOption" class="chart-container" />
  </PanelCard>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
