<script setup lang="ts">
import { computed } from 'vue'
import type { ConfigPlan } from '@/types/model'
import { useModelConfigStore } from '@/stores/modelConfig'
import { modelLabelMap, algorithmLabelMap } from '@/mock/model-config/linkage'

type Store = ReturnType<typeof useModelConfigStore>

interface Props {
  visible: boolean
  detailPlan: ConfigPlan | null
  store: Store
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (v: boolean) => emit('update:visible', v),
})

const reservoirGroupName = computed(() => {
  const map: Record<string, string> = {
    'long-liu': '龙刘组合',
    'long-liu-hei': '龙刘黑组合',
    'long-liu-qing': '龙刘青组合',
    'long-liu-gong': '龙刘公组合',
    all: '全部水库组合',
  }
  const groupId = props.store.dispatchSubject.selectedGroupId
  return map[groupId] || groupId || '龙刘组合'
})

const scenarioCategoryName = computed(() => {
  const map: Record<string, string> = {
    'multi-year': '多年调节',
    'critical-period': '枯水期',
    'realtime': '实时调度',
  }
  return map[props.store.dispatchScenario.categoryId] || props.store.dispatchScenario.categoryId || '—'
})

const scenarioSubOptionName = computed(() => {
  const map: Record<string, string> = {
    'multi-objective': '多目标调度',
  }
  return map[props.store.dispatchScenario.subOptionId] || props.store.dispatchScenario.subOptionId || '—'
})

const scenarioParamLabels: Record<string, Record<string, string>> = {
  westRoute: { none: '无', upper: '上线', lower: '下线', both: '上下线同引', all: '上线+下线' },
  backboneStatus: { normal: '正常运行', limited: '限制运行', maintenance: '检修停运', emergency: '应急运行' },
  ecologicalFlow: { none: '不考虑', plan: '按方案执行', minimum: '最低生态需水', enhanced: '强化生态保障', custom: '自定义' },
}

const scenarioParamLabel = (key: string) => {
  const value = props.store.scenarioConstraint.params[key]
  return scenarioParamLabels[key]?.[value] || value || '—'
}

const modelDisplay = computed(() => {
  const id = props.store.modelAlgorithm.selectedModel
  return modelLabelMap[id] || id
})

const algorithmDisplay = computed(() => {
  const id = props.store.modelAlgorithm.selectedAlgorithm
  return algorithmLabelMap[id] || id
})
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="当前配置摘要"
    width="640px"
    :close-on-click-modal="false"
    class="confirm-dialog detail-dialog"
  >
    <div class="summary-body">

      <!-- Step 1: 调度场景 -->
      <div class="summary-section">
        <div class="summary-section-header">
          <div class="step-badge">1</div>
          <span class="summary-section-title">调度场景</span>
        </div>
        <div class="summary-fields">
          <el-descriptions :column="2" size="small" border class="dark-descriptions">
            <el-descriptions-item label="场景大类">
              {{ scenarioCategoryName }}
            </el-descriptions-item>
            <el-descriptions-item label="调度目标">
              {{ scenarioSubOptionName }}
            </el-descriptions-item>
            <el-descriptions-item label="方案名称" :span="2">
              {{ store.dispatchScenario.scenarioName || '（未命名）' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <!-- Step 2: 调度主体 -->
      <div class="summary-section">
        <div class="summary-section-header">
          <div class="step-badge">2</div>
          <span class="summary-section-title">调度主体</span>
        </div>
        <div class="summary-fields">
          <el-descriptions :column="2" size="small" border class="dark-descriptions">
            <el-descriptions-item label="调度周期">
              {{ store.dispatchSubject.startTime || '?' }} ~ {{ store.dispatchSubject.endTime || '?' }}
            </el-descriptions-item>
            <el-descriptions-item label="水库组合">
              {{ reservoirGroupName }}
            </el-descriptions-item>
            <el-descriptions-item label="时段划分">
              {{ store.dispatchSubject.timeStep }}
            </el-descriptions-item>
            <el-descriptions-item label="调度频率">
              {{ store.dispatchSubject.scheduleFrequency }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <!-- Step 3: 调度数据 -->
      <div class="summary-section">
        <div class="summary-section-header">
          <div class="step-badge">3</div>
          <span class="summary-section-title">调度数据</span>
        </div>
        <div class="summary-fields">
          <el-descriptions :column="2" size="small" border class="dark-descriptions">
            <el-descriptions-item label="数据时间范围">
              {{ store.modelData.dateRange[0] }} ~ {{ store.modelData.dateRange[1] }}
            </el-descriptions-item>
            <el-descriptions-item label="数据项数">
              {{ store.modelData.selectedDataIds.length || 7 }} 项
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <!-- Step 4: 模型算法 -->
      <div class="summary-section">
        <div class="summary-section-header">
          <div class="step-badge">4</div>
          <span class="summary-section-title">模型算法</span>
        </div>
        <div class="summary-fields">
          <el-descriptions :column="2" size="small" border class="dark-descriptions">
            <el-descriptions-item label="调度模型">
              {{ modelDisplay }}
            </el-descriptions-item>
            <el-descriptions-item label="优化算法">
              {{ algorithmDisplay }}
            </el-descriptions-item>
            <el-descriptions-item label="目标函数" :span="2">
              {{ store.modelAlgorithm.selectedObjectives.join('、') || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="种群规模">
              {{ store.modelAlgorithm.parameters.populationSize || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="迭代次数">
              {{ store.modelAlgorithm.parameters.iterationCount || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="交叉率">
              {{ store.modelAlgorithm.parameters.crossoverRate || '—' }}
            </el-descriptions-item>
            <el-descriptions-item v-if="store.modelAlgorithm.selectedAlgorithm === 'paem'" label="变异参数 K_mut">
              {{ store.modelAlgorithm.parameters.kMut || '—' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <!-- Step 5: 场景约束 -->
      <div class="summary-section">
        <div class="summary-section-header">
          <div class="step-badge">5</div>
          <span class="summary-section-title">场景约束</span>
        </div>
        <div class="summary-fields">
          <el-descriptions :column="2" size="small" border class="dark-descriptions">
            <el-descriptions-item label="场景类型">
              {{ store.scenarioConstraint.scenarioType === 'typical' ? '典型场景' : '自定义场景' }}
            </el-descriptions-item>
            <el-descriptions-item label="西线调水">
              {{ scenarioParamLabel('westRoute') }}
            </el-descriptions-item>
            <el-descriptions-item label="来沙界限流量">
              {{ store.scenarioConstraint.params.sedimentFlow || '—' }} m³/s
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button size="small" @click="dialogVisible = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.summary-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 520px;
  overflow-y: auto;
  padding-right: 4px;
}

.summary-body::-webkit-scrollbar {
  width: 4px;
}

.summary-body::-webkit-scrollbar-track {
  background: transparent;
}

.summary-body::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.25);
  border-radius: 2px;
}

.summary-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-badge {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(var(--tech-blue-rgb), 0.15);
  border: 1px solid rgba(var(--tech-blue-rgb), 0.4);
  color: var(--tech-cyan);
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.summary-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--tech-text-primary);
}

.summary-fields {
  padding-left: 30px;
}

/* el-descriptions 深色适配 */
:deep(.dark-descriptions) {
  --el-descriptions-table-bg-color: transparent;
}

:deep(.dark-descriptions .el-descriptions__header) {
  display: none;
}

:deep(.dark-descriptions .el-descriptions__body) {
  background: transparent !important;
}

:deep(.dark-descriptions .el-descriptions__table) {
  border-collapse: collapse;
}

:deep(.dark-descriptions .el-descriptions__cell) {
  background: rgba(2, 27, 63, 0.6) !important;
  border-color: rgba(50, 150, 255, 0.15) !important;
  color: var(--tech-text-regular) !important;
  font-size: 12px;
}

:deep(.dark-descriptions .el-descriptions__label.is-bordered-label) {
  background: rgba(2, 27, 63, 0.8) !important;
  color: var(--tech-text-secondary) !important;
  font-weight: 500;
}

:deep(.dark-descriptions .el-descriptions__content) {
  color: var(--tech-text-regular) !important;
}
</style>
