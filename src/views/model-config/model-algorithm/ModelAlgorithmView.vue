<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import ModelConfigFooter from '@/components/model-config/ModelConfigFooter.vue'
import { useModelConfigStore } from '@/stores/modelConfig'
import {
  dispatchModels,
  optimizationAlgorithms,
  algorithmParameters,
  dispatchObjectives,
  constraintSummary,
} from '@/mock/modelConfig'
import type { DispatchModel, OptimizationAlgorithm, AlgorithmParameter, DispatchObjective, ConstraintDetail } from '@/mock/modelConfig'

// ==================== Store ====================
const store = useModelConfigStore()

// ==================== Mock 数据 ====================
const allModels = dispatchModels.data as DispatchModel[]
const allAlgorithms = optimizationAlgorithms.data as OptimizationAlgorithm[]
const paramDefs = algorithmParameters.data as AlgorithmParameter[]
const objectivesDef = dispatchObjectives.data as DispatchObjective[]
const constraintData = constraintSummary.data

// ==================== 路由 ====================
const router = useRouter()

// ==================== 左侧：模型与算法状态 ====================
const selectedModelId = ref(store.modelAlgorithm.selectedModel)
const selectedAlgorithmId = ref(store.modelAlgorithm.selectedAlgorithm)

// 参数值
const paramValues = ref<Record<string, number>>({...store.modelAlgorithm.parameters})
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

const selectedParamId = ref<string>('')

const currentParam = computed(() => {
  return paramDefs.find(p => p.id === selectedParamId.value) || null
})

// ==================== 右侧：调度目标与约束状态 ====================
const selectedObjectives = ref<string[]>([...store.basicConfig.selectedObjectives])
const constraintDialogVisible = ref(false)
const constraintEnabled = ref<boolean[]>(constraintData.constraints.map(() => true))
const editingConstraints = ref<ConstraintDetail[]>(
  constraintData.constraints.map(c => ({ ...c }))
)
const enabledConstraintCount = computed(() => constraintEnabled.value.filter(Boolean).length)

// ==================== 弹窗状态 ====================
const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)

// ==================== 计算属性 ====================

// 当前水库组合名称（联动 Step 2）
const currentGroupName = computed(() => {
  const groups = [
    { id: 'long-liu', name: '龙刘组合' },
    { id: 'long-liu-hei', name: '龙刘黑组合' },
    { id: 'all', name: '全部水库' },
  ]
  return groups.find(g => g.id === store.dispatchSubject.selectedGroupId)?.name
    || groups.find(g => g.id === store.basicConfig.selectedReservoirGroup)?.name
    || '龙刘组合'
})

// 当前水库组合兼容的模型列表
const models = computed(() => {
  // 从 dispatchSubject 或 basicConfig 获取
  return store.compatibleModels.length > 0 ? store.compatibleModels : allModels
})

const currentModel = computed(() => {
  return models.value.find(m => m.id === selectedModelId.value)
})

const supportedAlgorithms = computed(() => {
  if (!currentModel.value) return allAlgorithms
  return allAlgorithms.filter(a => currentModel.value!.supportedAlgorithms.includes(a.id))
})

const currentAlgorithm = computed(() => {
  return allAlgorithms.find(a => a.id === selectedAlgorithmId.value)
})

// ==================== 模型/算法切换联动 ====================
watch(selectedModelId, (newModelId) => {
  const model = allModels.find(m => m.id === newModelId)
  if (model && !model.supportedAlgorithms.includes(selectedAlgorithmId.value)) {
    if (model.supportedAlgorithms.length > 0) {
      selectedAlgorithmId.value = model.supportedAlgorithms[0]
    }
  }
})

watch(selectedAlgorithmId, (newAlgoId) => {
  const algo = allAlgorithms.find(a => a.id === newAlgoId)
  if (!algo) return
  const newValues: Record<string, number> = {}
  algo.paramIds.forEach(pid => {
    const def = paramDefs.find(p => p.id === pid)
    if (def) {
      newValues[pid] = pid in paramValues.value ? paramValues.value[pid] : def.value
    }
  })
  paramValues.value = newValues
  if (algo.paramIds.length > 0) {
    selectedParamId.value = algo.paramIds[0]
  }
})

// ==================== 参数操作 ====================
const handleParamInput = (paramId: string, rawValue: string | number, param: AlgorithmParameter) => {
  let val = typeof rawValue === 'string' ? parseFloat(rawValue) : rawValue
  if (isNaN(val)) val = param.min
  let clamped = Math.min(Math.max(val, param.min), param.max)
  const steps = Math.round((clamped - param.min) / param.step)
  clamped = param.min + steps * param.step
  clamped = Math.round(clamped * 100) / 100
  paramValues.value[paramId] = clamped
}

const handleResetDefault = () => {
  if (!currentParam.value) return
  const def = paramDefs.find(p => p.id === currentParam.value!.id)
  if (def) paramValues.value[def.id] = def.value
}

const getParamDef = (id: string) => paramDefs.find(p => p.id === id)

// 初始化选中第一个参数
const algo = allAlgorithms.find(a => a.id === selectedAlgorithmId.value)
if (algo && algo.paramIds.length > 0) {
  selectedParamId.value = algo.paramIds[0]
}

// ==================== Tooltip ====================
const renderTooltipContent = (desc: string) => {
  return `<div style="font-size:12px;line-height:1.6;color:#c0c8d4;max-width:220px;">${desc}</div>`
}

const formatParamValue = (param: AlgorithmParameter) => {
  const val = paramValues.value[param.id]
  if (param.step >= 1) return val.toString()
  return val.toFixed(2)
}

// ==================== 调度目标交互 ====================
const handleToggleObjective = (id: string) => {
  const idx = selectedObjectives.value.indexOf(id)
  if (idx >= 0) {
    if (selectedObjectives.value.length > 1) {
      selectedObjectives.value.splice(idx, 1)
    } else {
      ElMessage.warning('至少保留一个调度目标')
    }
  } else {
    selectedObjectives.value.push(id)
  }
}

// ==================== 约束弹窗操作 ====================
const confirmConstraints = () => {
  constraintDialogVisible.value = false
  ElMessage.success('约束条件已更新')
}

// ==================== 底部操作 ====================
const handlePrev = () => { router.push('/model-config/model-data') }
const handleCancel = () => { cancelDialogVisible.value = true }
const handleSave = () => { saveDialogVisible.value = true }

const handleNext = () => {
  if (!selectedModelId.value || !selectedAlgorithmId.value) {
    ElMessage.warning('请选择调度模型和优化算法')
    return
  }
  if (selectedObjectives.value.length === 0) {
    ElMessage.warning('请至少选择一个调度目标')
    return
  }
  // 写入模型算法
  store.setModelAlgorithm({
    selectedModel: selectedModelId.value,
    selectedAlgorithm: selectedAlgorithmId.value,
    parameters: { ...paramValues.value },
  })
  // 写入调度目标和约束
  store.setBasicConfig({
    selectedObjectives: [...selectedObjectives.value],
    constraintEnabled: [...constraintEnabled.value],
  })
  store.markStepCompleted(4)
  router.push('/model-config/scenario-constraint')
}

const confirmSave = () => {
  saveDialogVisible.value = false
  store.setModelAlgorithm({
    selectedModel: selectedModelId.value,
    selectedAlgorithm: selectedAlgorithmId.value,
    parameters: { ...paramValues.value },
  })
  store.setBasicConfig({
    selectedObjectives: [...selectedObjectives.value],
    constraintEnabled: [...constraintEnabled.value],
  })
  ElMessage.success('模型算法配置已保存')
}

const confirmCancel = () => {
  cancelDialogVisible.value = false
  ElMessage.info('已取消，未保存任何更改')
}

// ==================== SVG 图标 ====================
const objectiveIcons: Record<string, string> = {
  shield: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 4L5 7v5c0 4.4 7 8 7 8s7-3.6 7-8V7l-7-3z" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linejoin="round"/><path d="M10 13l1.5 1.5L15 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  flash: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M13 3L7 13h5l-1 8 7-12h-5l1-6z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" fill="none"/></svg>',
  leaf: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 5c-4 0-7 3-7 7 0 6 7 8 7 8s7-2 7-8c0-4-3-7-7-7z" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M12 13v-6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M9 11l3-3 3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  sand: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M6 4h12l-3 7H9L6 4z" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M7 11l-3 9h16l-3-9" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M9 16h6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
  sync: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M19 7c-2-3-5-4-8-3S6 8 5 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M5 17c2 3 5 4 8 3s5-5 6-9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M15 5l4-2v4l-4-2z" fill="currentColor"/><path d="M9 19l-4 2v-4l4 2z" fill="currentColor"/></svg>',
}
</script>

<template>
  <div class="model-algorithm-view">
    <!-- 步骤条 -->
    <ModelConfigStepBar :current-step="4" version="new" />

    <!-- 主体：左右分区 -->
    <div class="main-content">
      <!-- ===== 左侧：模型与算法 ===== -->
      <div class="left-panel">
        <!-- 第一行：模型 + 算法选择 -->
        <div class="selection-row">
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
              <el-select v-model="selectedModelId" size="small" class="dark-select full-width-select">
                <el-option v-for="model in models" :key="model.id" :label="model.name" :value="model.id" />
              </el-select>
              <div class="select-hint">
                当前模型：<span class="hint-value">{{ currentModel?.name || '未选择' }}</span>
              </div>
              <div class="linkage-hint">
                <svg width="12" height="12" viewBox="0 0 16 16" fill="none" class="linkage-icon">
                  <path d="M4 8h8M8 4v8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                </svg>
                <span class="linkage-text">当前水库组合「{{ currentGroupName }}」可用的模型</span>
              </div>
            </div>
          </div>

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
              <el-select v-model="selectedAlgorithmId" size="small" class="dark-select full-width-select">
                <el-option v-for="algo in supportedAlgorithms" :key="algo.id" :label="algo.name" :value="algo.id" />
              </el-select>
              <div class="select-hint">
                当前算法：<span class="hint-value">{{ currentAlgorithm?.name || '未选择' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 第二行：算法参数设置 -->
        <div class="card params-card">
          <div class="card-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
              <circle cx="5" cy="4" r="2" stroke="currentColor" stroke-width="1.3"/>
              <circle cx="11" cy="12" r="2" stroke="currentColor" stroke-width="1.3"/>
              <path d="M5 6v6M11 4v2" stroke="currentColor" stroke-width="1.3"/>
            </svg>
            <span class="card-title">算法参数设置</span>
            <span v-if="currentAlgorithm" class="algo-name-tag">{{ currentAlgorithm.name }}</span>
          </div>
          <div class="card-body params-body">
            <!-- 左列表 -->
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

            <!-- 右详情 -->
            <div v-if="currentParam" class="param-detail">
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
              <div class="detail-value-row">
                <el-input
                  :model-value="formatParamValue(currentParam)"
                  size="small"
                  class="dark-input detail-input"
                  @update:model-value="(val: string|number) => handleParamInput(currentParam.id, val, currentParam)"
                />
              </div>
              <div class="detail-slider-row">
                <span class="slider-label">{{ currentParam.min }}</span>
                <el-slider v-model="paramValues[currentParam.id]" :min="currentParam.min" :max="currentParam.max" :step="currentParam.step" size="small" class="dark-slider" />
                <span class="slider-label">{{ currentParam.max }}</span>
              </div>
              <div class="detail-range">
                取值范围：<span class="range-val">{{ currentParam.min }} ~ {{ currentParam.max }}</span>
                <button class="reset-btn" @click="handleResetDefault">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M3 7a4 4 0 016.5-3.1M11 7a4 4 0 01-6.5 3.1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                    <path d="M9.5 2.5L12 4l-2.5 1.5M4.5 11.5L2 10l2.5-1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  恢复默认值
                </button>
              </div>
              <div class="detail-divider"></div>
              <div class="detail-desc">
                <div class="desc-label">参数说明</div>
                <p class="desc-text">{{ currentParam.description }}</p>
              </div>
            </div>
            <div v-else class="param-detail param-detail-empty">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="empty-icon">
                <circle cx="24" cy="24" r="20" stroke="rgba(50,150,255,0.2)" stroke-width="1.5" stroke-dasharray="4 4"/>
                <path d="M18 24l4 4 8-8" stroke="rgba(50,150,255,0.3)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="empty-text">请在左侧选择参数</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== 右侧：调度目标 + 约束条件 ===== -->
      <div class="right-panel">
        <!-- 调度目标 -->
        <div class="card right-card objectives-card">
          <div class="card-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
              <circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.3"/>
              <circle cx="8" cy="8" r="2.5" stroke="currentColor" stroke-width="1.3"/>
              <circle cx="8" cy="8" r="1" fill="currentColor"/>
            </svg>
            <span class="card-title">调度目标</span>
            <span class="card-badge">{{ selectedObjectives.length }} / {{ objectivesDef.length }}</span>
          </div>
          <div class="card-body objective-body">
            <div class="objective-list">
              <div
                v-for="obj in objectivesDef"
                :key="obj.id"
                class="objective-item"
                :class="{ 'obj-active': selectedObjectives.includes(obj.id) }"
                @click="handleToggleObjective(obj.id)"
              >
                <div class="obj-left">
                  <div class="obj-icon" v-html="objectiveIcons[obj.icon] || ''"></div>
                  <div class="obj-info">
                    <div class="obj-name">{{ obj.name }}</div>
                    <div class="obj-desc">{{ obj.description }}</div>
                  </div>
                </div>
                <div v-if="selectedObjectives.includes(obj.id)" class="obj-check">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="8" r="6.5" fill="rgba(0,175,255,0.15)" stroke="#00afff" stroke-width="1.5"/>
                    <path d="M5.5 8.5L7 10l3.5-4" stroke="#00afff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 约束条件 -->
        <div class="card right-card constraint-card">
          <div class="card-header">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="card-icon">
              <rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.3"/>
              <path d="M6 5h4M6 8h4M6 11h2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            <span class="card-title">约束条件</span>
          </div>
          <div class="card-body constraint-body">
            <div class="constraint-summary">
              <div class="constraint-count-row">
                <span class="constraint-count-label">已启用</span>
                <span class="constraint-count-value">{{ enabledConstraintCount }}</span>
                <span class="constraint-count-label">项约束条件</span>
              </div>
              <div class="constraint-desc">{{ constraintData.description }}</div>
              <el-button size="small" class="constraint-btn" @click="constraintDialogVisible = true">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
                  <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                查看详情
              </el-button>
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

    <!-- ===== 约束条件弹窗 ===== -->
    <el-dialog
      v-model="constraintDialogVisible"
      title="约束条件详情"
      width="620px"
      :close-on-click-modal="false"
      class="confirm-dialog constraint-detail-dialog"
    >
      <div class="constraint-detail-body">
        <div class="constraint-summary-text">
          选择本次计算需要启用的约束条件，并可编辑各约束的数值范围：
        </div>
        <div class="constraint-switch-list">
          <div
            v-for="(c, cIdx) in editingConstraints"
            :key="cIdx"
            class="constraint-switch-item"
            :class="{ 'constraint-disabled': !constraintEnabled[cIdx] }"
          >
            <div class="constraint-switch-top">
              <div class="constraint-switch-left">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="constraint-item-icon">
                  <circle cx="8" cy="8" r="4" fill="rgba(0,175,255,0.15)" stroke="#00afff" stroke-width="1.2"/>
                  <path d="M6 8l1.5 1.5L10 7" stroke="#00afff" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span class="constraint-item-name">{{ c.name }}</span>
              </div>
              <el-switch v-model="constraintEnabled[cIdx]" size="small" class="dark-switch" />
            </div>
            <div class="constraint-range-row">
              <div class="range-item">
                <label class="range-label">最小值</label>
                <el-input-number v-model="c.min" size="small" :disabled="!constraintEnabled[cIdx]" controls-position="right" class="dark-input-number" />
              </div>
              <div class="range-item">
                <label class="range-label">最大值</label>
                <el-input-number v-model="c.max" size="small" :disabled="!constraintEnabled[cIdx]" controls-position="right" class="dark-input-number" />
              </div>
              <span class="range-unit">{{ c.unit }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="constraintDialogVisible = false">取消</el-button>
          <el-button type="primary" size="small" @click="confirmConstraints">确认</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- ===== 保存确认弹窗 ===== -->
    <el-dialog v-model="saveDialogVisible" title="保存确认" width="400px" :close-on-click-modal="false" class="confirm-dialog">
      <div class="dialog-body">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
          <circle cx="24" cy="24" r="22" stroke="#00afff" stroke-width="2" fill="rgba(0,175,255,0.1)"/>
          <path d="M16 24l6 6 10-10" stroke="#00afff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <div class="dialog-text">
          <span class="dialog-title-main">确认保存当前配置？</span>
          <span class="dialog-desc">保存后模型算法、调度目标和约束条件将保留。</span>
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
.model-algorithm-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 8px 12px;
  gap: 8px;
  overflow: hidden;
}

/* ===== 主体：左右分区 ===== */
.main-content {
  flex: 1;
  display: flex;
  gap: 8px;
  min-height: 0;
  overflow: hidden;
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  min-height: 0;
}

.right-panel {
  width: 280px;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
}

/* ===== 选择行 ===== */
.selection-row {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.selection-row > * {
  flex: 1;
  min-width: 0;
}

/* ===== 通用卡片 ===== */
.card {
  background: rgba(6, 30, 70, 0.5);
  border: 1px solid rgba(50, 150, 255, 0.25);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.select-card {
  overflow: visible;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.18);
  flex-shrink: 0;
}

.card-icon {
  color: #00d4ff;
  flex-shrink: 0;
}

.card-title {
  font-size: 12px;
  font-weight: 600;
  color: #e0e6ed;
}

.card-body {
  padding: 12px 14px;
  flex: 1;
}

.select-card .card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
}

.full-width-select { width: 100%; }

.select-hint {
  font-size: 11px;
  color: #5a6f83;
}

.hint-value { color: #00d4ff; font-weight: 500; }

.linkage-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: rgba(0, 175, 255, 0.06);
  border-radius: 4px;
  border: 1px solid rgba(0, 175, 255, 0.12);
}

.linkage-icon { color: #00d4ff; flex-shrink: 0; }
.linkage-text { font-size: 10px; color: #7a8fa3; line-height: 1.4; }

/* ===== 参数卡片 ===== */
.params-card {
  flex: 1;
  min-height: 0;
}

.params-card .card-body { padding: 0; }

.algo-name-tag {
  margin-left: auto;
  font-size: 10px;
  color: #00d4ff;
  background: rgba(0, 175, 255, 0.12);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.params-body {
  display: flex;
  flex: 1;
  min-height: 0;
}

/* 左列表 */
.param-list {
  width: 170px;
  flex-shrink: 0;
  overflow-y: auto;
  border-right: 1px solid rgba(50, 150, 255, 0.1);
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.param-list::-webkit-scrollbar { width: 3px; }
.param-list::-webkit-scrollbar-track { background: transparent; }
.param-list::-webkit-scrollbar-thumb { background: rgba(50,150,255,0.2); border-radius: 2px; }

.param-list-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 6px;
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
  font-size: 11px;
  color: #c0c8d4;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.param-list-item.active .param-list-name { color: #00d4ff; }

.param-list-value {
  font-size: 11px;
  color: #7a8fa3;
  font-weight: 500;
  min-width: 28px;
  text-align: right;
}

.param-list-item.active .param-list-value { color: #e0e6ed; }

.param-list-arrow { color: rgba(50,150,255,0.3); flex-shrink: 0; opacity: 0; transition: opacity 0.2s; }
.param-list-item.active .param-list-arrow { opacity: 1; color: #00d4ff; }

/* 右详情 */
.param-detail {
  flex: 1;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
  overflow-y: auto;
}

.param-detail-empty {
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.empty-icon { flex-shrink: 0; }
.empty-text { font-size: 12px; color: #5a6f83; }

.detail-header { display: flex; align-items: center; gap: 8px; }
.detail-name { font-size: 16px; font-weight: 600; color: #e0e6ed; }
.detail-info-icon { color: #5a6f83; cursor: pointer; flex-shrink: 0; }
.detail-info-icon:hover { color: #00d4ff; }
.detail-value-row { display: flex; }
.detail-input { width: 140px; }
.detail-input :deep(.el-input__wrapper) { background: rgba(2,27,63,0.8)!important; box-shadow: 0 0 0 1px rgba(50,150,255,0.25) inset!important; }
.detail-input :deep(.el-input__inner) { color: #00d4ff!important; font-size: 22px; font-weight: 700; text-align: center; }
.detail-slider-row { display: flex; align-items: center; gap: 10px; }
.slider-label { font-size: 10px; color: #5a6f83; flex-shrink: 0; min-width: 30px; text-align: center; }
.detail-range { display: flex; align-items: center; gap: 12px; font-size: 11px; color: #5a6f83; }
.range-val { color: #7a8fa3; font-weight: 500; }
.reset-btn {
  display: flex; align-items: center; gap: 4px; margin-left: auto;
  padding: 3px 8px; background: rgba(50,150,255,0.08);
  border: 1px solid rgba(50,150,255,0.2); border-radius: 4px;
  color: #7a8fa3; font-size: 10px; cursor: pointer; transition: all 0.2s;
}
.reset-btn:hover { background: rgba(0,175,255,0.15); border-color: rgba(0,175,255,0.4); color: #00d4ff; }
.detail-divider { height: 1px; background: rgba(50,150,255,0.1); }
.detail-desc { display: flex; flex-direction: column; gap: 6px; }
.desc-label { font-size: 12px; font-weight: 600; color: #7a8fa3; }
.desc-text { margin: 0; font-size: 12px; color: #c0c8d4; line-height: 1.7; }

/* ===== 右侧：调度目标 ===== */
.right-card .card-body { padding: 8px 10px; }

.objective-body {
  overflow-y: auto;
  min-height: 0;
}

.objective-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.objective-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.objective-item:hover {
  background: rgba(0, 175, 255, 0.04);
  border-color: rgba(50, 150, 255, 0.1);
}

.objective-item.obj-active {
  background: rgba(0, 175, 255, 0.06);
  border-color: rgba(0, 175, 255, 0.3);
}

.obj-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.obj-icon {
  width: 20px;
  height: 20px;
  color: #5a8abf;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.obj-active .obj-icon { color: #00d4ff; }

.obj-info { min-width: 0; }

.obj-name {
  font-size: 12px;
  font-weight: 600;
  color: #7a8fa3;
  transition: color 0.2s;
}

.obj-active .obj-name { color: #e0e6ed; }

.obj-desc {
  font-size: 10px;
  color: #5a6f83;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.obj-check {
  flex-shrink: 0;
  animation: checkPop 0.2s ease;
}

@keyframes checkPop {
  0% { transform: scale(0); opacity: 0; }
  60% { transform: scale(1.15); }
  100% { transform: scale(1); opacity: 1; }
}

.card-badge {
  margin-left: auto;
  font-size: 10px;
  color: #5a8abf;
  background: rgba(0, 175, 255, 0.08);
  padding: 1px 8px;
  border-radius: 10px;
  font-weight: 500;
}

/* ===== 右侧：约束条件 ===== */
.constraint-card {
  flex-shrink: 0;
}

.constraint-body {
  display: flex;
  align-items: center;
}

.constraint-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
  text-align: center;
}

.constraint-count-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.constraint-count-label {
  font-size: 11px;
  color: #5a6f83;
}

.constraint-count-value {
  font-size: 24px;
  font-weight: 700;
  color: #e0e6ed;
  font-variant-numeric: tabular-nums;
}

.constraint-desc {
  font-size: 10px;
  color: #5a6f83;
  line-height: 1.4;
}

.constraint-btn {
  font-size: 11px !important;
  display: inline-flex !important;
  align-items: center;
  gap: 4px;
}

.btn-icon { flex-shrink: 0; }

/* ===== 约束弹窗 ===== */
.constraint-detail-body {
  max-height: 420px;
  overflow-y: auto;
  padding: 4px 0;
}

.constraint-summary-text {
  font-size: 12px;
  color: #c0c8d4;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.15);
}

.constraint-switch-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.constraint-switch-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(2, 27, 63, 0.4);
  border: 1px solid rgba(50, 150, 255, 0.12);
  transition: all 0.2s;
}

.constraint-switch-item.constraint-disabled {
  opacity: 0.45;
}

.constraint-switch-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.constraint-switch-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.constraint-item-icon { color: #00d4ff; flex-shrink: 0; }

.constraint-item-name {
  font-size: 12px;
  font-weight: 500;
  color: #c0c8d4;
}

.constraint-disabled .constraint-item-name {
  color: #5a6f83;
}

.constraint-range-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 22px;
}

.range-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.range-label {
  font-size: 10px;
  color: #5a6f83;
  white-space: nowrap;
}

.range-unit {
  font-size: 11px;
  color: #5a6f83;
  margin-left: 4px;
}

/* ===== 弹窗 ===== */
.confirm-dialog :deep(.el-dialog) {
  background: rgba(6, 30, 70, 0.98) !important;
  border: 1px solid rgba(50, 150, 255, 0.4);
  border-radius: 12px;
}

.confirm-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  padding: 14px 18px;
  margin: 0;
}

.confirm-dialog :deep(.el-dialog__title) {
  color: #e0e6ed;
  font-size: 14px;
  font-weight: 600;
}

.confirm-dialog :deep(.el-dialog__body) {
  padding: 18px 18px;
}

.confirm-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid rgba(50, 150, 255, 0.1);
  padding: 10px 18px;
}

.dialog-body { display: flex; align-items: flex-start; gap: 14px; }
.dialog-icon { flex-shrink: 0; margin-top: 2px; }
.dialog-text { display: flex; flex-direction: column; gap: 4px; }
.dialog-title-main { color: #e0e6ed; font-size: 13px; font-weight: 500; }
.dialog-desc { color: #7a8fa3; font-size: 11px; line-height: 1.5; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 8px; }

/* ===== Element Plus 深色覆盖 ===== */
:deep(.el-button) { --el-button-bg-color: transparent; --el-button-border-color: rgba(50,150,255,0.3); --el-button-text-color: #c0c8d4; --el-button-hover-bg-color: rgba(0,175,255,0.1); --el-button-hover-border-color: rgba(50,150,255,0.5); --el-button-hover-text-color: #e0e6ed; }
:deep(.el-button--primary) { --el-button-bg-color: rgba(0,175,255,0.2); --el-button-border-color: rgba(0,175,255,0.5); --el-button-text-color: #00d4ff; --el-button-hover-bg-color: rgba(0,175,255,0.3); --el-button-hover-border-color: rgba(0,175,255,0.7); --el-button-hover-text-color: #00e5ff; }
:deep(.el-select) { width: 100%; }
:deep(.dark-select .el-input__wrapper) { background: rgba(2,27,63,0.8)!important; box-shadow: 0 0 0 1px rgba(50,150,255,0.25) inset!important; }
:deep(.dark-select .el-input__inner) { color: #c0c8d4!important; font-size: 11px; }
:deep(.el-select-dropdown) { background: #0a1a2e!important; border: 1px solid rgba(50,150,255,0.3)!important; }
:deep(.el-select-dropdown__item) { color: #c0c8d4!important; }
:deep(.el-select-dropdown__item.hover) { background: rgba(0,175,255,0.1)!important; }
:deep(.el-select-dropdown__item.selected) { color: #00d4ff!important; font-weight: 600; }
:deep(.el-slider__runway) { background: rgba(50,150,255,0.15)!important; }
:deep(.el-slider__bar) { background: linear-gradient(90deg, rgba(0,175,255,0.4), #00d4ff)!important; }
:deep(.el-slider__button) { border: 2px solid #00d4ff!important; background: rgba(2,27,63,0.9)!important; box-shadow: 0 0 6px rgba(0,212,255,0.3)!important; }
:deep(.el-slider__button:hover) { transform: scale(1.15)!important; }
:deep(.dark-switch.el-switch.is-checked .el-switch__core) { background: rgba(0,175,255,0.5)!important; border-color: rgba(0,175,255,0.6)!important; }
:deep(.dark-input-number .el-input__wrapper) { background: rgba(2,27,63,0.8)!important; box-shadow: 0 0 0 1px rgba(50,150,255,0.2) inset!important; }
:deep(.dark-input-number .el-input__inner) { color: #c0c8d4!important; }
:deep(.param-tooltip) { background: rgba(6,30,70,0.98)!important; border: 1px solid rgba(50,150,255,0.4)!important; color: #c0c8d4!important; font-size: 11px!important; line-height: 1.6!important; max-width: 220px!important; }
:deep(.param-tooltip .el-tooltip__arrow) { color: rgba(6,30,70,0.98)!important; }
</style>
