<script setup lang="ts">
/**
 * CaseDetailPanel — 案例库右侧详情容器
 *
 * 由 detail-header / detail-tabs / detail-content / metrics-section / detail-footer 组成。
 * 内部按 activeTab 切换显示 4 个 tab 内容（配置摘要 / 历史结果摘要 / 过程预览 / 评价结论）。
 * 持有 waterLevelOption、outflowOption、powerOption 三个 ECharts option computed。
 *
 * 业务事件通过 emits 抛给父组件处理：
 * favorite / export / view-report / compare / reproduce / tab-change
 */
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'
import { ElMessage } from 'element-plus'
import BaseChart from '@/components/chart/BaseChart.vue'
import CaseMetricsSection from '@/components/case-library/CaseMetricsSection.vue'
import {
  TEXT_PRIMARY,
  TECH_CYAN,
  baseTooltip,
  baseCategoryXAxis,
  baseValueYAxis,
  createGrid,
  createAreaGradient,
} from '@/utils/chart'
import { getScoreColor } from '@/utils/caseLibrary'

const props = defineProps<{
  caseData: any
  activeTab: string
  isFavorited: boolean
}>()

const emit = defineEmits<{
  (e: 'favorite'): void
  (e: 'export'): void
  (e: 'view-report'): void
  (e: 'compare'): void
  (e: 'reproduce'): void
  (e: 'tab-change', tab: string): void
}>()

const tabs = [
  { key: 'config-summary', label: '配置摘要' },
  { key: 'history-result', label: '历史结果摘要' },
  { key: 'process-preview', label: '过程预览' },
  { key: 'evaluation', label: '评价结论' },
]

const handleFavorite = () => emit('favorite')
const handleExport = () => emit('export')
const handleViewReport = () => emit('view-report')
const handleCompare = () => emit('compare')
const handleReproduce = () => emit('reproduce')
const handleTabChange = (tab: string) => emit('tab-change', tab)

const handleRename = () => ElMessage.info('重命名功能开发中')
const handleCopy = () => ElMessage.info('复制案例功能开发中')
const handleDelete = () => ElMessage.info('删除功能开发中')

const showMetrics = computed(() =>
  props.activeTab === 'config-summary' || props.activeTab === 'history-result'
)

const waterLevelOption = computed<EChartsOption>(() => {
  if (!props.caseData) return {}
  const data = props.caseData.processCharts.waterLevel
  const color = TECH_CYAN
  return {
    backgroundColor: 'transparent',
    title: {
      text: data.title,
      textStyle: { color: TEXT_PRIMARY, fontSize: 12, fontWeight: 500 },
      left: 0, top: 0,
    },
    grid: createGrid(35, 25, 50, 15),
    tooltip: { ...baseTooltip },
    xAxis: { ...baseCategoryXAxis, data: data.times },
    yAxis: { ...baseValueYAxis, name: data.unit },
    series: [{
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: data.data,
      lineStyle: { color, width: 2 },
      itemStyle: { color },
      areaStyle: createAreaGradient(color, 0.3, 0),
    }],
  }
})

const outflowOption = computed<EChartsOption>(() => {
  if (!props.caseData) return {}
  const data = props.caseData.processCharts.outflow
  const color = '#00ff88'
  return {
    backgroundColor: 'transparent',
    title: {
      text: data.title,
      textStyle: { color: TEXT_PRIMARY, fontSize: 12, fontWeight: 500 },
      left: 0, top: 0,
    },
    grid: createGrid(35, 25, 50, 15),
    tooltip: { ...baseTooltip },
    xAxis: { ...baseCategoryXAxis, data: data.times },
    yAxis: { ...baseValueYAxis, name: data.unit },
    series: [{
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: data.data,
      lineStyle: { color, width: 2 },
      itemStyle: { color },
      areaStyle: createAreaGradient(color, 0.3, 0),
    }],
  }
})

const powerOption = computed<EChartsOption>(() => {
  if (!props.caseData) return {}
  const data = props.caseData.processCharts.power
  const color = '#b37feb'
  return {
    backgroundColor: 'transparent',
    title: {
      text: data.title,
      textStyle: { color: TEXT_PRIMARY, fontSize: 12, fontWeight: 500 },
      left: 0, top: 0,
    },
    grid: createGrid(35, 25, 50, 15),
    tooltip: { ...baseTooltip },
    xAxis: { ...baseCategoryXAxis, data: data.times },
    yAxis: { ...baseValueYAxis, name: data.unit },
    series: [{
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      data: data.data,
      lineStyle: { color, width: 2 },
      itemStyle: { color },
      areaStyle: createAreaGradient(color, 0.3, 0),
    }],
  }
})
</script>

<template>
  <div class="case-detail-panel" v-if="caseData">
    <!-- 顶部操作栏 -->
    <div class="detail-header">
      <div class="header-left">
        <h2 class="detail-title">{{ caseData.title }}</h2>
        <div class="detail-meta">
          <span class="meta-tag" :style="{ background: caseData.tagColor + '20', color: caseData.tagColor, borderColor: caseData.tagColor + '40' }">
            {{ caseData.tag }}
          </span>
          <span class="meta-status" :style="{ color: caseData.statusColor }">{{ caseData.status }}</span>
          <span class="meta-score">
            综合评分：<span :style="{ color: getScoreColor(caseData.score) }">{{ caseData.score }}</span> 分（{{ caseData.scoreLevel }}）
          </span>
        </div>
        <div class="detail-info">
          <span>创建时间：{{ caseData.createdAt }}</span>
          <span>创建人：{{ caseData.creator }}</span>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-outline-sm" @click="handleFavorite">
          <svg class="w-4 h-4" :fill="isFavorited ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          {{ isFavorited ? '已收藏' : '收藏' }}
        </button>
        <button class="btn-outline-sm" @click="handleExport">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          导出报告
        </button>
        <el-dropdown trigger="click">
          <button class="btn-outline-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
            </svg>
            更多
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleRename">重命名</el-dropdown-item>
              <el-dropdown-item @click="handleCopy">复制案例</el-dropdown-item>
              <el-dropdown-item @click="handleCompare">加入对比</el-dropdown-item>
              <el-dropdown-item divided @click="handleDelete">删除案例</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 页签区 -->
    <div class="detail-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="handleTabChange(tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 页签内容 -->
    <div class="detail-content">
      <!-- 配置摘要 -->
      <div v-if="activeTab === 'config-summary'" class="tab-content">
        <div class="config-grid">
          <div class="config-section">
            <h4 class="section-title">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              基础信息
            </h4>
            <div class="config-items">
              <div class="config-item">
                <span class="item-label">调度周期</span>
                <span class="item-value">{{ caseData.configSummary.period }}</span>
              </div>
              <div class="config-item">
                <span class="item-label">涉及水库</span>
                <span class="item-value">{{ caseData.configSummary.reservoirs }}</span>
              </div>
              <div class="config-item">
                <span class="item-label">调度目标</span>
                <span class="item-value">{{ caseData.configSummary.objective }}</span>
              </div>
              <div class="config-item">
                <span class="item-label">约束条件</span>
                <span class="item-value">{{ caseData.configSummary.constraints }}</span>
              </div>
            </div>
          </div>
          <div class="config-section">
            <h4 class="section-title">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              模型与算法
            </h4>
            <div class="config-items">
              <div class="config-item">
                <span class="item-label">模型类型</span>
                <span class="item-value highlight">{{ caseData.configSummary.modelType }}</span>
              </div>
              <div class="config-item">
                <span class="item-label">优化算法</span>
                <span class="item-value highlight">{{ caseData.configSummary.algorithm }}</span>
              </div>
              <div class="config-item">
                <span class="item-label">种群规模</span>
                <span class="item-value">{{ caseData.configSummary.population }}</span>
              </div>
              <div class="config-item">
                <span class="item-label">迭代次数</span>
                <span class="item-value">{{ caseData.configSummary.iterations }}</span>
              </div>
              <div class="config-item">
                <span class="item-label">模型版本</span>
                <span class="item-value version">{{ caseData.configSummary.modelVersion }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史结果摘要 -->
      <div v-if="activeTab === 'history-result'" class="tab-content">
        <div class="result-summary">
          <p class="summary-text">{{ caseData.historyResult.summary }}</p>
          <div class="key-findings">
            <h4 class="findings-title">关键发现</h4>
            <ul class="findings-list">
              <li v-for="(finding, index) in caseData.historyResult.keyFindings" :key="index">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                {{ finding }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 过程预览 -->
      <div v-if="activeTab === 'process-preview'" class="tab-content">
        <div class="preview-charts">
          <div class="chart-box">
            <div class="chart-container">
              <BaseChart :option="waterLevelOption" />
            </div>
          </div>
          <div class="chart-box">
            <div class="chart-container">
              <BaseChart :option="outflowOption" />
            </div>
          </div>
          <div class="chart-box">
            <div class="chart-container">
              <BaseChart :option="powerOption" />
            </div>
          </div>
        </div>
      </div>

      <!-- 评价结论 -->
      <div v-if="activeTab === 'evaluation'" class="tab-content">
        <div class="evaluation-content">
          <div class="evaluation-score">
            <div class="score-circle" :style="{ borderColor: getScoreColor(caseData.evaluation.overall) }">
              <span class="score-value" :style="{ color: getScoreColor(caseData.evaluation.overall) }">{{ caseData.evaluation.overall }}</span>
              <span class="score-label">综合评分</span>
            </div>
          </div>
          <div class="evaluation-dimensions">
            <div v-for="dim in caseData.evaluation.dimensions" :key="dim.name" class="dimension-item">
              <div class="dimension-header">
                <span class="dimension-name">{{ dim.name }}</span>
                <span class="dimension-score" :style="{ color: getScoreColor(dim.score) }">{{ dim.score }}分</span>
              </div>
              <div class="dimension-bar">
                <div class="dimension-progress" :style="{ width: dim.score + '%', background: getScoreColor(dim.score) }"></div>
              </div>
              <span class="dimension-weight">权重 {{ (dim.weight * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 关键指标区 -->
    <CaseMetricsSection v-if="showMetrics" :metrics="caseData.metrics" />

    <!-- 底部操作栏 -->
    <div class="detail-footer">
      <button class="btn-secondary" @click="handleViewReport">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        查看详细报告
      </button>
      <button class="btn-secondary" @click="handleCompare">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        对比分析
      </button>
      <button class="btn-primary" @click="handleReproduce">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        复现案例
      </button>
    </div>
  </div>
</template>

<style scoped>
.case-detail-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: transparent;
  border: none;
  border-radius: 0;
  overflow: hidden;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
}

.header-left {
  flex: 1;
}

.detail-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--tech-text-primary);
  margin: 0 0 8px 0;
}

.detail-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.meta-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid;
  font-weight: 500;
}

.meta-status {
  font-size: 12px;
  font-weight: 500;
}

.meta-score {
  font-size: 12px;
  color: var(--tech-text-secondary);
}

.detail-info {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--tech-text-secondary);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-outline-sm {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: transparent;
  border: 1px solid rgba(50, 150, 255, 0.25);
  border-radius: 4px;
  color: var(--tech-text-secondary);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-outline-sm:hover {
  background: rgba(50, 150, 255, 0.1);
  color: var(--tech-text-primary);
  border-color: rgba(50, 150, 255, 0.4);
}

/* 页签区 */
.detail-tabs {
  display: flex;
  gap: 0;
  padding: 0 16px;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  background: transparent;
}

.tab-btn {
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  border-radius: 0;
  color: var(--tech-text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  color: var(--tech-text-primary);
  background: transparent;
}

.tab-btn.active {
  color: var(--tech-cyan);
  background: transparent;
  border-bottom-color: rgba(var(--tech-cyan-rgb), 0.6);
}

/* 页签内容 */
.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.tab-content {
  height: 100%;
}

/* 配置摘要 */
.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  height: 100%;
}

.config-section {
  background: transparent;
  border: none;
  border-right: 1px solid rgba(var(--tech-blue-rgb), 0.08);
  border-radius: 0;
  padding: 12px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--tech-cyan);
  margin: 0 0 12px 0;
}

.config-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-label {
  font-size: 11px;
  color: var(--tech-text-secondary);
}

.item-value {
  font-size: 12px;
  color: var(--tech-text-primary);
  line-height: 1.5;
}

.item-value.highlight {
  color: var(--tech-cyan);
  font-weight: 500;
}

.item-value.version {
  font-family: monospace;
  background: rgba(var(--tech-blue-rgb), 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}

/* 历史结果摘要 */
.result-summary {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-text {
  font-size: 13px;
  color: var(--tech-text-primary);
  line-height: 1.6;
  margin: 0;
}

.key-findings {
  background: transparent;
  border: none;
  border-top: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  border-radius: 0;
  padding: 12px;
}

.findings-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--tech-cyan);
  margin: 0 0 10px 0;
}

.findings-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.findings-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--tech-text-primary);
}

.findings-list li svg {
  color: #00ff88;
  flex-shrink: 0;
}

/* 过程预览 */
.preview-charts {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  height: 100%;
  min-height: 280px;
}

.chart-box {
  background: transparent;
  border: none;
  border-right: 1px solid rgba(var(--tech-blue-rgb), 0.08);
  border-radius: 0;
  padding: 12px;
}

.chart-container {
  width: 100%;
  height: 250px;
}

/* 评价结论 */
.evaluation-content {
  display: flex;
  gap: 24px;
  height: 100%;
}

.evaluation-score {
  flex-shrink: 0;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: transparent;
}

.score-value {
  font-size: 32px;
  font-weight: 700;
}

.score-label {
  font-size: 11px;
  color: var(--tech-text-secondary);
}

.evaluation-dimensions {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  justify-content: center;
}

.dimension-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dimension-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dimension-name {
  font-size: 12px;
  color: var(--tech-text-primary);
}

.dimension-score {
  font-size: 12px;
  font-weight: 600;
}

.dimension-bar {
  height: 6px;
  background: rgba(50, 150, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.dimension-progress {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s;
}

.dimension-weight {
  font-size: 10px;
  color: var(--tech-text-secondary);
}

/* 底部操作栏 */
.detail-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 16px;
  border-top: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  background: transparent;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: linear-gradient(135deg, var(--tech-blue) 0%, var(--tech-cyan) 100%);
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--tech-cyan) 0%, var(--tech-cyan-light) 100%);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: rgba(50, 150, 255, 0.1);
  border: 1px solid rgba(50, 150, 255, 0.3);
  border-radius: 6px;
  color: var(--tech-cyan);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(50, 150, 255, 0.2);
  border-color: rgba(50, 150, 255, 0.5);
}
</style>
