<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import ModelConfigFooter from '@/components/model-config/ModelConfigFooter.vue'
import { useModelConfigStore } from '@/stores/modelConfig'
import {
  dispatchModels,
  optimizationAlgorithms,
  algorithmParameters,
  reservoirGroups,
} from '@/mock/modelConfig'
import type { DispatchModel, OptimizationAlgorithm, AlgorithmParameter } from '@/mock/modelConfig'

// ==================== Store ====================
const store = useModelConfigStore()

// ==================== Mock 数据 ====================
const allModels = dispatchModels.data as DispatchModel[]
const allAlgorithms = optimizationAlgorithms.data as OptimizationAlgorithm[]
const paramDefs = algorithmParameters.data as AlgorithmParameter[]
const groups = reservoirGroups.data

// ==================== 响应式状态 ====================
const router = useRouter()

// 从 Store 读取初始值（已被 Step 2 联动影响）
const selectedModelId = ref(store.modelAlgorithm.selectedModel)
const selectedAlgorithmId = ref(store.modelAlgorithm.selectedAlgorithm)

// 参数值 - 以 id 为 key 存储当前值
const paramValues = ref<Record<string, number>>({...store.modelAlgorithm.parameters})
// 初始化所有参数默认值
paramDefs.forEach(p => {
  if (!(p.id in paramValues.value)) {
    paramValues.value[p.id] = p.value
  }
})

// 当前算法对应的可见参数列表
const visibleParams = computed(() => {
  if (!currentAlgorithm.value) return paramDefs
  return paramDefs.filter(p => currentAlgorithm.value!.paramIds.includes(p.id))
})

// 当前选中的参数 ID（左侧列表选中项）
const selectedParamId = ref<string>('')

// 当前选中的参数详情
const currentParam = computed(() => {
  return paramDefs.find(p => p.id === selectedParamId.value) || null
})

// 监听算法切换，更新参数值，并自动选中第一个参数
watch(selectedAlgorithmId, (newAlgoId) => {
  const algo = allAlgorithms.find(a => a.id === newAlgoId)
  if (!algo) return
  // 保留当前算法支持的参数值，移除不支持的参数，添加新参数默认值
  const newValues: Record<string, number> = {}
  algo.paramIds.forEach(pid => {
    const def = paramDefs.find(p => p.id === pid)
    if (def) {
      newValues[pid] = pid in paramValues.value ? paramValues.value[pid] : def.value
    }
  })
  paramValues.value = newValues
  // 自动选中第一个参数
  if (algo.paramIds.length > 0) {
    selectedParamId.value = algo.paramIds[0]
  }
})

// 弹窗状态
const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)

// ==================== 计算属性 ====================

// 当前水库组合名称（联动 Step 2）
const currentGroupName = computed(() => {
  return groups.find(g => g.id === store.basicConfig.selectedReservoirGroup)?.name || '龙刘组合'
})

// 当前水库组合兼容的模型列表
const models = computed(() => {
  return store.compatibleModels.length > 0 ? store.compatibleModels : allModels
})

// 当前选中的模型
const currentModel = computed(() => {
  return models.value.find(m => m.id === selectedModelId.value)
})

// 当前模型支持的算法列表
const supportedAlgorithms = computed(() => {
  if (!currentModel.value) return allAlgorithms
  return allAlgorithms.filter(a => currentModel.value!.supportedAlgorithms.includes(a.id))
})

// 当前选中的算法
const currentAlgorithm = computed(() => {
  return allAlgorithms.find(a => a.id === selectedAlgorithmId.value)
})

// ==================== 模型/算法切换 ====================
watch(selectedModelId, (newModelId) => {
  const model = allModels.find(m => m.id === newModelId)
  if (model && !model.supportedAlgorithms.includes(selectedAlgorithmId.value)) {
    // 当前算法不被新模型支持，切换到第一个可用算法
    if (model.supportedAlgorithms.length > 0) {
      selectedAlgorithmId.value = model.supportedAlgorithms[0]
    }
  }
})

// ==================== 参数操作 ====================

// 手动输入处理
const handleParamInput = (paramId: string, rawValue: string | number, param: AlgorithmParameter) => {
  let val = typeof rawValue === 'string' ? parseFloat(rawValue) : rawValue
  if (isNaN(val)) {
    val = param.min
  }
  let clamped = Math.min(Math.max(val, param.min), param.max)
  // step 取整
  const steps = Math.round((clamped - param.min) / param.step)
  clamped = param.min + steps * param.step
  clamped = Math.round(clamped * 100) / 100
  paramValues.value[paramId] = clamped
}

// 恢复当前参数为默认值
const handleResetDefault = () => {
  if (!currentParam.value) return
  const def = paramDefs.find(p => p.id === currentParam.value!.id)
  if (def) {
    paramValues.value[def.id] = def.value
  }
}

// 获取参数定义
const getParamDef = (id: string) => paramDefs.find(p => p.id === id)

// 初始化选中第一个参数
const algo = allAlgorithms.find(a => a.id === selectedAlgorithmId.value)
if (algo && algo.paramIds.length > 0) {
  selectedParamId.value = algo.paramIds[0]
}

// ==================== 步骤条点击 ====================
const handleStepClick = (step: number) => {
  if (step === 1) router.push('/model-config/model-data')
  if (step === 2) router.push('/model-config/basic-config')
}

// ==================== 底部操作 ====================
const handleCancel = () => { cancelDialogVisible.value = true }
const handleSave = () => { saveDialogVisible.value = true }
const handlePrev = () => { router.push('/model-config/basic-config') }
const handleNext = () => {
  if (!selectedModelId.value || !selectedAlgorithmId.value) {
    ElMessage.warning('请选择调度模型和优化算法')
    return
  }
  // 写入 Store（联动 Step 4）
  store.setModelAlgorithm({
    selectedModel: selectedModelId.value,
    selectedAlgorithm: selectedAlgorithmId.value,
    parameters: { ...paramValues.value },
  })
  router.push('/model-config/scenario-constraint')
}

const confirmSave = () => {
  saveDialogVisible.value = false
  // 写入 Store
  store.setModelAlgorithm({
    selectedModel: selectedModelId.value,
    selectedAlgorithm: selectedAlgorithmId.value,
    parameters: { ...paramValues.value },
  })
  ElMessage.success('模型算法配置已保存')
}

const confirmCancel = () => {
  cancelDialogVisible.value = false
  ElMessage.info('已取消，未保存任何更改')
}

// ==================== Tooltip 渲染 ====================
const renderTooltipContent = (desc: string) => {
  return `<div style="font-size:12px;line-height:1.6;color:#c0c8d4;max-width:220px;">${desc}</div>`
}

// 参数格式化显示
const formatParamValue = (param: AlgorithmParameter) => {
  const val = paramValues.value[param.id]
  if (param.step >= 1) return val.toString()
  return val.toFixed(2)
}
</script>

<template>
  <div class="model-algorithm-view">
    <!-- 步骤条 -->
    <ModelConfigStepBar :current-step="3" @step-click="handleStepClick" />

    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 第一行：模型与算法选择 -->
      <div class="selection-row">
        <!-- 左侧：调度模型选择（联动 Step 2 水库组合） -->
        <div class="card select-card">
          <div class="card-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
              <rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.3"/>
              <circle cx="8" cy="6" r="1.5" stroke="currentColor" stroke-width="1.3"/>
              <path d="M5 11c0-1.7 1.3-3 3-3s3 1.3 3 3" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            <span class="card-title">调度模型选择</span>
          </div>
          <div class="card-body">
            <el-select
              v-model="selectedModelId"
              size="small"
              class="dark-select full-width-select"
            >
              <el-option
                v-for="model in models"
                :key="model.id"
                :label="model.name"
                :value="model.id"
              />
            </el-select>
            <div class="select-hint">
              当前模型：
              <span class="hint-value">{{ currentModel?.name || '未选择' }}</span>
            </div>
            <div class="linkage-hint">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none" class="linkage-icon">
                <path d="M4 8h8M8 4v8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
              <span class="linkage-text">当前水库组合「{{ currentGroupName }}」可用的模型</span>
            </div>
          </div>
        </div>

        <!-- 右侧：优化算法选择 -->
        <div class="card select-card">
          <div class="card-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
              <path d="M2 12l4-6 3 3 5-5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="3" cy="13" r="1" fill="currentColor"/>
              <circle cx="7" cy="7" r="1" fill="currentColor"/>
              <circle cx="13" cy="4" r="1" fill="currentColor"/>
            </svg>
            <span class="card-title">优化算法选择</span>
          </div>
          <div class="card-body">
            <el-select
              v-model="selectedAlgorithmId"
              size="small"
              class="dark-select full-width-select"
            >
              <el-option
                v-for="algo in supportedAlgorithms"
                :key="algo.id"
                :label="algo.name"
                :value="algo.id"
              />
            </el-select>
            <div class="select-hint">
              当前算法：
              <span class="hint-value">{{ currentAlgorithm?.name || '未选择' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 第二行：算法参数设置（左列表 + 右详情） -->
      <div class="card params-card">
        <div class="card-header">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
            <circle cx="5" cy="4" r="2" stroke="currentColor" stroke-width="1.3"/>
            <circle cx="11" cy="12" r="2" stroke="currentColor" stroke-width="1.3"/>
            <path d="M5 6v6M11 4v2" stroke="currentColor" stroke-width="1.3"/>
          </svg>
          <span class="card-title">算法参数设置</span>
          <span class="algo-name-tag" v-if="currentAlgorithm">{{ currentAlgorithm.name }}</span>
        </div>
        <div class="card-body params-body">
          <!-- 左侧：参数列表 -->
          <div class="param-list">
            <div
              v-for="param in visibleParams"
              :key="param.id"
              class="param-list-item"
              :class="{ active: selectedParamId === param.id }"
              @click="selectedParamId = param.id"
            >
              <div class="param-list-name">{{ param.name }}</div>
              <div class="param-list-value">{{ formatParamValue(param) }}</div>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="param-list-arrow">
                <path d="M5 3l4 4-4 4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>

          <!-- 右侧：参数详情 -->
          <div class="param-detail" v-if="currentParam">
            <div class="detail-header">
              <div class="detail-name">{{ currentParam.name }}</div>
              <el-tooltip
                :content="currentParam.description"
                placement="top"
                effect="dark"
                :show-after="300"
                popper-class="param-tooltip"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="detail-info-icon">
                  <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.2"/>
                  <path d="M8 5.5v4M8 5.5v-1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                </svg>
              </el-tooltip>
            </div>

            <!-- 数值输入 -->
            <div class="detail-value-row">
              <el-input
                :model-value="formatParamValue(currentParam)"
                size="small"
                class="dark-input detail-input"
                @update:model-value="(val: string | number) => handleParamInput(currentParam.id, val, currentParam)"
              />
            </div>

            <!-- 滑块 -->
            <div class="detail-slider-row">
              <span class="slider-label">{{ currentParam.min }}</span>
              <el-slider
                v-model="paramValues[currentParam.id]"
                :min="currentParam.min"
                :max="currentParam.max"
                :step="currentParam.step"
                size="small"
                class="dark-slider"
              />
              <span class="slider-label">{{ currentParam.max }}</span>
            </div>

            <!-- 范围提示 -->
            <div class="detail-range">
              取值范围：<span class="range-val">{{ currentParam.min }} ~ {{ currentParam.max }}</span>
              <button class="reset-btn" @click="handleResetDefault" title="恢复为默认值">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M3 7a4 4 0 016.5-3.1M11 7a4 4 0 01-6.5 3.1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                  <path d="M9.5 2.5L12 4l-2.5 1.5M4.5 11.5L2 10l2.5-1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                恢复默认值
              </button>
            </div>

            <!-- 分隔线 -->
            <div class="detail-divider"></div>

            <!-- 参数说明 -->
            <div class="detail-desc">
              <div class="desc-label">参数说明</div>
              <p class="desc-text">{{ currentParam.description }}</p>
            </div>
          </div>

          <!-- 右侧空状态 -->
          <div class="param-detail param-detail-empty" v-else>
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="empty-icon">
              <circle cx="24" cy="24" r="20" stroke="rgba(50,150,255,0.2)" stroke-width="1.5" stroke-dasharray="4 4"/>
              <path d="M18 24l4 4 8-8" stroke="rgba(50,150,255,0.3)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="empty-text">请在左侧选择参数</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <ModelConfigFooter
      :step="3"
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
          <span class="dialog-title-main">确认保存当前模型算法配置？</span>
          <span class="dialog-desc">保存后模型、算法和参数配置将保留。</span>
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
.model-algorithm-view {
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

/* ===== 选择行 ===== */
.selection-row {
  display: flex;
  gap: 8px;
}

.selection-row > * {
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

/* 选择卡片需要可见溢出以支持下拉框交互 */
.select-card {
  overflow: visible;
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

/* ===== 选择卡片 ===== */
.select-card .card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  justify-content: center;
}

.full-width-select {
  width: 100%;
}

.select-hint {
  font-size: 12px;
  color: #5a6f83;
}

.hint-value {
  color: #00d4ff;
  font-weight: 500;
}

/* ===== 联动提示 ===== */
.linkage-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  padding: 4px 8px;
  background: rgba(0, 175, 255, 0.06);
  border-radius: 4px;
  border: 1px solid rgba(0, 175, 255, 0.12);
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

/* ===== 参数卡片 ===== */
.params-card {
  flex: 1;
  min-height: 0;
}

.params-card .card-body {
  padding: 0;
}

/* 算法名称标签（标题右侧） */
.algo-name-tag {
  margin-left: auto;
  font-size: 11px;
  color: #00d4ff;
  background: rgba(0, 175, 255, 0.12);
  padding: 2px 10px;
  border-radius: 4px;
  font-weight: 500;
}

/* ===== 参数左右布局 ===== */
.params-body {
  display: flex;
  flex: 1;
  min-height: 0;
}

/* 左侧参数列表 */
.param-list {
  width: 200px;
  flex-shrink: 0;
  overflow-y: auto;
  border-right: 1px solid rgba(50, 150, 255, 0.1);
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.param-list::-webkit-scrollbar {
  width: 3px;
}
.param-list::-webkit-scrollbar-track {
  background: transparent;
}
.param-list::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.2);
  border-radius: 2px;
}

.param-list-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.param-list-item:hover {
  background: rgba(0, 175, 255, 0.06);
  border-color: rgba(50, 150, 255, 0.15);
}

.param-list-item.active {
  background: rgba(0, 175, 255, 0.1);
  border-color: rgba(0, 175, 255, 0.3);
}

.param-list-name {
  flex: 1;
  font-size: 12px;
  color: #c0c8d4;
  font-weight: 500;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.param-list-item.active .param-list-name {
  color: #00d4ff;
}

.param-list-value {
  font-size: 12px;
  color: #7a8fa3;
  font-weight: 500;
  min-width: 32px;
  text-align: right;
}

.param-list-item.active .param-list-value {
  color: #e0e6ed;
}

.param-list-arrow {
  color: rgba(50, 150, 255, 0.3);
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s;
}

.param-list-item.active .param-list-arrow {
  opacity: 1;
  color: #00d4ff;
}

/* 右侧参数详情 */
.param-detail {
  flex: 1;
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

.param-detail-empty {
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.empty-icon {
  flex-shrink: 0;
}

.empty-text {
  font-size: 13px;
  color: #5a6f83;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-name {
  font-size: 18px;
  font-weight: 600;
  color: #e0e6ed;
}

.detail-info-icon {
  color: #5a6f83;
  cursor: pointer;
  transition: color 0.2s;
  flex-shrink: 0;
}

.detail-info-icon:hover {
  color: #00d4ff;
}

.detail-value-row {
  display: flex;
}

.detail-input {
  width: 160px;
}

.detail-input :deep(.el-input__wrapper) {
  background: rgba(2, 27, 63, 0.8) !important;
  box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.25) inset !important;
}

.detail-input :deep(.el-input__inner) {
  color: #00d4ff !important;
  font-size: 24px;
  font-weight: 700;
  text-align: center;
}

.detail-slider-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slider-label {
  font-size: 11px;
  color: #5a6f83;
  flex-shrink: 0;
  min-width: 36px;
  text-align: center;
}

.detail-range {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #5a6f83;
}

.range-val {
  color: #7a8fa3;
  font-weight: 500;
}

.reset-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  padding: 4px 10px;
  background: rgba(50, 150, 255, 0.08);
  border: 1px solid rgba(50, 150, 255, 0.2);
  border-radius: 4px;
  color: #7a8fa3;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover {
  background: rgba(0, 175, 255, 0.15);
  border-color: rgba(0, 175, 255, 0.4);
  color: #00d4ff;
}

.detail-divider {
  height: 1px;
  background: rgba(50, 150, 255, 0.1);
}

.detail-desc {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.desc-label {
  font-size: 13px;
  font-weight: 600;
  color: #7a8fa3;
}

.desc-text {
  margin: 0;
  font-size: 13px;
  color: #c0c8d4;
  line-height: 1.8;
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

/* 滑块深色适配 */
:deep(.el-slider__runway) {
  background: rgba(50, 150, 255, 0.15) !important;
}

:deep(.el-slider__bar) {
  background: linear-gradient(90deg, rgba(0, 175, 255, 0.4), #00d4ff) !important;
}

:deep(.el-slider__button) {
  border: 2px solid #00d4ff !important;
  background: rgba(2, 27, 63, 0.9) !important;
  box-shadow: 0 0 6px rgba(0, 212, 255, 0.3) !important;
}

:deep(.el-slider__button:hover) {
  transform: scale(1.15) !important;
}

:deep(.el-slider__marks-text) {
  color: #5a6f83 !important;
  font-size: 10px !important;
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

/* ===== Tooltip 深色适配 ===== */
:deep(.param-tooltip) {
  background: rgba(6, 30, 70, 0.98) !important;
  border: 1px solid rgba(50, 150, 255, 0.4) !important;
  color: #c0c8d4 !important;
  font-size: 12px !important;
  line-height: 1.6 !important;
  max-width: 240px !important;
}

:deep(.param-tooltip .el-tooltip__arrow) {
  color: rgba(6, 30, 70, 0.98) !important;
}
</style>
