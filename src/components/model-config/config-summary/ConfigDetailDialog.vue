<script setup lang="ts">
import { computed } from 'vue'
import type { ConfigPlan } from '@/types/model'
import { useModelConfigStore } from '@/stores/modelConfig'

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
  return map[props.store.basicConfig.selectedReservoirGroup] || props.store.basicConfig.selectedReservoirGroup
})

const scenarioParamLabels: Record<string, Record<string, string>> = {
  westRoute: { none: '无', upper: '上线', lower: '下线', both: '上下线同引', all: '上线+下线' },
  backboneStatus: { normal: '正常运行', limited: '限制运行', maintenance: '检修停运', emergency: '应急运行' },
  ecologicalFlow: { none: '不考虑', plan: '按方案执行', minimum: '最低生态需水', enhanced: '强化生态保障', custom: '自定义' },
}

const scenarioParamLabel = (key: string) => {
  const value = props.store.scenarioConstraint.params[key]
  return scenarioParamLabels[key]?.[value] || value
}
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

      <!-- Step 1: 调度数据 -->
      <div class="summary-section">
        <div class="summary-section-header">
          <div class="step-badge">1</div>
          <span class="summary-section-title">调度数据</span>
        </div>
        <div class="summary-fields">
          <el-descriptions :column="2" size="small" border class="dark-descriptions">
            <el-descriptions-item label="时间范围">
              {{ store.modelData.dateRange[0] }} ~ {{ store.modelData.dateRange[1] }}
            </el-descriptions-item>
            <el-descriptions-item label="数据项数">
              {{ store.modelData.selectedDataIds.length || 7 }} 项
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <!-- Step 2: 基础配置 -->
      <div class="summary-section">
        <div class="summary-section-header">
          <div class="step-badge">2</div>
          <span class="summary-section-title">基础配置</span>
        </div>
        <div class="summary-fields">
          <el-descriptions :column="2" size="small" border class="dark-descriptions">
            <el-descriptions-item label="方案名称">
              {{ store.basicConfig.schemeName || '（未命名）' }}
            </el-descriptions-item>
            <el-descriptions-item label="水库组合">
              {{ reservoirGroupName }}
            </el-descriptions-item>
            <el-descriptions-item label="调度周期">
              {{ store.basicConfig.timeStep }}
            </el-descriptions-item>
            <el-descriptions-item label="调度频率">
              {{ store.basicConfig.scheduleFrequency }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <!-- Step 3: 模型算法 -->
      <div class="summary-section">
        <div class="summary-section-header">
          <div class="step-badge">3</div>
          <span class="summary-section-title">模型算法</span>
        </div>
        <div class="summary-fields">
          <el-descriptions :column="2" size="small" border class="dark-descriptions">
            <el-descriptions-item label="调度模型">
              {{ store.modelAlgorithm.selectedModel }}
            </el-descriptions-item>
            <el-descriptions-item label="优化算法">
              {{ store.modelAlgorithm.selectedAlgorithm }}
            </el-descriptions-item>
            <el-descriptions-item label="参数摘要" :span="2">
              种群: {{ store.modelAlgorithm.parameters.populationSize }} |
              迭代: {{ store.modelAlgorithm.parameters.iterationCount }} |
              交叉: {{ store.modelAlgorithm.parameters.crossoverRate }} |
              变异: {{ store.modelAlgorithm.parameters.mutationRate }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <!-- Step 4: 场景约束 -->
      <div class="summary-section">
        <div class="summary-section-header">
          <div class="step-badge">4</div>
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
            <el-descriptions-item label="骨干工程">
              {{ scenarioParamLabel('backboneStatus') }}
            </el-descriptions-item>
            <el-descriptions-item label="生态流量">
              {{ scenarioParamLabel('ecologicalFlow') }}
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
  color: var(--tech-text-primary);
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.summary-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 480px;
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

/* Element Plus 深色覆盖 */
:deep(.el-button) {
  --el-button-bg-color: transparent;
  --el-button-border-color: rgba(50, 150, 255, 0.3);
  --el-button-text-color: var(--tech-text-regular);
  --el-button-hover-bg-color: rgba(var(--tech-blue-rgb), 0.1);
  --el-button-hover-border-color: rgba(50, 150, 255, 0.5);
  --el-button-hover-text-color: var(--tech-text-primary);
}

:deep(.el-button--primary) {
  --el-button-bg-color: rgba(var(--tech-blue-rgb), 0.2);
  --el-button-border-color: rgba(var(--tech-blue-rgb), 0.5);
  --el-button-text-color: var(--tech-cyan);
  --el-button-hover-bg-color: rgba(var(--tech-blue-rgb), 0.3);
  --el-button-hover-border-color: rgba(var(--tech-blue-rgb), 0.7);
  --el-button-hover-text-color: var(--tech-cyan-light);
}
</style>
