<script setup lang="ts">
/**
 * DataContentPanel — 模型数据右侧内容面板
 *
 * 根据 content.type 渲染图表（BaseChart）或表格（el-table）。
 * 标题取自 content.chartData.title 或 content.tableData.title。
 */
import { computed } from 'vue'
import type * as echarts from 'echarts'
import BaseChart from '@/components/chart/BaseChart.vue'
import type { MenuContent } from '@/types/model'

interface Props {
  /** 当前菜单内容（含 type / chartData / tableData） */
  content: MenuContent | undefined
  /** 图表配置（仅 chart 类型时使用） */
  chartOption: echarts.EChartsOption
}

const props = defineProps<Props>()

const isChartType = computed(() => props.content?.type === 'chart')
const isTableType = computed(() => props.content?.type === 'table')

const contentTitle = computed(() => {
  if (!props.content) return ''
  if (isChartType.value && props.content.chartData) {
    return props.content.chartData.title
  }
  if (isTableType.value && props.content.tableData) {
    return props.content.tableData.title
  }
  return ''
})
</script>

<template>
  <div class="content-panel">
    <!-- 标题 -->
    <div class="content-header">
      <span class="content-title">{{ contentTitle }}</span>
    </div>

    <!-- 图表区 -->
    <div v-if="isChartType && content?.chartData" class="chart-wrapper">
      <BaseChart :option="chartOption" class="chart-container" />
    </div>

    <!-- 表格区 -->
    <div v-if="isTableType && content?.tableData" class="table-wrapper">
      <el-table
        :data="content.tableData.rows"
        stripe
        size="small"
        class="dark-table"
        style="width: 100%"
      >
        <el-table-column
          v-for="col in content.tableData.columns"
          :key="col.key"
          :prop="col.key"
          :label="col.unit ? `${col.label}（${col.unit}）` : col.label"
          min-width="120"
        />
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.content-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.content-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}

.content-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--tech-text-primary);
}

/* ===== 图表 ===== */
.chart-wrapper {
  flex: 1;
  padding: 8px 16px 16px;
  min-height: 0;
}

.chart-container {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

/* ===== 表格 ===== */
.table-wrapper {
  flex: 1;
  padding: 8px 16px 16px;
  overflow: auto;
}

.dark-table {
  width: 100%;
}
</style>
