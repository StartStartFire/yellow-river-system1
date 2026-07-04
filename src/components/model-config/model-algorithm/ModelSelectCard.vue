<script setup lang="ts">
import type { DispatchModel } from '@/types/model'

interface Props {
  models: DispatchModel[]
  modelId: string
  scenarioName?: string
  groupName?: string
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:modelId', value: string): void
}>()

const selectModel = (id: string) => emit('update:modelId', id)
</script>

<template>
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
      <span v-if="scenarioName" class="scenario-badge">场景：{{ scenarioName }}</span>
      <span class="group-badge">水库组合：{{ groupName }}</span>
    </div>
    <div class="card-body">
      <div class="model-options">
        <div
          v-for="model in models"
          :key="model.id"
          class="model-option"
          :class="{ active: modelId === model.id }"
          @click="selectModel(model.id)"
        >
          <div class="model-option-dot" :class="{ 'dot-active': modelId === model.id }"></div>
          <div class="model-option-info">
            <div class="model-option-name">{{ model.name }}</div>
            <div class="model-option-desc">{{ model.description }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
</style>
