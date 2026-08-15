<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseChart from '@/components/chart/BaseChart.vue'
import PanelCard from '@/components/common/PanelCard.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import {
  TEXT_SECONDARY, baseTooltip, baseCategoryXAxis, baseValueYAxis,
  createGrid, createAreaGradient, SERIES_COLORS,
} from '@/utils/chart'
import { useModelConfigStore } from '@/stores/modelConfig'

const router = useRouter()
const route = useRoute()

// ── 从 URL 获取 job_id ──
const jobId = ref(route.query.job_id as string || '')

// ── WebSocket ──
let ws: WebSocket | null = null

// ── 方案情景（模板需要） ──
const scenarios = [
  { id: 'current', name: jobId.value ? `任务 ${jobId.value.slice(0, 8)}` : '当前方案', taskId: jobId.value ? `JOB_${jobId.value.slice(0, 8)}` : '' },
]
const activeScenarioId = ref('current')

// ── 页面状态 ──
const status = ref('等待任务')
const progress = ref(0)
const elapsedSec = ref(0)
const elapsedTime = computed(() => {
  const h = Math.floor(elapsedSec.value / 3600)
  const m = Math.floor((elapsedSec.value % 3600) / 60)
  const s = elapsedSec.value % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})
const remainingTime = computed(() => {
  if (progress.value <= 0) return '--:--:--'
  const remain = Math.round(elapsedSec.value / progress.value * (100 - progress.value))
  const h = Math.floor(remain / 3600)
  const m = Math.floor((remain % 3600) / 60)
  const s = remain % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})
const modelConfigStore = useModelConfigStore()

// ── 从 Store 获取调度起止年份 ──
const period = computed(() => {
  const s = modelConfigStore.dispatchSubject.startTime
  const e = modelConfigStore.dispatchSubject.endTime
  if (s && e) return `${s} ~ ${e}`
  return '1970 ~ 2023'
})
let elapsedTimer: ReturnType<typeof setInterval> | null = null

const statusColor = computed(() => {
  if (status.value === '运行中') return '#00ff88'
  if (status.value === '已完成') return 'var(--tech-blue)'
  if (status.value === '已终止') return '#ff4d4f'
  if (status.value === '等待任务') return 'var(--tech-text-placeholder)'
  return '#8aa0b8'
})

// ── 真实数据 refs ──
const convergenceData = ref({ iterations: [] as number[], fitness: [] as number[] })
interface ParetoFrontSnapshot {
  iteration: number
  points: number[][]  // [[f1, f2], ...]
}
const paretoHistory = ref<ParetoFrontSnapshot[]>([])
const waterLevelData = ref({ dates: [] as string[], longyang: { optimal: [] as number[] }, liujia: { optimal: [] as number[] } })
const dischargeData = ref({ dates: [] as string[], longyang: { optimal: [] as number[] }, liujia: { optimal: [] as number[] } })
const powerOutputData = ref({ dates: [] as string[], longyang: { optimal: [] as number[] }, liujia: { optimal: [] as number[] } })

// 底部信息栏实时数据（从 WS 推送获取）
const latestBestObjectives = ref<number[]>([])   // [f1, f2] 缺水量, 发电量
const latestCoordination = ref({ h_water: 0, h_ele: 0, h_sed: 0, h_eco: 0 })
const latestConstraint = ref({ water_guarantee: 0, eco_guarantee: 0, power_guarantee: 0, combined_rate: 0 })
const latestParetoSize = ref(0)

// 约束状态颜色
function constraintColor(rate: number): string {
  if (rate >= 90) return '#00ff88'
  if (rate >= 70) return '#f0a020'
  return '#ff6b6b'
}

const logsDisplay = ref<{ time: string; level: string; message: string }[]>([])

// ── 给模板用的 scenariosData 聚合对象 ──
const allScenarioData = computed(() => ({
  'current': {
    convergenceData: convergenceData.value,
    waterLevelData: waterLevelData.value,
    dischargeData: dischargeData.value,
    powerOutputData: powerOutputData.value,
  }
}))

const getScenarioData = (id: string) => allScenarioData.value[id] || allScenarioData.value['current']
const scenarioData = computed(() => getScenarioData(activeScenarioId.value))

// ── WebSocket 连接 ──
const connectWebSocket = () => {
  if (!jobId.value) return

  const wsUrl = `ws://${window.location.hostname}:18080/ws/${jobId.value}`
  try {
    ws = new WebSocket(wsUrl)
    ws.onopen = () => { status.value = '运行中' }
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        handleWsMessage(msg)
      } catch { /* ignore */ }
    }
    ws.onerror = () => {}
    ws.onclose = () => {}
  } catch { /* ignore */ }
}

// 辅助函数：生成年份标签
function buildTimeLabels(len: number, startYear: number): string[] {
  const labels: string[] = []
  for (let i = 0; i < len; i++) {
    if (i % 20 === 0) {
      labels.push(`${startYear + Math.floor(i / 20)}年`)
    } else {
      labels.push('')
    }
  }
  return labels
}

// ── 处理 WS 消息 ──
const handleWsMessage = (msg: any) => {
  if (msg.type === 'progress' && msg.payload) {
    const d = msg.payload
    progress.value = d.progress_percent

    // 收敛数据 + 种群质量
    if (d.best_objectives) {
      const iters = convergenceData.value.iterations
      iters.push(d.iteration)
      const f1 = d.best_objectives[0] || 0
      const f2 = d.best_objectives[1] || 0

      convergenceData.value = {
        iterations: [...iters],
        fitness: [...convergenceData.value.fitness, f1],
      }
      // 底部信息栏：最新最优值
      latestBestObjectives.value = [Math.abs(f1), Math.abs(f2)]
      latestParetoSize.value = d.pareto_size || 0
    }

    // Pareto 前沿演化快照
    if (d.pareto_objectives && d.pareto_objectives.length > 0) {
      paretoHistory.value.push({
        iteration: d.iteration,
        points: d.pareto_objectives.map((p: number[]) => [Math.abs(p[0]), Math.abs(p[1])]),
      })
      if (paretoHistory.value.length > 50) paretoHistory.value = paretoHistory.value.slice(-50)
    }

    if (d.progress_percent >= 100) status.value = '已完成'

    // 日志
    const now = new Date()
    const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`
    const bestStr = d.best_objectives?.map((v: number) => v.toFixed(4)).join(', ') || ''
    logsDisplay.value.unshift({
      time, level: 'INFO',
      message: `代 ${d.iteration}，最优: [${bestStr}]，前沿: ${d.pareto_size} 个，进度: ${d.progress_percent}%`,
    })
    if (logsDisplay.value.length > 100) logsDisplay.value = logsDisplay.value.slice(0, 100)
  }

  // 过程数据更新
  if (msg.type === 'process_data' && msg.payload) {
    const pd = msg.payload
    const labels = buildTimeLabels(pd.longyang_level?.length || 0, pd.start_year || 2014)
    waterLevelData.value = {
      dates: labels,
      longyang: { optimal: pd.longyang_level || [] },
      liujia: { optimal: pd.liujia_level || [] },
    }
    dischargeData.value = {
      dates: labels,
      longyang: { optimal: pd.longyang_outflow || [] },
      liujia: { optimal: pd.liujia_outflow || [] },
    }
    powerOutputData.value = {
      dates: labels,
      longyang: { optimal: pd.longyang_power || [] },
      liujia: { optimal: pd.liujia_power || [] },
    }
    // 底部信息栏：子系统协调度
    if (pd.coordination) {
      latestCoordination.value = {
        h_water: pd.coordination.h_water || 0,
        h_ele: pd.coordination.h_ele || 0,
        h_sed: pd.coordination.h_sed || 0,
        h_eco: pd.coordination.h_eco || 0,
      }
    }
    // 底部信息栏：约束满足率
    if (pd.constraint) {
      latestConstraint.value = {
        water_guarantee: pd.constraint.water_guarantee || 0,
        eco_guarantee: pd.constraint.eco_guarantee || 0,
        power_guarantee: pd.constraint.power_guarantee || 0,
        combined_rate: pd.constraint.combined_rate || 0,
      }
    }
  }
}

// ── 操作 ──
const handleViewEvaluation = () => {
  router.push(`/evaluation-decision${jobId.value ? `?job_id=${jobId.value}` : ''}`)
}

const handleSave = () => { ElMessage.success('当前方案已保存') }

const handleTerminate = () => {
  ElMessageBox.confirm('确定要终止当前计算任务吗？', '终止确认', {
    confirmButtonText: '确定终止', cancelButtonText: '取消', type: 'warning',
  }).then(() => {
    status.value = '已终止'
    if (ws) { ws.close(); ws = null }
  }).catch(() => {})
}

// ══════════════════════════════════════
//  ECharts 图表 — 使用 BaseChart + computed
// ══════════════════════════════════════

const rightTabOptions = [
  { key: 'water', label: '水位变化' },
  { key: 'discharge', label: '下泄流量变化' },
  { key: 'power', label: '出力变化' },
]
const activeRightTab = ref('water')

const convergenceOption = computed(() => {
  const d = scenarioData.value.convergenceData
  return {
    tooltip: { ...baseTooltip },
    grid: createGrid(30, 20, 46, 12),
    xAxis: { ...baseCategoryXAxis, data: d.iterations, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
    yAxis: {
      ...baseValueYAxis,
      name: '缺水量（亿m³）',
      nameTextStyle: { color: TEXT_SECONDARY, fontSize: 9 },
      axisLabel: { color: TEXT_SECONDARY, fontSize: 9 },
    },
    series: [{
      name: '当前最优适应度', type: 'line', data: d.fitness, smooth: true, symbol: 'none',
      lineStyle: { width: 2, color: SERIES_COLORS[0] },
      areaStyle: createAreaGradient(SERIES_COLORS[0], 0.3, 0.02),
    }],
  }
})

const objectiveOption = computed(() => {
  const history = paretoHistory.value
  if (history.length === 0) {
    return {
      tooltip: { ...baseTooltip },
      grid: createGrid(32, 20, 46, 12),
      xAxis: { ...baseCategoryXAxis, data: [], axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
      yAxis: { ...baseValueYAxis, name: '发电量（亿kWh）', nameTextStyle: { color: TEXT_SECONDARY, fontSize: 9 }, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
      series: [],
    }
  }

  const colors = ['rgba(0,175,255,0.15)', 'rgba(0,175,255,0.25)', 'rgba(0,175,255,0.4)', 'rgba(0,175,255,0.6)', 'rgba(0,175,255,0.9)']
  const legends: string[] = []
  const series: any[] = []

  const snapshots = history.slice(-5)
  snapshots.forEach((snap, idx) => {
    const label = `第${snap.iteration}代`
    legends.push(label)
    series.push({
      name: label,
      type: 'scatter',
      data: snap.points,
      symbolSize: 6,
      itemStyle: { color: colors[idx % colors.length] },
    })
  })

  return {
    tooltip: {
      ...baseTooltip,
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        return `${p.seriesName}<br/>缺水量: ${p.value[0]} 亿m³<br/>发电量: ${p.value[1]} 亿kWh`
      }
    },
    legend: { data: legends, textStyle: { color: TEXT_SECONDARY, fontSize: 9 }, top: 0 },
    grid: createGrid(32, 20, 46, 12),
    xAxis: { ...baseCategoryXAxis, name: '缺水量（亿m³）', nameTextStyle: { color: TEXT_SECONDARY, fontSize: 9 }, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
    yAxis: { ...baseValueYAxis, name: '发电量（亿kWh）', nameTextStyle: { color: TEXT_SECONDARY, fontSize: 9 }, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
    series: series,
  }
})

const buildReservoirOption = (reservoirKey: 'lyx' | 'ljx') => {
  const tab = activeRightTab.value
  const name = reservoirKey === 'lyx' ? '龙羊峡' : '刘家峡'
  const lineColor = reservoirKey === 'lyx' ? SERIES_COLORS[0] : SERIES_COLORS[1]

  if (tab === 'water') {
    const d = scenarioData.value.waterLevelData
    const r = reservoirKey === 'lyx' ? d.longyang : d.liujia
    const [yMin, yMax] = reservoirKey === 'lyx' ? [2530, 2600] : [1690, 1735]
    return {
      tooltip: { ...baseTooltip },
      title: { text: name, left: 'center', top: 2, textStyle: { color: TEXT_SECONDARY, fontSize: 11, fontWeight: 600 } },
      grid: createGrid(42, 18, 42, 20),
      xAxis: { ...baseCategoryXAxis, data: d.dates, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
      yAxis: { ...baseValueYAxis, name: '水位（m）', min: yMin, max: yMax, nameTextStyle: { color: TEXT_SECONDARY, fontSize: 9 }, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
      dataZoom: [{ type: 'inside', start: 0, end: 100, minValueSpan: 10 }],
      series: [
        { name: '优化水位', type: 'line', data: r.optimal, smooth: true, symbol: 'none', lineStyle: { width: 2, color: lineColor } },
      ],
    }
  } else if (tab === 'discharge') {
    const d = scenarioData.value.dischargeData
    const r = reservoirKey === 'lyx' ? d.longyang : d.liujia
    return {
      tooltip: { ...baseTooltip },
      title: { text: name, left: 'center', top: 2, textStyle: { color: TEXT_SECONDARY, fontSize: 11, fontWeight: 600 } },
      grid: createGrid(42, 18, 46, 20),
      xAxis: { ...baseCategoryXAxis, data: d.dates, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
      yAxis: { ...baseValueYAxis, name: '流量（m³/s）', nameTextStyle: { color: TEXT_SECONDARY, fontSize: 9 }, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
      dataZoom: [{ type: 'inside', start: 0, end: 100, minValueSpan: 10 }],
      series: [
        { name: '优化下泄流量', type: 'line', data: r.optimal, smooth: true, symbol: 'none', lineStyle: { width: 2, color: lineColor } },
      ],
    }
  } else {
    const d = scenarioData.value.powerOutputData
    const r = reservoirKey === 'lyx' ? d.longyang : d.liujia
    return {
      tooltip: { ...baseTooltip },
      title: { text: name, left: 'center', top: 2, textStyle: { color: TEXT_SECONDARY, fontSize: 11, fontWeight: 600 } },
      grid: createGrid(42, 18, 46, 20),
      xAxis: { ...baseCategoryXAxis, data: d.dates, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
      yAxis: { ...baseValueYAxis, name: '出力（MW）', nameTextStyle: { color: TEXT_SECONDARY, fontSize: 9 }, axisLabel: { color: TEXT_SECONDARY, fontSize: 9 } },
      dataZoom: [{ type: 'inside', start: 0, end: 100, minValueSpan: 10 }],
      series: [
        { name: '优化出力', type: 'line', data: r.optimal, smooth: true, symbol: 'none', lineStyle: { width: 2, color: lineColor } },
      ],
    }
  }
}

const lyxOption = computed(() => buildReservoirOption('lyx'))
const ljxOption = computed(() => buildReservoirOption('ljx'))

// ── 生命周期 ──
onMounted(() => {
  connectWebSocket()
  elapsedTimer = setInterval(() => {
    if (status.value === '运行中' && progress.value > 0 && progress.value < 100) {
      elapsedSec.value++
    }
  }, 1000)
})

onUnmounted(() => {
  if (elapsedTimer) clearInterval(elapsedTimer)
  if (ws) { ws.onclose = null; ws.close(); ws = null }
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
          <StatusTag
            :label="status"
            :color="statusColor"
            :pulse="status === '运行中'"
          />
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
            <BaseChart :option="convergenceOption" class="chart-container-sm" />
          </div>
          <div class="chart-card">
            <div class="chart-card-header"><span class="chart-label">Pareto前沿演化</span></div>
            <BaseChart :option="objectiveOption" class="chart-container-sm" />
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
            <BaseChart :option="lyxOption" class="chart-container-md" />
          </div>
          <div class="right-chart-wrap">
            <BaseChart :option="ljxOption" class="chart-container-md" />
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
            <span class="info-label">子系统协同度</span>
            <span class="info-value" style="color:var(--tech-cyan);">{{
              latestCoordination.h_water > 0 && latestCoordination.h_ele > 0
                ? Math.pow(latestCoordination.h_water * latestCoordination.h_ele * Math.max(latestCoordination.h_sed, 0.01) * latestCoordination.h_eco, 0.25).toFixed(3)
                : '--'
            }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">缺水量最优值</span>
            <span class="info-value" style="color:#00ff88;">{{ latestBestObjectives[0]?.toFixed(2) || '--' }} 亿m³</span>
          </div>
          <div class="info-item">
            <span class="info-label">发电量最优值</span>
            <span class="info-value" style="color:#f0a020;">{{ latestBestObjectives[1]?.toFixed(2) || '--' }} 亿kWh</span>
          </div>
          <div class="info-item">
            <span class="info-label">生态目标值</span>
            <span class="info-value" style="color:var(--tech-blue);">{{ latestCoordination.h_eco.toFixed(3) }}</span>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="约束满足情况" class="bottom-card">
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">供水保证率</span>
            <span class="constraint-status" :style="{ color: constraintColor(latestConstraint.water_guarantee) }">{{ latestConstraint.water_guarantee }}%</span>
          </div>
          <div class="info-item">
            <span class="info-label">生态需水率</span>
            <span class="constraint-status" :style="{ color: constraintColor(latestConstraint.eco_guarantee) }">{{ latestConstraint.eco_guarantee }}%</span>
          </div>
          <div class="info-item">
            <span class="info-label">出力保证率</span>
            <span class="constraint-status" :style="{ color: constraintColor(latestConstraint.power_guarantee) }">{{ latestConstraint.power_guarantee }}%</span>
          </div>
          <div class="info-item">
            <span class="info-label">综合约束率</span>
            <span class="constraint-status" :style="{ color: constraintColor(latestConstraint.combined_rate) }">{{ latestConstraint.combined_rate }}%</span>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="全系列评估摘要" class="bottom-card">
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">年均缺水量</span>
            <span class="info-value" style="color:#f0a020;">{{ latestBestObjectives[0]?.toFixed(2) || '--' }} 亿m³</span>
          </div>
          <div class="info-item">
            <span class="info-label">年均发电量</span>
            <span class="info-value" style="color:#00ff88;">{{ latestBestObjectives[1]?.toFixed(2) || '--' }} 亿kWh</span>
          </div>
          <div class="info-item">
            <span class="info-label">供水保证率</span>
            <span class="info-value" style="color:var(--tech-cyan);">{{ latestConstraint.water_guarantee }}%</span>
          </div>
          <div class="info-item">
            <span class="info-label">Pareto 解集数</span>
            <span class="info-value" style="color:var(--tech-blue);">{{ latestParetoSize }}</span>
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
  background: rgba(var(--tech-bg-rgb), 0.92);
}

/* ── 方案情景选择区 ── */
.scenario-section {
  display: flex;
  gap: 0;
  flex-shrink: 0;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
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
  border-right: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  border-radius: 0;
  cursor: pointer;
  transition: all 0.25s;
}
.scenario-card:last-child {
  border-right: none;
}
.scenario-card:hover {
  background: rgba(var(--tech-blue-rgb), 0.04);
}
.scenario-card.active {
  background: rgba(var(--tech-blue-rgb), 0.06);
  border-bottom: 2px solid rgba(var(--tech-cyan-rgb), 0.5);
}
.scenario-radio { display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.radio-dot {
  width: 14px; height: 14px; border-radius: 50%;
  border: 2px solid rgba(50, 150, 255, 0.4);
  transition: all 0.25s; display: block;
}
.radio-dot.active {
  border-color: var(--tech-blue); background: var(--tech-blue);
  box-shadow: 0 0 6px rgba(var(--tech-blue-rgb), 0.5);
}
.scenario-info { display: flex; flex-direction: column; gap: 2px; }
.scenario-name { font-size: 14px; font-weight: 600; color: var(--tech-text-primary); }
.scenario-taskId { font-size: 11px; color: var(--tech-text-placeholder); }

/* ── 状态栏 ── */
.status-bar {
  display: flex; flex-direction: column; gap: 4px;
  padding: 6px 10px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  border-radius: 0;
  flex-shrink: 0;
}
.status-bar-title {
  font-size: 13px; font-weight: 600; color: var(--tech-text-secondary); letter-spacing: 0.5px;
}
.status-fields { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.status-field { display: flex; align-items: center; gap: 4px; }
.field-label { font-size: 11px; color: var(--tech-text-secondary); white-space: nowrap; }
.field-value { font-size: 12px; color: var(--tech-text-regular); display: flex; align-items: center; gap: 4px; }
.progress-field { flex: 1; min-width: 200px; }
.progress-wrapper { display: flex; align-items: center; gap: 8px; flex: 1; }
.progress-bar { flex:1; height:6px; background:rgba(50,150,255,0.15); border-radius:3px; overflow:hidden; min-width:80px; }
.progress-fill { height:100%; background:linear-gradient(90deg,#0088cc,var(--tech-blue)); border-radius:3px; transition:width 1s ease; }
.progress-text { font-size:13px; color:var(--tech-blue); font-weight:600; min-width:48px; }

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
  border-right: 1px solid rgba(var(--tech-blue-rgb), 0.1);
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
  color: var(--tech-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}
.right-tab-btn:hover {
  color: var(--tech-text-regular);
  border-bottom-color: rgba(var(--tech-blue-rgb), 0.3);
}
.right-tab-btn.active {
  color: var(--tech-blue);
  border-bottom-color: rgba(var(--tech-cyan-rgb), 0.6);
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
  color: var(--tech-text-secondary);
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
  border-top: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  padding-top: 8px;
}
.bottom-card {
  flex: 1;
  min-width: 0;
  border-right: 1px solid rgba(var(--tech-blue-rgb), 0.08);
}
.bottom-card:last-child {
  border-right: none;
}
.bottom-card :deep(.section-header) {
  padding: 1px 6px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.12);
}
.bottom-card :deep(.section-title) {
  font-size: 10px;
  font-weight: 600;
  color: var(--tech-text-secondary);
  letter-spacing: 0;
}
.bottom-card :deep(.section-body) { padding: 2px 6px; }
.log-card { flex: 1.2; }
.log-list { display: flex; flex-direction: column; gap: 1px; }
.log-entry {
  display: flex; gap: 4px;
  font-size: 10px; line-height: 1.3;
  font-family: 'Courier New', monospace;
}
.log-time { color: var(--tech-text-placeholder); flex-shrink: 0; }
.log-level { color: var(--tech-blue); flex-shrink: 0; font-weight: 600; }
.log-msg { color: var(--tech-text-regular); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 6px; }
.info-item { display: flex; justify-content: space-between; align-items: center; padding: 0; }
.info-label { font-size: 10px; color: var(--tech-text-secondary); }
.info-value { font-size: 10px; color: var(--tech-text-primary); font-weight: 600; }
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
  color: var(--tech-text-regular);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.op-btn:hover { border-color: rgba(50,150,255,0.5); background: rgba(6,30,70,0.9); }
.op-btn.primary { border-color: rgba(0,175,255,0.4); color: var(--tech-blue); }
.op-btn.primary:hover { background: rgba(0,175,255,0.12); border-color: rgba(0,175,255,0.6); }
.op-btn.danger { border-color: rgba(255,77,79,0.3); color: #ff6b6b; }
.op-btn.danger:hover { background: rgba(255,77,79,0.1); border-color: rgba(255,77,79,0.5); }

/* ── Scrollbar ── */
.process-transparent-view::-webkit-scrollbar { width: 4px; }
.process-transparent-view::-webkit-scrollbar-track { background: transparent; }
.process-transparent-view::-webkit-scrollbar-thumb { background: rgba(50,150,255,0.2); border-radius: 2px; }
</style>
