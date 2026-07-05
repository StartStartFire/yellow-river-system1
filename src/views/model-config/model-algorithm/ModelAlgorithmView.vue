<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import ModelConfigFooter from '@/components/model-config/ModelConfigFooter.vue'
import ConfirmActionDialog from '@/components/model-config/common/ConfirmActionDialog.vue'
import ModelSelectCard from '@/components/model-config/model-algorithm/ModelSelectCard.vue'
import AlgorithmSelectCard from '@/components/model-config/model-algorithm/AlgorithmSelectCard.vue'
import ObjectiveSelectCard from '@/components/model-config/model-algorithm/ObjectiveSelectCard.vue'
import ConstraintPanel from '@/components/model-config/model-algorithm/ConstraintPanel.vue'
import AlgorithmParamDialog from '@/components/model-config/model-algorithm/AlgorithmParamDialog.vue'
import { useModelConfigStore } from '@/stores/modelConfig'
import {
  dispatchModels,
  optimizationAlgorithms,
  algorithmParameters,
  dispatchObjectives,
  constraintSummary,
} from '@/mock/model-config/modelAlgorithm'
import { scenarioModelMap } from '@/mock/model-config/linkage'
import type { DispatchModel, OptimizationAlgorithm, AlgorithmParameter, ConstraintDetail } from '@/types/model'

const store = useModelConfigStore()
const router = useRouter()

const allModels = dispatchModels.data as DispatchModel[]
const allAlgorithms = optimizationAlgorithms.data as OptimizationAlgorithm[]
const paramDefs = algorithmParameters.data as AlgorithmParameter[]
const objectivesDef = dispatchObjectives.data
const constraintData = constraintSummary.data

const selectedModelId = ref(store.modelAlgorithm.selectedModel)
const selectedAlgorithmId = ref(store.modelAlgorithm.selectedAlgorithm)
const paramValues = ref<Record<string, number>>({...store.modelAlgorithm.parameters})
paramDefs.forEach(p => { if (!(p.id in paramValues.value)) paramValues.value[p.id] = p.value })

const visibleParams = computed(() => {
  if (!currentAlgorithm.value) return paramDefs
  return paramDefs.filter(p => currentAlgorithm.value!.paramIds.includes(p.id))
})

const selectedObjectives = ref<string[]>([...store.modelAlgorithm.selectedObjectives])
const editingConstraints = ref<ConstraintDetail[]>(constraintData.constraints.map(c => ({ ...c })))
const constraintEnabledMap = ref<Record<string, boolean>>(
  Object.fromEntries(constraintData.constraints.map(c => [c.name, true]))
)

const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)
const paramDialogVisible = ref(false)

const handleConstraintsEdit = () => {
  ElMessage.success('约束条件已更新')
}

const currentGroupName = computed(() => {
  const groups = [
    { id: 'long-liu', name: '龙刘组合' },
    { id: 'long-liu-hei', name: '龙刘黑组合' },
    { id: 'all', name: '全部水库' },
  ]
  return groups.find(g => g.id === store.dispatchSubject.selectedGroupId)?.name
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

const constraintEnabledArray = computed(() =>
  editingConstraints.value.map(c => constraintEnabledMap.value[c.name] ?? true)
)

const handleNext = () => {
  if (!selectedModelId.value || !selectedAlgorithmId.value) { ElMessage.warning('请选择调度模型和优化算法'); return }
  if (selectedObjectives.value.length === 0) { ElMessage.warning('请至少选择一个调度目标'); return }
  store.setModelAlgorithm({
    selectedModel: selectedModelId.value,
    selectedAlgorithm: selectedAlgorithmId.value,
    selectedObjectives: [...selectedObjectives.value],
    parameters: { ...paramValues.value },
  })
  store.markStepCompleted(4)
  router.push('/model-config/scenario-constraint')
}

const confirmSave = () => {
  saveDialogVisible.value = false
  store.setModelAlgorithm({
    selectedModel: selectedModelId.value,
    selectedAlgorithm: selectedAlgorithmId.value,
    selectedObjectives: [...selectedObjectives.value],
    parameters: { ...paramValues.value },
  })
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
        <ModelSelectCard
          v-model:modelId="selectedModelId"
          :models="models"
          :scenario-name="currentScenarioName"
          :group-name="currentGroupName"
        />

        <AlgorithmSelectCard
          v-model:algorithmId="selectedAlgorithmId"
          :algorithms="supportedAlgorithms"
          @open-params="paramDialogVisible = true"
        />

        <ObjectiveSelectCard
          :objectives="objectivesDef"
          :selected="selectedObjectives"
          :icons="objectiveIcons"
          @toggle="handleToggleObjective"
        />
      </div>

      <!-- ===== 底部：约束条件网格 ===== -->
      <ConstraintPanel
        v-model:constraints="editingConstraints"
        v-model:enabledMap="constraintEnabledMap"
        @edit="handleConstraintsEdit"
      />
    </div>

    <ModelConfigFooter :step="4" @cancel="handleCancel" @save="handleSave" @prev="handlePrev" @next="handleNext" />

    <!-- 算法参数弹窗 -->
    <AlgorithmParamDialog
      v-model:visible="paramDialogVisible"
      v-model:values="paramValues"
      :params="visibleParams"
      :algorithm-name="currentAlgorithm?.name || ''"
    />

    <!-- 保存确认弹窗 -->
    <ConfirmActionDialog
      v-model:visible="saveDialogVisible"
      title="保存确认"
      icon-type="success"
      main-text="确认保存当前配置？"
      desc-text="保存后模型算法、调度目标和约束条件将保留。"
      confirm-text="确认保存"
      cancel-text="取消"
      @confirm="confirmSave"
    />

    <!-- 取消确认弹窗 -->
    <ConfirmActionDialog
      v-model:visible="cancelDialogVisible"
      title="取消确认"
      icon-type="warning"
      main-text="确认取消当前操作？"
      desc-text="取消后当前页面的更改将不会保存。"
      confirm-text="确认取消"
      cancel-text="继续编辑"
      confirm-type="warning"
      @confirm="confirmCancel"
    />
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
</style>
