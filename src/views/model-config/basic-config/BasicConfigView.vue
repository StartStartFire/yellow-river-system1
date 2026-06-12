<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import {
  basicConfigState,
  reservoirGroups,
  dispatchObjectives,
  constraintSummary,
} from '@/mock/modelConfig'
import type { ReservoirGroup, DispatchObjective } from '@/mock/modelConfig'

// ==================== Mock 数据 ====================
const configData = basicConfigState.data
const groups = reservoirGroups.data as ReservoirGroup[]
const objectives = dispatchObjectives.data as DispatchObjective[]
const constraintData = constraintSummary.data

// ==================== 响应式状态 ====================
const router = useRouter()

// 表单数据
const startTime = ref(configData.startTime)
const endTime = ref(configData.endTime)
const timeStep = ref(configData.timeStep)
const scheduleFrequency = ref(configData.scheduleFrequency)
const schemeName = ref(configData.schemeName)
const selectedGroup = ref(configData.selectedReservoirGroup)
const selectedObjectives = ref<string[]>([...configData.selectedObjectives])

// 计算总时段数
const totalPeriods = computed(() => {
  if (!startTime.value || !endTime.value) return 0
  const start = new Date(startTime.value)
  const end = new Date(endTime.value)
  const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
  if (timeStep.value === '每日') return diffDays + 1
  if (timeStep.value === '每旬') return Math.ceil((diffDays + 1) / 10)
  if (timeStep.value === '每月') return Math.ceil((diffDays + 1) / 30)
  return diffDays + 1
})

// 方案名字数统计
const schemeNameLength = computed(() => schemeName.value.length)

// 时间步长选项
const timeStepOptions = [
  { value: '每日', label: '每日' },
  { value: '每旬', label: '每旬' },
  { value: '每月', label: '每月' },
]

// 调度频率选项
const frequencyOptions = [
  { value: '每周一次', label: '每周一次' },
  { value: '每月一次', label: '每月一次' },
  { value: '按需调度', label: '按需调度' },
]

// ==================== 弹窗状态 ====================
const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)
const constraintDialogVisible = ref(false)

// ==================== 交互 ====================

// 步骤条点击（从 Step 1 跳转回来）
const handleStepClick = (step: number) => {
  if (step === 1) {
    router.push('/model-config/model-data')
  }
}

// 水库组合选择
const handleSelectGroup = (id: string) => {
  selectedGroup.value = id
}

// 调度目标切换
const handleToggleObjective = (id: string) => {
  const idx = selectedObjectives.value.indexOf(id)
  if (idx >= 0) {
    if (selectedObjectives.value.length > 1) {
      selectedObjectives.value.splice(idx, 1)
    }
  } else {
    selectedObjectives.value.push(id)
  }
}

// 底部按钮
const handleCancel = () => {
  cancelDialogVisible.value = true
}

const handleSave = () => {
  saveDialogVisible.value = true
}

const handlePrev = () => {
  router.push('/model-config/model-data')
}

const handleNext = () => {
  // 方案名称校验
  if (!schemeName.value.trim()) {
    ElMessage.warning('请输入方案名称')
    return
  }
  router.push('/model-config/model-algorithm')
}

// 弹窗确认
const confirmSave = () => {
  saveDialogVisible.value = false
  // 实际保存可写入 Pinia，当前阶段只做前端提示
  ElMessage.success('基础配置已保存')
}

const confirmCancel = () => {
  cancelDialogVisible.value = false
  ElMessage.info('已取消，未保存任何更改')
  router.push('/model-config/model-data')
}

// ==================== 图标映射 ====================
const objectiveIcons: Record<string, string> = {
  shield: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 3L4 6v5c0 5 3.5 9.7 8 11 4.5-1.3 8-6 8-11V6l-8-3z" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M10 12l1.5 1.5L14 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  flash: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>`,
  leaf: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M17 7C13 8 7 11 4 16c2-3 5-5 8-6l-1 4c3-2 6-5 7-9l-1 2z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M12 14c-2 2-4 5-4 7" stroke="currentColor" stroke-width="1.5"/></svg>`,
}

const getObjectiveIcon = (icon: string) => objectiveIcons[icon] || objectiveIcons.shield
</script>

<template>
  <div class="basic-config-view">
    <!-- 步骤条 -->
    <ModelConfigStepBar :current-step="2" @step-click="handleStepClick" />

    <!-- 主体内容区 -->
    <div class="main-content">
      <!-- Row 1: 调度周期设置 + 方案名称 -->
      <div class="content-row row-2col">
        <!-- 调度周期设置 -->
        <div class="card schedule-card">
          <div class="card-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
              <circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.3"/>
              <path d="M8 5v3.5H11" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            <span class="card-title">1. 调度周期设置</span>
          </div>
          <div class="card-body">
            <div class="form-grid">
              <div class="form-item">
                <label class="form-label">开始时间</label>
                <el-date-picker
                  v-model="startTime"
                  type="date"
                  placeholder="选择开始日期"
                  size="small"
                  class="dark-date-picker"
                  value-format="YYYY-MM-DD"
                />
              </div>
              <div class="form-item">
                <label class="form-label">结束时间</label>
                <el-date-picker
                  v-model="endTime"
                  type="date"
                  placeholder="选择结束日期"
                  size="small"
                  class="dark-date-picker"
                  value-format="YYYY-MM-DD"
                />
              </div>
              <div class="form-item">
                <label class="form-label">时间步长</label>
                <el-select v-model="timeStep" size="small" class="dark-select">
                  <el-option
                    v-for="opt in timeStepOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  />
                </el-select>
              </div>
              <div class="form-item">
                <label class="form-label">调度频率</label>
                <el-select v-model="scheduleFrequency" size="small" class="dark-select">
                  <el-option
                    v-for="opt in frequencyOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  />
                </el-select>
              </div>
            </div>
            <div class="total-periods">
              总时段数：<span class="period-value">{{ totalPeriods }}</span> 个时段
            </div>
          </div>
        </div>

        <!-- 方案名称 -->
        <div class="card scheme-card">
          <div class="card-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
              <path d="M2 4h12M2 8h12M2 12h8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              <rect x="10" y="10" width="4" height="4" rx="1" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            <span class="card-title">1a. 方案名称</span>
          </div>
          <div class="card-body">
            <label class="form-label">方案名称</label>
            <el-input
              v-model="schemeName"
              placeholder="请输入方案名称（建议包含调度目标与时间范围）"
              maxlength="50"
              size="small"
              class="dark-input"
            />
            <div class="char-count">{{ schemeNameLength }} / 50</div>
          </div>
        </div>
      </div>

      <!-- Row 2: 水库组合选择 -->
      <div class="card reservoir-card">
        <div class="card-header">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
            <rect x="2" y="4" width="5" height="8" rx="1" stroke="currentColor" stroke-width="1.3"/>
            <rect x="9" y="4" width="5" height="8" rx="1" stroke="currentColor" stroke-width="1.3"/>
            <path d="M2 4l2.5-2h7L14 4" stroke="currentColor" stroke-width="1.3"/>
          </svg>
          <span class="card-title">2. 水库组合选择</span>
        </div>
        <div class="card-body">
          <div class="group-list">
            <div
              v-for="group in groups"
              :key="group.id"
              class="group-card"
              :class="{ 'group-active': selectedGroup === group.id }"
              @click="handleSelectGroup(group.id)"
            >
              <div class="group-radio">
                <div class="radio-circle" :class="{ 'radio-checked': selectedGroup === group.id }">
                  <div v-if="selectedGroup === group.id" class="radio-dot"></div>
                </div>
              </div>
              <div class="group-info">
                <div class="group-name">{{ group.name }}</div>
                <div class="group-reservoirs">
                  <span v-for="(r, rIdx) in group.reservoirs" :key="rIdx" class="reservoir-tag">
                    {{ r }}
                  </span>
                </div>
              </div>
              <div v-if="selectedGroup === group.id" class="group-badge">已选</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Row 3: 调度目标设置 + 约束条件设置 -->
      <div class="content-row row-2col">
        <!-- 调度目标设置 -->
        <div class="card objective-card">
          <div class="card-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
              <circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.3"/>
              <circle cx="8" cy="8" r="2.5" stroke="currentColor" stroke-width="1.3"/>
              <circle cx="8" cy="8" r="1" fill="currentColor"/>
            </svg>
            <span class="card-title">3. 调度目标设置</span>
          </div>
          <div class="card-body">
            <div class="objective-list">
              <div
                v-for="obj in objectives"
                :key="obj.id"
                class="objective-card-item"
                :class="{ 'objective-active': selectedObjectives.includes(obj.id) }"
                @click="handleToggleObjective(obj.id)"
              >
                <div class="objective-icon" v-html="getObjectiveIcon(obj.icon)"></div>
                <div class="objective-info">
                  <div class="objective-name">{{ obj.name }}</div>
                  <div class="objective-desc">{{ obj.description }}</div>
                </div>
                <div v-if="selectedObjectives.includes(obj.id)" class="objective-check">
                  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                    <circle cx="9" cy="9" r="7" fill="rgba(0,175,255,0.2)" stroke="#00d4ff" stroke-width="1.5"/>
                    <path d="M6 9l2 2 4-4" stroke="#00d4ff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 约束条件设置 -->
        <div class="card constraint-card">
          <div class="card-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
              <rect x="2.5" y="2.5" width="11" height="11" rx="2" stroke="currentColor" stroke-width="1.3"/>
              <path d="M6 5.5h4M6 8h4M6 10.5h2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            <span class="card-title">4. 约束条件设置</span>
          </div>
          <div class="card-body constraint-body">
            <div class="constraint-left">
              <div class="constraint-icon">
                <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
                  <circle cx="18" cy="18" r="15" stroke="#00ff88" stroke-width="2" fill="rgba(0,255,136,0.1)"/>
                  <path d="M12 18l4 4 8-8" stroke="#00ff88" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </div>
            <div class="constraint-middle">
              <div class="constraint-count">已配置 <span class="count-value">{{ constraintData.count }}</span> 项约束条件</div>
              <div class="constraint-desc">{{ constraintData.description }}</div>
            </div>
            <div class="constraint-right">
              <el-button type="primary" size="small" class="constraint-btn" @click="constraintDialogVisible = true">
                查看详情
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="footer-bar">
      <div class="footer-left">
        <el-button size="default" @click="handleCancel" class="footer-btn-cancel">取消</el-button>
      </div>
      <div class="footer-right">
        <el-button size="default" @click="handlePrev" class="footer-btn-prev">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
            <path d="M10 13L5 8l5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          上一步
        </el-button>
        <el-button size="default" @click="handleSave" class="footer-btn-save">保存</el-button>
        <el-button type="primary" size="default" @click="handleNext" class="footer-btn-next">
          下一步
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
            <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </el-button>
      </div>
    </div>

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
          <span class="dialog-title-main">确认保存当前基础配置？</span>
          <span class="dialog-desc">保存后调度周期、方案名称、水库组合等配置将保留。</span>
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

    <!-- ===== 约束详情弹窗 ===== -->
    <el-dialog
      v-model="constraintDialogVisible"
      title="约束条件详情"
      width="520px"
      :close-on-click-modal="false"
      class="confirm-dialog constraint-detail-dialog"
    >
      <div class="constraint-detail-body">
        <div class="constraint-summary-text">
          当前已配置 <span class="count-value">{{ constraintData.count }}</span> 项约束条件
        </div>
        <div class="constraint-list">
          <div
            v-for="(c, cIdx) in constraintData.constraints"
            :key="cIdx"
            class="constraint-item"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="constraint-item-icon">
              <circle cx="8" cy="8" r="4" fill="rgba(0,175,255,0.15)" stroke="#00afff" stroke-width="1.2"/>
              <path d="M6 8l1.5 1.5L10 7" stroke="#00afff" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="constraint-item-name">{{ c }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="constraintDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.basic-config-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 8px 12px;
  gap: 8px;
  overflow: hidden;
}

/* ===== 主体内容 ===== */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
  overflow-y: auto;
  padding-right: 2px;
}

.main-content::-webkit-scrollbar {
  width: 4px;
}

.main-content::-webkit-scrollbar-track {
  background: transparent;
}

.main-content::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.25);
  border-radius: 2px;
}

/* ===== 两列布局 ===== */
.content-row {
  display: flex;
  gap: 8px;
}

.row-2col > * {
  flex: 1;
  min-width: 0;
}

/* ===== 通用卡片 ===== */
.card {
  background: rgba(6, 30, 70, 0.85);
  border: 1px solid rgba(50, 150, 255, 0.35);
  border-radius: 12px;
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
  color: #00d4ff;
  flex-shrink: 0;
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  color: #e0e6ed;
}

.card-body {
  padding: 14px 16px;
  flex: 1;
}

/* ===== 调度周期设置表单 ===== */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 12px;
  color: #7a8fa3;
  font-weight: 500;
}

.total-periods {
  font-size: 12px;
  color: #7a8fa3;
  text-align: right;
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid rgba(50, 150, 255, 0.12);
}

.period-value {
  color: #00d4ff;
  font-weight: 600;
  font-size: 14px;
}

/* ===== 方案名称 ===== */
.scheme-card .card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.char-count {
  font-size: 11px;
  color: #5a6f83;
  text-align: right;
  margin-top: 2px;
}

/* ===== 水库组合选择 ===== */
.reservoir-card .card-body {
  padding: 12px 16px;
}

.group-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.group-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid rgba(50, 150, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s;
  background: rgba(0, 175, 255, 0.03);
  min-width: 180px;
  flex: 1;
  position: relative;
}

.group-card:hover {
  border-color: rgba(0, 175, 255, 0.5);
  background: rgba(0, 175, 255, 0.06);
}

.group-card.group-active {
  border-color: rgba(0, 175, 255, 0.7);
  background: rgba(0, 175, 255, 0.1);
  box-shadow: 0 0 12px rgba(0, 175, 255, 0.15);
}

/* 单选圆点 */
.radio-circle {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid rgba(50, 150, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.radio-checked {
  border-color: #00d4ff;
}

.radio-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00d4ff;
  box-shadow: 0 0 6px rgba(0, 212, 255, 0.5);
}

.group-info {
  flex: 1;
  min-width: 0;
}

.group-name {
  font-size: 13px;
  font-weight: 600;
  color: #e0e6ed;
  margin-bottom: 4px;
}

.group-reservoirs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.reservoir-tag {
  font-size: 11px;
  color: #7a8fa3;
  background: rgba(50, 150, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.group-badge {
  position: absolute;
  top: -1px;
  right: -1px;
  font-size: 10px;
  color: #00d4ff;
  background: rgba(0, 175, 255, 0.2);
  border: 1px solid rgba(0, 175, 255, 0.5);
  padding: 1px 8px;
  border-radius: 0 8px 0 8px;
  line-height: 1.6;
}

/* ===== 调度目标 ===== */
.objective-list {
  display: flex;
  gap: 10px;
}

.objective-card-item {
  flex: 1;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px;
  border: 1px solid rgba(50, 150, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.25s;
  background: rgba(0, 175, 255, 0.03);
  position: relative;
}

.objective-card-item:hover {
  border-color: rgba(0, 175, 255, 0.5);
  background: rgba(0, 175, 255, 0.06);
}

.objective-card-item.objective-active {
  border-color: rgba(0, 175, 255, 0.7);
  background: rgba(0, 175, 255, 0.1);
  box-shadow: 0 0 10px rgba(0, 175, 255, 0.12);
}

.objective-icon {
  color: #00d4ff;
  flex-shrink: 0;
  margin-top: 2px;
  opacity: 0.7;
}

.objective-active .objective-icon {
  opacity: 1;
}

.objective-info {
  flex: 1;
  min-width: 0;
}

.objective-name {
  font-size: 13px;
  font-weight: 600;
  color: #e0e6ed;
  margin-bottom: 3px;
}

.objective-desc {
  font-size: 11px;
  color: #7a8fa3;
  line-height: 1.4;
}

.objective-check {
  flex-shrink: 0;
}

/* ===== 约束条件 ===== */
.constraint-body {
  display: flex;
  align-items: center;
  gap: 16px;
}

.constraint-left {
  flex-shrink: 0;
}

.constraint-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.constraint-middle {
  flex: 1;
  min-width: 0;
}

.constraint-count {
  font-size: 14px;
  color: #e0e6ed;
  font-weight: 500;
  margin-bottom: 4px;
}

.count-value {
  color: #00ff88;
  font-weight: 700;
  font-size: 18px;
}

.constraint-desc {
  font-size: 12px;
  color: #7a8fa3;
  line-height: 1.4;
}

.constraint-right {
  flex-shrink: 0;
}

.constraint-btn {
  font-size: 12px !important;
}

/* ===== 约束详情弹窗 ===== */
.constraint-detail-body {
  padding: 4px 0;
}

.constraint-summary-text {
  font-size: 13px;
  color: #c0c8d4;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.15);
}

.constraint-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 12px;
}

.constraint-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  background: rgba(0, 175, 255, 0.04);
  transition: background 0.2s;
}

.constraint-item:hover {
  background: rgba(0, 175, 255, 0.08);
}

.constraint-item-icon {
  flex-shrink: 0;
}

.constraint-item-name {
  font-size: 12px;
  color: #c0c8d4;
}

/* ===== 底部操作栏 ===== */
.footer-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: rgba(6, 30, 70, 0.85);
  border: 1px solid rgba(50, 150, 255, 0.35);
  border-radius: 12px;
  flex-shrink: 0;
}

.footer-left,
.footer-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.footer-btn-cancel {
  font-size: 12px !important;
}

.footer-btn-prev {
  font-size: 12px !important;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.footer-btn-save {
  font-size: 12px !important;
  background: rgba(0, 175, 255, 0.1) !important;
  border-color: rgba(0, 175, 255, 0.4) !important;
  color: #00d4ff !important;
}

.footer-btn-save:hover {
  background: rgba(0, 175, 255, 0.2) !important;
  border-color: rgba(0, 175, 255, 0.6) !important;
}

.footer-btn-next {
  font-size: 12px !important;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-icon {
  flex-shrink: 0;
}

/* ===== Element Plus 深色覆盖 ===== */

/* 日期选择器深色适配 */
:deep(.dark-date-picker .el-input__wrapper) {
  background: rgba(2, 27, 63, 0.8) !important;
  box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.25) inset !important;
}

:deep(.dark-date-picker .el-input__inner) {
  color: #c0c8d4 !important;
  font-size: 12px;
}

:deep(.dark-select .el-input__wrapper) {
  background: rgba(2, 27, 63, 0.8) !important;
  box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.25) inset !important;
}

:deep(.dark-select .el-input__inner) {
  color: #c0c8d4 !important;
  font-size: 12px;
}

/* 输入框 */
:deep(.dark-input .el-input__wrapper) {
  background: rgba(2, 27, 63, 0.8) !important;
  box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.25) inset !important;
}

:deep(.dark-input .el-input__inner) {
  color: #c0c8d4 !important;
  font-size: 12px;
}

:deep(.dark-input .el-input__inner::placeholder) {
  color: #5a6f83;
}

/* ===== 通用 Element Plus 按钮深色覆盖 ===== */
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

/* ===== 弹窗样式 ===== */
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

/* ===== 日期选择器下拉面板深色适配 ===== */
:deep(.el-picker-panel) {
  background: #0a1a2e !important;
  border: 1px solid rgba(50, 150, 255, 0.3) !important;
}

:deep(.el-date-table th) {
  color: #7a8fa3 !important;
}

:deep(.el-date-table td) {
  color: #c0c8d4 !important;
}

:deep(.el-date-table td.today) {
  color: #00d4ff !important;
  font-weight: 700;
}

:deep(.el-date-table td.available:hover) {
  background: rgba(0, 175, 255, 0.15) !important;
}

:deep(.el-date-table td.current:not(.disabled)) {
  background: rgba(0, 175, 255, 0.25) !important;
  color: #00d4ff !important;
}

:deep(.el-date-table td.in-range) {
  background: rgba(0, 175, 255, 0.1) !important;
}

:deep(.el-month-table td .cell:hover) {
  background: rgba(0, 175, 255, 0.15) !important;
}

:deep(.el-year-table td .cell:hover) {
  background: rgba(0, 175, 255, 0.15) !important;
}

:deep(.el-date-editor .el-range-separator) {
  color: #7a8fa3 !important;
}

:deep(.el-popper) {
  border: 1px solid rgba(50, 150, 255, 0.3) !important;
}

/* ===== 下拉选择面板深色适配 ===== */
:deep(.el-select-dropdown) {
  background: #0a1a2e !important;
  border: 1px solid rgba(50, 150, 255, 0.3) !important;
}

:deep(.el-select-dropdown__item) {
  color: #c0c8d4 !important;
}

:deep(.el-select-dropdown__item.hover) {
  background: rgba(0, 175, 255, 0.1) !important;
}

:deep(.el-select-dropdown__item.selected) {
  color: #00d4ff !important;
  font-weight: 600;
}
</style>
