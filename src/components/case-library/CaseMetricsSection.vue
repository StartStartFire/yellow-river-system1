<script setup lang="ts">
/**
 * CaseMetricsSection — 案例库右侧详情区「关键指标」区
 *
 * 纯展示组件：根据 metrics 数组渲染指标卡片网格，
 * 变化颜色由 getChangeColor 决定。
 */
import { getChangeColor } from '@/utils/caseLibrary'

defineProps<{
  metrics: any[]
}>()
</script>

<template>
  <div class="metrics-section">
    <h4 class="metrics-title">关键指标（历史结果）</h4>
    <div class="metrics-grid">
      <div v-for="metric in metrics" :key="metric.name" class="metric-card">
        <span class="metric-name">{{ metric.name }}</span>
        <span class="metric-value">{{ metric.value }}</span>
        <span class="metric-change" :style="{ color: getChangeColor(metric.changeType) }">
          {{ metric.baseline }} {{ metric.change }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.metrics-section {
  padding: 12px 16px;
  border-top: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  background: transparent;
}

.metrics-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--tech-text-secondary);
  margin: 0 0 10px 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.metric-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
  background: transparent;
  border: none;
  border-right: 1px solid rgba(var(--tech-blue-rgb), 0.08);
  border-radius: 0;
}

.metric-name {
  font-size: 10px;
  color: var(--tech-text-secondary);
}

.metric-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--tech-text-primary);
}

.metric-change {
  font-size: 10px;
  font-weight: 500;
}
</style>
