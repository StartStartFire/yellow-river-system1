<script setup lang="ts">
/**
 * EvaluationPanel — 评价分析面板
 *
 * 包含 4 个图表区域：多方案评价雷达图 + 评价指标桑基图 + 帕累托曲线 + 评价算法排名表格。
 * 纯展示组件，图表 option 由父组件构建后传入，内部用 BaseChart 渲染。
 */
import { ref, computed } from 'vue'
import * as echarts from 'echarts'
import BaseChart from '@/components/chart/BaseChart.vue'

interface Props {
  /** 雷达图 option */
  radarOption: echarts.EChartsOption
  /** 评价指标桑基图 option */
  sankeyOption: echarts.EChartsOption
  /** 帕累托曲线 option */
  paretoOption: echarts.EChartsOption
  /** 评价算法排名数据 */
  rankingData: any
  /** 当前选中的方案标签集合（用于图表过滤，预留） */
  selectedPlanLabels: string[]
}

const props = defineProps<Props>()

// ========== BaseChart refs（供父组件统一 resize） ==========
const radarBaseChart = ref<InstanceType<typeof BaseChart> | null>(null)
const sankeyBaseChart = ref<InstanceType<typeof BaseChart> | null>(null)
const paretoBaseChart = ref<InstanceType<typeof BaseChart> | null>(null)

// 排名表格的表头列（从第一行 scores 中提取）
const rankingColumns = computed(() => {
  return props.rankingData?.data?.[0]?.scores || []
})

// 暴露 resize 方法供父组件 Tab 切换后调用
defineExpose({
  resize: () => {
    radarBaseChart.value?.resize()
    sankeyBaseChart.value?.resize()
    paretoBaseChart.value?.resize()
  },
})
</script>

<template>
  <div class="evaluation-panel">
    <!-- 第一行图表：雷达图 + 评价指标桑基图 -->
    <div class="charts-row">
      <div class="chart-box chart-box-left">
        <BaseChart ref="radarBaseChart" :option="radarOption" class="chart-container chart-container-eva" />
      </div>
      <div class="chart-box chart-box-right">
        <BaseChart ref="sankeyBaseChart" :option="sankeyOption" class="chart-container chart-container-eva" />
      </div>
    </div>

    <!-- 第二行图表：帕累托曲线 + 评价算法排名分析 -->
    <div class="charts-row">
      <div class="chart-box chart-box-left">
        <BaseChart ref="paretoBaseChart" :option="paretoOption" class="chart-container chart-container-eva-sm" />
      </div>
      <div class="chart-box chart-box-right">
        <div class="ranking-table-wrap eva-ranking-table">
          <el-table
            :data="rankingData.data"
            stripe
            size="small"
            style="width: 100%"
            :header-cell-style="{
              color: 'var(--tech-text-primary)',
              borderBottom: '1px solid rgba(50, 150, 255, 0.15)',
              fontSize: '11px',
              fontWeight: 600,
              padding: '2px 8px',
            }"
            :cell-style="{
              background: 'transparent',
              color: 'var(--tech-text-regular)',
              borderBottom: '1px solid rgba(50, 150, 255, 0.08)',
              fontSize: '11px',
              padding: '4px 8px',
            }"
          >
            <el-table-column prop="rank" label="排名" width="50" />
            <el-table-column prop="algorithm" label="评价算法" min-width="130" />
            <el-table-column v-for="score in rankingColumns" :key="score.plan" :label="score.plan" min-width="100">
              <template #default="{ row }">
                <div class="score-cell">
                  <span class="score-value">{{ row.scores.find((s: any) => s.plan === score.plan)?.value.toFixed(3) }}</span>
                  <div class="score-bar-bg">
                    <div
                      class="score-bar-fill"
                      :style="{ width: (row.scores.find((s: any) => s.plan === score.plan)?.value * 100).toFixed(1) + '%' }"
                    ></div>
                  </div>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.evaluation-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

/* ===== 图表行 ===== */
.charts-row {
  display: flex;
  gap: 0;
  flex-shrink: 0;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.08);
}
.charts-row:last-child {
  border-bottom: none;
}

.chart-box {
  display: flex;
  flex-direction: column;
  background: transparent;
  border: none;
  border-radius: 0;
  overflow: hidden;
}
.chart-box-left {
  flex: 4;
  min-width: 0;
}
.chart-box-right {
  flex: 6;
  min-width: 0;
}
.chart-container {
  flex: 1;
  width: 100%;
  min-height: 0;
}
.chart-container-eva {
  min-height: 280px;
}
.chart-container-eva-sm {
  min-height: 200px;
}

/* ===== 排名表格 ===== */
.ranking-table-wrap {
  flex: 1;
  overflow: auto;
  padding: 4px;
}
:deep(.el-table) {
  --el-table-border-color: transparent;
  background: transparent;
  border: none;
}
:deep(.el-table thead tr) {
  height: 28px;
}
:deep(.el-table thead th) {
  padding: 0 8px;
}

.score-cell {
  align-items: center;
  gap: 6px;
  width: 100%;
}
.score-value {
  font-size: 10px;
  color: var(--tech-text-regular);
  min-width: 38px;
  font-family: monospace;
}
.score-bar-bg {
  flex: 1;
  height: 5px;
  background: rgba(50, 150, 255, 0.12);
  border-radius: 3px;
  overflow: hidden;
  min-width: 30px;
}
.score-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #0088cc, var(--tech-blue));
  border-radius: 3px;
  transition: width 0.4s ease;
}
</style>

<!-- 非 scoped 样式：确保表头背景透明，透出 tr 背景色 -->
<style>
.eva-ranking-table .el-table {
  --el-table-header-bg-color: transparent !important;
}
.eva-ranking-table .el-table thead th.el-table__cell {
  background-color: transparent !important;
}
</style>
