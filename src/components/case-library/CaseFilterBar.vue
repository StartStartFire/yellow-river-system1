<script setup lang="ts">
/**
 * CaseFilterBar — 案例库顶部筛选区
 *
 * 包含 4 个筛选项（时间范围 / 案例类型 / 涉及水库 / 关键词）
 * 以及查询、重置、高级筛选 3 个按钮。
 *
 * 父组件通过 v-model:filters 双向绑定筛选状态，
 * 并监听 search / reset / advanced-filter 三个事件。
 */
import { ElMessage } from 'element-plus'
import { caseTypeOptions, reservoirOptions } from '@/mock/caseLibrary'

export interface CaseFilters {
  dateRange: string[]
  caseType: string
  reservoir: string
  keyword: string
}

const props = defineProps<{
  filters: CaseFilters
}>()

const emit = defineEmits<{
  (e: 'update:filters', value: CaseFilters): void
  (e: 'search'): void
  (e: 'reset'): void
  (e: 'advanced-filter'): void
}>()

const updateField = <K extends keyof CaseFilters>(field: K, value: CaseFilters[K]) => {
  emit('update:filters', { ...props.filters, [field]: value })
}

const handleSearch = () => emit('search')

const handleReset = () => emit('reset')

const handleAdvancedFilter = () => {
  ElMessage.info('高级筛选功能开发中')
  emit('advanced-filter')
}
</script>

<template>
  <div class="filter-bar">
    <div class="filter-items">
      <div class="filter-item">
        <label class="filter-label">时间范围</label>
        <el-date-picker
          :model-value="filters.dateRange"
          @update:model-value="updateField('dateRange', $event as string[])"
          type="daterange"
          range-separator="~"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          class="dark-date-picker"
        />
      </div>
      <div class="filter-item">
        <label class="filter-label">案例类型</label>
        <el-select
          :model-value="filters.caseType"
          @update:model-value="updateField('caseType', $event)"
          class="dark-select"
          style="width: 140px;"
        >
          <el-option v-for="item in caseTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </div>
      <div class="filter-item">
        <label class="filter-label">涉及水库</label>
        <el-select
          :model-value="filters.reservoir"
          @update:model-value="updateField('reservoir', $event)"
          class="dark-select"
          style="width: 140px;"
        >
          <el-option v-for="item in reservoirOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </div>
      <div class="filter-item">
        <label class="filter-label">关键词</label>
        <el-input
          :model-value="filters.keyword"
          @update:model-value="updateField('keyword', $event)"
          placeholder="请输入案例名称或关键词"
          class="dark-input"
          clearable
        />
      </div>
    </div>
    <div class="filter-actions">
      <button class="btn-primary" @click="handleSearch">查询</button>
      <button class="btn-secondary" @click="handleReset">重置</button>
      <button class="btn-outline" @click="handleAdvancedFilter">
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        高级筛选
      </button>
    </div>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  flex-shrink: 0;
}

.filter-items {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 12px;
  color: var(--tech-text-secondary);
  white-space: nowrap;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: linear-gradient(135deg, var(--tech-blue) 0%, var(--tech-cyan) 100%);
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--tech-cyan) 0%, var(--tech-cyan-light) 100%);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: rgba(50, 150, 255, 0.1);
  border: 1px solid rgba(50, 150, 255, 0.3);
  border-radius: 6px;
  color: var(--tech-cyan);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(50, 150, 255, 0.2);
  border-color: rgba(50, 150, 255, 0.5);
}

.btn-outline {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: transparent;
  border: 1px solid rgba(50, 150, 255, 0.25);
  border-radius: 6px;
  color: var(--tech-text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-outline:hover {
  background: rgba(50, 150, 255, 0.1);
  color: var(--tech-text-primary);
  border-color: rgba(50, 150, 255, 0.4);
}

:deep(.dark-date-picker .el-input__wrapper),
:deep(.dark-select .el-input__wrapper) {
  background: transparent;
  border: 1px solid rgba(50, 150, 255, 0.25);
  box-shadow: none;
}

:deep(.dark-date-picker .el-input__inner),
:deep(.dark-select .el-input__inner) {
  color: var(--tech-text-primary);
}

:deep(.dark-input .el-input__wrapper) {
  background: transparent;
  border: 1px solid rgba(50, 150, 255, 0.25);
  box-shadow: none;
}

:deep(.dark-input .el-input__inner) {
  color: var(--tech-text-primary);
}

:deep(.el-range-input) {
  color: var(--tech-text-primary);
}

:deep(.el-range-separator) {
  color: var(--tech-text-secondary);
}

:deep(.el-date-editor .el-range__icon) {
  color: var(--tech-text-secondary);
}

:deep(.el-date-editor .el-range-close-icon) {
  color: var(--tech-text-secondary);
}

:deep(.el-popper) {
  background: #112536;
  border-color: rgba(50, 150, 255, 0.25);
}

:deep(.el-popper__arrow::before) {
  background: #112536;
  border-color: rgba(50, 150, 255, 0.25);
}
</style>
