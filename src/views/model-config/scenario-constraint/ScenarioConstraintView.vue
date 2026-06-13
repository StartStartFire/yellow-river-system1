<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import {
  scenarioConstraintState,
  scenarioTypeOptions,
  scenarioParams,
  constraintList,
} from '@/mock/modelConfig'
import type { ScenarioParam, ConstraintItem } from '@/mock/modelConfig'

// ==================== Mock 数据 ====================
const stateData = scenarioConstraintState.data
const typeOptions = scenarioTypeOptions.data
const paramsDef = scenarioParams.data as ScenarioParam[]
const constraints = constraintList.data as ConstraintItem[]

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

// 约束已配置数量
const configuredCount = computed(() => constraints.length)

// 是否为典型场景
const isTypical = computed(() => scenarioType.value === 'typical')

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
  router.push('/model-config/config-summary')
}

const confirmSave = () => {
  saveDialogVisible.value = false
  ElMessage.success('场景约束配置已保存')
}

const confirmCancel = () => {
  cancelDialogVisible.value = false
  ElMessage.info('已取消，未保存任何更改')
}

// 获取参数定义
const getParamDef = (id: string) => paramsDef.find(p => p.id === id)

// 获取参数当前选中选项的 label
const getParamLabel = (param: ScenarioParam) => {
  const opt = param.options.find(o => o.value === paramValues.value[param.id])
  return opt ? opt.label : param.options[0].label
}

// ==================== SVG 图标 ====================
const paramIcons: Record<string, string> = {
  westRoute: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 10h12M8 2v8M5 5l3-3 3 3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 12v1.5h12V12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>`,
  sedimentFlow: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 6C4 4 6 6 8 6s4-2 6 0" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M2 9C4 7 6 9 8 9s4-2 6 0" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M2 12c2-2 4 0 6 0s4-2 6 0" stroke="currentColor" stroke-width="1.3" fill="none"/></svg>`,
  backboneStatus: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="4" y="2" width="8" height="12" rx="1.5" stroke="currentColor" stroke-width="1.3"/><circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.3"/><path d="M8 2v2" stroke="currentColor" stroke-width="1.3"/></svg>`,
  sedimentRequirement: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5" stroke="currentColor" stroke-width="1.3"/><path d="M8 5v3l2 2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>`,
  ecologicalFlow: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2C8 2 4 6.5 4 9.5C4 11.7 5.8 13.5 8 13.5S12 11.7 12 9.5C12 6.5 8 2 8 2Z" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M6.5 9.5C6.5 10.3 7.2 11 8 11" stroke="currentColor" stroke-width="1.2"/></svg>`,
}

const constraintIcons: Record<string, string> = {
  level: `<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><rect x="2" y="6" width="10" height="2" rx="0.5" stroke="currentColor" stroke-width="1.2"/><path d="M4 6V3" stroke="currentColor" stroke-width="1.2"/><path d="M7 6V2" stroke="currentColor" stroke-width="1.2"/><path d="M10 6V4" stroke="currentColor" stroke-width="1.2"/></svg>`,
  flow: `<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M1 10c2-2 3 0 5 0s3-2 5 0" stroke="currentColor" stroke-width="1.2" fill="none"/><path d="M1 7c2-2 3 0 5 0s3-2 5 0" stroke="currentColor" stroke-width="1.2" fill="none"/></svg>`,
  flood: `<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M7 1L2 5v7h10V5L7 1z" stroke="currentColor" stroke-width="1.2" fill="none"/><path d="M7 5v3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><circle cx="7" cy="10.5" r="0.5" fill="currentColor"/></svg>`,
  power: `<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M8 1L3 8h4l-1 5 5-7H7l1-5z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/></svg>`,
  sediment: `<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><circle cx="7" cy="7" r="4.5" stroke="currentColor" stroke-width="1.2"/><path d="M7 4.5v5M4.5 7h5" stroke="currentColor" stroke-width="1.2"/></svg>`,
  ecology: `<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M7 2c-2 0-4 1.5-5 4 1.5-2 3.5-3 5.5-2.5L7 2z" stroke="currentColor" stroke-width="1.2" fill="none"/><path d="M7 2c2 0 4 1.5 5 4-1.5-2-3.5-3-5.5-2.5L7 2z" stroke="currentColor" stroke-width="1.2" fill="none"/></svg>`,
  engineering: `<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><rect x="2.5" y="2.5" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/><circle cx="7" cy="7" r="2" stroke="currentColor" stroke-width="1.2"/></svg>`,
  balance: `<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M1 12h12M7 2v10" stroke="currentColor" stroke-width="1.2"/><path d="M4 6l3-4 3 4" stroke="currentColor" stroke-width="1.2" fill="none"/></svg>`,
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

      <!-- 下部：场景参数配置 + 约束条件展示 -->
      <div class="bottom-row">
        <!-- 左侧：场景参数配置 -->
        <div class="card params-card">
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
            >
              <div class="param-label-row">
                <span class="param-icon" v-html="paramIcons[param.id] || ''"></span>
                <span class="param-name">{{ param.name }}</span>
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

        <!-- 右侧：约束条件展示 -->
        <div class="card constraint-card">
          <div class="card-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
              <rect x="2.5" y="2.5" width="11" height="11" rx="2" stroke="currentColor" stroke-width="1.3"/>
              <path d="M6 5.5h4M6 8h4M6 10.5h2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            <span class="card-title">约束条件展示</span>
            <div class="constraint-count-badge">
              已配置 <span class="badge-num">{{ configuredCount }}</span> 项约束
            </div>
          </div>
          <div class="card-body constraint-body-list">
            <div
              v-for="item in constraints"
              :key="item.id"
              class="constraint-row"
            >
              <div class="constraint-icon" v-html="constraintIcons[item.id] || ''"></div>
              <div class="constraint-info">
                <div class="constraint-name">{{ item.name }}</div>
                <div class="constraint-desc">{{ item.description }}</div>
              </div>
              <div class="constraint-status">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none" class="status-check">
                  <circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.2" fill="rgba(0,255,136,0.1)"/>
                  <path d="M4 6l1.5 1.5L8 5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span class="status-text">已配置</span>
              </div>
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

/* ===== 下部双列布局 ===== */
.bottom-row {
  display: flex;
  gap: 8px;
  flex: 1;
  min-height: 0;
}

.bottom-row > * {
  flex: 1;
  min-width: 0;
}

/* ===== 场景参数 ===== */
.params-card {
  flex: 1;
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

/* ===== 约束条件 ===== */
.constraint-card {
  flex: 1;
}

.constraint-count-badge {
  margin-left: auto;
  font-size: 11px;
  color: #00ff88;
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.25);
  padding: 2px 10px;
  border-radius: 12px;
  white-space: nowrap;
}

.badge-num {
  font-weight: 700;
  font-size: 13px;
}

.constraint-body-list {
  padding: 4px 16px;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow-y: auto;
}

.constraint-body-list::-webkit-scrollbar {
  width: 3px;
}

.constraint-body-list::-webkit-scrollbar-track {
  background: transparent;
}

.constraint-body-list::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.2);
  border-radius: 2px;
}

.constraint-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(50, 150, 255, 0.06);
}

.constraint-row:last-child {
  border-bottom: none;
}

.constraint-icon {
  color: #00d4ff;
  flex-shrink: 0;
  opacity: 0.8;
  display: flex;
  align-items: center;
}

.constraint-info {
  flex: 1;
  min-width: 0;
}

.constraint-name {
  font-size: 12px;
  font-weight: 500;
  color: #c0c8d4;
  margin-bottom: 1px;
}

.constraint-desc {
  font-size: 11px;
  color: #5a6f83;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.constraint-status {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.status-check {
  color: #00ff88;
}

.status-text {
  font-size: 11px;
  color: #00ff88;
  font-weight: 500;
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
