<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import PanelCard from '@/components/common/PanelCard.vue'
import {
  processPageState as pageState,
  scenarioOptions,
  getScenarioData,
} from '@/mock/processTransparent'

const router = useRouter()

// ── 方案情景 ──
const scenarios = scenarioOptions.data
const activeScenarioId = ref('flood-priority')

// ── 页面状态（含进度模拟） ──
const status = ref('running')
const progress = ref(26.2)
const elapsedTime = ref('00:08:24')
const remainingTime = ref('00:22:36')
const period = ref('2025-05-16 08:00 ~ 2025-05-26 08:00（241时段）')

let progressTimer: ReturnType<typeof setInterval> | null = null

const formatTime = (seconds: number) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

const startProgressSimulation = () => {
  let elapsedSec = 8 * 60 + 24
  let remainSec = 22 * 60 + 36
  const totalSec = elapsedSec + remainSec

  if (progressTimer) clearInterval(progressTimer)
  progressTimer = setInterval(() => {
    if (progress.value >= 100) {
      status.value = '已完成'
      if (progressTimer) clearInterval(progressTimer)
      return
    }
    progress.value = parseFloat((progress.value + 0.5 + Math.random() * 0.8).toFixed(1))
    if (progress.value > 100) progress.value = 100
    elapsedSec = Math.floor(totalSec * progress.value / 100)
    remainSec = Math.max(0, totalSec - elapsedSec)
    elapsedTime.value = formatTime(elapsedSec)
    remainingTime.value = formatTime(remainSec)
    if (progress.value >= 100) {
      status.value = '已完成'
      if (progressTimer) clearInterval(progressTimer)
    }
  }, 2500)
}

// ── 方案切换 ──
const scenarioData = computed(() => getScenarioData(activeScenarioId.value))
const summary = computed(() => scenarioData.value.summary)
const logs = computed(() => scenarioData.value.logs)

const logsDisplay = ref([...logs.value])

// ── 操作区 ──

const handleViewEvaluation = () => {
  router.push('/evaluation-decision')
}

const handleSave = () => {
  ElMessage.success('当前方案已保存')
}

const handleTerminate = () => {
  ElMessageBox.confirm('确定要终止当前计算任务吗？', '终止确认', {
    confirmButtonText: '确定终止',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    status.value = '已终止'
    if (progressTimer) clearInterval(progressTimer)
  }).catch(() => {
    // 取消操作
  })
}

// ══════════════════════════════════════
//  ECharts 图表 — 新布局：左40% + 右60%
// ══════════════════════════════════════

// ── 左侧图表 refs ──
const convergenceChartRef = ref<HTMLDivElement | null>(null)
const objectiveChartRef = ref<HTMLDivElement | null>(null)

let convergenceChart: echarts.ECharts | null = null
let objectiveChart: echarts.ECharts | null = null

let resizeObserver: ResizeObserver | null = null

// ──────────── 左侧：算法收敛曲线 ────────────
const buildConvergenceOption = () => {
  const d = scenarioData.value.convergenceData
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(6, 30, 70, 0.9)',
      borderColor: 'rgba(50, 150, 255, 0.4)',
      textStyle: { color: '#e0e6ed', fontSize: 11 },
    },
    grid: { left: 46, right: 12, top: 30, bottom: 20 },
    xAxis: {
      type: 'category',
      data: d.iterations,
      axisLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.3)' } },
      axisLabel: { color: '#8aa0b8', fontSize: 9 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      name: '适应度值',
      nameTextStyle: { color: '#8aa0b8', fontSize: 9 },
      axisLine: { show: false },
      axisLabel: { color: '#8aa0b8', fontSize: 9 },
      splitLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.1)' } },
    },
    series: [{
      name: '当前最优适应度',
      type: 'line',
      data: d.fitness,
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2, color: '#00afff' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 175, 255, 0.3)' },
          { offset: 1, color: 'rgba(0, 175, 255, 0.02)' },
        ]),
      },
    }],
  }
}

// ──────────── 左侧：最优目标值变化趋势 ────────────
const buildObjectiveOption = () => {
  const d = scenarioData.value.objectiveTrendData
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(6, 30, 70, 0.9)',
      borderColor: 'rgba(50, 150, 255, 0.4)',
      textStyle: { color: '#e0e6ed', fontSize: 11 },
    },
    legend: {
      data:['总目标值','防洪目标','发电目标','生态目标'],
      textStyle: { color: '#8aa0b8', fontSize: 9 },
      top: 0,
    },
    grid: { left: 46, right: 12, top: 32, bottom: 20 },
    xAxis: {
      type: 'category',
      data: d.iterations,
      axisLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.3)' } },
      axisLabel: { color: '#8aa0b8', fontSize: 9 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      name: '目标值',
      nameTextStyle: { color: '#8aa0b8', fontSize: 9 },
      axisLine: { show: false },
      axisLabel: { color: '#8aa0b8', fontSize: 9 },
      splitLine: { lineStyle: { color: 'rgba(50, 150, 255, 0.1)' } },
    },
    series: [
      { name:'总目标值', type:'line', data:d.total, smooth:true, symbol:'none', lineStyle:{width:2,color:'#00afff'} },
      { name:'防洪目标', type:'line', data:d.flood, smooth:true, symbol:'none', lineStyle:{width:2,color:'#ff6b6b'} },
      { name:'发电目标', type:'line', data:d.power, smooth:true, symbol:'none', lineStyle:{width:2,color:'#ffaa00'} },
      { name:'生态目标', type:'line', data:d.ecology, smooth:true, symbol:'none', lineStyle:{width:2,color:'#00e5a0'} },
    ],
  }
}

// ══════════════════════════════════════
//  右侧：一个大图表，Tab 切换指标，同时展示龙羊峡+刘家峡
// ══════════════════════════════════════

const rightTabOptions = [
  { key: 'water', label: '水位变化' },
  { key: 'discharge', label: '下泄流量变化' },
  { key: 'power', label: '出力变化' },
]
const activeRightTab = ref('water')
const rightLYXChartRef = ref<HTMLDivElement | null>(null)
const rightLJXChartRef = ref<HTMLDivElement | null>(null)
let rightLYXChart: echarts.ECharts | null = null
let rightLJXChart: echarts.ECharts | null = null

const buildReservoirOption = (reservoirKey: 'lyx' | 'ljx') => {
  const tab = activeRightTab.value
  const name = reservoirKey === 'lyx' ? '龙羊峡' : '刘家峡'
  const lineColor = reservoirKey === 'lyx' ? '#00afff' : '#00e5a0'
  const dashColor = reservoirKey === 'lyx' ? '#00e5ff' : '#52c41a'

  if (tab === 'water') {
    const d = scenarioData.value.waterLevelData
    const r = reservoirKey === 'lyx' ? d.longyang : d.liujia
    return {
      tooltip: { trigger:'axis', backgroundColor:'rgba(6,30,70,0.9)', borderColor:'rgba(50,150,255,0.4)', textStyle:{color:'#e0e6ed',fontSize:11} },
      title: { text: name, left:'center', top:2, textStyle:{color:'#8aa0b8',fontSize:11,fontWeight:600} },
      legend: { data:['当前优化方案','入库预报','历史运行'], textStyle:{color:'#8aa0b8',fontSize:9}, top:18 },
      grid: { left:42, right:8, top:42, bottom:18 },
      xAxis: { type:'category', data:d.dates, axisLine:{lineStyle:{color:'rgba(50,150,255,0.3)'}}, axisLabel:{color:'#8aa0b8',fontSize:9}, splitLine:{show:false} },
      yAxis: { type:'value', name:'水位（m）', nameTextStyle:{color:'#8aa0b8',fontSize:9}, axisLine:{show:false}, axisLabel:{color:'#8aa0b8',fontSize:9}, splitLine:{lineStyle:{color:'rgba(50,150,255,0.1)'}} },
      series: [
        { name:'当前优化方案', type:'line', data:r.optimal, smooth:true, symbol:'none', lineStyle:{width:2,color:lineColor} },
        { name:'入库预报', type:'line', data:r.forecast, smooth:true, symbol:'none', lineStyle:{width:2,color:dashColor,type:'dashed'} },
        { name:'历史运行', type:'line', data:r.history, smooth:true, symbol:'none', lineStyle:{width:1.5,color:'rgba(255,255,255,0.25)'} },
      ],
    }
  } else if (tab === 'discharge') {
    const d = scenarioData.value.dischargeData
    const r = reservoirKey === 'lyx' ? d.longyang : d.liujia
    return {
      tooltip: { trigger:'axis', backgroundColor:'rgba(6,30,70,0.9)', borderColor:'rgba(50,150,255,0.4)', textStyle:{color:'#e0e6ed',fontSize:11} },
      title: { text: name, left:'center', top:2, textStyle:{color:'#8aa0b8',fontSize:11,fontWeight:600} },
      legend: { data:['优化下泄流量','历史下泄流量','最小生态流量'], textStyle:{color:'#8aa0b8',fontSize:9}, top:18 },
      grid: { left:46, right:8, top:42, bottom:18 },
      xAxis: { type:'category', data:d.dates, axisLine:{lineStyle:{color:'rgba(50,150,255,0.3)'}}, axisLabel:{color:'#8aa0b8',fontSize:9}, splitLine:{show:false} },
      yAxis: { type:'value', name:'流量（m³/s）', nameTextStyle:{color:'#8aa0b8',fontSize:9}, axisLine:{show:false}, axisLabel:{color:'#8aa0b8',fontSize:9}, splitLine:{lineStyle:{color:'rgba(50,150,255,0.1)'}} },
      series: [
        { name:'优化下泄流量', type:'line', data:r.optimal, smooth:true, symbol:'none', lineStyle:{width:2,color:lineColor} },
        { name:'历史下泄流量', type:'line', data:r.schedule, smooth:true, symbol:'none', lineStyle:{width:2,color:'#ffaa00'} },
        { name:'最小生态流量', type:'line', data:r.minDischarge, smooth:true, symbol:'none', lineStyle:{width:1.5,color:'#ff6b6b',type:'dashed'} },
      ],
    }
  } else {
    const d = scenarioData.value.powerOutputData
    const r = reservoirKey === 'lyx' ? d.longyang : d.liujia
    return {
      tooltip: { trigger:'axis', backgroundColor:'rgba(6,30,70,0.9)', borderColor:'rgba(50,150,255,0.4)', textStyle:{color:'#e0e6ed',fontSize:11} },
      title: { text: name, left:'center', top:2, textStyle:{color:'#8aa0b8',fontSize:11,fontWeight:600} },
      legend: { data:['优化出力','历史出力','装机容量'], textStyle:{color:'#8aa0b8',fontSize:9}, top:18 },
      grid: { left:46, right:8, top:42, bottom:18 },
      xAxis: { type:'category', data:d.dates, axisLine:{lineStyle:{color:'rgba(50,150,255,0.3)'}}, axisLabel:{color:'#8aa0b8',fontSize:9}, splitLine:{show:false} },
      yAxis: { type:'value', name:'出力（MW）', nameTextStyle:{color:'#8aa0b8',fontSize:9}, axisLine:{show:false}, axisLabel:{color:'#8aa0b8',fontSize:9}, splitLine:{lineStyle:{color:'rgba(50,150,255,0.1)'}} },
      series: [
        { name:'优化出力', type:'line', data:r.optimal, smooth:true, symbol:'none', lineStyle:{width:2,color:lineColor} },
        { name:'历史出力', type:'line', data:r.schedule, smooth:true, symbol:'none', lineStyle:{width:2,color:'#ffaa00'} },
        { name:'装机容量', type:'line', data:r.capacity ? d.dates.map(()=>r.capacity) : [], smooth:true, symbol:'none', lineStyle:{width:2,color:'#ff6b6b',type:'dashed'} },
      ],
    }
  }
}

// ── 渲染全部图表 ──
const renderCharts = () => {
  nextTick(() => {
    if (convergenceChartRef.value) {
      if (!convergenceChart) convergenceChart = echarts.init(convergenceChartRef.value)
      convergenceChart.setOption(buildConvergenceOption(), true)
      convergenceChart.resize()
    }
    if (objectiveChartRef.value) {
      if (!objectiveChart) objectiveChart = echarts.init(objectiveChartRef.value)
      objectiveChart.setOption(buildObjectiveOption(), true)
      objectiveChart.resize()
    }
    if (rightLYXChartRef.value) {
      if (!rightLYXChart) rightLYXChart = echarts.init(rightLYXChartRef.value)
      rightLYXChart.setOption(buildReservoirOption('lyx'), true)
      rightLYXChart.resize()
    }
    if (rightLJXChartRef.value) {
      if (!rightLJXChart) rightLJXChart = echarts.init(rightLJXChartRef.value)
      rightLJXChart.setOption(buildReservoirOption('ljx'), true)
      rightLJXChart.resize()
    }
  })
}

const initResizeObserver = () => {
  if (resizeObserver) resizeObserver.disconnect()
  resizeObserver = new ResizeObserver(() => {
    convergenceChart?.resize()
    objectiveChart?.resize()
    rightLYXChart?.resize()
    rightLJXChart?.resize()
  })
  const container = document.querySelector('.process-transparent-view')
  if (container) resizeObserver.observe(container)
}

// ── 日志追加模拟 ──
let logTimer: ReturnType<typeof setInterval> | null = null
const startLogSimulation = () => {
  const logMessages = [
    { level:'INFO', message:'迭代 450/2000，当前最优适应度：1.4521E-03，平均适应度：2.0158E-02' },
    { level:'INFO', message:'龙羊峡水位约束满足率：100%，刘家峡水位约束满足率：100%' },
    { level:'INFO', message:'防洪目标满足，生态下泄满足，发电目标优化中...' },
    { level:'INFO', message:'种群多样性指数：0.4235，搜索范围收敛正常' },
    { level:'INFO', message:'迭代 500/2000，当前最优适应度：1.3856E-03，平均适应度：1.9523E-02' },
  ]
  let logIndex = 0
  if (logTimer) clearInterval(logTimer)
  logTimer = setInterval(() => {
    if (status.value === '已完成' || status.value === '已终止') {
      if (logTimer) clearInterval(logTimer)
      return
    }
    const msg = logMessages[logIndex % logMessages.length]
    const now = new Date()
    const time = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`
    logsDisplay.value.unshift({ time, ...msg })
    if (logsDisplay.value.length > 20) logsDisplay.value = logsDisplay.value.slice(0, 20)
    logIndex++
  }, 6000)
}

// ── watch ──
watch(activeScenarioId, () => {
  logsDisplay.value = [...logs.value]
  renderCharts()
})

watch(activeRightTab, () => {
  if (rightLYXChart) rightLYXChart.setOption(buildReservoirOption('lyx'), true)
  if (rightLJXChart) rightLJXChart.setOption(buildReservoirOption('ljx'), true)
})

// ── 生命周期 ──
onMounted(() => {
  logsDisplay.value = [...logs.value]
  startProgressSimulation()
  startLogSimulation()
  setTimeout(() => {
    renderCharts()
    initResizeObserver()
  }, 300)
})

onUnmounted(() => {
  if (progressTimer) clearInterval(progressTimer)
  if (logTimer) clearInterval(logTimer)
  if (resizeObserver) resizeObserver.disconnect()
  ;[convergenceChart, objectiveChart, rightLYXChart, rightLJXChart].forEach(c => c?.dispose())
})
</script>

<template>
  <div class="process-transparent-view">
    <!-- ===== 方案情景选择区 ===== -->
    <div class="scenario-section">
      <div
        v-for="sc in scenarios"
        :key="sc.id"
        class="scenario-card"
        :class="{ active: activeScenarioId === sc.id }"
        @click="activeScenarioId = sc.id"
      >
        <div class="scenario-radio">
          <span class="radio-dot" :class="{ active: activeScenarioId === sc.id }"></span>
        </div>
        <div class="scenario-info">
          <div class="scenario-name">{{ sc.name }}</div>
          <div class="scenario-taskId">{{ sc.taskId }}</div>
        </div>
      </div>
    </div>

    <!-- ===== 过程展示状态栏 ===== -->
    <div class="status-bar">
      <div class="status-bar-title">过程展示</div>
      <div class="status-fields">
        <div class="status-field">
          <span class="field-label">任务状态</span>
          <span class="field-value" :class="{ 'status-running': status === '运行中', 'status-done': status === '已完成', 'status-terminated': status === '已终止' }">
            <span class="status-dot"></span>{{ status }}
          </span>
        </div>
        <div class="status-field">
          <span class="field-label">调度周期</span>
          <span class="field-value">{{ period }}</span>
        </div>
        <div class="status-field">
          <span class="field-label">已运行时间</span>
          <span class="field-value">{{ elapsedTime }}</span>
        </div>
        <div class="status-field">
          <span class="field-label">预计剩余时间</span>
          <span class="field-value">{{ remainingTime }}</span>
        </div>
        <div class="status-field progress-field">
          <span class="field-label">整体进度</span>
          <div class="progress-wrapper">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progress + '%' }"></div>
            </div>
            <span class="progress-text">{{ progress.toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 中部图表区：左40% 优化过程 + 右60% 水库运行响应 ===== -->
    <div class="middle-section">
      <!-- 左侧：优化过程分析（40%） -->
      <div class="left-panel">
        <div class="left-charts">
          <div class="chart-card">
            <div class="chart-card-header"><span class="chart-label">算法收敛曲线</span></div>
            <div ref="convergenceChartRef" class="chart-container-sm"></div>
          </div>
          <div class="chart-card">
            <div class="chart-card-header"><span class="chart-label">最优目标值变化趋势</span></div>
            <div ref="objectiveChartRef" class="chart-container-sm"></div>
          </div>
        </div>
      </div>

      <!-- 右侧：水库运行响应（60%） -->
      <div class="right-panel">

        <!-- 指标 Tab：水位变化 / 下泄流量变化 / 出力变化 -->
        <div class="right-tabs">
          <button
            v-for="tab in rightTabOptions"
            :key="tab.key"
            class="right-tab-btn"
            :class="{ active: activeRightTab === tab.key }"
            @click="activeRightTab = tab.key"
          >{{ tab.label }}</button>
        </div>

        <!-- 两个竖排图表：龙羊峡 + 刘家峡 -->
        <div class="right-charts-col">
          <div class="right-chart-wrap">
            <div ref="rightLYXChartRef" class="chart-container-md"></div>
          </div>
          <div class="right-chart-wrap">
            <div ref="rightLJXChartRef" class="chart-container-md"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 底部辅助信息区 ===== -->
    <div class="bottom-section">
      <PanelCard title="运行日志" class="bottom-card log-card">
        <div class="log-list">
          <div v-for="(log, i) in logsDisplay.slice(0, 3)" :key="i" class="log-entry">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-level">{{ log.level }}</span>
            <span class="log-msg">{{ log.message }}</span>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="当前最优方案信息" class="bottom-card">
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">总目标值</span>
            <span class="info-value">{{ summary.bestSolution.totalObjective }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">防洪目标值</span>
            <span class="info-value">{{ summary.bestSolution.floodObjective }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">发电目标值</span>
            <span class="info-value">{{ summary.bestSolution.powerObjective }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">生态目标值</span>
            <span class="info-value">{{ summary.bestSolution.ecologyObjective }}</span>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="约束满足情况" class="bottom-card">
        <div class="info-grid">
          <div v-for="(c, i) in summary.constraintStatus" :key="i" class="info-item">
            <span class="info-label">{{ c.name }}</span>
            <span class="constraint-status satisfied">{{ c.status }}</span>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="预估结果摘要" class="bottom-card">
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">峰值削减</span>
            <span class="info-value">{{ summary.estimatedResult.peakReduction }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">总发电量</span>
            <span class="info-value">{{ summary.estimatedResult.totalPower }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">平均下泄流量</span>
            <span class="info-value">{{ summary.estimatedResult.avgOutflow }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">最小下泄流量</span>
            <span class="info-value">{{ summary.estimatedResult.minOutflow }}</span>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="操作" class="bottom-card ops-card">
        <div class="ops-buttons">
          <button class="op-btn primary" @click="handleViewEvaluation">查看评价结果</button>
          <button class="op-btn" @click="handleSave">保存当前方案</button>
          <button class="op-btn danger" @click="handleTerminate">终止计算</button>
        </div>
      </PanelCard>
    </div>
  </div>
</template>

<style scoped>
.process-transparent-view {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 10px 14px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  position: relative;
  background: rgba(6, 20, 42, 0.92);
}

/* ── 方案情景选择区 ── */
.scenario-section {
  display: flex;
  gap: 0;
  flex-shrink: 0;
  border-bottom: 1px solid rgba(0, 175, 255, 0.1);
  padding-bottom: 6px;
  margin-bottom: 6px;
}
.scenario-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: transparent;
  border: none;
  border-right: 1px solid rgba(0, 175, 255, 0.1);
  border-radius: 0;
  cursor: pointer;
  transition: all 0.25s;
}
.scenario-card:last-child {
  border-right: none;
}
.scenario-card:hover {
  background: rgba(0, 175, 255, 0.04);
}
.scenario-card.active {
  background: rgba(0, 175, 255, 0.06);
  border-bottom: 2px solid rgba(0, 212, 255, 0.5);
}
.scenario-radio { display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.radio-dot {
  width: 14px; height: 14px; border-radius: 50%;
  border: 2px solid rgba(50, 150, 255, 0.4);
  transition: all 0.25s; display: block;
}
.radio-dot.active {
  border-color: #00afff; background: #00afff;
  box-shadow: 0 0 6px rgba(0, 175, 255, 0.5);
}
.scenario-info { display: flex; flex-direction: column; gap: 2px; }
.scenario-name { font-size: 14px; font-weight: 600; color: #e0e6ed; }
.scenario-taskId { font-size: 11px; color: #6e8a9e; }

/* ── 状态栏 ── */
.status-bar {
  display: flex; flex-direction: column; gap: 4px;
  padding: 6px 10px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(0, 175, 255, 0.1);
  border-radius: 0;
  flex-shrink: 0;
}
.status-bar-title {
  font-size: 13px; font-weight: 600; color: #8aa0b8; letter-spacing: 0.5px;
}
.status-fields { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.status-field { display: flex; align-items: center; gap: 4px; }
.field-label { font-size: 11px; color: #8aa0b8; white-space: nowrap; }
.field-value { font-size: 12px; color: #c0c8d4; display: flex; align-items: center; gap: 4px; }
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #00ff88; display: inline-block; animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.4} }
.status-running .status-dot { background: #00ff88; }
.status-done .status-dot { background: #00afff; animation: none; }
.status-terminated .status-dot { background: #ff4d4f; animation: none; }
.progress-field { flex: 1; min-width: 200px; }
.progress-wrapper { display: flex; align-items: center; gap: 8px; flex: 1; }
.progress-bar { flex:1; height:6px; background:rgba(50,150,255,0.15); border-radius:3px; overflow:hidden; min-width:80px; }
.progress-fill { height:100%; background:linear-gradient(90deg,#0088cc,#00afff); border-radius:3px; transition:width 1s ease; }
.progress-text { font-size:13px; color:#00afff; font-weight:600; min-width:48px; }

/* ════════════════════════════════════
   中部图表区 — 左40% + 右60%
   ════════════════════════════════════ */
.middle-section {
  display: flex;
  gap: 0;
  flex: 1;
  min-height: 0;
}

/* ── 左侧面板 ── */
.left-panel {
  flex: 5;
  display: flex;
  flex-direction: column;
  min-width: 0;
  border-right: 1px solid rgba(0, 175, 255, 0.1);
}
.left-charts {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* ── 右侧面板 ── */
.right-panel {
  flex: 5;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* ── 右侧 Tab ── */
.right-tabs {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}
.right-tab-btn {
  flex: 1;
  padding: 5px 0;
  font-size: 12px;
  font-weight: 500;
  border: none;
  border-radius: 0;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: #8aa0b8;
  cursor: pointer;
  transition: all 0.2s;
}
.right-tab-btn:hover {
  color: #c0c8d4;
  border-bottom-color: rgba(0, 175, 255, 0.3);
}
.right-tab-btn.active {
  color: #00afff;
  border-bottom-color: rgba(0, 212, 255, 0.6);
}

.right-charts-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-height: 0;
}
.right-chart-wrap {
  flex: 1;
  display: flex;
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 2px;
  min-width: 0;
}
.chart-container-md {
  flex: 1;
  width: 100%;
  min-height: 0;
}

/* ── 左侧图表卡片 ── */
.chart-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 0;
}
.chart-card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: 3px 8px;
  background: transparent;
  border-bottom: 1px solid rgba(50, 150, 255, 0.15);
}
.chart-card-header .chart-label {
  font-size: 11px;
  font-weight: 600;
  color: #8aa0b8;
}
.chart-container-sm {
  flex: 1;
  width: 100%;
}

/* ── 底部辅助信息区 ── */
.bottom-section {
  display: flex;
  gap: 0;
  flex-shrink: 0;
  border-top: 1px solid rgba(0, 175, 255, 0.1);
  padding-top: 8px;
}
.bottom-card {
  flex: 1;
  min-width: 0;
  border-right: 1px solid rgba(0, 175, 255, 0.08);
}
.bottom-card:last-child {
  border-right: none;
}
.bottom-card :deep(.panel-header) {
  padding: 1px 6px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.12);
}
.bottom-card :deep(.panel-title) {
  font-size: 10px;
  font-weight: 600;
  color: #8aa0b8;
  letter-spacing: 0;
}
.bottom-card :deep(.panel-body) { padding: 2px 6px; }
.log-card { flex: 1.2; }
.log-list { display: flex; flex-direction: column; gap: 1px; }
.log-entry {
  display: flex; gap: 4px;
  font-size: 10px; line-height: 1.3;
  font-family: 'Courier New', monospace;
}
.log-time { color: #6e8a9e; flex-shrink: 0; }
.log-level { color: #00afff; flex-shrink: 0; font-weight: 600; }
.log-msg { color: #c0c8d4; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 6px; }
.info-item { display: flex; justify-content: space-between; align-items: center; padding: 0; }
.info-label { font-size: 10px; color: #8aa0b8; }
.info-value { font-size: 10px; color: #e0e6ed; font-weight: 600; }
.constraint-status { font-size: 10px; font-weight: 600; color: #00ff88; }

/* ── 操作 ── */
.ops-card { flex: 0 0 180px; }
.ops-buttons { display: flex; flex-direction: row; flex-wrap: wrap; gap: 2px; justify-content: center; }
.ops-buttons .op-btn { flex: 1 1 42%; min-width: 50px; }
.op-btn {
  padding: 2px 6px; font-size: 10px;
  border: 1px solid rgba(50,150,255,0.3);
  border-radius: 5px;
  background: rgba(6,30,70,0.6);
  color: #c0c8d4;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.op-btn:hover { border-color: rgba(50,150,255,0.5); background: rgba(6,30,70,0.9); }
.op-btn.primary { border-color: rgba(0,175,255,0.4); color: #00afff; }
.op-btn.primary:hover { background: rgba(0,175,255,0.12); border-color: rgba(0,175,255,0.6); }
.op-btn.danger { border-color: rgba(255,77,79,0.3); color: #ff6b6b; }
.op-btn.danger:hover { background: rgba(255,77,79,0.1); border-color: rgba(255,77,79,0.5); }

/* ── Scrollbar ── */
.process-transparent-view::-webkit-scrollbar { width: 4px; }
.process-transparent-view::-webkit-scrollbar-track { background: transparent; }
.process-transparent-view::-webkit-scrollbar-thumb { background: rgba(50,150,255,0.2); border-radius: 2px; }
</style>
