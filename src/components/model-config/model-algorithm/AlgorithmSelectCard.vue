<script setup lang="ts">
import type { OptimizationAlgorithm } from '@/types/model'

interface Props {
  algorithms: OptimizationAlgorithm[]
  algorithmId: string
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:algorithmId', value: string): void
  (e: 'open-params'): void
}>()

const selectAlgo = (id: string) => emit('update:algorithmId', id)
</script>

<template>
  <div class="card-base algo-card">
    <div class="card-header">
      <div class="card-icon-box algo-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="3"/>
          <path d="M12 2v4M12 18v4M2 12h4M18 12h4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
        </svg>
      </div>
      <div class="card-title-group">
        <span class="card-title">优化算法</span>
        <span class="card-sub">选择优化求解算法</span>
      </div>
      <button class="param-btn" @click="emit('open-params')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12.22 2h-.44a2 2 0 00-2 2v.18a2 2 0 01-1 1.73l-.43.25a2 2 0 01-2 0l-.15-.08a2 2 0 00-2.73.73l-.22.38a2 2 0 00.73 2.73l.15.1a2 2 0 011 1.73v.18a2 2 0 002 2h.44a2 2 0 002-2v-.18a2 2 0 011-1.73l.43-.25a2 2 0 012 0l.15.08a2 2 0 002.73-.73l.22-.38a2 2 0 00-.73-2.73l-.15-.1a2 2 0 01-1-1.73v-.18a2 2 0 00-2-2h.44"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        参数设置
      </button>
    </div>
    <div class="card-body">
      <div class="algo-options">
        <div
          v-for="algo in algorithms"
          :key="algo.id"
          class="algo-option"
          :class="{ active: algorithmId === algo.id }"
          @click="selectAlgo(algo.id)"
        >
          <div class="algo-option-dot" :class="{ 'dot-active': algorithmId === algo.id }"></div>
          <div class="algo-option-info">
            <div class="algo-option-name">{{ algo.name }}</div>
            <div class="algo-option-desc">{{ algo.paramIds.length }} 个参数</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.algo-icon { background: rgba(var(--tech-green-rgb), 0.12); color: #00ff88; }

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

.param-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  padding: 4px 10px;
  font-size: 10px;
  color: var(--tech-cyan);
  background: rgba(var(--tech-blue-rgb), 0.08);
  border: 1px solid rgba(var(--tech-blue-rgb), 0.25);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.param-btn:hover { background: rgba(var(--tech-blue-rgb), 0.15); border-color: rgba(var(--tech-blue-rgb), 0.4); }

.algo-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.algo-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.algo-option:hover { background: rgba(var(--tech-green-rgb), 0.04); }
.algo-option.active { background: rgba(var(--tech-green-rgb), 0.06); border-color: rgba(var(--tech-green-rgb), 0.25); }

.algo-option-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid rgba(80, 100, 120, 0.5);
  flex-shrink: 0;
  transition: all 0.2s;
}

.algo-option-dot.dot-active { border-color: #00ff88; background: #00ff88; box-shadow: 0 0 6px rgba(var(--tech-green-rgb), 0.4); }

.algo-option-info { min-width: 0; }
.algo-option-name { font-size: 11px; font-weight: 600; color: var(--tech-text-regular); }
.algo-option.active .algo-option-name { color: var(--tech-text-primary); }
.algo-option-desc { font-size: 9px; color: var(--tech-text-placeholder); }
</style>
