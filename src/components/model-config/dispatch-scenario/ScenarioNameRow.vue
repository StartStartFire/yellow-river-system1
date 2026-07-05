<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const inputValue = computed({
  get: () => props.modelValue,
  set: (v: string) => emit('update:modelValue', v),
})
</script>

<template>
  <div class="name-row">
    <div class="name-row-left">
      <div class="name-row-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path d="M3 6h18M3 12h15M3 18h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <span class="name-row-label">方案名称</span>
    </div>
    <div class="name-row-center">
      <el-input
        v-model="inputValue"
        placeholder="请输入本次调度方案名称，例如：2025年龙羊峡-刘家峡联合调度方案"
        size="default"
        class="name-input"
        clearable
      />
    </div>
    <div class="name-row-hint">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5"/>
        <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <span>点击下方卡片选择一个调度场景，每个方案只能选择一个场景</span>
    </div>
  </div>
</template>

<style scoped>
.name-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  flex-shrink: 0;
  background: rgba(var(--tech-blue-rgb), 0.02);
}

.name-row-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.name-row-icon {
  color: var(--tech-cyan);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: rgba(var(--tech-blue-rgb), 0.1);
  justify-content: center;
}

.name-row-label {
  font-size: 18px;
  font-weight: 700;
  color: var(--tech-text-primary);
  white-space: nowrap;
  flex-shrink: 0;
}

.name-row-center {
  flex: 1;
  max-width: 520px;
}

.name-row-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #5a8abf;
  font-size: 11px;
  flex-shrink: 0;
  padding: 4px 10px;
  background: rgba(var(--tech-blue-rgb), 0.04);
  border: 1px solid rgba(var(--tech-blue-rgb), 0.08);
  border-radius: 6px;
  line-height: 1.4;
}

.name-row-hint svg {
  color: #4a7a9e;
  flex-shrink: 0;
  margin-top: 1px;
}

/* 名称输入框：大尺寸圆角样式（组件特有，与全局默认差异大） */
.name-input :deep(.el-input__wrapper) {
  background: rgba(6, 30, 70, 0.5) !important;
  border: 1px solid rgba(50, 150, 255, 0.2) !important;
  border-radius: 8px !important;
  padding: 6px 12px !important;
  height: 40px !important;
  box-shadow: none !important;
}

.name-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(50, 150, 255, 0.4) !important;
}

.name-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--tech-cyan) !important;
  box-shadow: 0 0 12px rgba(var(--tech-blue-rgb), 0.15) !important;
}

.name-input :deep(.el-input__inner) {
  color: var(--tech-text-primary) !important;
  font-size: 14px;
  font-weight: 500;
}

.name-input :deep(.el-input__inner::placeholder) {
  color: #4a6a7e;
}
</style>
