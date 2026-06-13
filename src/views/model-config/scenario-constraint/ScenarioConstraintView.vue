<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import ModelConfigFooter from '@/components/model-config/ModelConfigFooter.vue'
import { useModelConfigStore } from '@/stores/modelConfig'
import {
  scenarioConstraintState,
  scenarioTypeOptions,
  scenarioParams,
  dispatchObjectives,
} from '@/mock/modelConfig'
import type { ScenarioParam } from '@/mock/modelConfig'

// ==================== Store ====================
const store = useModelConfigStore()

// ==================== Mock 数据 ====================
const stateData = scenarioConstraintState.data
const typeOptions = scenarioTypeOptions.data
const paramsDef = scenarioParams.data as ScenarioParam[]
const objectives = dispatchObjectives.data

// ==================== 响应式状态 ====================
const router = useRouter()

// 场景类型
const scenarioType = ref(stateData.scenarioType)

// 场景描述
const scenarioDescription = ref(stateData.scenarioDescription)

// 场景参数值 - 以 id 为 key
const paramValues = ref<Record<string, string>>({ ...stateData.params })

// 弹窗状态
const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)

// ==================== 计算属性 ====================

// 字数统计
const descLength = computed(() => scenarioDescription.value.length)

// 当前调度目标关联的场景参数ID集合（联动 Step 2）
const relevantParamIds = computed(() => {
  return new Set(store.relevantScenarioParamIds)
})

// ==================== 交互 ====================

// 步骤条点击
const handleStepClick = (step: number) => {
  if (step === 1) router.push('/model-config/model-data')
  if (step === 2) router.push('/model-config/basic-config')
  if (step === 3) router.push('/model-config/model-algorithm')
}

// 场景类型切换
const handleTypeSwitch = (type: string) => {
  scenarioType.value = type
}

// 参数值更新
const handleParamChange = (paramId: string, value: string) => {
  paramValues.value[paramId] = value
}

// 底部操作
const handleCancel = () => { cancelDialogVisible.value = true }
const handleSave = () => { saveDialogVisible.value = true }
const handlePrev = () => { router.push('/model-config/model-algorithm') }
const handleNext = () => {
  if (!scenarioDescription.value.trim()) {
    ElMessage.warning('请填写场景描述')
    return
  }
  // 写入 Store（联动 Step 5 配置汇总）
  store.setScenarioConstraint({
    scenarioType: scenarioType.value,
    scenarioDescription: scenarioDescription.value,
    params: { ...paramValues.value },
  })
  router.push('/model-config/config-summary')
}

const confirmSave = () => {
  saveDialogVisible.value = false
  // 写入 Store
  store.setScenarioConstraint({
    scenarioType: scenarioType.value,
    scenarioDescription: scenarioDescription.value,
    params: { ...paramValues.value },
  })
  ElMessage.success('场景约束配置已保存')
}

const confirmCancel = () => {
  cancelDialogVisible.value = false
  ElMessage.info('已取消，未保存任何更改')
}

// ==================== SVG 图标 ====================
const paramIcons: Record<string, string> = {
  westRoute: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 10h12M8 2v8M5 5l3-3 3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 12v1.5h12V12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>`,
  sedimentFlow: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 6C4 4 6 6 8 6s4-2 6 0" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M2 9C4 7 6 9 8 9s4-2 6 0" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M2 12c2-2 4 0 6 0s4-2 6 0" stroke="currentColor" stroke-width="1.3" fill="none"/></svg>`,
  backboneStatus: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="4" y="2" width="8" height="12" rx="1.5" stroke="currentColor" stroke-width="1.3"/><circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.3"/><path d="M8 2v2" stroke="currentColor" stroke-width="1.3"/></svg>`,
  sedimentRequirement: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5" stroke="currentColor" stroke-width="1.3"/><path d="M8 5v3l2 2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>`,
  ecologicalFlow: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2C8 2 4 6.5 4 9.5C4 11.7 5.8 13.5 8 13.5S12 11.7 12 9.5C12 6.5 8 2 8 2Z" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M6.5 9.5C6.5 10.3 7.2 11 8 11" stroke="currentColor" stroke-width="1.2"/></svg>`,
}

</script>

<template>
  <div class="scenario-constraint-view">
    <!-- 步骤条 -->
    <ModelConfigStepBar :current-step="4" @step-click="handleStepClick" />

    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 场景配置标题区 + 类型切换 -->
      <div class="card header-card">
        <div class="card-header">
          <div class="header-title-row">
            <div class="header-accent-line"></div>
            <span class="header-title">场景配置</span>
          </div>
        </div>

        <!-- 联动上下文提示：来自 Step 2 调度目标 -->
        <div class="linkage-context" v-if="store.basicConfig.selectedObjectives.length > 0">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none" class="linkage-icon">
            <path d="M4 8h8M8 4v8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
          <span class="linkage-text">
            调度目标「{{ store.basicConfig.selectedObjectives.map(o => objectives.find(d => d.id === o)?.name || o).join('、') }}」关联的约束参数已高亮
          </span>
        </div>

        <!-- 场景类型切换 -->
        <div class="switch-row">
          <div
            v-for="opt in typeOptions"
            :key="opt.id"
            class="switch-btn"
            :class="{ 'switch-active': scenarioType === opt.id }"
            @click="handleTypeSwitch(opt.id)"
          >
            <svg v-if="opt.id === 'typical'" width="14" height="14" viewBox="0 0 16 16" fill="none" class="switch-icon">
              <circle cx="8" cy="8" r="5" stroke="currentColor" stroke-width="1.3"/>
              <path d="M8 5v3l2 1.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            <svg v-else width="14" height="14" viewBox="0 0 16 16" fill="none" class="switch-icon">
              <path d="M2 4h12M2 8h12M2 12h8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              <circle cx="12" cy="12" r="2.5" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            <span>{{ opt.name }}</span>
          </div>
        </div>

        <!-- 场景描述 -->
        <div class="description-section">
          <div class="desc-header">
            <span class="desc-label">场景描述</span>
          </div>
          <el-input
            v-model="scenarioDescription"
            type="textarea"
            :rows="3"
            maxlength="300"
            placeholder="请输入场景描述..."
            class="dark-textarea"
          />
          <div class="char-count">{{ descLength }} / 300</div>
        </div>
      </div>

      <!-- 下部：场景参数配置（全宽） -->
      <div class="card params-card full-width-card">
          <div class="card-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
              <circle cx="5" cy="4" r="2" stroke="currentColor" stroke-width="1.3"/>
              <circle cx="11" cy="12" r="2" stroke="currentColor" stroke-width="1.3"/>
              <path d="M5 6v6M11 4v2" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            <span class="card-title">场景参数配置</span>
          </div>
          <div class="card-body params-body">
            <div
              v-for="param in paramsDef"
              :key="param.id"
              class="param-row"
              :class="{ 'param-relevant': relevantParamIds.has(param.id) }"
            >
              <div class="param-label-row">
                <span class="param-icon" v-html="paramIcons[param.id] || ''"></span>
                <span class="param-name">{{ param.name }}</span>
                <span v-if="relevantParamIds.has(param.id)" class="param-tag">关联</span>
              </div>
              <div class="param-control">
                <el-select
                  :model-value="paramValues[param.id]"
                  size="small"
                  class="dark-select param-select"
                  @update:model-value="(val: string) => handleParamChange(param.id, val)"
                >
                  <el-option
                    v-for="opt in param.options"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  />
                </el-select>
              </div>
            </div>
          </div>
        </div>

    </div>

    <!-- 底部操作栏 -->
    <ModelConfigFooter
      :step="4"
      @cancel="handleCancel"
      @save="handleSave"
      @prev="handlePrev"
      @next="handleNext"
    />

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
          <span class="dialog-title-main">确认保存当前场景约束配置？</span>
          <span class="dialog-desc">保存后场景参数和约束配置将保留。</span>
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
  </div>
</template>

<style scoped>
.scenario-constraint-view {
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

/* ===== 标题区卡片 ===== */
.header-card.card {
  overflow: visible;
}

.header-card .card-header {
  border-bottom: none;
  padding-bottom: 6px;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-accent-line {
  width: 3px;
  height: 18px;
  background: linear-gradient(180deg, #00d4ff, rgba(0, 212, 255, 0.3));
  border-radius: 2px;
  flex-shrink: 0;
}

.header-title {
  font-size: 15px;
  font-weight: 700;
  color: #e0e6ed;
}

/* ===== 场景类型切换 ===== */
.switch-row {
  display: flex;
  gap: 8px;
  padding: 2px 16px 12px;
}

.switch-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.25s;
  background: rgba(2, 27, 63, 0.6);
  border: 1px solid rgba(50, 150, 255, 0.2);
  color: #7a8fa3;
}

.switch-btn:hover {
  border-color: rgba(50, 150, 255, 0.4);
  color: #c0c8d4;
}

.switch-btn.switch-active {
  background: linear-gradient(135deg, rgba(0, 175, 255, 0.2), rgba(0, 229, 255, 0.1));
  border-color: rgba(0, 175, 255, 0.5);
  color: #00d4ff;
  box-shadow: 0 0 10px rgba(0, 175, 255, 0.1);
}

.switch-icon {
  flex-shrink: 0;
}

/* ===== 联动上下文提示 ===== */
.linkage-context {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0 16px 10px;
  padding: 6px 10px;
  background: rgba(0, 175, 255, 0.05);
  border: 1px solid rgba(0, 175, 255, 0.12);
  border-radius: 6px;
}

.linkage-icon {
  color: #00d4ff;
  flex-shrink: 0;
}

.linkage-text {
  font-size: 11px;
  color: #7a8fa3;
  line-height: 1.4;
}

/* ===== 关联参数高亮 ===== */
.param-row.param-relevant {
  background: rgba(0, 175, 255, 0.06);
  border-radius: 6px;
  margin: 0 -8px;
  padding: 10px 8px;
  border: 1px solid rgba(0, 175, 255, 0.15);
}

.param-tag {
  font-size: 10px;
  color: #00d4ff;
  background: rgba(0, 175, 255, 0.12);
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 500;
  line-height: 1.6;
}

/* ===== 场景描述 ===== */
.description-section {
  padding: 0 16px 14px;
}

.desc-header {
  margin-bottom: 8px;
}

.desc-label {
  font-size: 12px;
  font-weight: 500;
  color: #7a8fa3;
}

.char-count {
  font-size: 11px;
  color: #5a6f83;
  text-align: right;
  margin-top: 4px;
}

/* ===== 场景参数（全宽） ===== */
.params-card {
  flex: 1;
}

.full-width-card {
  flex: 1;
  min-height: 0;
}

.params-body {
  padding: 8px 16px;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.param-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(50, 150, 255, 0.08);
}

.param-row:last-child {
  border-bottom: none;
}

.param-label-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.param-icon {
  color: #00d4ff;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.param-name {
  font-size: 13px;
  color: #c0c8d4;
  white-space: nowrap;
}

.param-control {
  flex-shrink: 0;
}

.param-select {
  width: 170px;
}

/* ===== Element Plus 深色覆盖 ===== */

/* 下拉框 */
:deep(.dark-select .el-input__wrapper) {
  background: rgba(2, 27, 63, 0.8) !important;
  box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.25) inset !important;
}

:deep(.dark-select .el-input__inner) {
  color: #c0c8d4 !important;
  font-size: 12px;
}

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

/* textarea */
:deep(.dark-textarea .el-textarea__inner) {
  background: rgba(2, 27, 63, 0.8) !important;
  box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.25) inset !important;
  border: none !important;
  color: #c0c8d4 !important;
  font-size: 12px !important;
  line-height: 1.6 !important;
  resize: none;
}

:deep(.dark-textarea .el-textarea__inner::placeholder) {
  color: #5a6f83;
}

:deep(.dark-textarea .el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px rgba(0, 175, 255, 0.5) inset !important;
}

/* 按钮 */
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

</style>
