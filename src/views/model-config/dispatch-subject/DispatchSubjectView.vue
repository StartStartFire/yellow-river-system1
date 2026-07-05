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
} from '@/mock/model-config/dispatchSubject'
import { metricsMap, reservoirGroups as basicDataGroups } from '@/mock/basicData'
import type { MetricCardData } from '@/types/reservoir'

const store = useModelConfigStore()
const router = useRouter()

// 水库指标数据（用于展示水位和入库流量）
const reservoirMetrics = computed(() => {
  const map: Record<string, Record<string, MetricCardData>> = {}
  for (const [id, metrics] of Object.entries(metricsMap)) {
    map[id] = metrics
  }
  return map
})

const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)

// ==================== Step 1 ====================
const subOptionId = computed(() => store.dispatchScenario.subOptionId)
const categoryId = computed(() => store.dispatchScenario.categoryId)
const categoryConstraint = computed(() => scenarioCategoryConstraints[categoryId.value] || null)

// ==================== 表单 ====================
const startTime = ref('')
const endTime = ref('')
const timeStep = ref('每日')
const scheduleFrequency = ref('每月一次')
const selectedReservoirIds = ref<string[]>([])
const selectedGroupId = ref('')

const allowedTimeSteps = computed(() => categoryConstraint.value?.allowedTimeSteps || ['每日', '每旬', '每月'])
const isTimeStepLocked = computed(() => categoryId.value === 'realtime')

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

const selectedReservoirSummary = computed(() => {
  if (selectedReservoirIds.value.length === 0) return '未选择水库'
  const names = selectedReservoirIds.value.map(id => reservoirNameMap[id]).filter(Boolean)
  if (names.length <= 3) return names.join('、')
  return names.slice(0, 3).join('、') + ` 等 ${names.length} 座水库`
})

const groups = subjectReservoirGroups

const currentGroupName = computed(() => {
  if (!selectedGroupId.value) return ''
  const g = groups.find(g => g.id === selectedGroupId.value)
  return g ? g.name : ''
})

// ==================== 联动 ====================
const applyDefaultsFromScenario = () => {
  const defaults = subOptionId.value ? scenarioToSubjectDefaults[subOptionId.value] : null
  if (defaults) {
    startTime.value = defaults.startTime
    endTime.value = defaults.endTime
    timeStep.value = defaults.timeStep
    scheduleFrequency.value = defaults.scheduleFrequency
    selectedReservoirIds.value = [...defaults.reservoirIds]
    matchGroupFromReservoirs(defaults.reservoirIds)
  }
}

const matchGroupFromReservoirs = (ids: string[]) => {
  const sortedIds = [...ids].sort()
  const matched = groups.find(g => {
    const gIds = [...g.reservoirIds].sort()
    return sortedIds.length === gIds.length && sortedIds.every((id, i) => id === gIds[i])
  })
  selectedGroupId.value = matched ? matched.id : ''
}

// ==================== 水库操作 ====================
const handleSelectGroup = (groupId: string) => {
  if (selectedGroupId.value === groupId) {
    selectedGroupId.value = ''
    return
  }
  const group = groups.find(g => g.id === groupId)
  if (group) {
    selectedGroupId.value = groupId
    selectedReservoirIds.value = [...group.reservoirIds]
  }
}

const toggleReservoir = (id: string) => {
  const idx = selectedReservoirIds.value.indexOf(id)
  if (idx >= 0) {
    selectedReservoirIds.value.splice(idx, 1)
  } else {
    selectedReservoirIds.value.push(id)
  }
  matchGroupFromReservoirs(selectedReservoirIds.value)
}

const getReservoirStatus = (id: string): { label: string; color: string } => {
  const statusMap: Record<string, { label: string; color: string }> = {
    longyangxia: { label: '正常', color: '#00ff88' }, liujiaxia: { label: '正常', color: '#00ff88' },
    gongboxia: { label: '关注', color: 'var(--tech-orange)' }, jishixia: { label: '正常', color: '#00ff88' },
    qingtongxia: { label: '正常', color: '#00ff88' }, yangqu: { label: '正常', color: '#00ff88' },
    banduo: { label: '正常', color: '#00ff88' }, cihaxia: { label: '正常', color: '#00ff88' },
    maerdang: { label: '正常', color: '#00ff88' }, xiaoxia: { label: '正常', color: '#00ff88' },
    daxia: { label: '正常', color: '#00ff88' }, wujinxia: { label: '正常', color: '#00ff88' },
    heishanxia: { label: '正常', color: '#00ff88' },
  }
  return statusMap[id] || { label: '正常', color: '#00ff88' }
}

const reservoirGroups = computed(() => {
  return basicDataGroups.data.map(group => ({
    name: group.name,
    items: group.items.map(item => ({
      ...item,
      fullName: reservoirNameMap[item.id] || item.name,
      checked: selectedReservoirIds.value.includes(item.id),
    })),
  }))
})

// ==================== 校验 ====================
const validateTimeRange = (): string | null => {
  if (!startTime.value || !endTime.value) return '请选择调度起止时间'
  const start = new Date(startTime.value)
  const end = new Date(endTime.value)
  if (end < start) return '结束时间不能早于开始时间'
  const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
  if (categoryConstraint.value) {
    if (diffDays > categoryConstraint.value.maxDays) {
      if (categoryId.value === 'realtime') return '实时调度时间范围不能超过31天'
      if (categoryId.value === 'critical-period') return '关键期调度必须在同一年内'
      return '中长期调度时间跨度不能超过5年'
    }
    if (categoryId.value === 'multi-year' && diffDays < 365) return '中长期调度时间跨度应不少于1年'
    if (categoryId.value === 'critical-period') {
      if (start.getFullYear() !== end.getFullYear()) return '关键期调度起止时间必须在同一年内'
    }
  }
  return null
}

const validateTimeStep = (): string | null => {
  if (categoryId.value === 'multi-year' && timeStep.value === '每日') return '中长期调度不支持日步长'
  if (categoryId.value === 'critical-period' && timeStep.value === '每日') return '关键期调度不支持日步长'
  return null
}

const validateReservoir = (): string | null => {
  if (selectedReservoirIds.value.length === 0) return '请至少选择一个参与调度的水库'
  return null
}

// ==================== 按钮 ====================
const handlePrev = () => router.push('/model-config/dispatch-scenario')
const handleSave = () => { saveDialogVisible.value = true }
const handleCancel = () => { cancelDialogVisible.value = true }

const confirmSave = () => {
  saveDialogVisible.value = false
  store.setDispatchSubject({ startTime: startTime.value, endTime: endTime.value, timeStep: timeStep.value, scheduleFrequency: scheduleFrequency.value, selectedReservoirIds: selectedReservoirIds.value, selectedGroupId: selectedGroupId.value })
  ElMessage.success('调度主体配置已保存')
}

const confirmCancel = () => {
  cancelDialogVisible.value = false
  applyDefaultsFromScenario()
  ElMessage.info('已取消，未保存任何更改')
}

const handleNext = () => {
  const timeErr = validateTimeRange()
  if (timeErr) { ElMessage.warning(timeErr); return }
  const stepErr = validateTimeStep()
  if (stepErr) { ElMessage.warning(stepErr); return }
  const resErr = validateReservoir()
  if (resErr) { ElMessage.warning(resErr); return }
  store.setDispatchSubject({ startTime: startTime.value, endTime: endTime.value, timeStep: timeStep.value, scheduleFrequency: scheduleFrequency.value, selectedReservoirIds: selectedReservoirIds.value, selectedGroupId: selectedGroupId.value })
  store.markStepCompleted(2)
  router.push('/model-config/model-data')
}

onMounted(() => {
  if (store.dispatchSubject.startTime) {
    startTime.value = store.dispatchSubject.startTime
    endTime.value = store.dispatchSubject.endTime
    timeStep.value = store.dispatchSubject.timeStep
    scheduleFrequency.value = store.dispatchSubject.scheduleFrequency
    selectedReservoirIds.value = [...store.dispatchSubject.selectedReservoirIds]
    selectedGroupId.value = store.dispatchSubject.selectedGroupId
  } else {
    applyDefaultsFromScenario()
  }
})
</script>

<template>
  <div class="dispatch-subject-view">
    <ModelConfigStepBar :current-step="2" version="new" />

    <div class="main-content">
      <!-- ===== 区域1：预设组合 ===== -->
      <div class="section-title-row">
        <div class="section-accent"></div>
        <span class="section-title">预设组合</span>
        <span class="section-hint">快速选择水库组合方案</span>
        <div class="selected-badge">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
            <path d="M3 8.5L6 11.5L13 4.5" stroke="#00d4ff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          已选 {{ selectedReservoirIds.length }} 座
        </div>
      </div>

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
          <div class="group-count">{{ group.reservoirIds.length }} 座水库</div>
        </div>
      </div>

      <!-- ===== 区域2：更多组合水库 ===== -->
      <div class="section-title-row">
        <div class="section-accent"></div>
        <span class="section-title">更多组合水库</span>
        <span class="section-hint">勾选参与调度的水库</span>
      </div>

      <div class="reservoir-grid">
        <template v-for="group in reservoirGroups" :key="group.name">
          <div class="reservoir-group-header">
            <span class="res-group-line"></span>
            <span class="res-group-name">{{ group.name }}</span>
            <span class="res-group-line"></span>
          </div>
          <div class="reservoir-items">
            <div
              v-for="res in group.items"
              :key="res.id"
              class="reservoir-item"
              :class="{ 'item-checked': res.checked }"
              @click="toggleReservoir(res.id)"
            >
              <div class="item-checkbox" :class="{ 'checkbox-checked': res.checked }">
                <svg v-if="res.checked" width="10" height="10" viewBox="0 0 16 16" fill="none">
                  <path d="M3 8.5L6 11.5L13 4.5" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <span class="item-name">{{ res.fullName }}</span>
              <span class="item-status" :style="{ color: getReservoirStatus(res.id).color }">{{ getReservoirStatus(res.id).label }}</span>
            </div>
          </div>
        </template>
      </div>

      <!-- ===== 区域3：调度时期与周期 ===== -->
      <div class="section-title-row">
        <div class="section-accent"></div>
        <span class="section-title">调度时期与周期</span>
        <span class="section-hint">设定时间范围与计算精度</span>
        <div class="section-total">
          <span class="total-number-sm">{{ totalPeriods }}</span>
          <span class="total-unit-sm">时段</span>
        </div>
      </div>

      <div class="period-grid">
        <div class="param-card">
          <div class="param-label">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="param-icon">
              <rect x="2" y="3" width="12" height="11" rx="2" stroke="currentColor" stroke-width="1.3" fill="none"/>
              <path d="M5 1v4M11 1v4M2 7h12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            调度起止时间
          </div>
          <div class="date-picker-wrapper">
            <el-date-picker v-model="startTime" type="date" placeholder="开始日期" class="date-picker-half" value-format="YYYY-MM-DD" />
            <span class="date-separator">~</span>
            <el-date-picker v-model="endTime" type="date" placeholder="结束日期" class="date-picker-half" value-format="YYYY-MM-DD" />
          </div>
        </div>
        <div class="param-card">
          <div class="param-label">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="param-icon">
              <circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.3" fill="none"/>
              <path d="M8 5v3.5H11" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            时间步长
            <span v-if="isTimeStepLocked" class="lock-badge">锁定</span>
          </div>
          <el-select v-model="timeStep" :disabled="isTimeStepLocked" class="param-select">
            <el-option v-for="ts in allowedTimeSteps" :key="ts" :label="ts" :value="ts" />
          </el-select>
        </div>
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
          </el-select>
        </div>
      </div>
    </div>

    <ModelConfigFooter :step="2" @cancel="handleCancel" @save="handleSave" @prev="handlePrev" @next="handleNext" />

    <!-- 保存弹窗 -->
    <el-dialog v-model="saveDialogVisible" title="保存确认" width="400px" :close-on-click-modal="false" class="confirm-dialog">
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

    <!-- 取消弹窗 -->
    <el-dialog v-model="cancelDialogVisible" title="取消确认" width="400px" :close-on-click-modal="false" class="confirm-dialog">
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
  </div>
</template>

<style scoped>
.dispatch-subject-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
  gap: 0;
  overflow: hidden;
  background: rgba(var(--tech-bg-rgb), 0.92);
}

.main-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  padding: 12px 14px;
}

.main-content::-webkit-scrollbar { width: 4px; }
.main-content::-webkit-scrollbar-track { background: transparent; }
.main-content::-webkit-scrollbar-thumb { background: rgba(50, 150, 255, 0.2); border-radius: 2px; }

/* 分区标题 */
.section-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  padding-top: 2px;
  margin-bottom: 8px;
}

.section-accent { width: 3px; height: 18px; background: linear-gradient(180deg, var(--tech-cyan), rgba(var(--tech-cyan-rgb), 0.3)); border-radius: 2px; flex-shrink: 0; }
.section-title { font-size: 15px; font-weight: 600; color: var(--tech-text-primary); }
.section-hint { font-size: 12px; color: var(--tech-text-placeholder); margin-left: 4px; }

.selected-badge {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--tech-cyan);
  background: rgba(var(--tech-blue-rgb), 0.08);
  padding: 2px 10px;
  border-radius: 10px;
}

/* 预设组合卡片 */
.group-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 8px;
}

.group-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 16px 12px;
  border-radius: 10px;
  border: 1px solid rgba(50, 150, 255, 0.12);
  background: rgba(10, 25, 41, 0.4);
  cursor: pointer;
  transition: all 0.25s ease;
  text-align: center;
  position: relative;
}

.group-card:hover { border-color: rgba(var(--tech-blue-rgb), 0.3); background: rgba(var(--tech-blue-rgb), 0.04); }
.group-card.group-selected { border-color: rgba(var(--tech-blue-rgb), 0.5); background: rgba(var(--tech-blue-rgb), 0.08); box-shadow: 0 0 16px rgba(var(--tech-blue-rgb), 0.1); }

.group-check { position: absolute; top: 8px; right: 8px; }
.group-name { font-size: 15px; font-weight: 600; color: var(--tech-text-regular); }
.group-selected .group-name { color: var(--tech-text-primary); }
.group-count { font-size: 12px; color: #5a8abf; }

/* 更多组合水库区域 */
.reservoir-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}

.reservoir-group-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 0;
  grid-column: 1 / -1;
}

.res-group-line { flex: 1; height: 1px; background: rgba(50, 150, 255, 0.12); }
.res-group-name { font-size: 11px; color: #5a8abf; white-space: nowrap; font-weight: 600; letter-spacing: 0.5px; }

.reservoir-items {
  display: contents;
}

.reservoir-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid rgba(50, 150, 255, 0.08);
  background: rgba(10, 25, 41, 0.3);
  cursor: pointer;
  transition: all 0.2s;
}

.reservoir-item:hover { border-color: rgba(var(--tech-blue-rgb), 0.2); background: rgba(var(--tech-blue-rgb), 0.03); }
.reservoir-item.item-checked { border-color: rgba(var(--tech-blue-rgb), 0.35); background: rgba(var(--tech-blue-rgb), 0.06); }

.item-checkbox {
  width: 16px; height: 16px; border-radius: 3px;
  border: 2px solid rgba(80, 100, 120, 0.4);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  transition: all 0.2s;
}
.item-checkbox.checkbox-checked { border-color: var(--tech-cyan); background: var(--tech-cyan); }

.item-name { font-size: 12px; font-weight: 600; color: var(--tech-text-regular); white-space: nowrap; }
.item-meta { font-size: 10px; color: #5a8abf; white-space: nowrap; }
.item-status { font-size: 10px; font-weight: 500; margin-left: auto; flex-shrink: 0; }

/* 时段参数 */
.period-grid {
  display: grid;
  grid-template-columns: 2.5fr 1fr 1fr;
  gap: 8px;
}

.param-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  border: 1px solid rgba(50, 150, 255, 0.08);
  border-radius: 8px;
  background: rgba(10, 25, 41, 0.3);
}

.param-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 500;
  color: var(--tech-text-secondary);
  white-space: nowrap;
  flex-shrink: 0;
}

.param-icon { color: #5a8abf; flex-shrink: 0; }

.lock-badge {
  font-size: 9px; padding: 1px 6px; border-radius: 4px;
  background: rgba(240, 160, 32, 0.15); color: #f0a020; font-weight: 600; margin-left: 4px;
}

.param-select { width: 100%; min-width: 0; }

.date-picker-wrapper { display: flex; align-items: center; gap: 6px; flex: 1; min-width: 0; }
.date-picker-half { flex: 1; min-width: 0; }
.date-separator { color: var(--tech-text-placeholder); font-size: 12px; flex-shrink: 0; }

.section-total { margin-left: auto; display: flex; align-items: baseline; gap: 4px; }
.total-number-sm { font-size: 20px; font-weight: 700; color: var(--tech-cyan); font-variant-numeric: tabular-nums; }
.total-unit-sm { font-size: 12px; color: var(--tech-text-secondary); }

.dialog-body { display: flex; align-items: flex-start; gap: 16px; }
.dialog-icon { flex-shrink: 0; margin-top: 2px; }
.dialog-text { display: flex; flex-direction: column; gap: 6px; }
.dialog-title-main { color: var(--tech-text-primary); font-size: 14px; font-weight: 500; }
.dialog-desc { color: var(--tech-text-secondary); font-size: 12px; line-height: 1.5; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 8px; }

/* 日期选择器外层透明背景（组件特有，全局未定义） */
:deep(.el-date-editor) { background: transparent !important; }
</style>
