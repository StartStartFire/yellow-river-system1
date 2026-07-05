<script setup lang="ts">
import { computed } from 'vue'
import type { ConfigPlan } from '@/types/model'

interface Props {
  plans: ConfigPlan[]
  currentPage: number
  pageSize: number
  searchQuery: string
  selectedCount: number
  totalCount: number
  totalPages: number
  tableSelected: ConfigPlan[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:searchQuery', value: string): void
  (e: 'update:currentPage', value: number): void
  (e: 'add'): void
  (e: 'filter'): void
  (e: 'selection-change', rows: ConfigPlan[]): void
  (e: 'detail'): void
  (e: 'edit'): void
  (e: 'copy', plan: ConfigPlan): void
  (e: 'delete', plan: ConfigPlan): void
  (e: 'run-single', plan: ConfigPlan): void
}>()

const localSearch = computed({
  get: () => props.searchQuery,
  set: (v: string) => emit('update:searchQuery', v),
})

const onSelectionChange = (val: ConfigPlan[]) => {
  emit('selection-change', val)
}

const goPage = (page: number) => {
  if (page >= 1 && page <= props.totalPages) {
    emit('update:currentPage', page)
  }
}

const pageNumbers = computed(() => {
  const total = props.totalPages
  const current = props.currentPage
  const pages: (number | string)[] = []
  if (total <= 5) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})
</script>

<template>
  <div class="table-section">
    <div class="card table-card">
      <!-- 标题 + 操作栏 -->
      <div class="card-header">
        <div class="header-title-row">
          <div class="header-accent-line"></div>
          <span class="header-title">配置汇总</span>
        </div>
        <div class="toolbar-actions">
          <el-button size="small" type="primary" class="toolbar-btn" @click="emit('add')">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" class="btn-icon-sm">
              <path d="M6 2v8M2 6h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            新增
          </el-button>
          <el-button size="small" class="toolbar-btn" @click="emit('filter')">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" class="btn-icon-sm">
              <path d="M1 2h10L7 6.5V10L5 11V6.5L1 2z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
            </svg>
            筛选
          </el-button>
          <el-input
            v-model="localSearch"
            placeholder="搜索方案名、模型、算法或场景"
            size="small"
            clearable
            class="search-input"
          >
            <template #prefix>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="search-icon">
                <circle cx="6" cy="6" r="4" stroke="#6e8a9e" stroke-width="1.3"/>
                <path d="M9.5 9.5L13 13" stroke="#6e8a9e" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
            </template>
          </el-input>
        </div>
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <el-table
          :data="plans"
          height="100%"
          style="width: 100%"
          size="small"
          stripe
          class="dark-table"
          @selection-change="onSelectionChange"
          row-key="id"
        >
          <el-table-column type="selection" width="40" />
          <el-table-column label="序号" width="50" prop="index" />
          <el-table-column label="方案名" min-width="160" prop="name" />
          <el-table-column label="模型" min-width="150" prop="model" />
          <el-table-column label="算法" min-width="140" prop="algorithm" />
          <el-table-column label="场景" min-width="130" prop="scenario" />
          <el-table-column label="功能操作" width="240" fixed="right">
            <template #default="{ row }">
              <div class="action-btns">
                <el-button size="small" text class="action-btn action-detail" @click="emit('detail')">详情</el-button>
                <el-button size="small" text class="action-btn action-edit" @click="emit('edit')">编辑</el-button>
                <el-button size="small" text class="action-btn action-copy" @click="emit('copy', row)">复制</el-button>
                <el-button size="small" text class="action-btn action-delete" @click="emit('delete', row)">删除</el-button>
                <el-button size="small" text class="action-btn action-run" @click="emit('run-single', row)">运行</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-bar">
        <div class="pagination-info">
          共 <span class="pagination-num">{{ totalCount }}</span> 条
        </div>
        <div class="pagination-controls">
          <button class="page-btn" :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">‹</button>
          <template v-for="pg in pageNumbers" :key="pg">
            <button
              v-if="pg === '...'"
              class="page-btn page-ellipsis"
              disabled
            >…</button>
            <button
              v-else
              class="page-btn"
              :class="{ 'page-active': pg === currentPage }"
              @click="goPage(pg as number)"
            >{{ pg }}</button>
          </template>
          <button class="page-btn" :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)">›</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.table-section {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  border-right: 1px solid rgba(var(--tech-blue-rgb), 0.08);
}

.card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}

.table-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-accent-line {
  width: 3px;
  height: 18px;
  background: linear-gradient(180deg, var(--tech-cyan), rgba(var(--tech-cyan-rgb), 0.3));
  border-radius: 2px;
  flex-shrink: 0;
}

.header-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--tech-text-primary);
}

.toolbar-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
}

.toolbar-btn {
  font-size: 11px !important;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-icon-sm {
  flex-shrink: 0;
}

.search-input {
  width: 220px;
}

.search-icon {
  flex-shrink: 0;
}

.table-wrapper {
  flex: 1 1 auto;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.dark-table {
  width: 100%;
  height: 100%;
}

.action-btns {
  display: flex;
  gap: 2px;
  flex-wrap: nowrap;
}

.action-btn {
  font-size: 11px !important;
  padding: 2px 5px !important;
  min-width: 0 !important;
  height: auto !important;
}

.action-detail { color: var(--tech-cyan) !important; }
.action-edit { color: var(--tech-text-regular) !important; }
.action-copy { color: #f0a020 !important; }
.action-delete { color: #ff6b6b !important; }
.action-run { color: #00ff88 !important; }

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  border-top: 1px solid rgba(50, 150, 255, 0.1);
  flex-shrink: 0;
}

.pagination-info {
  font-size: 12px;
  color: var(--tech-text-secondary);
}

.pagination-num {
  color: var(--tech-cyan);
  font-weight: 600;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 2px;
}

.page-btn {
  width: 28px;
  height: 28px;
  border: 1px solid rgba(50, 150, 255, 0.2);
  border-radius: 6px;
  background: transparent;
  color: var(--tech-text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  border-color: rgba(50, 150, 255, 0.5);
  color: var(--tech-text-regular);
  background: rgba(var(--tech-blue-rgb), 0.05);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-btn.page-active {
  background: rgba(var(--tech-blue-rgb), 0.2);
  border-color: rgba(var(--tech-blue-rgb), 0.5);
  color: var(--tech-cyan);
  font-weight: 600;
}

.page-ellipsis {
  border: none;
  cursor: default;
}

</style>
