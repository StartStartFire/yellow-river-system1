<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ConstraintDetail } from '@/types/model'

interface Props {
  constraints: ConstraintDetail[]
  enabledMap: Record<string, boolean>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:enabledMap', value: Record<string, boolean>): void
  (e: 'update:constraints', value: ConstraintDetail[]): void
  (e: 'edit'): void
}>()

const dialogVisible = ref(false)

const enabledCount = computed(() =>
  Object.values(props.enabledMap).filter(Boolean).length
)

const isEnabled = (name: string) => props.enabledMap[name] ?? true

const toggleEnabled = (name: string, value: boolean | string | number) => {
  emit('update:enabledMap', { ...props.enabledMap, [name]: !!value })
}

const updateConstraintField = (idx: number, field: 'min' | 'max', value: number | undefined) => {
  if (value === undefined || value === null) return
  const updated = props.constraints.map((c, i) =>
    i === idx ? { ...c, [field]: value } : c
  )
  emit('update:constraints', updated)
}

const openDialog = () => {
  dialogVisible.value = true
}

const confirmDialog = () => {
  dialogVisible.value = false
  emit('edit')
}

const cancelDialog = () => {
  dialogVisible.value = false
}
</script>

<template>
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
          <span class="constraint-sub">已启用 {{ enabledCount }} / {{ constraints.length }} 项约束</span>
        </div>
        <button class="constraint-edit-btn" @click="openDialog" title="编辑约束详情">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
            <path d="M11 2l3 3-9 9H2v-3l9-9z" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          编辑
        </button>
      </div>
    </div>
    <div class="constraint-grid">
      <div
        v-for="(c, cIdx) in constraints"
        :key="cIdx"
        class="constraint-item"
        :class="{ 'constraint-disabled': !isEnabled(c.name) }"
      >
        <div class="constraint-top">
          <span class="constraint-dot" :class="{ 'dot-on': isEnabled(c.name) }"></span>
          <span class="constraint-name">{{ c.name }}</span>
          <span class="constraint-range">{{ c.min }} ~ {{ c.max }} {{ c.unit }}</span>
        </div>
      </div>
    </div>

    <!-- 约束条件编辑弹窗 -->
    <el-dialog v-model="dialogVisible" title="约束条件设置" width="620px" :close-on-click-modal="false" class="confirm-dialog">
      <div class="constraint-dialog-body">
        <div class="constraint-summary-text">
          选择本次计算需要启用的约束条件，并可编辑各约束的数值范围：
        </div>
        <div class="constraint-switch-list">
          <div
            v-for="(c, cIdx) in constraints"
            :key="cIdx"
            class="constraint-switch-item"
            :class="{ 'constraint-disabled': !isEnabled(c.name) }"
          >
            <div class="constraint-switch-top">
              <div class="constraint-switch-left">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="constraint-item-icon">
                  <circle cx="8" cy="8" r="4" fill="rgba(0,175,255,0.15)" stroke="#00afff" stroke-width="1.2"/>
                  <path d="M6 8l1.5 1.5L10 7" stroke="#00afff" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span class="constraint-item-name">{{ c.name }}</span>
              </div>
              <el-switch
                :model-value="isEnabled(c.name)"
                @update:model-value="(val: boolean | string | number) => toggleEnabled(c.name, val)"
                size="small"
                class="dark-switch"
              />
            </div>
            <div class="constraint-range-row">
              <div class="range-item">
                <label class="range-label">最小值</label>
                <el-input-number
                  :model-value="c.min"
                  @update:model-value="(val: number | undefined) => updateConstraintField(cIdx, 'min', val)"
                  size="small"
                  :disabled="!isEnabled(c.name)"
                  controls-position="right"
                  class="dark-input-number"
                />
              </div>
              <div class="range-item">
                <label class="range-label">最大值</label>
                <el-input-number
                  :model-value="c.max"
                  @update:model-value="(val: number | undefined) => updateConstraintField(cIdx, 'max', val)"
                  size="small"
                  :disabled="!isEnabled(c.name)"
                  controls-position="right"
                  class="dark-input-number"
                />
              </div>
              <span class="range-unit">{{ c.unit }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="cancelDialog">取消</el-button>
          <el-button type="primary" size="small" @click="confirmDialog">确认</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
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

/* ===== 弹窗通用 ===== */
.confirm-dialog :deep(.el-dialog) { background: rgba(6, 30, 70, 0.98) !important; border: 1px solid rgba(50, 150, 255, 0.4); border-radius: 12px; }
.confirm-dialog :deep(.el-dialog__header) { border-bottom: 1px solid rgba(50, 150, 255, 0.2); padding: 14px 18px; margin: 0; }
.confirm-dialog :deep(.el-dialog__title) { color: var(--tech-text-primary); font-size: 14px; font-weight: 600; }
.confirm-dialog :deep(.el-dialog__body) { padding: 18px; }
.confirm-dialog :deep(.el-dialog__footer) { border-top: 1px solid rgba(50, 150, 255, 0.1); padding: 10px 18px; }

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
</style>
