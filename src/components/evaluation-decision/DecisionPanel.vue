<script setup lang="ts">
/**
 * DecisionPanel — 决策分析面板
 *
 * 包含顶部控件（方案选择 + 导出）+ 三列布局：
 *   左列：目标满足情况
 *   中列：过程曲线（水位/流量/出力切换）
 *   右列：水量使用流向图
 */
import { ref } from 'vue'
import * as echarts from 'echarts'
import BaseChart from '@/components/chart/BaseChart.vue'
import { formatPercent } from '@/utils/format'

interface PlanOption {
  label: string
  value: string
}

interface ProcessTabOption {
  key: string
  label: string
}

interface Props {
  /** 全部可选方案列表 */
  plans: PlanOption[]
  /** 当前决策方案 value */
  currentPlan: string
  /** 目标满足情况数据 */
  targets: any[]
  /** 过程曲线 option */
  processOption: echarts.EChartsOption
  /** 过程曲线页签选项 */
  processTabOptions: ProcessTabOption[]
  /** 当前激活的过程曲线页签 key */
  activeProcessTab: string
  /** 水量使用流向图 option */
  waterFlowOption: echarts.EChartsOption
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:currentPlan', value: string): void
  (e: 'update:activeProcessTab', value: string): void
  (e: 'export-plan'): void
}>()

// ========== BaseChart refs（供父组件统一 resize） ==========
const processBaseChart = ref<InstanceType<typeof BaseChart> | null>(null)
const waterFlowBaseChart = ref<InstanceType<typeof BaseChart> | null>(null)

const handlePlanChange = (val: string) => {
  emit('update:currentPlan', val)
}

const handleProcessTabChange = (key: string) => {
  emit('update:activeProcessTab', key)
}

const handleExport = () => {
  emit('export-plan')
}

// 暴露 resize 方法供父组件 Tab 切换后调用
defineExpose({
  resize: () => {
    processBaseChart.value?.resize()
    waterFlowBaseChart.value?.resize()
  },
})
</script>

<template>
  <div class="decision-panel">
    <!-- 顶部控件 -->
    <div class="decision-top-bar">
      <div class="decision-selector">
        <span class="selector-label">当前决策方案：</span>
        <el-select
          :model-value="currentPlan"
          size="small"
          style="width: 140px;"
          @update:model-value="handlePlanChange"
        >
          <el-option
            v-for="plan in plans"
            :key="plan.value"
            :value="plan.value"
            :label="plan.label"
          />
        </el-select>
      </div>
      <button class="export-btn" @click="handleExport">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="margin-right: 4px;">
          <path d="M7 1L7 9M7 1L4 4M7 1L10 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M1 10V12C1 12.5523 1.44772 13 2 13H12C12.5523 13 13 12.5523 13 12V10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        导出方案
      </button>
    </div>

    <!-- 三列布局 -->
    <div class="decision-body">
      <!-- 左列：目标满足情况 -->
      <div class="decision-col decision-col-left">
        <div class="sub-chart-box">
          <div class="sub-chart-title">目标满足情况</div>
          <div class="target-list">
            <div v-for="(target, i) in targets" :key="i" class="target-item">
              <div class="target-icon" :class="target.status === '已满足' ? 'icon-satisfied' : target.status === '基本满足' ? 'icon-basic' : 'icon-unsatisfied'">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.2"/>
                  <path d="M4.5 7L6.5 9L9.5 5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="target-info">
                <div class="target-name">{{ target.name }}</div>
                <div class="target-status" :class="{
                  'text-green': target.status === '已满足',
                  'text-yellow': target.status === '基本满足',
                  'text-red': target.status === '未满足',
                }">{{ target.status }}</div>
              </div>
              <div class="target-progress-wrap">
                <div class="target-progress-bg">
                  <div
                    class="target-progress-fill"
                    :class="{
                      'fill-green': target.status === '已满足',
                      'fill-yellow': target.status === '基本满足',
                      'fill-red': target.status === '未满足',
                    }"
                    :style="{ width: Math.min(target.rate, 100) + '%' }"
                  ></div>
                </div>
                <span class="target-rate">{{ formatPercent(target.rate, 1) }}</span>
              </div>
            </div>
          </div>
          <div class="target-footnote">完成率 = 实际值 / 目标值 × 100%</div>
        </div>
      </div>

      <!-- 中列：过程曲线 -->
      <div class="decision-col decision-col-center">
        <div class="sub-chart-box">
          <!-- 内部页签 -->
          <div class="process-tabs">
            <button
              v-for="tab in processTabOptions"
              :key="tab.key"
              class="process-tab-btn"
              :class="{ active: activeProcessTab === tab.key }"
              @click="handleProcessTabChange(tab.key)"
            >{{ tab.label }}</button>
          </div>
          <BaseChart ref="processBaseChart" :option="processOption" class="chart-container chart-container-process" />
        </div>
      </div>

      <!-- 右列：水量使用流向图 -->
      <div class="decision-col decision-col-right">
        <div class="sub-chart-box">
          <BaseChart ref="waterFlowBaseChart" :option="waterFlowOption" class="chart-container" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.decision-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

/* ===== 决策分析顶部 ===== */
.decision-top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
  flex-shrink: 0;
}
.decision-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}
.selector-label {
  font-size: 12px;
  color: var(--tech-text-secondary);
  white-space: nowrap;
}

/* 导出按钮 */
.export-btn {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 500;
  color: var(--tech-blue);
  background: rgba(var(--tech-blue-rgb), 0.1);
  border: 1px solid rgba(var(--tech-blue-rgb), 0.4);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.export-btn:hover {
  background: rgba(var(--tech-blue-rgb), 0.2);
  border-color: rgba(var(--tech-blue-rgb), 0.6);
  box-shadow: 0 0 12px rgba(0, 160, 255, 0.15);
}

/* ===== 决策分析三列布局 ===== */
.decision-body {
  display: flex;
  gap: 0;
  flex: 1;
  min-height: 0;
}
.decision-col {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}
.decision-col-left {
  flex: 32;
}
.decision-col-center {
  flex: 33;
  border-left: 1px solid rgba(var(--tech-blue-rgb), 0.08);
}
.decision-col-right {
  flex: 35;
  border-left: 1px solid rgba(var(--tech-blue-rgb), 0.08);
}

/* ===== 子图表盒子 ===== */
.sub-chart-box {
  display: flex;
  flex-direction: column;
  background: transparent;
  border: none;
  border-radius: 0;
  overflow: hidden;
  flex: 1;
  min-height: 0;
}
.sub-chart-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--tech-text-secondary);
  padding: 6px 10px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.1);
  letter-spacing: 0.3px;
  flex-shrink: 0;
}

/* ===== 目标满足情况 ===== */
.target-list {
  padding: 6px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-height: 0;
  justify-content: space-evenly;
}
.target-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.target-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  flex-shrink: 0;
}
.icon-satisfied {
  color: #00ff88;
  background: rgba(var(--tech-green-rgb), 0.1);
}
.icon-basic {
  color: var(--tech-orange);
  background: rgba(255, 170, 0, 0.1);
}
.icon-unsatisfied {
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.1);
}
.target-info {
  display: flex;
  flex-direction: column;
  min-width: 72px;
  flex-shrink: 0;
}
.target-name {
  font-size: 12px;
  color: var(--tech-text-regular);
  font-weight: 500;
}
.target-status {
  font-size: 10px;
}
.text-green { color: #00ff88; }
.text-yellow { color: var(--tech-orange); }
.text-red { color: #ff4d4f; }

.target-progress-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}
.target-progress-bg {
  flex: 1;
  height: 6px;
  background: rgba(50, 150, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}
.target-progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.6s ease;
}
.fill-green { background: linear-gradient(90deg, #00cc66, #00ff88); }
.fill-yellow { background: linear-gradient(90deg, #dd8800, var(--tech-orange)); }
.fill-red { background: linear-gradient(90deg, #cc3333, #ff4d4f); }

.target-rate {
  font-size: 11px;
  color: var(--tech-text-regular);
  font-weight: 600;
  min-width: 48px;
  text-align: right;
  font-family: monospace;
}

.target-footnote {
  font-size: 10px;
  color: var(--tech-text-placeholder);
  padding: 4px 10px 6px;
  border-top: 1px solid rgba(50, 150, 255, 0.08);
  flex-shrink: 0;
}

/* ===== 过程曲线页签 ===== */
.process-tabs {
  display: flex;
  gap: 2px;
  padding: 4px 8px 0;
  flex-shrink: 0;
}
.process-tab-btn {
  flex: 1;
  padding: 4px 0;
  font-size: 11px;
  font-weight: 500;
  border: 1px solid rgba(50, 150, 255, 0.2);
  border-radius: 4px 4px 0 0;
  background: rgba(6, 30, 70, 0.5);
  color: var(--tech-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}
.process-tab-btn:hover {
  color: var(--tech-text-regular);
  background: rgba(6, 30, 70, 0.8);
  border-color: rgba(50, 150, 255, 0.35);
}
.process-tab-btn.active {
  color: var(--tech-blue);
  background: rgba(var(--tech-blue-rgb), 0.08);
  border-color: rgba(var(--tech-blue-rgb), 0.4);
  border-bottom-color: transparent;
}

/* ===== 图表容器 ===== */
.chart-container {
  flex: 1;
  width: 100%;
  min-height: 0;
}
.chart-container-process {
  flex: 1;
  min-height: 0;
}
</style>
