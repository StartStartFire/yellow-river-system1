<script setup lang="ts">
/**
 * EvaluationPanel — 评价分析面板
 *
 * 包含 4 个图表区域：子系统得分雷达图 + 评价指标桑基图 + 算法收敛曲线 + 评价算法排名表格。
 * 排名表格采用行转置形式：行=方案（前 10 个体），列=各算法得分+整合排名。
 */
import { ref, computed } from 'vue'
import * as echarts from 'echarts'
import BaseChart from '@/components/chart/BaseChart.vue'
import { formatScore, formatPercent } from '@/utils/format'

interface Props {
  /** 雷达图 option（AHP-Fuzzy 子系统得分） */
  radarOption: echarts.EChartsOption
  /** 评价指标桑基图 option */
  sankeyOption: echarts.EChartsOption
  /** 算法收敛曲线 option（原帕累托） */
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

/** 算法名称列表（列头），排除 ALL */
const algoColumns = computed(() => {
  if (!props.rankingData?.data) return []
  return props.rankingData.data
    .filter((r: any) => r.algorithm !== 'ALL 序号总和整合')
    .map((r: any) => r.algorithm)
})

/** ALL 行（整合排名） */
const allRow = computed(() => {
  if (!props.rankingData?.data) return null
  return props.rankingData.data.find((r: any) => r.algorithm === 'ALL 序号总和整合') || null
})

/** 前 10 个方案的方案名列表（按勾选筛选） */
const planNames = computed(() => {
  if (!props.rankingData?.data?.[0]?.scores) return []
  const allNames = props.rankingData.data[0].scores.map((s: any) => s.plan)
  const idx = allNames
    .map((name: string, i: number) => (props.selectedPlanLabels.includes(name) ? i : -1))
    .filter((i: number) => i >= 0)
  return idx.map((i: number) => allNames[i])
})

/** 获取某个方案在某算法下的得分 */
const getScore = (algorithm: string, plan: string): number | null => {
  const row = props.rankingData?.data?.find((r: any) => r.algorithm === algorithm)
  if (!row) return null
  const score = row.scores.find((s: any) => s.plan === plan)
  return score?.value ?? null
}

/** 获取某个方案的整合排名 */
const getAllRank = (plan: string): number | null => {
  if (!allRow.value) return null
  const score = allRow.value.scores.find((s: any) => s.plan === plan)
  return score?.value ?? null
}

/** 判断某方案是否被选中（用于高亮） */
const isPlanSelected = (plan: string) => props.selectedPlanLabels.includes(plan)

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

    <!-- 第二行图表：帕累托曲线 + 方案排名表（行转置） -->
    <div class="charts-row">
      <div class="chart-box chart-box-left">
        <BaseChart ref="paretoBaseChart" :key="'pareto-' + (props.paretoOption?.series as any)?.length" :option="paretoOption" class="chart-container chart-container-eva-sm" />
      </div>
      <div class="chart-box chart-box-right">
        <div class="ranking-table-wrap eva-ranking-table">
          <el-table
            :key="'rank-' + (planNames.length || 0)"
            :data="planNames"
            stripe
            size="small"
            style="width: 100%"
            class="eva-ranking-el-table"
            height="100%"
          >
            <el-table-column label="排名" width="52">
              <template #default="{ row }">
                <span class="rank-cell">{{ getAllRank(row) ? getAllRank(row) + '名' : '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="方案" min-width="60">
              <template #default="{ row }">
                <span class="plan-name" :class="{ 'plan-selected': isPlanSelected(row) }">{{ row }}</span>
              </template>
            </el-table-column>
            <el-table-column
              v-for="algo in algoColumns"
              :key="algo"
              :label="algo"
              min-width="110"
            >
              <template #default="{ row }">
                <div class="score-cell">
                  <span class="score-value">{{ formatScore(getScore(algo, row)) }}</span>
                  <div class="score-bar-bg">
                    <div
                      class="score-bar-fill"
                      :style="{ width: formatPercent(getScore(algo, row), 1) }"
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
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.08);
}
.charts-row:first-child {
  flex: 5;
  min-height: 0;
}
.charts-row:last-child {
  flex: 4;
  min-height: 0;
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

/* 排名表格特有样式 */
.eva-ranking-el-table :deep(.el-table thead tr) {
  height: 28px;
}
.eva-ranking-el-table :deep(.el-table thead th) {
  color: var(--tech-text-primary);
  border-bottom: 1px solid var(--el-border-color);
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  background: transparent;
}
.eva-ranking-el-table :deep(.el-table td) {
  background: transparent;
  color: var(--tech-text-regular);
  border-bottom: 1px solid var(--el-border-color-light);
  font-size: 11px;
  padding: 4px 8px;
}

.score-cell {
  display: flex;
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

/* 行转置排名表格：排名列 */
.rank-cell {
  font-size: 12px;
  font-weight: 600;
  color: var(--tech-cyan);
  font-family: monospace;
}

/* 方案名称列 */
.plan-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--tech-text-regular);
}
.plan-name.plan-selected {
  color: var(--tech-blue);
  font-weight: 600;
}

/* 得分进度条 */
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
