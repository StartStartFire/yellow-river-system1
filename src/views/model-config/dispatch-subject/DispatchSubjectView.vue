<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import ModelConfigFooter from '@/components/model-config/ModelConfigFooter.vue'
import { useModelConfigStore } from '@/stores/modelConfig'
import {
  subjectReservoirGroups,
  scenarioToSubjectDefaults,
  scenarioCategoryConstraints,
  reservoirNameMap,
} from '@/mock/modelConfig'
import { metricsMap, reservoirGroups as basicDataGroups } from '@/mock/basicData'
import type { MetricCardData } from '@/mock/basicData'

// ==================== Store ====================
const store = useModelConfigStore()

// ==================== 弹窗状态 ====================
const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)
const reservoirDialogVisible = ref(false)

// ==================== 路由 ====================
const router = useRouter()

// ==================== Step 1 场景信息 ====================
const subOptionId = computed(() => store.dispatchScenario.subOptionId)
const categoryId = computed(() => store.dispatchScenario.categoryId)

// 当前场景类别的约束
const categoryConstraint = computed(() => {
  return scenarioCategoryConstraints[categoryId.value] || null
})

// ==================== 表单状态 ====================
const startTime = ref('')
const endTime = ref('')
const timeStep = ref('每日')
const scheduleFrequency = ref('不限制')
const selectedReservoirIds = ref<string[]>([])
const selectedGroupId = ref('')

// 弹窗中暂存的水库勾选
const dialogReservoirIds = ref<string[]>([])

// ==================== 计算属性 ====================

/** 可用步长选项（根据场景大类过滤） */
const allowedTimeSteps = computed(() => {
  return categoryConstraint.value?.allowedTimeSteps || ['每日', '每旬', '每月']
})

/** 步长是否被锁定（实时调度只能每日） */
const isTimeStepLocked = computed(() => {
  return categoryId.value === 'realtime'
})

/** 总时段数 */
const totalPeriods = computed(() => {
  if (!startTime.value || !endTime.value) return 0
  const start = new Date(startTime.value)
  const end = new Date(endTime.value)
  const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
  if (diffDays < 0) return 0
  if (timeStep.value === '每日') return diffDays + 1
  if (timeStep.value === '每旬') return Math.ceil((diffDays + 1) / 10)
  if (timeStep.value === '每月') return Math.ceil((diffDays + 1) / 30)
  return diffDays + 1
})

/** 已选水库摘要文字 */
const selectedReservoirSummary = computed(() => {
  if (selectedReservoirIds.value.length === 0) return '未选择水库'
  const names = selectedReservoirIds.value
    .map(id => reservoirNameMap[id])
    .filter(Boolean)
  if (names.length <= 3) return names.join('、')
  return names.slice(0, 3).join('、') + ` 等 ${names.length} 座水库`
})

/** 预设组合列表 */
const groups = subjectReservoirGroups

/** 查找预设组合名称 */
const currentGroupName = computed(() => {
  if (!selectedGroupId.value) return ''
  const g = groups.find(g => g.id === selectedGroupId.value)
  return g ? g.name : ''
})

// ==================== 初始化/联动 ====================

/** 根据 Step 1 子选项自动预填 */
const applyDefaultsFromScenario = () => {
  const defaults = subOptionId.value ? scenarioToSubjectDefaults[subOptionId.value] : null
  if (defaults) {
    startTime.value = defaults.startTime
    endTime.value = defaults.endTime
    timeStep.value = defaults.timeStep
    scheduleFrequency.value = defaults.scheduleFrequency
    selectedReservoirIds.value = [...defaults.reservoirIds]
    // 自动匹配预设组合
    matchGroupFromReservoirs(defaults.reservoirIds)
  }
}

/** 根据水库ID列表自动匹配预设组合 */
const matchGroupFromReservoirs = (ids: string[]) => {
  const sortedIds = [...ids].sort()
  const matched = groups.find(g => {
    const gIds = [...g.reservoirIds].sort()
    return sortedIds.length === gIds.length && sortedIds.every((id, i) => id === gIds[i])
  })
  selectedGroupId.value = matched ? matched.id : ''
}

// ==================== 交互 ====================

/** 点击预设组合卡片 */
const handleSelectGroup = (groupId: string) => {
  if (selectedGroupId.value === groupId) {
    // 取消选中 - 不清空水库
    selectedGroupId.value = ''
    return
  }
  const group = groups.find(g => g.id === groupId)
  if (group) {
    selectedGroupId.value = groupId
    selectedReservoirIds.value = [...group.reservoirIds]
  }
}

/** 打开水库弹窗 */
const handleOpenReservoirDialog = () => {
  dialogReservoirIds.value = [...selectedReservoirIds.value]
  reservoirDialogVisible.value = true
}

/** 弹窗确认 */
const confirmReservoirDialog = () => {
  reservoirDialogVisible.value = false
  selectedReservoirIds.value = [...dialogReservoirIds.value]
  // 取消预设组合选中态
  selectedGroupId.value = ''
}

/** 弹窗取消 */
const cancelReservoirDialog = () => {
  reservoirDialogVisible.value = false
}

/** 切换步长 */
const handleTimeStepChange = (val: string) => {
  timeStep.value = val
}

/** 时间范围校验 */
const validateTimeRange = (): string | null => {
  if (!startTime.value || !endTime.value) return '请选择调度起止时间'
  const start = new Date(startTime.value)
  const end = new Date(endTime.value)
  if (end < start) return '结束时间不能早于开始时间'
  const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))

  // 场景时长约束
  if (categoryConstraint.value) {
    if (diffDays > categoryConstraint.value.maxDays) {
      if (categoryId.value === 'multi-year') return '中长期调度时间跨度不能超过 5 年'
      if (categoryId.value === 'critical-period') return '关键期调度时间范围必须在同一年内，不能超过 365 天'
      if (categoryId.value === 'realtime') return '实时调度时间范围不能超过 31 天'
    }
    if (categoryId.value === 'multi-year' && diffDays < 365) {
      return '中长期调度时间跨度应不少于 1 年'
    }
    if (categoryId.value === 'critical-period') {
      const startYear = start.getFullYear()
      const endYear = end.getFullYear()
      if (startYear !== endYear) return '关键期调度起止时间必须在同一年内'
    }
  }
  return null
}

/** 步长校验 */
const validateTimeStep = (): string | null => {
  if (categoryId.value === 'multi-year' && timeStep.value === '每日') {
    return '中长期调度不支持日步长，请选择每旬或每月'
  }
  if (categoryId.value === 'critical-period' && timeStep.value === '每日') {
    return '关键期调度不支持日步长，请选择每旬或每月'
  }
  return null
}

/** 水库校验 */
const validateReservoir = (): string | null => {
  if (selectedReservoirIds.value.length === 0) return '请至少选择一个参与调度的水库'
  return null
}

// ==================== 按钮操作 ====================

const handlePrev = () => {
  router.push('/model-config/dispatch-scenario')
}

const handleSave = () => {
  saveDialogVisible.value = true
}

const handleCancel = () => {
  cancelDialogVisible.value = true
}

const confirmSave = () => {
  saveDialogVisible.value = false
  store.setDispatchSubject({
    startTime: startTime.value,
    endTime: endTime.value,
    timeStep: timeStep.value,
    scheduleFrequency: scheduleFrequency.value,
    selectedReservoirIds: selectedReservoirIds.value,
    selectedGroupId: selectedGroupId.value,
  })
  ElMessage.success('调度主体配置已保存')
}

const confirmCancel = () => {
  cancelDialogVisible.value = false
  // 重置为初始值
  applyDefaultsFromScenario()
  ElMessage.info('已取消，未保存任何更改')
}

const handleNext = () => {
  // 校验
  const timeErr = validateTimeRange()
  if (timeErr) {
    ElMessage.warning(timeErr)
    return
  }
  const stepErr = validateTimeStep()
  if (stepErr) {
    ElMessage.warning(stepErr)
    return
  }
  const resErr = validateReservoir()
  if (resErr) {
    ElMessage.warning(resErr)
    return
  }

  // 写入 Store
  store.setDispatchSubject({
    startTime: startTime.value,
    endTime: endTime.value,
    timeStep: timeStep.value,
    scheduleFrequency: scheduleFrequency.value,
    selectedReservoirIds: selectedReservoirIds.value,
    selectedGroupId: selectedGroupId.value,
  })
  store.markStepCompleted(2)
  router.push('/model-config/model-data')
}

// ==================== 水库状态数据 ====================
type MetricsMap = Record<string, Record<string, MetricCardData>>

const reservoirMetrics = (metricsMap as MetricsMap)

/** 按区域分组的水库列表（与基础数据保持一致） */
const reservoirGroups = computed(() => {
  return basicDataGroups.data.map(group => ({
    name: group.name,
    items: group.items.map(item => ({
      ...item,
      fullName: reservoirNameMap[item.id] || item.name,
    })),
  }))
})

const getReservoirStatus = (id: string): { label: string; color: string } => {
  const statusMap: Record<string, { label: string; color: string }> = {
    longyangxia: { label: '正常', color: '#00ff88' },
    liujiaxia: { label: '正常', color: '#00ff88' },
    gongboxia: { label: '关注', color: '#ffaa00' },
    jishixia: { label: '正常', color: '#00ff88' },
    qingtongxia: { label: '正常', color: '#00ff88' },
    yangqu: { label: '正常', color: '#00ff88' },
    banduo: { label: '正常', color: '#00ff88' },
    cihaxia: { label: '正常', color: '#00ff88' },
    maerdang: { label: '正常', color: '#00ff88' },
    xiaoxia: { label: '正常', color: '#00ff88' },
    daxia: { label: '正常', color: '#00ff88' },
    wujinxia: { label: '正常', color: '#00ff88' },
    heishanxia: { label: '正常', color: '#00ff88' },
  }
  return statusMap[id] || { label: '正常', color: '#00ff88' }
}

// ==================== 生命周期 ====================
onMounted(() => {
  // 如果已有保存的状态，恢复
  if (store.dispatchSubject.startTime) {
    startTime.value = store.dispatchSubject.startTime
    endTime.value = store.dispatchSubject.endTime
    timeStep.value = store.dispatchSubject.timeStep
    scheduleFrequency.value = store.dispatchSubject.scheduleFrequency
    selectedReservoirIds.value = [...store.dispatchSubject.selectedReservoirIds]
    selectedGroupId.value = store.dispatchSubject.selectedGroupId
  } else {
    // 否则从 Step 1 联动预填
    applyDefaultsFromScenario()
  }
})
</script>

<template>
  <div class="dispatch-subject-view">
    <!-- 步骤条 -->
    <ModelConfigStepBar :current-step="2" version="new" />

    <!-- 主体 -->
    <div class="main-content">
      <!-- 上半区：调度时段与周期 -->
      <div class="section-title-row">
        <div class="section-accent"></div>
        <span class="section-title">调度时段与周期</span>
        <span class="section-hint">设定本次调度的时间范围与计算精度</span>
      </div>

      <div class="period-grid">
        <!-- 调度起止时间 -->
        <div class="param-card">
          <div class="param-label">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="param-icon">
              <rect x="2" y="3" width="12" height="11" rx="2" stroke="currentColor" stroke-width="1.3" fill="none"/>
              <path d="M5 1v4M11 1v4M2 7h12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            调度起止时间
          </div>
          <el-date-picker
            v-model="startTime"
            type="date"
            placeholder="开始日期"
            class="date-picker-half"
            value-format="YYYY-MM-DD"
          />
          <span class="date-separator">~</span>
          <el-date-picker
            v-model="endTime"
            type="date"
            placeholder="结束日期"
            class="date-picker-half"
            value-format="YYYY-MM-DD"
          />
        </div>

        <!-- 时间步长 -->
        <div class="param-card">
          <div class="param-label">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="param-icon">
              <circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.3" fill="none"/>
              <path d="M8 5v3.5H11" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            时间步长
            <span v-if="isTimeStepLocked" class="lock-badge">锁定</span>
          </div>
          <el-select
            v-model="timeStep"
            :disabled="isTimeStepLocked"
            class="param-select"
            @change="handleTimeStepChange"
          >
            <el-option
              v-for="ts in allowedTimeSteps"
              :key="ts"
              :label="ts"
              :value="ts"
            />
          </el-select>
          <div v-if="isTimeStepLocked" class="param-hint">实时调度仅支持日步长</div>
        </div>

        <!-- 调度频率 -->
        <div class="param-card">
          <div class="param-label">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="param-icon">
              <path d="M2 8h12M8 2v12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.3" fill="none"/>
            </svg>
            调度频率
          </div>
          <el-select v-model="scheduleFrequency" class="param-select">
            <el-option label="每月一次" value="每月一次" />
            <el-option label="每旬一次" value="每旬一次" />
            <el-option label="每周一次" value="每周一次" />
            <el-option label="不限制" value="不限制" />
          </el-select>
        </div>

        <!-- 总时段数 -->
        <div class="param-card total-card">
          <div class="param-label">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="param-icon">
              <rect x="2" y="3" width="12" height="10" rx="1.5" stroke="currentColor" stroke-width="1.3" fill="none"/>
              <path d="M5 7h6M5 10h4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            总时段数
          </div>
          <div class="total-display">
            <span class="total-number">{{ totalPeriods }}</span>
            <span class="total-unit">时段</span>
          </div>
        </div>
      </div>

      <!-- 下半区：水库选择 -->
      <div class="section-title-row">
        <div class="section-accent"></div>
        <span class="section-title">参与调度水库</span>
        <span class="section-hint">选择参与本次调度的水库</span>
      </div>

      <div class="reservoir-section">
        <!-- 预设组合卡片 -->
        <div class="group-cards">
          <div
            v-for="group in groups"
            :key="group.id"
            class="group-card"
            :class="{ 'group-selected': selectedGroupId === group.id }"
            @click="handleSelectGroup(group.id)"
          >
            <div v-if="selectedGroupId === group.id" class="group-check">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="7" fill="rgba(0,175,255,0.2)" stroke="#00afff" stroke-width="1.5"/>
                <path d="M5 8.5l2 2 4-4.5" stroke="#00afff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="group-name">{{ group.name }}</div>
            <div class="group-desc">{{ group.description }}</div>
            <div class="group-count">{{ group.reservoirIds.length }} 座水库</div>
          </div>

          <!-- 更多组合入口 -->
          <div class="group-card group-more" @click="handleOpenReservoirDialog">
            <div class="more-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="5" r="2" fill="currentColor"/>
                <circle cx="12" cy="12" r="2" fill="currentColor"/>
                <circle cx="12" cy="19" r="2" fill="currentColor"/>
              </svg>
            </div>
            <div class="group-name">更多组合</div>
            <div class="group-desc">自定义勾选水库</div>
          </div>
        </div>

        <!-- 已选摘要 -->
        <div class="selected-summary">
          <div class="summary-left">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="summary-icon">
              <path d="M3 8.5L6 11.5L13 4.5" stroke="#00afff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="summary-label">当前已选：</span>
            <span class="summary-reservoirs">{{ selectedReservoirSummary }}</span>
          </div>
          <div class="summary-right">
            <span class="summary-count">共 {{ selectedReservoirIds.length }} 座水库</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <ModelConfigFooter
      :step="2"
      @cancel="handleCancel"
      @save="handleSave"
      @prev="handlePrev"
      @next="handleNext"
    />
  </div>

  <!-- ===== 水库多选弹窗 ===== -->
  <el-dialog
    v-model="reservoirDialogVisible"
    title="参与调度的水库"
    width="520px"
    :close-on-click-modal="false"
    class="reservoir-dialog"
  >
    <div class="dialog-reservoir-list">
      <template v-for="group in reservoirGroups" :key="group.name">
        <div class="dialog-group-header">
          <span class="dialog-group-line"></span>
          <span class="dialog-group-name">{{ group.name }}</span>
          <span class="dialog-group-line"></span>
        </div>
        <div
          v-for="res in group.items"
          :key="res.id"
          class="dialog-reservoir-item"
          :class="{ 'item-checked': dialogReservoirIds.includes(res.id) }"
          @click="
            dialogReservoirIds.includes(res.id)
              ? dialogReservoirIds = dialogReservoirIds.filter(id => id !== res.id)
              : dialogReservoirIds.push(res.id)
          "
        >
          <div class="item-checkbox" :class="{ 'checkbox-checked': dialogReservoirIds.includes(res.id) }">
            <svg v-if="dialogReservoirIds.includes(res.id)" width="12" height="12" viewBox="0 0 16 16" fill="none">
              <path d="M3 8.5L6 11.5L13 4.5" stroke="#00afff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="item-info">
            <span class="item-name">{{ res.fullName }}</span>
            <span class="item-meta">
              水位 {{ reservoirMetrics[res.id]?.waterLevel?.value ?? '--' }}m
            </span>
            <span class="item-meta">
              入库 {{ reservoirMetrics[res.id]?.inflow?.value ?? '--' }}m³/s
            </span>
          </div>
          <div
            class="item-status"
            :style="{ color: getReservoirStatus(res.id).color }"
          >
            {{ getReservoirStatus(res.id).label }}
          </div>
        </div>
      </template>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button size="small" @click="cancelReservoirDialog">取消</el-button>
        <el-button type="primary" size="small" @click="confirmReservoirDialog">确认</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- ===== 保存确认弹窗 ===== -->
  <el-dialog
    v-model="saveDialogVisible"
    title="保存确认"
    width="400px"
    :close-on-click-modal="false"
    class="confirm-dialog"
  >
    <div class="dialog-body">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
        <circle cx="24" cy="24" r="22" stroke="#00afff" stroke-width="2" fill="rgba(0,175,255,0.1)"/>
        <path d="M16 24l6 6 10-10" stroke="#00afff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <div class="dialog-text">
        <span class="dialog-title-main">确认保存当前调度主体配置？</span>
        <span class="dialog-desc">保存后调度时段与水库选择将保留。</span>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button size="small" @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" size="small" @click="confirmSave">确认保存</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- ===== 取消确认弹窗 ===== -->
  <el-dialog
    v-model="cancelDialogVisible"
    title="取消确认"
    width="400px"
    :close-on-click-modal="false"
    class="confirm-dialog"
  >
    <div class="dialog-body">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
        <circle cx="24" cy="24" r="22" stroke="#f0a020" stroke-width="2" fill="rgba(240,160,32,0.1)"/>
        <path d="M16 16l16 16M32 16l-16 16" stroke="#f0a020" stroke-width="2.5" stroke-linecap="round"/>
      </svg>
      <div class="dialog-text">
        <span class="dialog-title-main">确认取消当前操作？</span>
        <span class="dialog-desc">取消后当前页面的更改将不会保存。</span>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button size="small" @click="cancelDialogVisible = false">继续编辑</el-button>
        <el-button type="warning" size="small" @click="confirmCancel">确认取消</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.dispatch-subject-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 8px 12px;
  gap: 8px;
  overflow: hidden;
}

/* ===== 主体 ===== */
.main-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
  padding-right: 2px;
}

.main-content::-webkit-scrollbar {
  width: 4px;
}
.main-content::-webkit-scrollbar-track {
  background: transparent;
}
.main-content::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.2);
  border-radius: 2px;
}

/* ===== 分区标题 ===== */
.section-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  padding-top: 2px;
}

.section-accent {
  width: 3px;
  height: 18px;
  background: linear-gradient(180deg, #00d4ff, rgba(0, 212, 255, 0.3));
  border-radius: 2px;
  flex-shrink: 0;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #e0e6ed;
}

.section-hint {
  font-size: 12px;
  color: #5a6f83;
  margin-left: 4px;
}

/* ===== 上半区：参数卡片网格 ===== */
.period-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  flex-shrink: 0;
}

.param-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 18px;
  background: rgba(6, 30, 70, 0.5);
  border: 1px solid rgba(50, 150, 255, 0.25);
  border-radius: 10px;
  flex-wrap: wrap;
}

.param-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #7a8fa3;
  white-space: nowrap;
  width: 100%;
  margin-bottom: 2px;
}

.param-icon {
  color: #5a8abf;
  flex-shrink: 0;
}

.lock-badge {
  font-size: 9px;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(240, 160, 32, 0.15);
  color: #f0a020;
  font-weight: 600;
  margin-left: auto;
}

.param-select {
  width: 160px;
}

.date-picker-half {
  width: calc(50% - 24px);
  min-width: 0;
  flex: 1;
}

.date-separator {
  color: #5a6f83;
  font-size: 12px;
  flex-shrink: 0;
}

.param-hint {
  width: 100%;
  font-size: 10px;
  color: #f0a020;
  margin-top: -2px;
}

/* 总时段数卡片 */
.total-card {
  display: flex;
  align-items: center;
}

.total-display {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-left: auto;
}

.total-number {
  font-size: 28px;
  font-weight: 700;
  color: #e0e6ed;
  font-variant-numeric: tabular-nums;
  letter-spacing: 1px;
}

.total-unit {
  font-size: 13px;
  color: #7a8fa3;
}

/* ===== 下半区：水库选择 ===== */
.reservoir-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  min-height: 0;
}

/* 预设组合卡片 */
.group-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.group-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 20px 12px;
  background: rgba(6, 30, 70, 0.5);
  border: 1px solid rgba(50, 150, 255, 0.25);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  text-align: center;
  min-height: 100px;
}

.group-card:hover {
  border-color: rgba(0, 175, 255, 0.35);
  background: rgba(0, 175, 255, 0.03);
}

.group-card.group-selected {
  border-color: rgba(0, 175, 255, 0.6);
  background: rgba(0, 175, 255, 0.06);
  box-shadow: 0 0 16px rgba(0, 175, 255, 0.12);
}

.group-check {
  position: absolute;
  top: 6px;
  right: 6px;
  animation: checkPop 0.25s ease;
}

@keyframes checkPop {
  0% { transform: scale(0); opacity: 0; }
  60% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}

.group-name {
  font-size: 16px;
  font-weight: 600;
  color: #c0c8d4;
  transition: color 0.2s;
}

.group-selected .group-name {
  color: #e0e6ed;
}

.group-desc {
  font-size: 12px;
  color: #5a6f83;
}

.group-count {
  font-size: 13px;
  color: #5a8abf;
  margin-top: 4px;
  font-weight: 500;
}

/* 更多组合卡片 */
.group-more {
  border-style: dashed;
  border-color: rgba(50, 150, 255, 0.2);
  cursor: pointer;
}

.group-more:hover {
  border-color: rgba(0, 175, 255, 0.4);
  background: rgba(0, 175, 255, 0.05);
}

.more-icon {
  color: #5a8abf;
  margin-bottom: 2px;
}

/* 已选摘要 */
.selected-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: rgba(6, 30, 70, 0.4);
  border: 1px solid rgba(50, 150, 255, 0.15);
  border-radius: 8px;
  flex-shrink: 0;
}

.summary-left {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.summary-icon {
  flex-shrink: 0;
}

.summary-label {
  font-size: 13px;
  color: #7a8fa3;
  white-space: nowrap;
}

.summary-reservoirs {
  font-size: 13px;
  color: #00d4ff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-right {
  flex-shrink: 0;
}

.summary-count {
  font-size: 13px;
  color: #5a6f83;
}

/* ===== 弹窗：水库多选 ===== */
.reservoir-dialog :deep(.el-dialog) {
  background: rgba(6, 30, 70, 0.98) !important;
  border: 1px solid rgba(50, 150, 255, 0.4);
  border-radius: 12px;
}

.reservoir-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  padding: 16px 20px;
  margin: 0;
}

.reservoir-dialog :deep(.el-dialog__title) {
  color: #e0e6ed;
  font-size: 15px;
  font-weight: 600;
}

.reservoir-dialog :deep(.el-dialog__body) {
  padding: 16px 20px;
}

.reservoir-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid rgba(50, 150, 255, 0.1);
  padding: 12px 20px;
}

.dialog-reservoir-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dialog-group-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0 6px;
}

.dialog-group-header:first-child {
  padding-top: 0;
}

.dialog-group-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(50, 150, 255, 0.25), transparent);
}

.dialog-group-name {
  font-size: 11px;
  font-weight: 600;
  color: #5a8abf;
  white-space: nowrap;
  letter-spacing: 1px;
}

.dialog-reservoir-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.dialog-reservoir-item:hover {
  background: rgba(0, 175, 255, 0.04);
}

.dialog-reservoir-item.item-checked {
  background: rgba(0, 175, 255, 0.06);
  border-color: rgba(0, 175, 255, 0.15);
}

.item-checkbox {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 2px solid rgba(80, 100, 120, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.item-checkbox.checkbox-checked {
  border-color: #00afff;
  background: rgba(0, 175, 255, 0.15);
}

.item-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.item-name {
  font-size: 13px;
  font-weight: 600;
  color: #c0c8d4;
  min-width: 80px;
}

.item-meta {
  font-size: 11px;
  color: #5a6f83;
}

.item-status {
  font-size: 11px;
  font-weight: 500;
  flex-shrink: 0;
}

/* ===== 弹窗通用 ===== */
.confirm-dialog :deep(.el-dialog) {
  background: rgba(6, 30, 70, 0.98) !important;
  border: 1px solid rgba(50, 150, 255, 0.4);
  border-radius: 12px;
}

.confirm-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  padding: 16px 20px;
  margin: 0;
}

.confirm-dialog :deep(.el-dialog__title) {
  color: #e0e6ed;
  font-size: 15px;
  font-weight: 600;
}

.confirm-dialog :deep(.el-dialog__body) {
  padding: 24px 20px;
}

.confirm-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid rgba(50, 150, 255, 0.1);
  padding: 12px 20px;
}

.dialog-body {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.dialog-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.dialog-text {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.dialog-title-main {
  color: #e0e6ed;
  font-size: 14px;
  font-weight: 500;
}

.dialog-desc {
  color: #7a8fa3;
  font-size: 12px;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* ===== Element Plus 深色覆盖 ===== */
:deep(.el-button) {
  --el-button-bg-color: transparent;
  --el-button-border-color: rgba(50, 150, 255, 0.3);
  --el-button-text-color: #c0c8d4;
  --el-button-hover-bg-color: rgba(0, 175, 255, 0.1);
  --el-button-hover-border-color: rgba(50, 150, 255, 0.5);
  --el-button-hover-text-color: #e0e6ed;
}

:deep(.el-button--primary) {
  --el-button-bg-color: rgba(0, 175, 255, 0.2);
  --el-button-border-color: rgba(0, 175, 255, 0.5);
  --el-button-text-color: #00d4ff;
  --el-button-hover-bg-color: rgba(0, 175, 255, 0.3);
  --el-button-hover-border-color: rgba(0, 175, 255, 0.7);
  --el-button-hover-text-color: #00e5ff;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-date-editor) {
  background: transparent !important;
}

:deep(.el-input__wrapper) {
  background: rgba(2, 27, 63, 0.6) !important;
  box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.2) inset !important;
}

:deep(.el-input__inner) {
  color: #c0c8d4 !important;
  font-size: 12px;
}

:deep(.el-input__inner::placeholder) {
  color: #5a6f83;
}
</style>
