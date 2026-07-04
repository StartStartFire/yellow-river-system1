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
  scenarioModelMap,
} from '@/mock/modelConfig'
import type { DispatchModel, OptimizationAlgorithm, AlgorithmParameter, DispatchObjective, ConstraintDetail } from '@/types/model'

const store = useModelConfigStore()
const router = useRouter()

const allModels = dispatchModels.data as DispatchModel[]
const allAlgorithms = optimizationAlgorithms.data as OptimizationAlgorithm[]
const paramDefs = algorithmParameters.data as AlgorithmParameter[]
const objectivesDef = dispatchObjectives.data as DispatchObjective[]
const constraintData = constraintSummary.data

const selectedModelId = ref(store.modelAlgorithm.selectedModel)
const selectedAlgorithmId = ref(store.modelAlgorithm.selectedAlgorithm)
const paramValues = ref<Record<string, number>>({...store.modelAlgorithm.parameters})
paramDefs.forEach(p => { if (!(p.id in paramValues.value)) paramValues.value[p.id] = p.value })

const visibleParams = computed(() => {
  if (!currentAlgorithm.value) return paramDefs
  return paramDefs.filter(p => currentAlgorithm.value!.paramIds.includes(p.id))
})

const selectedObjectives = ref<string[]>([...store.basicConfig.selectedObjectives])
const constraintEnabled = ref<boolean[]>(constraintData.constraints.map(() => true))
const editingConstraints = ref<ConstraintDetail[]>(constraintData.constraints.map(c => ({ ...c })))
const enabledConstraintCount = computed(() => constraintEnabled.value.filter(Boolean).length)

const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)
const paramDialogVisible = ref(false)
const constraintDialogVisible = ref(false)

const confirmConstraints = () => {
  constraintDialogVisible.value = false
  ElMessage.success('约束条件已更新')
}

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

// 场景兼容的模型列表（从 Step 1 的 categoryId 获取）
const scenarioCompatibleModels = computed(() => {
  const categoryId = store.dispatchScenario.categoryId
  if (!categoryId) return allModels
  const compatibleIds = scenarioModelMap[categoryId] || []
  if (compatibleIds.length === 0) return allModels
  return allModels.filter(m => compatibleIds.includes(m.id))
})

// 最终模型列表：优先使用场景兼容的模型
const models = computed(() => {
  if (scenarioCompatibleModels.value.length > 0) return scenarioCompatibleModels.value
  return store.compatibleModels.length > 0 ? store.compatibleModels : allModels
})

const currentModel = computed(() => models.value.find(m => m.id === selectedModelId.value))

// 当前场景名称
const currentScenarioName = computed(() => {
  const nameMap: Record<string, string> = {
    'multi-year': '多年的中长期调度',
    'critical-period': '年内关键期调度',
    'realtime': '实时调度',
  }
  return nameMap[store.dispatchScenario.categoryId] || ''
})

const supportedAlgorithms = computed(() => {
  if (!currentModel.value) return allAlgorithms
  return allAlgorithms.filter(a => currentModel.value!.supportedAlgorithms.includes(a.id))
})

const currentAlgorithm = computed(() => allAlgorithms.find(a => a.id === selectedAlgorithmId.value))

watch(selectedModelId, (newModelId) => {
  const model = allModels.find(m => m.id === newModelId)
  if (model && !model.supportedAlgorithms.includes(selectedAlgorithmId.value)) {
    if (model.supportedAlgorithms.length > 0) selectedAlgorithmId.value = model.supportedAlgorithms[0]
  }
})

watch(selectedAlgorithmId, (newAlgoId) => {
  const algo = allAlgorithms.find(a => a.id === newAlgoId)
  if (!algo) return
  const newValues: Record<string, number> = {}
  algo.paramIds.forEach(pid => {
    const def = paramDefs.find(p => p.id === pid)
    if (def) newValues[pid] = pid in paramValues.value ? paramValues.value[pid] : def.value
  })
  paramValues.value = newValues
})

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
  return param.step >= 1 ? val.toString() : val.toFixed(2)
}

const handleToggleObjective = (id: string) => {
  const idx = selectedObjectives.value.indexOf(id)
  if (idx >= 0) {
    if (selectedObjectives.value.length > 1) selectedObjectives.value.splice(idx, 1)
    else ElMessage.warning('至少保留一个调度目标')
  } else {
    selectedObjectives.value.push(id)
  }
}

const handlePrev = () => router.push('/model-config/model-data')
const handleCancel = () => { cancelDialogVisible.value = true }
const handleSave = () => { saveDialogVisible.value = true }

const handleNext = () => {
  if (!selectedModelId.value || !selectedAlgorithmId.value) { ElMessage.warning('请选择调度模型和优化算法'); return }
  if (selectedObjectives.value.length === 0) { ElMessage.warning('请至少选择一个调度目标'); return }
  store.setModelAlgorithm({ selectedModel: selectedModelId.value, selectedAlgorithm: selectedAlgorithmId.value, parameters: { ...paramValues.value } })
  store.setBasicConfig({ selectedObjectives: [...selectedObjectives.value], constraintEnabled: [...constraintEnabled.value] })
  store.markStepCompleted(4)
  router.push('/model-config/scenario-constraint')
}

const confirmSave = () => {
  saveDialogVisible.value = false
  store.setModelAlgorithm({ selectedModel: selectedModelId.value, selectedAlgorithm: selectedAlgorithmId.value, parameters: { ...paramValues.value } })
  store.setBasicConfig({ selectedObjectives: [...selectedObjectives.value], constraintEnabled: [...constraintEnabled.value] })
  ElMessage.success('模型算法配置已保存')
}

const confirmCancel = () => { cancelDialogVisible.value = false; ElMessage.info('已取消，未保存任何更改') }

const objectiveIcons: Record<string, string> = {
  shield: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M12 4L5 7v5c0 4.4 7 8 7 8s7-3.6 7-8V7l-7-3z" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linejoin="round"/><path d="M10 13l1.5 1.5L15 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
  flash: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M13 3L7 13h5l-1 8 7-12h-5l1-6z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" fill="none"/></svg>',
  leaf: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M12 5c-4 0-7 3-7 7 0 6 7 8 7 8s7-2 7-8c0-4-3-7-7-7z" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M12 13v-6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
  sand: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M6 4h12l-3 7H9L6 4z" stroke="currentColor" stroke-width="1.5" fill="none"/><path d="M7 11l-3 9h16l-3-9" stroke="currentColor" stroke-width="1.5" fill="none"/></svg>',
  sync: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M19 7c-2-3-5-4-8-3S6 8 5 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M5 17c2 3 5 4 8 3s5-5 6-9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
}
</script>

<template>
  <div class="model-algorithm-view">
    <ModelConfigStepBar :current-step="4" version="new" />

    <div class="main-content">
      <!-- ===== 顶部：模型与算法卡片行 ===== -->
      <div class="top-row">
        <!-- 模型选择卡片 -->
        <div class="card model-card">
          <div class="card-header">
            <div class="card-icon-box model-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="3"/>
                <circle cx="12" cy="8" r="2.5" fill="rgba(0,175,255,0.2)"/>
                <path d="M7 17c0-2.8 2.2-5 5-5s5 2.2 5 5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="card-title-group">
              <span class="card-title">调度模型</span>
              <span class="card-sub">选择调度计算使用的模型</span>
            </div>
            <span v-if="currentScenarioName" class="scenario-badge">场景：{{ currentScenarioName }}</span>
            <span class="group-badge">水库组合：{{ currentGroupName }}</span>
          </div>
          <div class="card-body">
            <div class="model-options">
              <div
                v-for="model in models"
                :key="model.id"
                class="model-option"
                :class="{ active: selectedModelId === model.id }"
                @click="selectedModelId = model.id"
              >
                <div class="model-option-dot" :class="{ 'dot-active': selectedModelId === model.id }"></div>
                <div class="model-option-info">
                  <div class="model-option-name">{{ model.name }}</div>
                  <div class="model-option-desc">{{ model.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 算法选择卡片 -->
        <div class="card algo-card">
          <div class="card-header">
            <div class="card-icon-box algo-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="3"/>
                <path d="M12 2v4M12 18v4M2 12h4M18 12h4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              </svg>
            </div>
            <div class="card-title-group">
              <span class="card-title">优化算法</span>
              <span class="card-sub">选择优化求解算法</span>
            </div>
            <button class="param-btn" @click="paramDialogVisible = true">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12.22 2h-.44a2 2 0 00-2 2v.18a2 2 0 01-1 1.73l-.43.25a2 2 0 01-2 0l-.15-.08a2 2 0 00-2.73.73l-.22.38a2 2 0 00.73 2.73l.15.1a2 2 0 011 1.73v.18a2 2 0 002 2h.44a2 2 0 002-2v-.18a2 2 0 011-1.73l.43-.25a2 2 0 012 0l.15.08a2 2 0 002.73-.73l.22-.38a2 2 0 00-.73-2.73l-.15-.1a2 2 0 01-1-1.73v-.18a2 2 0 00-2-2h.44"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              参数设置
            </button>
          </div>
          <div class="card-body">
            <div class="algo-options">
              <div
                v-for="algo in supportedAlgorithms"
                :key="algo.id"
                class="algo-option"
                :class="{ active: selectedAlgorithmId === algo.id }"
                @click="selectedAlgorithmId = algo.id"
              >
                <div class="algo-option-dot" :class="{ 'dot-active': selectedAlgorithmId === algo.id }"></div>
                <div class="algo-option-info">
                  <div class="algo-option-name">{{ algo.name }}</div>
                  <div class="algo-option-desc">{{ algo.paramIds.length }} 个参数</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 调度目标卡片 -->
        <div class="card objectives-card">
          <div class="card-header">
            <div class="card-icon-box obj-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="9"/>
                <circle cx="12" cy="12" r="4"/>
                <circle cx="12" cy="12" r="1.5" fill="currentColor"/>
              </svg>
            </div>
            <div class="card-title-group">
              <span class="card-title">调度目标</span>
              <span class="card-sub">选择需要优化的目标（可多选）</span>
            </div>
            <span class="obj-badge">{{ selectedObjectives.length }} / {{ objectivesDef.length }}</span>
          </div>
          <div class="card-body">
            <div class="obj-grid">
              <div
                v-for="obj in objectivesDef"
                :key="obj.id"
                class="obj-item"
                :class="{ 'obj-active': selectedObjectives.includes(obj.id) }"
                @click="handleToggleObjective(obj.id)"
              >
                <div class="obj-item-icon" v-html="objectiveIcons[obj.icon] || ''"></div>
                <div class="obj-item-info">
                  <div class="obj-item-name">{{ obj.name }}</div>
                  <div class="obj-item-desc">{{ obj.description }}</div>
                </div>
                <div class="obj-check" :class="{ checked: selectedObjectives.includes(obj.id) }">
                  <svg v-if="selectedObjectives.includes(obj.id)" width="12" height="12" viewBox="0 0 16 16" fill="none">
                    <path d="M4 8l3 3 5-6" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== 底部：约束条件网格 ===== -->
      <div class="constraint-section">
        <div class="constraint-header">
          <div class="constraint-title-group">
            <div class="constraint-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
                <rect x="9" y="3" width="6" height="4" rx="1"/>
                <path d="M9 14h6M9 10h6"/>
              </svg>
            </div>
            <div class="constraint-title-text">
              <span class="constraint-title">约束条件</span>
              <span class="constraint-sub">已启用 {{ enabledConstraintCount }} / {{ editingConstraints.length }} 项约束</span>
            </div>
            <button class="constraint-edit-btn" @click="constraintDialogVisible = true" title="编辑约束详情">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                <path d="M11 2l3 3-9 9H2v-3l9-9z" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              编辑
            </button>
          </div>
        </div>
        <div class="constraint-grid">
          <div
            v-for="(c, cIdx) in editingConstraints"
            :key="cIdx"
            class="constraint-item"
            :class="{ 'constraint-disabled': !constraintEnabled[cIdx] }"
          >
            <div class="constraint-top">
              <span class="constraint-dot" :class="{ 'dot-on': constraintEnabled[cIdx] }"></span>
              <span class="constraint-name">{{ c.name }}</span>
              <span class="constraint-range">{{ c.min }} ~ {{ c.max }} {{ c.unit }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ModelConfigFooter :step="4" @cancel="handleCancel" @save="handleSave" @prev="handlePrev" @next="handleNext" />

    <!-- 算法参数弹窗 -->
    <el-dialog v-model="paramDialogVisible" title="算法参数设置" width="560px" :close-on-click-modal="false" class="confirm-dialog param-dialog">
      <div class="param-dialog-header">
        <span class="param-dialog-sub">当前算法：<span class="highlight">{{ currentAlgorithm?.name || '未选择' }}</span></span>
        <span class="param-dialog-hint">拖动滑块或直接输入数值调整参数</span>
      </div>
      <div class="param-dialog-body">
        <div v-for="param in visibleParams" :key="param.id" class="param-dialog-row">
          <div class="param-dialog-left">
            <span class="param-dialog-name">{{ param.name }}</span>
            <el-tooltip :content="param.description" placement="top" effect="dark" :show-after="300" popper-class="param-tooltip">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none" class="param-info-icon">
                <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.2" fill="none"/>
                <path d="M8 5.5v4M8 5.5v-1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
            </el-tooltip>
          </div>
          <div class="param-dialog-center">
            <el-slider v-model="paramValues[param.id]" :min="param.min" :max="param.max" :step="param.step" size="small" class="dark-slider" />
          </div>
          <div class="param-dialog-right">
            <el-input :model-value="formatParamValue(param)" size="small" class="param-value-input" @update:model-value="(val: string|number) => handleParamInput(param.id, val, param)" />
            <span class="param-range">{{ param.min }}~{{ param.max }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button size="small" @click="paramDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- ===== 约束条件编辑弹窗 ===== -->
    <el-dialog v-model="constraintDialogVisible" title="约束条件设置" width="620px" :close-on-click-modal="false" class="confirm-dialog">
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

    <!-- 保存确认弹窗 -->
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

    <!-- 取消确认弹窗 -->
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
  background: rgba(var(--tech-bg-rgb), 0.92);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px 14px;
  min-height: 0;
  overflow-y: auto;
}

.main-content::-webkit-scrollbar { width: 4px; }
.main-content::-webkit-scrollbar-track { background: transparent; }
.main-content::-webkit-scrollbar-thumb { background: rgba(50, 150, 255, 0.2); border-radius: 2px; }

/* ===== 顶部行：3个卡片 ===== */
.top-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  flex-shrink: 0;
}

/* ===== 通用卡片 ===== */
.card {
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(50, 150, 255, 0.12);
  border-radius: 10px;
  background: rgba(10, 25, 41, 0.4);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.08);
  flex-shrink: 0;
}

.card-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.model-icon { background: rgba(var(--tech-blue-rgb), 0.12); color: var(--tech-cyan); }
.algo-icon { background: rgba(var(--tech-green-rgb), 0.12); color: #00ff88; }
.obj-icon { background: rgba(179, 127, 235, 0.12); color: #b37feb; }

.card-title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--tech-text-primary);
}

.card-sub {
  font-size: 10px;
  color: var(--tech-text-placeholder);
}

.card-body {
  flex: 1;
  padding: 8px 10px;
  overflow: hidden;
}

/* ===== 模型选择 ===== */
.model-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.model-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.model-option:hover { background: rgba(var(--tech-blue-rgb), 0.04); }
.model-option.active { background: rgba(var(--tech-blue-rgb), 0.06); border-color: rgba(var(--tech-blue-rgb), 0.25); }

.model-option-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid rgba(80, 100, 120, 0.5);
  flex-shrink: 0;
  transition: all 0.2s;
}

.model-option-dot.dot-active { border-color: var(--tech-cyan); background: var(--tech-cyan); box-shadow: 0 0 6px rgba(var(--tech-cyan-rgb), 0.4); }

.model-option-info { min-width: 0; }
.model-option-name { font-size: 11px; font-weight: 600; color: var(--tech-text-regular); }
.model-option.active .model-option-name { color: var(--tech-text-primary); }
.model-option-desc { font-size: 9px; color: var(--tech-text-placeholder); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* ===== 算法选择 ===== */
.param-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  padding: 4px 10px;
  font-size: 10px;
  color: var(--tech-cyan);
  background: rgba(var(--tech-blue-rgb), 0.08);
  border: 1px solid rgba(var(--tech-blue-rgb), 0.25);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.param-btn:hover { background: rgba(var(--tech-blue-rgb), 0.15); border-color: rgba(var(--tech-blue-rgb), 0.4); }

.algo-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.algo-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.algo-option:hover { background: rgba(var(--tech-green-rgb), 0.04); }
.algo-option.active { background: rgba(var(--tech-green-rgb), 0.06); border-color: rgba(var(--tech-green-rgb), 0.25); }

.algo-option-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid rgba(80, 100, 120, 0.5);
  flex-shrink: 0;
  transition: all 0.2s;
}

.algo-option-dot.dot-active { border-color: #00ff88; background: #00ff88; box-shadow: 0 0 6px rgba(var(--tech-green-rgb), 0.4); }

.algo-option-info { min-width: 0; }
.algo-option-name { font-size: 11px; font-weight: 600; color: var(--tech-text-regular); }
.algo-option.active .algo-option-name { color: var(--tech-text-primary); }
.algo-option-desc { font-size: 9px; color: var(--tech-text-placeholder); }

/* ===== 调度目标 ===== */
.obj-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.obj-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.obj-item:hover { background: rgba(179, 127, 235, 0.04); }
.obj-item.obj-active { background: rgba(179, 127, 235, 0.06); border-color: rgba(179, 127, 235, 0.2); }

.obj-item-icon { width: 16px; height: 16px; color: var(--tech-text-placeholder); flex-shrink: 0; }
.obj-item.obj-active .obj-item-icon { color: #b37feb; }
.obj-item-info { min-width: 0; flex: 1; }
.obj-item-name { font-size: 11px; font-weight: 600; color: var(--tech-text-regular); }
.obj-item.obj-active .obj-item-name { color: var(--tech-text-primary); }
.obj-item-desc { font-size: 9px; color: var(--tech-text-placeholder); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.obj-check {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid rgba(80, 100, 120, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.obj-check.checked { border-color: #b37feb; background: #b37feb; }

.obj-badge {
  font-size: 10px;
  color: #8a7ab8;
  background: rgba(179, 127, 235, 0.08);
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.scenario-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  color: var(--tech-cyan);
  background: rgba(var(--tech-blue-rgb), 0.1);
  border: 1px solid rgba(var(--tech-blue-rgb), 0.2);
}

.group-badge {
  margin-left: auto;
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
  color: #5a8abf;
  background: rgba(var(--tech-blue-rgb), 0.08);
}

/* ===== 约束条件区域 ===== */
.constraint-section {
  border: 1px solid rgba(50, 150, 255, 0.12);
  border-radius: 10px;
  background: rgba(10, 25, 41, 0.4);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.constraint-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.08);
  flex-shrink: 0;
}

.constraint-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.constraint-edit-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 10px;
  color: #5a8abf;
  background: rgba(var(--tech-blue-rgb), 0.06);
  border: 1px solid rgba(50, 150, 255, 0.2);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s;
}

.constraint-edit-btn:hover { background: rgba(var(--tech-blue-rgb), 0.12); border-color: rgba(var(--tech-blue-rgb), 0.4); color: var(--tech-cyan); }

.constraint-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 229, 255, 0.1);
  color: var(--tech-cyan-light);
}

.constraint-title-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.constraint-title { font-size: 13px; font-weight: 600; color: var(--tech-text-primary); }
.constraint-sub { font-size: 10px; color: var(--tech-text-placeholder); }

.constraint-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 12px;
  flex: 1;
}

.constraint-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(17, 37, 54, 0.5);
  border: 1px solid rgba(50, 150, 255, 0.08);
  transition: all 0.2s;
}

.constraint-item:hover { border-color: rgba(50, 150, 255, 0.2); }

.constraint-item.constraint-disabled { opacity: 0.45; }

.constraint-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3a5068;
  flex-shrink: 0;
  transition: all 0.25s;
}

.constraint-dot.dot-on {
  background: var(--tech-cyan);
  box-shadow: 0 0 6px rgba(var(--tech-cyan-rgb), 0.4);
}

.constraint-top {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.constraint-name {
  font-size: 11px;
  color: var(--tech-text-regular);
  white-space: nowrap;
}

.constraint-range {
  font-size: 9px;
  color: #5a8abf;
  white-space: nowrap;
}

/* ===== 算法参数弹窗 ===== */
.param-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  margin-bottom: 12px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.15);
}

.param-dialog-sub { font-size: 12px; color: var(--tech-text-regular); }
.param-dialog-hint { font-size: 10px; color: var(--tech-text-placeholder); }

.param-dialog-body {
  max-height: 360px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-dialog-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px;
  border-radius: 8px;
  background: rgba(2, 27, 63, 0.4);
  border: 1px solid rgba(50, 150, 255, 0.08);
}

.param-dialog-left {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 120px;
  flex-shrink: 0;
}

.param-dialog-name {
  font-size: 11px;
  font-weight: 500;
  color: var(--tech-text-regular);
  white-space: nowrap;
}

.param-info-icon { color: var(--tech-text-placeholder); cursor: pointer; flex-shrink: 0; transition: color 0.2s; }
.param-info-icon:hover { color: var(--tech-cyan); }

.param-dialog-center {
  flex: 1;
  min-width: 80px;
}

.param-dialog-right {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 140px;
  flex-shrink: 0;
}

.param-value-input { width: 70px; }
.param-value-input :deep(.el-input__wrapper) { background: rgba(2, 27, 63, 0.6) !important; box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.2) inset !important; }
.param-value-input :deep(.el-input__inner) { color: var(--tech-cyan) !important; font-size: 12px; font-weight: 600; text-align: center; }

.param-range { font-size: 9px; color: var(--tech-text-placeholder); white-space: nowrap; }

.highlight { color: var(--tech-cyan); font-weight: 500; }

/* ===== 弹窗通用 ===== */
.confirm-dialog :deep(.el-dialog) { background: rgba(6, 30, 70, 0.98) !important; border: 1px solid rgba(50, 150, 255, 0.4); border-radius: 12px; }
.confirm-dialog :deep(.el-dialog__header) { border-bottom: 1px solid rgba(50, 150, 255, 0.2); padding: 14px 18px; margin: 0; }
.confirm-dialog :deep(.el-dialog__title) { color: var(--tech-text-primary); font-size: 14px; font-weight: 600; }
.confirm-dialog :deep(.el-dialog__body) { padding: 18px; }
.confirm-dialog :deep(.el-dialog__footer) { border-top: 1px solid rgba(50, 150, 255, 0.1); padding: 10px 18px; }

.dialog-body { display: flex; align-items: flex-start; gap: 14px; }
.dialog-icon { flex-shrink: 0; margin-top: 2px; }
.dialog-text { display: flex; flex-direction: column; gap: 4px; }
.dialog-title-main { color: var(--tech-text-primary); font-size: 13px; font-weight: 500; }
.dialog-desc { color: var(--tech-text-secondary); font-size: 11px; line-height: 1.5; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 8px; }

/* ===== 约束条件弹窗 ===== */
.constraint-dialog-body { max-height: 400px; overflow-y: auto; }
.constraint-summary-text { font-size: 12px; color: var(--tech-text-regular); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid rgba(50, 150, 255, 0.15); }
.constraint-switch-list { display: flex; flex-direction: column; gap: 6px; }
.constraint-switch-item { display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border-radius: 8px; background: rgba(2, 27, 63, 0.4); border: 1px solid rgba(50, 150, 255, 0.12); transition: all 0.2s; }
.constraint-switch-item.constraint-disabled { opacity: 0.45; }
.constraint-switch-top { display: flex; align-items: center; justify-content: space-between; }
.constraint-switch-left { display: flex; align-items: center; gap: 6px; }
.constraint-item-icon { color: var(--tech-cyan); flex-shrink: 0; }
.constraint-item-name { font-size: 12px; font-weight: 500; color: var(--tech-text-regular); }
.constraint-disabled .constraint-item-name { color: var(--tech-text-placeholder); }
.constraint-range-row { display: flex; align-items: center; gap: 8px; padding-left: 22px; }
.range-item { display: flex; align-items: center; gap: 4px; }
.range-label { font-size: 10px; color: var(--tech-text-placeholder); white-space: nowrap; }
.range-unit { font-size: 11px; color: var(--tech-text-placeholder); margin-left: 4px; }

:deep(.dark-switch.el-switch.is-checked .el-switch__core) { background: rgba(0,175,255,0.5) !important; border-color: rgba(0,175,255,0.6) !important; }
:deep(.dark-input-number .el-input__wrapper) { background: rgba(2,27,63,0.8) !important; box-shadow: 0 0 0 1px rgba(50,150,255,0.2) inset !important; }
:deep(.dark-input-number .el-input__inner) { color: var(--tech-text-regular) !important; }

/* ===== Element Plus 深色覆盖 ===== */
:deep(.el-button) { --el-button-bg-color: transparent; --el-button-border-color: rgba(50,150,255,0.3); --el-button-text-color: var(--tech-text-regular); --el-button-hover-bg-color: rgba(0,175,255,0.1); --el-button-hover-border-color: rgba(50,150,255,0.5); --el-button-hover-text-color: var(--tech-text-primary); }
:deep(.el-button--primary) { --el-button-bg-color: rgba(0,175,255,0.2); --el-button-border-color: rgba(0,175,255,0.5); --el-button-text-color: var(--tech-cyan); --el-button-hover-bg-color: rgba(0,175,255,0.3); --el-button-hover-border-color: rgba(0,175,255,0.7); --el-button-hover-text-color: var(--tech-cyan-light); }
:deep(.dark-slider .el-slider__runway) { background: rgba(50,150,255,0.15) !important; }
:deep(.dark-slider .el-slider__bar) { background: linear-gradient(90deg, rgba(0,175,255,0.4), var(--tech-cyan)) !important; }
:deep(.dark-slider .el-slider__button) { border: 2px solid var(--tech-cyan) !important; background: rgba(2,27,63,0.9) !important; width: 14px !important; height: 14px !important; }
:deep(.dark-slider .el-slider__button:hover) { transform: scale(1.15) !important; }
:deep(.param-tooltip) { background: rgba(6,30,70,0.98) !important; border: 1px solid rgba(50,150,255,0.4) !important; color: var(--tech-text-regular) !important; font-size: 11px !important; line-height: 1.6 !important; max-width: 220px !important; }
</style>
