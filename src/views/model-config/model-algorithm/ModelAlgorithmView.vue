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

    <!-- 主体：四方格 2×2 布局 -->
    <div class="main-content">
      <!-- ===== 卡1：模型与算法（左上） ===== -->
      <div class="card card-model">
        <div class="card-header">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
            <rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.3"/>
            <circle cx="8" cy="6" r="1.5" stroke="currentColor" stroke-width="1.3"/>
            <path d="M5 11c0-1.7 1.3-3 3-3s3 1.3 3 3" stroke="currentColor" stroke-width="1.3"/>
          </svg>
          <span>模型与算法</span>
          <span class="group-badge badge-blue">水库组合：{{ currentGroupName }}</span>
        </div>
        <div class="card-body">
          <div class="model-row">
            <div class="model-col">
              <div class="col-label">调度模型</div>
              <el-select v-model="selectedModelId" size="small" class="dark-select">
                <el-option v-for="model in models" :key="model.id" :label="model.name" :value="model.id" />
              </el-select>
              <div class="select-desc">当前：<span class="highlight">{{ currentModel?.name || '未选择' }}</span></div>
            </div>
            <div class="model-col">
              <div class="col-label">优化算法</div>
              <el-select v-model="selectedAlgorithmId" size="small" class="dark-select">
                <el-option v-for="algo in supportedAlgorithms" :key="algo.id" :label="algo.name" :value="algo.id" />
              </el-select>
              <div class="select-desc">当前：<span class="highlight">{{ currentAlgorithm?.name || '未选择' }}</span></div>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== 卡2：调度目标（右上） ===== -->
      <div class="card card-objectives">
        <div class="card-header">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
            <circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.3"/>
            <circle cx="8" cy="8" r="2.5" stroke="currentColor" stroke-width="1.3"/>
            <circle cx="8" cy="8" r="1" fill="currentColor"/>
          </svg>
          <span>调度目标</span>
          <span class="card-badge">{{ selectedObjectives.length }} / {{ objectivesDef.length }}</span>
        </div>
        <div class="card-body objective-body">
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
            <div class="obj-check-mark">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <circle cx="8" cy="8" r="6.5" fill="rgba(0,175,255,0.15)" stroke="#00afff" stroke-width="1.5"/>
                <path d="M5.5 8.5L7 10l3.5-4" stroke="#00afff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== 卡3：算法参数设置（左下） ===== -->
      <div class="card card-params">
        <div class="card-header">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
            <circle cx="5" cy="4" r="2" stroke="currentColor" stroke-width="1.3"/>
            <circle cx="11" cy="12" r="2" stroke="currentColor" stroke-width="1.3"/>
            <path d="M5 6v6M11 4v2" stroke="currentColor" stroke-width="1.3"/>
          </svg>
          <span>算法参数设置</span>
          <span v-if="currentAlgorithm" class="algo-tag">{{ currentAlgorithm.name }}</span>
        </div>
        <div class="card-body params-body">
          <div
            v-for="param in visibleParams"
            :key="param.id"
            class="param-row"
          >
            <div class="param-row-name">
              <span>{{ param.name }}</span>
              <el-tooltip
                :content="param.description"
                placement="top"
                effect="dark"
                :show-after="300"
                popper-class="param-tooltip"
              >
                <svg width="12" height="12" viewBox="0 0 16 16" fill="none" class="param-info-icon">
                  <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.2" fill="none"/>
                  <path d="M8 5.5v4M8 5.5v-1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                </svg>
              </el-tooltip>
            </div>
            <div class="param-row-controls">
              <el-input
                :model-value="formatParamValue(param)"
                size="small"
                class="param-value-input"
                @update:model-value="(val: string|number) => handleParamInput(param.id, val, param)"
              />
            </div>
            <div class="param-row-slider">
              <el-slider
                v-model="paramValues[param.id]"
                :min="param.min"
                :max="param.max"
                :step="param.step"
                size="small"
                class="dark-slider"
              />
            </div>
            <div class="param-row-range">{{ param.min }} ~ {{ param.max }}</div>
          </div>
        </div>
      </div>

      <!-- ===== 卡4：约束条件（右下） ===== -->
      <div class="card card-constraint">
        <div class="card-header">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="card-icon">
            <rect x="2" y="2" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.3"/>
            <path d="M6 5h4M6 8h4M6 11h2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
          <span>约束条件</span>
          <span class="card-badge">{{ enabledConstraintCount }} / {{ editingConstraints.length }}</span>
          <button class="constraint-edit-btn" @click="constraintDialogVisible = true" title="编辑约束">
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
              <path d="M11 2l3 3-9 9H2v-3l9-9z" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        <div class="card-body constraint-body">
          <div
            v-for="(c, cIdx) in editingConstraints"
            :key="cIdx"
            class="constraint-item"
            :class="{ 'constraint-disabled': !constraintEnabled[cIdx] }"
          >
            <div class="constraint-item-left">
              <span class="constraint-item-dot" :class="{ 'dot-on': constraintEnabled[cIdx] }"></span>
              <span class="constraint-item-name">{{ c.name }}</span>
            </div>
            <div class="constraint-item-right">
              <span class="constraint-item-range">{{ c.min }} ~ {{ c.max }}</span>
              <span class="constraint-item-unit">{{ c.unit }}</span>
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
      class="confirm-dialog"
    >
      <div class="constraint-dialog-body">
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
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="constraint-item-icon">
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
  padding: 0;
  gap: 0;
  overflow: hidden;
  background: rgba(6, 20, 42, 0.92);
}

/* ===== 主体：四方格 2×2 ===== */
.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto 1fr;
  gap: 0;
  min-height: 0;
  overflow: hidden;
}

/* ===== 通用卡片 ===== */
.card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.12);
  font-size: 12px;
  font-weight: 600;
  color: #e0e6ed;
  flex-shrink: 0;
}

.card-icon { color: #00d4ff; flex-shrink: 0; }

.card-body {
  padding: 10px 12px;
  flex: 1;
  min-height: 0;
}

/* ===== 卡1：模型与算法 ===== */
.card-model { grid-column: 1; grid-row: 1; border-right: 1px solid rgba(0, 175, 255, 0.08); border-bottom: 1px solid rgba(0, 175, 255, 0.1); }

.model-row {
  display: flex;
  gap: 10px;
  height: 100%;
  align-items: stretch;
}

.model-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.col-label {
  font-size: 11px;
  font-weight: 500;
  color: #8aa0b8;
}

.select-desc {
  font-size: 11px;
  color: #6e8a9e;
}

.highlight { color: #00d4ff; font-weight: 500; }

.group-badge {
  margin-left: auto;
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.badge-blue {
  color: #5a8abf;
  background: rgba(0, 175, 255, 0.08);
}

/* ===== 卡2：调度目标 ===== */
.card-objectives { grid-column: 2; grid-row: 1; border-bottom: 1px solid rgba(0, 175, 255, 0.1); }

.card-badge {
  margin-left: auto;
  font-size: 10px;
  color: #5a8abf;
  background: rgba(0, 175, 255, 0.08);
  padding: 1px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.objective-body {
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.objective-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  padding: 7px 8px;
  border-radius: 6px;
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
  gap: 6px;
  min-width: 0;
}

.obj-icon {
  width: 18px;
  height: 18px;
  color: #5a8abf;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.obj-active .obj-icon { color: #00d4ff; }

.obj-info { min-width: 0; }

.obj-name {
  font-size: 11px;
  font-weight: 600;
  color: #8aa0b8;
  transition: color 0.2s;
}

.obj-active .obj-name { color: #e0e6ed; }

.obj-desc {
  font-size: 10px;
  color: #6e8a9e;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.obj-check-mark {
  flex-shrink: 0;
  animation: checkPop 0.2s ease;
}

@keyframes checkPop {
  0% { transform: scale(0); opacity: 0; }
  60% { transform: scale(1.15); }
  100% { transform: scale(1); opacity: 1; }
}

/* ===== 卡3：算法参数设置 ===== */
.card-params { grid-column: 1; grid-row: 2; border-right: 1px solid rgba(0, 175, 255, 0.08); }

.algo-tag {
  margin-left: auto;
  font-size: 10px;
  color: #00d4ff;
  background: rgba(0, 175, 255, 0.12);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.params-body {
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 6px 10px 4px;
}

/* 单行参数 */
.param-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 6px;
  border-radius: 6px;
  transition: background 0.15s;
}

.param-row:hover {
  background: rgba(0, 175, 255, 0.03);
}

.param-row-name {
  width: 68px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  font-weight: 500;
  color: #c0c8d4;
}

.param-info-icon {
  color: #6e8a9e;
  cursor: pointer;
  flex-shrink: 0;
  transition: color 0.2s;
}

.param-info-icon:hover { color: #00d4ff; }

.param-row-controls {
  width: 80px;
  flex-shrink: 0;
}

.param-value-input { width: 100%; }

.param-value-input :deep(.el-input__wrapper) {
  background: rgba(2, 27, 63, 0.6) !important;
  box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.2) inset !important;
}

.param-value-input :deep(.el-input__inner) {
  color: #00d4ff !important;
  font-size: 13px;
  font-weight: 600;
  text-align: center;
}

.param-row-slider {
  flex: 1;
  min-width: 60px;
}

.param-row-range {
  width: 70px;
  flex-shrink: 0;
  font-size: 10px;
  color: #6e8a9e;
  text-align: right;
}

/* ===== 卡4：约束条件 ===== */
.card-constraint { grid-column: 2; grid-row: 2; }

.card-constraint .card-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.12);
  font-size: 12px;
  font-weight: 600;
  color: #e0e6ed;
  flex-shrink: 0;
}

.constraint-edit-btn {
  margin-left: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 4px;
  border: 1px solid rgba(50, 150, 255, 0.2);
  background: rgba(0, 175, 255, 0.06);
  color: #5a8abf;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.constraint-edit-btn:hover {
  background: rgba(0, 175, 255, 0.15);
  border-color: rgba(0, 175, 255, 0.4);
  color: #00d4ff;
}

.constraint-body {
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1px;
  padding: 4px 6px !important;
}

.constraint-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  padding: 5px 6px;
  border-radius: 4px;
  transition: background 0.15s;
}

.constraint-item:hover {
  background: rgba(0, 175, 255, 0.03);
}

.constraint-item.constraint-disabled {
  opacity: 0.4;
}

.constraint-item-left {
  display: flex;
  align-items: center;
  gap: 5px;
  min-width: 0;
  flex: 1;
}

.constraint-item-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #3a5068;
  flex-shrink: 0;
  transition: all 0.25s;
}

.constraint-item-dot.dot-on {
  background: #00d4ff;
  box-shadow: 0 0 5px rgba(0, 212, 255, 0.4);
}

.constraint-item-name {
  font-size: 11px;
  color: #c0c8d4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.constraint-item-right {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.constraint-item-range {
  font-size: 10px;
  color: #5a8abf;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.constraint-item-unit {
  font-size: 10px;
  color: #6e8a9e;
}

/* ===== 约束弹窗 ===== */
.constraint-dialog-body {
  max-height: 420px;
  overflow-y: auto;
  padding: 4px 0;
}

.constraint-summary-text {
  font-size: 12px;
  color: #c0c8d4;
  margin-bottom: 10px;
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

.constraint-switch-item.constraint-disabled { opacity: 0.45; }

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

.constraint-disabled .constraint-item-name { color: #6e8a9e; }

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
  color: #6e8a9e;
  white-space: nowrap;
}

.range-unit {
  font-size: 11px;
  color: #6e8a9e;
  margin-left: 4px;
}

/* ===== 弹窗通用 ===== */
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

.confirm-dialog :deep(.el-dialog__body) { padding: 18px; }

.confirm-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid rgba(50, 150, 255, 0.1);
  padding: 10px 18px;
}

.dialog-body { display: flex; align-items: flex-start; gap: 14px; }
.dialog-icon { flex-shrink: 0; margin-top: 2px; }
.dialog-text { display: flex; flex-direction: column; gap: 4px; }
.dialog-title-main { color: #e0e6ed; font-size: 13px; font-weight: 500; }
.dialog-desc { color: #8aa0b8; font-size: 11px; line-height: 1.5; }
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
