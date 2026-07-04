<script setup lang="ts">
import { ref, computed } from 'vue'
import type { EChartsOption } from 'echarts'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import BaseChart from '@/components/chart/BaseChart.vue'
import PanelCard from '@/components/common/PanelCard.vue'
import {
  TEXT_PRIMARY,
  TEXT_SECONDARY,
  TECH_CYAN,
  TECH_ORANGE,
  baseTooltip,
  baseCategoryXAxis,
  baseValueYAxis,
  createGrid,
  createAreaGradient,
} from '@/utils/chart'
import { caseList, caseDetail, caseTypeOptions, reservoirOptions } from '@/mock/caseLibrary'

const router = useRouter()

const selectedCaseId = ref('case-2024-flood-001')
const activeTab = ref('config-summary')
const isFavorited = ref(false)

const filters = ref({
  dateRange: [] as string[],
  caseType: 'all',
  reservoir: 'all',
  keyword: '',
})

const filteredCases = computed(() => {
  return caseList.data.filter(c => {
    if (filters.value.caseType !== 'all' && !c.caseType.includes(filters.value.caseType)) return false
    if (filters.value.reservoir !== 'all' && !c.reservoirs.includes(filters.value.reservoir)) return false
    if (filters.value.keyword && !c.title.includes(filters.value.keyword) && !c.summary.includes(filters.value.keyword)) return false
    return true
  })
})

const currentCase = computed(() => {
  return caseDetail.data[selectedCaseId.value as keyof typeof caseDetail.data]
})

const selectedCase = computed(() => {
  return caseList.data.find(c => c.id === selectedCaseId.value)
})

const handleSelectCase = (id: string) => {
  selectedCaseId.value = id
  activeTab.value = 'config-summary'
  isFavorited.value = false
}

const handleReset = () => {
  filters.value = {
    dateRange: [],
    caseType: 'all',
    reservoir: 'all',
    keyword: '',
  }
}

const handleFavorite = () => {
  isFavorited.value = !isFavorited.value
  ElMessage.success(isFavorited.value ? '已收藏' : '已取消收藏')
}

const handleExport = () => {
  ElMessage.info('当前为前端原型，暂不支持真实报告导出')
}

const handleViewReport = () => {
  ElMessage.info('当前为前端原型，暂不支持查看详细报告')
}

const handleCompare = () => {
  router.push('/evaluation-decision')
}

const handleReproduce = () => {
  router.push('/model-config/model-data')
}

const handleTabChange = (tab: string) => {
  activeTab.value = tab
}

const waterLevelOption = computed<EChartsOption>(() => {
  if (!currentCase.value) return {}
  const data = currentCase.value.processCharts.waterLevel
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
  if (!currentCase.value) return {}
  const data = currentCase.value.processCharts.outflow
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
  if (!currentCase.value) return {}
  const data = currentCase.value.processCharts.power
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

const getScoreColor = (score: number) => {
  if (score >= 90) return '#00ff88'
  if (score >= 80) return TECH_CYAN
  if (score >= 70) return TECH_ORANGE
  return '#ff4d4f'
}

const getChangeColor = (type: string) => {
  if (type === 'up') return '#00ff88'
  if (type === 'down') return TECH_ORANGE
  if (type === 'success') return '#00ff88'
  if (type === 'excellent') return TECH_CYAN
  return TEXT_SECONDARY
}

const getIconByType = (type: string) => {
  const icons: Record<string, string> = {
    benefit: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    supply: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M12 2.69l5.66 5.66a8 8 0 11-11.31 0z" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    realtime: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <circle cx="12" cy="12" r="10"/>
      <path d="M12 6v6l4 2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    hybrid: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <circle cx="12" cy="12" r="4"/>
      <path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" stroke-linecap="round"/>
    </svg>`,
    flood: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M12 12v4m0 0l-2-2m2 2l2-2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    eco: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17.98.3 1.34.3C19 20 22 3 22 3c-1 2-8 2.25-13 3.25S2 11.5 2 13.5s1.75 3.75 1.75 3.75" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    drought: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M14 14.76V3.5a2.5 2.5 0 00-5 0v11.26a4.5 4.5 0 105 0z" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
  }
  return icons[type] || icons['benefit']
}
</script>

<template>
  <div class="case-library-view">
    <!-- 顶部筛选区 -->
    <div class="filter-bar">
      <div class="filter-items">
        <div class="filter-item">
          <label class="filter-label">时间范围</label>
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="~"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            class="dark-date-picker"
          />
        </div>
        <div class="filter-item">
          <label class="filter-label">案例类型</label>
          <el-select v-model="filters.caseType" class="dark-select" style="width: 140px;">
            <el-option v-for="item in caseTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </div>
        <div class="filter-item">
          <label class="filter-label">涉及水库</label>
          <el-select v-model="filters.reservoir" class="dark-select" style="width: 140px;">
            <el-option v-for="item in reservoirOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </div>
        <div class="filter-item">
          <label class="filter-label">关键词</label>
          <el-input
            v-model="filters.keyword"
            placeholder="请输入案例名称或关键词"
            class="dark-input"
            clearable
          />
        </div>
      </div>
      <div class="filter-actions">
        <button class="btn-primary">查询</button>
        <button class="btn-secondary" @click="handleReset">重置</button>
        <button class="btn-outline" @click="ElMessage.info('高级筛选功能开发中')">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          高级筛选
        </button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧案例列表 -->
      <div class="case-list-panel">
        <div class="panel-title-bar">
          <span class="title-text">案例列表</span>
          <span class="title-count">共 {{ filteredCases.length }} 条</span>
        </div>
        <div class="case-list">
          <div
            v-for="caseItem in filteredCases"
            :key="caseItem.id"
            class="case-card"
            :class="{ active: selectedCaseId === caseItem.id }"
            @click="handleSelectCase(caseItem.id)"
          >
            <div class="case-cover" :style="{ background: getCoverGradient(caseItem.cover) }">
              <div class="case-icon" v-html="getIconByType(caseItem.iconType)"></div>
              <span class="case-tag" :style="{ background: caseItem.tagColor + '20', color: caseItem.tagColor, borderColor: caseItem.tagColor + '40' }">
                {{ caseItem.tag }}
              </span>
            </div>
            <div class="case-info">
              <div class="case-header">
                <h4 class="case-title">{{ caseItem.title }}</h4>
                <span class="case-status" :style="{ color: caseItem.statusColor }">{{ caseItem.status }}</span>
              </div>
              <div class="case-meta">
                <span class="meta-item">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  {{ caseItem.reservoirs.join('、') }}
                </span>
              </div>
              <div class="case-meta">
                <span class="meta-item">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  {{ caseItem.caseType.join(' / ') }}
                </span>
                <span class="meta-item">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {{ caseItem.createdAt }}
                </span>
              </div>
              <p class="case-summary">{{ caseItem.summary }}</p>
            </div>
            <div class="case-actions">
              <button
                class="action-btn"
                :class="{ favorited: isFavorited && selectedCaseId === caseItem.id }"
                @click.stop="handleFavorite"
                title="收藏"
              >
                <svg class="w-4 h-4" :fill="isFavorited && selectedCaseId === caseItem.id ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </button>
              <button class="action-btn" @click.stop="handleSelectCase(caseItem.id)" title="查看详情">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧案例详情 -->
      <div class="case-detail-panel" v-if="currentCase">
        <!-- 顶部操作栏 -->
        <div class="detail-header">
          <div class="header-left">
            <h2 class="detail-title">{{ currentCase.title }}</h2>
            <div class="detail-meta">
              <span class="meta-tag" :style="{ background: currentCase.tagColor + '20', color: currentCase.tagColor, borderColor: currentCase.tagColor + '40' }">
                {{ currentCase.tag }}
              </span>
              <span class="meta-status" :style="{ color: currentCase.statusColor }">{{ currentCase.status }}</span>
              <span class="meta-score">
                综合评分：<span :style="{ color: getScoreColor(currentCase.score) }">{{ currentCase.score }}</span> 分（{{ currentCase.scoreLevel }}）
              </span>
            </div>
            <div class="detail-info">
              <span>创建时间：{{ currentCase.createdAt }}</span>
              <span>创建人：{{ currentCase.creator }}</span>
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
                  <el-dropdown-item @click="ElMessage.info('重命名功能开发中')">重命名</el-dropdown-item>
                  <el-dropdown-item @click="ElMessage.info('复制案例功能开发中')">复制案例</el-dropdown-item>
                  <el-dropdown-item @click="handleCompare">加入对比</el-dropdown-item>
                  <el-dropdown-item divided @click="ElMessage.info('删除功能开发中')">删除案例</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <!-- 页签区 -->
        <div class="detail-tabs">
          <button
            v-for="tab in [
              { key: 'config-summary', label: '配置摘要' },
              { key: 'history-result', label: '历史结果摘要' },
              { key: 'process-preview', label: '过程预览' },
              { key: 'evaluation', label: '评价结论' },
            ]"
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
                    <span class="item-value">{{ currentCase.configSummary.period }}</span>
                  </div>
                  <div class="config-item">
                    <span class="item-label">涉及水库</span>
                    <span class="item-value">{{ currentCase.configSummary.reservoirs }}</span>
                  </div>
                  <div class="config-item">
                    <span class="item-label">调度目标</span>
                    <span class="item-value">{{ currentCase.configSummary.objective }}</span>
                  </div>
                  <div class="config-item">
                    <span class="item-label">约束条件</span>
                    <span class="item-value">{{ currentCase.configSummary.constraints }}</span>
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
                    <span class="item-value highlight">{{ currentCase.configSummary.modelType }}</span>
                  </div>
                  <div class="config-item">
                    <span class="item-label">优化算法</span>
                    <span class="item-value highlight">{{ currentCase.configSummary.algorithm }}</span>
                  </div>
                  <div class="config-item">
                    <span class="item-label">种群规模</span>
                    <span class="item-value">{{ currentCase.configSummary.population }}</span>
                  </div>
                  <div class="config-item">
                    <span class="item-label">迭代次数</span>
                    <span class="item-value">{{ currentCase.configSummary.iterations }}</span>
                  </div>
                  <div class="config-item">
                    <span class="item-label">模型版本</span>
                    <span class="item-value version">{{ currentCase.configSummary.modelVersion }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 历史结果摘要 -->
          <div v-if="activeTab === 'history-result'" class="tab-content">
            <div class="result-summary">
              <p class="summary-text">{{ currentCase.historyResult.summary }}</p>
              <div class="key-findings">
                <h4 class="findings-title">关键发现</h4>
                <ul class="findings-list">
                  <li v-for="(finding, index) in currentCase.historyResult.keyFindings" :key="index">
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
                <div class="score-circle" :style="{ borderColor: getScoreColor(currentCase.evaluation.overall) }">
                  <span class="score-value" :style="{ color: getScoreColor(currentCase.evaluation.overall) }">{{ currentCase.evaluation.overall }}</span>
                  <span class="score-label">综合评分</span>
                </div>
              </div>
              <div class="evaluation-dimensions">
                <div v-for="dim in currentCase.evaluation.dimensions" :key="dim.name" class="dimension-item">
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
        <div class="metrics-section" v-if="activeTab === 'config-summary' || activeTab === 'history-result'">
          <h4 class="metrics-title">关键指标（历史结果）</h4>
          <div class="metrics-grid">
            <div v-for="metric in currentCase.metrics" :key="metric.name" class="metric-card">
              <span class="metric-name">{{ metric.name }}</span>
              <span class="metric-value">{{ metric.value }}</span>
              <span class="metric-change" :style="{ color: getChangeColor(metric.changeType) }">
                {{ metric.baseline }} {{ metric.change }}
              </span>
            </div>
          </div>
        </div>

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
    </div>
  </div>
</template>

<script lang="ts">
function getCoverGradient(type: string): string {
  const gradients: Record<string, string> = {
    'flood-control': 'linear-gradient(135deg, rgba(0, 175, 255, 0.25) 0%, rgba(0, 229, 255, 0.08) 100%)',
    'drought': 'linear-gradient(135deg, rgba(255, 170, 0, 0.25) 0%, rgba(255, 200, 0, 0.08) 100%)',
    'realtime': 'linear-gradient(135deg, rgba(255, 77, 79, 0.25) 0%, rgba(255, 100, 100, 0.08) 100%)',
    'hybrid': 'linear-gradient(135deg, rgba(179, 127, 235, 0.25) 0%, rgba(180, 130, 240, 0.08) 100%)',
    'autumn-flood': 'linear-gradient(135deg, rgba(255, 120, 50, 0.25) 0%, rgba(255, 150, 80, 0.08) 100%)',
    'benefit': 'linear-gradient(135deg, rgba(0, 175, 255, 0.25) 0%, rgba(0, 229, 255, 0.08) 100%)',
    'eco': 'linear-gradient(135deg, rgba(82, 196, 26, 0.25) 0%, rgba(100, 200, 50, 0.08) 100%)',
  }
  return gradients[type] || gradients['flood-control']
}
</script>

<style scoped>
.case-library-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0;
  gap: 0;
  background: rgba(var(--tech-bg-rgb), 0.92);
}

/* 筛选区 */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  flex-shrink: 0;
}

.filter-items {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 12px;
  color: var(--tech-text-secondary);
  white-space: nowrap;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 按钮样式 */
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
  background: linear-gradient(135deg, var(--tech-cyan) 0%, #00e5ff 100%);
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

.btn-outline {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: transparent;
  border: 1px solid rgba(50, 150, 255, 0.25);
  border-radius: 6px;
  color: var(--tech-text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-outline:hover {
  background: rgba(50, 150, 255, 0.1);
  color: var(--tech-text-primary);
  border-color: rgba(50, 150, 255, 0.4);
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

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  gap: 0;
  min-height: 0;
}

/* 左侧案例列表 */
.case-list-panel {
  width: 48%;
  display: flex;
  flex-direction: column;
  background: transparent;
  border: none;
  border-right: 1px solid rgba(var(--tech-blue-rgb), 0.08);
  border-radius: 0;
  overflow: hidden;
}

.panel-title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
}

.title-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--tech-text-primary);
}

.title-count {
  font-size: 12px;
  color: var(--tech-text-secondary);
}

.case-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.case-list::-webkit-scrollbar {
  width: 4px;
}

.case-list::-webkit-scrollbar-track {
  background: rgba(50, 150, 255, 0.05);
  border-radius: 2px;
}

.case-list::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.2);
  border-radius: 2px;
}

.case-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  border-radius: 0;
  cursor: pointer;
  transition: all 0.3s;
}

.case-card:hover {
  background: rgba(var(--tech-blue-rgb), 0.04);
  border-bottom-color: rgba(var(--tech-blue-rgb), 0.2);
}

.case-card.active {
  background: rgba(var(--tech-blue-rgb), 0.06);
  border-bottom-color: rgba(var(--tech-cyan-rgb), 0.4);
}

.case-cover {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  flex-shrink: 0;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.case-icon {
  width: 36px;
  height: 36px;
  color: rgba(255, 255, 255, 0.8);
}

.case-icon :deep(svg) {
  width: 100%;
  height: 100%;
}

.case-tag {
  position: absolute;
  top: 6px;
  left: 6px;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid;
  font-weight: 500;
}

.case-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.case-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.case-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--tech-text-primary);
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.case-status {
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.case-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--tech-text-secondary);
}

.case-summary {
  font-size: 11px;
  color: var(--tech-text-secondary);
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.case-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

.action-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 0;
  color: var(--tech-text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  background: rgba(var(--tech-blue-rgb), 0.08);
  color: var(--tech-text-primary);
}

.action-btn.favorited {
  color: #ff4d4f;
}

/* 右侧案例详情 */
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

/* 关键指标区 */
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

/* 底部操作栏 */
.detail-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 12px 16px;
  border-top: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  background: transparent;
}

/* Element Plus 深色主题覆盖 */
:deep(.dark-date-picker .el-input__wrapper),
:deep(.dark-select .el-input__wrapper) {
  background: transparent;
  border: 1px solid rgba(50, 150, 255, 0.25);
  box-shadow: none;
}

:deep(.dark-date-picker .el-input__inner),
:deep(.dark-select .el-input__inner) {
  color: var(--tech-text-primary);
}

:deep(.dark-input .el-input__wrapper) {
  background: transparent;
  border: 1px solid rgba(50, 150, 255, 0.25);
  box-shadow: none;
}

:deep(.dark-input .el-input__inner) {
  color: var(--tech-text-primary);
}

:deep(.el-range-input) {
  color: var(--tech-text-primary);
}

:deep(.el-range-separator) {
  color: var(--tech-text-secondary);
}

:deep(.el-date-editor .el-range__icon) {
  color: var(--tech-text-secondary);
}

:deep(.el-date-editor .el-range-close-icon) {
  color: var(--tech-text-secondary);
}

:deep(.el-popper) {
  background: #112536;
  border-color: rgba(50, 150, 255, 0.25);
}

:deep(.el-popper__arrow::before) {
  background: #112536;
  border-color: rgba(50, 150, 255, 0.25);
}
</style>
