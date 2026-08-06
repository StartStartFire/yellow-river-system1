<script setup lang="ts">
import { computed } from 'vue'
import type { AlgorithmParameter } from '@/types/model'

interface Props {
  visible: boolean
  params: AlgorithmParameter[]
  values: Record<string, number>
  algorithmName: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'update:values', value: Record<string, number>): void
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (v: boolean) => emit('update:visible', v),
})

const updateValue = (paramId: string, value: number) => {
  emit('update:values', { ...props.values, [paramId]: value })
}

const handleParamInput = (paramId: string, rawValue: string | number, param: AlgorithmParameter) => {
  let val = typeof rawValue === 'string' ? parseFloat(rawValue) : rawValue
  if (isNaN(val)) val = param.min
  let clamped = Math.min(Math.max(val, param.min), param.max)
  const steps = Math.round((clamped - param.min) / param.step)
  clamped = param.min + steps * param.step
  clamped = Math.round(clamped * 100) / 100
  updateValue(paramId, clamped)
}

const formatParamValue = (param: AlgorithmParameter) => {
  const val = props.values[param.id]
  return param.step >= 1 ? val.toString() : val.toFixed(2)
}

const close = () => {
  dialogVisible.value = false
}
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    title="算法参数设置"
    width="560px"
    :close-on-click-modal="false"
    class="confirm-dialog param-dialog"
  >
    <div class="param-dialog-header">
      <span class="param-dialog-sub">当前算法：<span class="highlight">{{ algorithmName || '未选择' }}</span></span>
      <span class="param-dialog-hint">拖动滑块或直接输入数值调整参数</span>
    </div>
    <div class="param-dialog-body">
      <div v-for="param in params" :key="param.id" class="param-dialog-row">
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
          <el-slider
            :model-value="values[param.id]"
            :min="param.min"
            :max="param.max"
            :step="param.step"
            size="small"
            class="dark-slider"
            @update:model-value="(val: number) => updateValue(param.id, val)"
          />
        </div>
        <div class="param-dialog-right">
          <el-input
            :model-value="formatParamValue(param)"
            size="small"
            class="param-value-input"
            @update:model-value="(val: string | number) => handleParamInput(param.id, val, param)"
          />
          <span class="param-range">{{ param.min }}~{{ param.max }}</span>
        </div>
      </div>
    </div>
    <template #footer>
      <el-button size="small" @click="close">关闭</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
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
/* 参数输入框：cyan 文字色 + 居中加粗（组件特有，与全局默认不同） */
.param-value-input :deep(.el-input__wrapper) { background: rgba(2, 27, 63, 0.6) !important; box-shadow: 0 0 0 1px rgba(50, 150, 255, 0.2) inset !important; }
.param-value-input :deep(.el-input__inner) { color: var(--tech-cyan) !important; font-size: 12px; font-weight: 600; text-align: center; }

.param-range { font-size: 9px; color: var(--tech-text-placeholder); white-space: nowrap; }

.highlight { color: var(--tech-cyan); font-weight: 500; }

/* ===== Element Plus 深色覆盖 ===== */
:deep(.dark-slider .el-slider__runway) { background: rgba(50,150,255,0.15) !important; }
:deep(.dark-slider .el-slider__bar) { background: linear-gradient(90deg, rgba(0,175,255,0.4), var(--tech-cyan)) !important; }
:deep(.dark-slider .el-slider__button) { border: 2px solid var(--tech-cyan) !important; background: rgba(2,27,63,0.9) !important; width: 14px !important; height: 14px !important; }
:deep(.dark-slider .el-slider__button:hover) { transform: scale(1.15) !important; }
:deep(.param-tooltip) { background: rgba(6,30,70,0.98) !important; border: 1px solid rgba(50,150,255,0.4) !important; color: var(--tech-text-regular) !important; font-size: 11px !important; line-height: 1.6 !important; max-width: 220px !important; }
</style>
