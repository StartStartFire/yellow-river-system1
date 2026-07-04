<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import BaseChart from '@/components/chart/BaseChart.vue'
import { SERIES_COLORS } from '@/utils/chart'
import type { DistributionItem } from '@/types/model'

interface Props {
  estimatedTime: string
  totalCount: number
  planCount: number
  modelChartOption: EChartsOption
  algoChartOption: EChartsOption
  modelDist: DistributionItem[]
  algoDist: DistributionItem[]
}

defineProps<Props>()
</script>

<template>
  <div class="info-section">
    <!-- 时间预估 -->
    <div class="card info-card">
      <div class="card-header info-card-header">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
          <circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.3"/>
          <path d="M8 5v3.5H11" stroke="currentColor" stroke-width="1.3"/>
        </svg>
        <span class="card-title">时间预估</span>
      </div>
      <div class="card-body info-card-body">
        <div class="time-display">{{ estimatedTime }}</div>
        <div class="time-label">预计总运行时间</div>
      </div>
    </div>

    <!-- 方案数量 -->
    <div class="card info-card">
      <div class="card-header info-card-header">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
          <rect x="2" y="3" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="9" y="3" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="2" y="10" width="5" height="3" rx="1" stroke="currentColor" stroke-width="1.3"/>
          <rect x="9" y="10" width="5" height="3" rx="1" stroke="currentColor" stroke-width="1.3"/>
        </svg>
        <span class="card-title">方案数量</span>
      </div>
      <div class="card-body info-card-body">
        <div class="plan-count-display">
          <span class="plan-count-num">{{ totalCount }}</span>
          <span class="plan-count-unit"> 个</span>
        </div>
        <div class="plan-count-label">已配置方案总数</div>
      </div>
    </div>

    <!-- 模型分布 -->
    <div class="card info-card chart-card">
      <div class="card-header info-card-header">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
          <rect x="2" y="10" width="3" height="4" rx="0.5" fill="currentColor"/>
          <rect x="6.5" y="6" width="3" height="8" rx="0.5" fill="currentColor"/>
          <rect x="11" y="3" width="3" height="11" rx="0.5" fill="currentColor"/>
        </svg>
        <span class="card-title">模型分布</span>
      </div>
      <div class="card-body">
        <div class="chart-legend-row">
          <BaseChart :option="modelChartOption" class="mini-donut" />
          <div class="legend-list">
            <div v-for="(item, i) in modelDist" :key="item.name" class="legend-item">
              <span class="legend-dot" :style="{ background: SERIES_COLORS[i % SERIES_COLORS.length] }"></span>
              <span class="legend-name">{{ item.name }}</span>
              <span class="legend-detail">{{ item.value }}个（{{ item.percent }}%）</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 算法分布 -->
    <div class="card info-card chart-card">
      <div class="card-header info-card-header">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
          <path d="M2 12l4-6 3 3 5-5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="3" cy="13" r="1" fill="currentColor"/>
          <circle cx="7" cy="7" r="1" fill="currentColor"/>
          <circle cx="13" cy="4" r="1" fill="currentColor"/>
        </svg>
        <span class="card-title">算法分布</span>
      </div>
      <div class="card-body">
        <div class="chart-legend-row">
          <BaseChart :option="algoChartOption" class="mini-donut" />
          <div class="legend-list">
            <div v-for="(item, i) in algoDist" :key="item.name" class="legend-item">
              <span class="legend-dot" :style="{ background: SERIES_COLORS[i % SERIES_COLORS.length] }"></span>
              <span class="legend-name">{{ item.name }}</span>
              <span class="legend-detail">{{ item.value }}个（{{ item.percent }}%）</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.info-section {
  width: 240px;
  min-width: 240px;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow-y: auto;
  padding-right: 2px;
}

.info-section::-webkit-scrollbar {
  width: 3px;
}

.info-section::-webkit-scrollbar-track {
  background: transparent;
}

.info-section::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.2);
  border-radius: 2px;
}

.card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}

.card-icon {
  color: var(--tech-cyan);
  flex-shrink: 0;
}

.card-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--tech-text-primary);
}

.card-body {
  padding: 12px 16px;
  flex: 1;
}

.info-card-header {
  padding: 8px 12px;
}

.info-card-body {
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.info-card {
  flex-shrink: 0;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
}

.info-card.chart-card {
  flex: 1;
  min-height: 0;
}

.info-card.chart-card .card-body {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 8px 12px;
}

.time-display {
  font-size: 22px;
  font-weight: 700;
  color: var(--tech-text-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: 1px;
}

.time-label {
  font-size: 11px;
  color: var(--tech-text-placeholder);
}

.plan-count-display {
  display: flex;
  align-items: baseline;
}

.plan-count-num {
  font-size: 28px;
  font-weight: 700;
  color: var(--tech-text-primary);
}

.plan-count-unit {
  font-size: 14px;
  color: var(--tech-text-secondary);
}

.plan-count-label {
  font-size: 11px;
  color: var(--tech-text-placeholder);
}

.chart-legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 100%;
}

.mini-donut {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.legend-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
}

.legend-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-name {
  color: var(--tech-text-regular);
  white-space: nowrap;
}

.legend-detail {
  color: var(--tech-text-placeholder);
  white-space: nowrap;
  margin-left: auto;
}
</style>
