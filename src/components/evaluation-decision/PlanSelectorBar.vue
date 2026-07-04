<script setup lang="ts">
/**
 * PlanSelectorBar — 评价分析顶部多方案对比选择器
 *
 * 通过复选框组选择需要对比的方案，选中值双向绑定到父组件。
 */
interface PlanOption {
  label: string
  value: string
}

interface Props {
  /** 全部可选方案列表 */
  plans: PlanOption[]
  /** 当前选中的方案 value 数组 */
  selectedPlans: string[]
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:selectedPlans', value: string[]): void
}>()

const handleChange = (val: string[]) => {
  emit('update:selectedPlans', val)
}
</script>

<template>
  <div class="selector-bar">
    <span class="selector-label">多方案对比：</span>
    <el-checkbox-group
      :model-value="selectedPlans"
      class="plan-checkboxes"
      @update:model-value="handleChange"
    >
      <el-checkbox v-for="plan in plans" :key="plan.value" :value="plan.value" :label="plan.label">
        <span class="checkbox-label-text">{{ plan.label }}</span>
      </el-checkbox>
    </el-checkbox-group>
  </div>
</template>

<style scoped>
.selector-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  margin-bottom: 4px;
  min-height: 24px;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.08);
  padding-bottom: 8px;
}
.selector-label {
  font-size: 12px;
  color: var(--tech-text-secondary);
  white-space: nowrap;
}
.plan-checkboxes {
  display: flex;
  gap: 8px;
}
/* 自定义复选框样式覆盖 */
:deep(.el-checkbox) {
  margin-right: 0;
  height: 20px;
}
:deep(.el-checkbox__label) {
  font-size: 11px;
  color: var(--tech-text-regular);
}
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: var(--tech-blue);
  border-color: var(--tech-blue);
}
:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: var(--tech-blue);
}
:deep(.el-checkbox__inner) {
  width: 12px;
  height: 12px;
}
.checkbox-label-text {
  font-size: 11px;
}
</style>
