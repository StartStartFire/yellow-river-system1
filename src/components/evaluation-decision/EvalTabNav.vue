<script setup lang="ts">
/**
 * EvalTabNav — 评价决策页面顶部 Tab 导航栏
 *
 * 在「评价分析」与「决策分析」两个面板之间切换。
 */
interface Props {
  /** 当前激活的 Tab 标识：'evaluation' | 'decision' */
  activeTab: string
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'switch', tab: string): void
}>()

const handleSwitch = (tab: string) => {
  emit('switch', tab)
}
</script>

<template>
  <div class="tab-nav-bar">
    <button
      class="tab-nav-btn"
      :class="{ active: activeTab === 'evaluation' }"
      @click="handleSwitch('evaluation')"
    >
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="8" cy="8" r="6"/>
        <path d="M5.5 8L7.5 10L11 5.5"/>
      </svg>
      评价分析
    </button>
    <button
      class="tab-nav-btn"
      :class="{ active: activeTab === 'decision' }"
      @click="handleSwitch('decision')"
    >
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="2" y="2" width="12" height="12" rx="2"/>
        <path d="M5 8L7 10L11 6"/>
      </svg>
      决策分析
    </button>
  </div>
</template>

<style scoped>
.tab-nav-bar {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  padding: 6px 14px;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.12);
}

.tab-nav-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  padding: 8px 0;
  font-size: 13px;
  font-weight: 500;
  color: var(--tech-text-secondary);
  background: transparent;
  border: none;
  border-radius: 0;
  cursor: pointer;
  transition: all 0.25s ease;
  justify-content: center;
}

.tab-nav-btn:hover {
  color: var(--tech-text-regular);
  background: rgba(var(--tech-blue-rgb), 0.05);
}

.tab-nav-btn.active {
  color: var(--tech-cyan);
  background: rgba(var(--tech-blue-rgb), 0.12);
  border-bottom: 2px solid rgba(var(--tech-cyan-rgb), 0.6);
}

.tab-nav-btn svg {
  flex-shrink: 0;
}
</style>
