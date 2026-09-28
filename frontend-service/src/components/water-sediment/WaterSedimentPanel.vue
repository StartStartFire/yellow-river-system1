<script setup lang="ts">
/**
 * WaterSedimentPanel — 水沙耦合仿真结果图表面板
 *
 * 展示 4 类图表：
 *  1. 断面洪水演进
 *  2. 刘家峡下泄 - 兰州断面流量迭代收敛
 *  3. 龙羊峡调度过程
 *  4. 河道冲淤
 *
 * 数据源：后端 /process 或 /results 的 result 字段（WaterSedimentResult）。
 * 顶部汇总指标统一在过程透明页底部信息栏展示（与多目标优化模型布局一致）。
 */
import { computed } from 'vue'
import BaseChart from '@/components/chart/BaseChart.vue'
import PanelCard from '@/components/common/PanelCard.vue'
import type { WaterSedimentResult } from '@/api'
import {
  buildSectionFloodAreaOption,
  buildIterationOption,
  buildReservoirOption,
  buildSedimentOption,
} from '@/utils/waterSedimentCharts'

const props = defineProps<{
  /** 水沙仿真结果 */
  result: WaterSedimentResult
}>()

const data = computed(() => props.result)

// 4 个图表 option
const sectionFloodOption = computed(() => buildSectionFloodAreaOption(data.value))
const iterationOption = computed(() => buildIterationOption(data.value))
const reservoirOption = computed(() => buildReservoirOption(data.value))
const sedimentOption = computed(() => buildSedimentOption(data.value))
</script>

<template>
  <div class="water-sediment-panel">
    <!-- 图表区：断面洪水（占满一行）+ 冲淤 + 迭代收敛 + 龙羊峡调度 -->
    <div class="charts-grid">
      <PanelCard title="断面洪水过程" accent class="chart-card chart-card-wide">
        <BaseChart :option="sectionFloodOption" class="chart-box" />
      </PanelCard>

      <PanelCard title="河道冲淤（各段）" accent class="chart-card">
        <BaseChart :option="sedimentOption" class="chart-box" />
      </PanelCard>

      <PanelCard title="刘家峡下泄 — 兰州断面流量迭代收敛" accent class="chart-card">
        <BaseChart :option="iterationOption" class="chart-box" />
      </PanelCard>

      <PanelCard title="龙羊峡调度过程" accent class="chart-card">
        <BaseChart :option="reservoirOption" class="chart-box" />
      </PanelCard>
    </div>
  </div>
</template>

<style scoped>
.water-sediment-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 4px;
  min-height: 0;
}

.charts-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1.2fr 1fr;
  gap: 10px;
  min-height: 0;
}

.chart-card {
  min-height: 0;
}

.chart-card :deep(.section-body) {
  padding: 4px;
}

.chart-box {
  width: 100%;
  height: 100%;
  min-height: 180px;
}

.chart-card-wide {
  grid-column: span 1;
}
</style>
