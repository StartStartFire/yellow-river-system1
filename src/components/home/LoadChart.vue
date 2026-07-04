<script setup lang="ts">
import { computed, ref } from 'vue'
import type { EChartsOption } from 'echarts'
import PanelCard from '@/components/common/PanelCard.vue'
import BaseChart from '@/components/chart/BaseChart.vue'
import { loadSeries } from '@/mock/home'
import {
  baseTooltip,
  baseLegend,
  baseCategoryXAxis,
  baseValueYAxis,
  RESERVOIR_COLORS,
  createGrid,
} from '@/utils/chart'

const seriesData = loadSeries.data

const activeType = ref<'active' | 'reactive'>('active')

// 只展示龙羊峡和刘家峡
const colorMap: Record<string, string> = {
  '龙羊峡水库': '#00afff',
  '刘家峡水库': '#00e5ff',
}

const chartOption = computed<EChartsOption>(() => {
  const rawData = activeType.value === 'active' ? seriesData.activePower : seriesData.reactivePower
  const displayData = rawData.filter(
    s => s.name === '龙羊峡水库' || s.name === '刘家峡水库'
  )
  const unit = activeType.value === 'active' ? '有功 (MW)' : '无功 (Mvar)'

  return {
    tooltip: {
      ...baseTooltip,
      textStyle: { color: '#e0e6ed', fontSize: 12 },
    },
    legend: {
      ...baseLegend,
      data: displayData.map(s => s.name),
      top: 0,
    },
    grid: createGrid(36, 30, 50, 20),
    xAxis: {
      ...baseCategoryXAxis,
      data: seriesData.xAxis,
    },
    yAxis: {
      ...baseValueYAxis,
      name: unit,
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
        color: colorMap[s.name] || RESERVOIR_COLORS[s.name] || '#00afff',
      },
    })),
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
    <BaseChart :option="chartOption" class="chart-container" />
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
  color: #8aa0b8;
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
