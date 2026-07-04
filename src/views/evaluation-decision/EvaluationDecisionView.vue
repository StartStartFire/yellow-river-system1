<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import BaseChart from '@/components/chart/BaseChart.vue'
import {
  PLAN_COLORS,
  SANKEY_NODE_COLORS,
  WATER_FLOW_COLORS,
  TEXT_PRIMARY,
  TEXT_REGULAR,
  TEXT_SECONDARY,
  TECH_BLUE,
  TECH_GREEN,
  TECH_ORANGE,
  AXIS_LINE_COLOR,
  SPLIT_LINE_COLOR,
  baseTooltip,
  baseItemTooltip,
  baseLegend,
  baseCategoryXAxis,
  baseValueYAxis,
  baseValueXAxis,
  createGrid,
} from '@/utils/chart'
import {
  evaluationDecisionState as pageState,
  planOptions,
  planLabelMap,
  radarData,
  evaluationSankeyData,
  paretoData,
  rankingData,
  getDecisionPlanData,
} from '@/mock/evaluationDecision'

// ========== 页面状态 ==========
const plans = planOptions.data

// 默认选中方案一、二、三
const selectedComparePlans = ref<string[]>([...pageState.data.selectedComparePlans])

// Tab 切换（默认评价分析）
const activeTab = ref('evaluation')

// 决策分析当前方案（默认方案二）
const currentDecisionPlan = ref(pageState.data.currentDecisionPlan)

// 决策分析方案数据
const decisionPlanData = computed(() => getDecisionPlanData(currentDecisionPlan.value))

// 决策分析目标满足情况
const targets = computed(() => decisionPlanData.value.targets)

// 过程曲线页签
const processTabOptions = [
  { key: 'water', label: '水位变化' },
  { key: 'flow', label: '流量变化' },
  { key: 'power', label: '出力变化' },
]
const activeProcessTab = ref('water')

// 被选中的方案标签集合（用于图表过滤）
const selectedPlanLabels = computed(() => {
  return selectedComparePlans.value.map(v => planLabelMap[v]).filter(Boolean)
})

// ========== BaseChart refs（用于 Tab 切换后手动 resize） ==========
const radarBaseChart = ref<InstanceType<typeof BaseChart> | null>(null)
const sankeyBaseChart = ref<InstanceType<typeof BaseChart> | null>(null)
const paretoBaseChart = ref<InstanceType<typeof BaseChart> | null>(null)
const processBaseChart = ref<InstanceType<typeof BaseChart> | null>(null)
const waterFlowBaseChart = ref<InstanceType<typeof BaseChart> | null>(null)

// ========== 雷达图 ==========
const radarOption = computed<echarts.EChartsOption>(() => {
  const data = radarData.data
  const filteredPlans = data.plans.filter(p => selectedPlanLabels.value.includes(p.plan))

  return {
    title: {
      text: '多方案评价雷达图',
      right: 12,
      top: 4,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    tooltip: {
      ...baseItemTooltip,
    },
    legend: {
      ...baseLegend,
      data: filteredPlans.map(p => p.plan),
      bottom: 2,
    },
    radar: {
      indicator: data.indicators.map(ind => ({
        name: ind.name,
        max: ind.max,
      })),
      center: ['50%', '52%'],
      radius: '56%',
      axisName: {
        color: TEXT_REGULAR,
        fontSize: 11,
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(0, 175, 255, 0.02)', 'rgba(0, 175, 255, 0.05)'],
        },
      },
      axisLine: {
        lineStyle: {
          color: AXIS_LINE_COLOR,
        },
      },
      splitLine: {
        lineStyle: {
          color: SPLIT_LINE_COLOR,
        },
      },
    },
    series: [{
      type: 'radar',
      data: filteredPlans.map(p => ({
        name: p.plan,
        value: p.values,
        lineStyle: { width: 2, color: PLAN_COLORS[p.plan] },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: PLAN_COLORS[p.plan] + '30' },
            { offset: 1, color: PLAN_COLORS[p.plan] + '05' },
          ]),
        },
        itemStyle: { color: PLAN_COLORS[p.plan] },
      })),
    }],
  }
})

// ========== 评价指标桑基图 ==========
const sankeyOption = computed<echarts.EChartsOption>(() => {
  const data = evaluationSankeyData.data

  return {
    title: {
      text: '多方案评价指标',
      right: 12,
      top: 6,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    tooltip: {
      ...baseItemTooltip,
      triggerOn: 'mousemove' as const,
    },
    series: [{
      type: 'sankey',
      emphasis: {
        focus: 'adjacency' as const,
      },
      nodeAlign: 'left' as const,
      nodeGap: 4,
      nodeWidth: 28,
      left: 50,
      right: 36,
      top: 36,
      bottom: 20,
      data: data.nodes.map((n, i) => ({
        ...n,
        itemStyle: {
          color: SANKEY_NODE_COLORS[i % SANKEY_NODE_COLORS.length],
          borderColor: 'rgba(255,255,255,0.15)',
          borderWidth: 1,
        },
        label: {
          show: true,
          color: '#ffffff',
          fontSize: 9,
          fontWeight: 600,
          // R编号和分类名称均在色块内部，右侧结果在色块外
          position: n.category === 2 ? 'right' : 'inside',
        },
      })),
      links: data.links.map(l => ({
        source: l.source,
        target: l.target,
        value: l.value,
        lineStyle: {
          color: 'gradient',
          opacity: 0.35,
          curveness: 0.5,
        },
      })),
      lineStyle: {
        color: 'gradient',
        opacity: 0.35,
        curveness: 0.5,
      },
    }],
  }
})

// ========== 帕累托曲线 ==========
const paretoOption = computed<echarts.EChartsOption>(() => {
  const data = paretoData.data
  const filteredData = data.filter(d => selectedPlanLabels.value.includes(d.plan))

  return {
    title: {
      text: '帕累托曲线',
      right: 12,
      top: 4,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    tooltip: {
      ...baseTooltip,
    },
    legend: {
      ...baseLegend,
      data: filteredData.map(d => d.plan),
      top: 22,
    },
    grid: createGrid(48, 22, 50, 16),
    xAxis: {
      ...baseValueXAxis,
      name: '最优投影值',
      nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
      axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
    },
    yAxis: {
      ...baseValueYAxis,
      name: '综合优选指数',
      nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
      axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
    },
    series: filteredData.map(d => ({
      name: d.plan,
      type: 'line',
      data: d.points.map(p => [p.projection, p.index]),
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width: 2, color: PLAN_COLORS[d.plan] },
      itemStyle: { color: PLAN_COLORS[d.plan] },
      connectNulls: false,
    })),
  }
})

// ========== 评价算法排名表格 ==========
// 使用模板中的 el-table 直接渲染（见模板部分）

// ========== 决策分析-目标满足情况 ==========
// 直接在模板中渲染

// ========== 决策分析-过程曲线 ==========
const processOption = computed<echarts.EChartsOption>(() => {
  const tab = activeProcessTab.value

  if (tab === 'water') {
    const d = decisionPlanData.value.waterLevel
    return {
      title: {
        text: '水位变化过程线',
        right: 12,
        top: 2,
        textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
      },
      tooltip: { ...baseTooltip },
      legend: {
        ...baseLegend,
        data: ['龙羊峡水库', '刘家峡水库', '汛限水位', '正常蓄水位'],
        textStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        top: 18,
      },
      grid: createGrid(46, 16, 42, 8),
      xAxis: {
        ...baseCategoryXAxis,
        data: d.dates,
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      yAxis: {
        ...baseValueYAxis,
        name: '水位（m）',
        nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      series: [
        {
          name: '龙羊峡水库',
          type: 'line',
          data: d.longyang,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_BLUE },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0, 175, 255, 0.2)' },
              { offset: 1, color: 'rgba(0, 175, 255, 0.02)' },
            ]),
          },
        },
        {
          name: '刘家峡水库',
          type: 'line',
          data: d.liujia,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_GREEN },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0, 229, 160, 0.2)' },
              { offset: 1, color: 'rgba(0, 229, 160, 0.02)' },
            ]),
          },
        },
        {
          name: '汛限水位',
          type: 'line',
          data: d.dates.map(() => d.floodLimit),
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 1.5, color: '#ff6b6b', type: 'dashed' },
        },
        {
          name: '正常蓄水位',
          type: 'line',
          data: d.dates.map(() => d.normalLevel),
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 1.5, color: TECH_ORANGE, type: 'dashed' },
        },
      ],
    }
  } else if (tab === 'flow') {
    const d = decisionPlanData.value.flow
    return {
      title: {
        text: '流量变化过程线',
        right: 12,
        top: 2,
        textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
      },
      tooltip: { ...baseTooltip },
      legend: {
        ...baseLegend,
        data: ['龙羊峡水库', '刘家峡水库'],
        textStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        top: 18,
      },
      grid: createGrid(46, 16, 42, 8),
      xAxis: {
        ...baseCategoryXAxis,
        data: d.dates,
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      yAxis: {
        ...baseValueYAxis,
        name: '流量（m³/s）',
        nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      series: [
        {
          name: '龙羊峡水库',
          type: 'line',
          data: d.longyang,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_BLUE },
        },
        {
          name: '刘家峡水库',
          type: 'line',
          data: d.liujia,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_GREEN },
        },
      ],
    }
  } else {
    const d = decisionPlanData.value.power
    return {
      title: {
        text: '出力变化过程线',
        right: 12,
        top: 2,
        textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
      },
      tooltip: { ...baseTooltip },
      legend: {
        ...baseLegend,
        data: ['龙羊峡水库', '刘家峡水库', '龙羊峡装机容量', '刘家峡装机容量'],
        textStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        top: 18,
      },
      grid: createGrid(46, 16, 42, 8),
      xAxis: {
        ...baseCategoryXAxis,
        data: d.dates,
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      yAxis: {
        ...baseValueYAxis,
        name: '出力（MW）',
        nameTextStyle: { color: TEXT_SECONDARY, fontSize: 10 },
        axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
      },
      series: [
        {
          name: '龙羊峡水库',
          type: 'line',
          data: d.longyang,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_BLUE },
        },
        {
          name: '刘家峡水库',
          type: 'line',
          data: d.liujia,
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 2, color: TECH_GREEN },
        },
        {
          name: '龙羊峡装机容量',
          type: 'line',
          data: d.dates.map(() => d.longyangCapacity),
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 1.5, color: '#ff6b6b', type: 'dashed' },
        },
        {
          name: '刘家峡装机容量',
          type: 'line',
          data: d.dates.map(() => d.liujiaCapacity),
          smooth: true,
          symbol: 'none',
          lineStyle: { width: 1.5, color: TECH_ORANGE, type: 'dashed' },
        },
      ],
    }
  }
})

// ========== 水量使用流向图 ==========
const waterFlowOption = computed<echarts.EChartsOption>(() => {
  const data = decisionPlanData.value.waterUsage
  const totalValue = data.reduce((sum: number, d: any) => sum + d.value, 0)
  const sourceName = `最终来水量\n${totalValue.toFixed(2)} 亿m³`

  const nodes = [
    { name: sourceName, itemStyle: { color: '#0088cc' } },
    ...data.map((d: any, i: number) => ({
      name: `${d.name}\n${d.value} 亿m³（${d.percent}%）`,
      itemStyle: { color: WATER_FLOW_COLORS[i % WATER_FLOW_COLORS.length] },
    })),
  ]

  const links = data.map((d: any) => ({
    source: sourceName,
    target: `${d.name}\n${d.value} 亿m³（${d.percent}%）`,
    value: d.value,
  }))

  return {
    title: {
      text: '水量使用流向图',
      right: 12,
      top: 6,
      textStyle: { color: TEXT_SECONDARY, fontSize: 13, fontWeight: 600 },
    },
    tooltip: {
      ...baseItemTooltip,
      triggerOn: 'mousemove' as const,
      formatter: (params: any) => {
        if (params.dataType === 'edge') {
          return `${params.data.source} → ${params.data.target}<br/>水量：${params.data.value} 亿m³`
        }
        return params.name
      },
    },
    series: [{
      type: 'sankey',
      layout: 'none',
      layoutIterations: 0,
      emphasis: {
        focus: 'adjacency' as const,
      },
      nodeAlign: 'left' as const,
      nodeGap: 10,
      nodeWidth: 18,
      left: 20,
      right: 40,
      top: 36,
      bottom: 20,
      data: nodes,
      links: links,
      lineStyle: {
        color: 'gradient',
        opacity: 0.4,
        curveness: 0.5,
      },
      label: {
        show: true,
        color: TEXT_PRIMARY,
        fontSize: 10,
        position: 'right',
      },
    }],
  }
})

// ========== 交互事件 ==========

const handleTabSwitch = (tab: string) => {
  activeTab.value = tab
  // 二次 resize 确保 display 变化后 ECharts 获取正确尺寸
  setTimeout(() => {
    radarBaseChart.value?.resize()
    sankeyBaseChart.value?.resize()
    paretoBaseChart.value?.resize()
    processBaseChart.value?.resize()
    waterFlowBaseChart.value?.resize()
  }, 200)
  setTimeout(() => {
    radarBaseChart.value?.resize()
    sankeyBaseChart.value?.resize()
    paretoBaseChart.value?.resize()
    processBaseChart.value?.resize()
    waterFlowBaseChart.value?.resize()
  }, 400)
}

// 导出方案
const handleExportPlan = () => {
  ElMessage.info('当前为前端原型，暂不支持真实导出')
}

// ========== watch ==========
watch(selectedComparePlans, (val, oldVal) => {
  if (val.length === 0 && oldVal && oldVal.length > 0) {
    // 避免无限循环：用 nextTick 重置
    nextTick(() => { selectedComparePlans.value = ['plan-1'] })
    return
  }
  // BaseChart 自动响应 computed option 变化，无需手动 renderCharts
})

// activeTab 变化时需要手动 resize（v-show display 切换后容器尺寸变化）
watch(activeTab, () => {
  setTimeout(() => {
    radarBaseChart.value?.resize()
    sankeyBaseChart.value?.resize()
    paretoBaseChart.value?.resize()
    processBaseChart.value?.resize()
    waterFlowBaseChart.value?.resize()
  }, 300)
})
</script>

<template>
  <div class="evaluation-decision-view">
    <!-- ===== Tab 导航栏 ===== -->
    <div class="tab-nav-bar">
      <button
        class="tab-nav-btn"
        :class="{ active: activeTab === 'evaluation' }"
        @click="handleTabSwitch('evaluation')"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="8" cy="8" r="6"/>
          <path d="M5.5 8L7.5 10L11 5.5"/>
        </svg>
        评价分析
      </button>
      <button
        class="tab-nav-btn"
        :class="{ active: activeTab === 'decision' }"
        @click="handleTabSwitch('decision')"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="2" y="2" width="12" height="12" rx="2"/>
          <path d="M5 8L7 10L11 6"/>
        </svg>
        决策分析
      </button>
    </div>

    <!-- ===== 评价分析内容 ===== -->
    <div v-show="activeTab === 'evaluation'" class="tab-content">
      <!-- 顶部：多方案对比选择 -->
      <div class="selector-bar">
        <span class="selector-label">多方案对比：</span>
        <el-checkbox-group v-model="selectedComparePlans" class="plan-checkboxes">
          <el-checkbox v-for="plan in plans" :key="plan.value" :value="plan.value" :label="plan.label">
            <span class="checkbox-label-text">{{ plan.label }}</span>
          </el-checkbox>
        </el-checkbox-group>
      </div>

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
              <el-table-column v-for="score in rankingData.data[0]?.scores || []" :key="score.plan" :label="score.plan" min-width="100">
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

    <!-- ===== 决策分析内容 ===== -->
    <div v-show="activeTab === 'decision'" class="tab-content tab-content-decision">
      <!-- 顶部控件 -->
      <div class="decision-top-bar">
        <div class="decision-selector">
          <span class="selector-label">当前决策方案：</span>
          <el-select v-model="currentDecisionPlan" size="small" style="width: 140px;">
            <el-option
              v-for="plan in plans"
              :key="plan.value"
              :value="plan.value"
              :label="plan.label"
            />
          </el-select>
        </div>
        <button class="export-btn" @click="handleExportPlan">
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
                  <span class="target-rate">{{ target.rate.toFixed(1) }}%</span>
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
                @click="activeProcessTab = tab.key"
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
  </div>
</template>

<style scoped>
.evaluation-decision-view {
  display: flex;
  flex-direction: column;
  padding: 0;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  position: relative;
  background: rgba(var(--tech-bg-rgb), 0.92);
}

/* ===== Tab 导航栏 ===== */
.tab-nav-bar {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  padding: 6px 14px;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.12);
}

.tab-nav-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  padding: 8px 0;
  font-size: 13px;
  font-weight: 500;
  color: var(--tech-text-secondary);
  background: transparent;
  border: none;
  border-radius: 0;
  cursor: pointer;
  transition: all 0.25s ease;
  justify-content: center;
}

.tab-nav-btn:hover {
  color: var(--tech-text-regular);
  background: rgba(var(--tech-blue-rgb), 0.05);
}

.tab-nav-btn.active {
  color: var(--tech-cyan);
  background: rgba(var(--tech-blue-rgb), 0.12);
  border-bottom: 2px solid rgba(var(--tech-cyan-rgb), 0.6);
}

.tab-nav-btn svg {
  flex-shrink: 0;
}

/* ===== Tab 内容区 ===== */
.tab-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
  padding: 0;
}

.tab-content-decision {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ===== 方案选择器 ===== */
.selector-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  margin-bottom: 4px;
  min-height: 24px;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.08);
  padding-bottom: 8px;
}
.selector-label {
  font-size: 12px;
  color: var(--tech-text-secondary);
  white-space: nowrap;
}
.plan-checkboxes {
  display: flex;
  gap: 8px;
}
/* 自定义复选框样式覆盖 */
:deep(.el-checkbox) {
  margin-right: 0;
  height: 20px;
}
:deep(.el-checkbox__label) {
  font-size: 11px;
  color: var(--tech-text-regular);
}
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: var(--tech-blue);
  border-color: var(--tech-blue);
}
:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: var(--tech-blue);
}
:deep(.el-checkbox__inner) {
  width: 12px;
  height: 12px;
}
.checkbox-label-text {
  font-size: 11px;
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
.chart-container-process {
  flex: 1;
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
:deep(.el-select) {
  --el-select-input-focus-border-color: var(--tech-blue);
}
:deep(.el-select .el-input__wrapper) {
  background: rgba(6, 30, 70, 0.6);
  box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.25);
}
:deep(.el-select .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--tech-blue);
}
:deep(.el-select .el-input__inner) {
  color: var(--tech-text-regular);
}
:deep(.el-select-dropdown) {
  background: #0f1f33;
  border: 1px solid rgba(50, 150, 255, 0.3);
}
:deep(.el-select-dropdown__item) {
  color: var(--tech-text-regular);
}
:deep(.el-select-dropdown__item.hover) {
  background: rgba(var(--tech-blue-rgb), 0.1);
  color: var(--tech-blue);
}
:deep(.el-select-dropdown__item.selected) {
  color: var(--tech-blue);
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
