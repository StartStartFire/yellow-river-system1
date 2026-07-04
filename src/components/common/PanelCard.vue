<script setup lang="ts">
interface Props {
  title?: string
  unit?: string
  /** 是否显示底部分割线 */
  divider?: boolean
  /** 紧凑模式 - 更小的padding */
  compact?: boolean
}
withDefaults(defineProps<Props>(), {
  divider: false,
  compact: false,
})
</script>

<template>
  <div class="section-panel" :class="{ compact }">
    <div v-if="title" class="section-header">
      <span class="section-title">{{ title }}</span>
      <span v-if="unit" class="section-unit">{{ unit }}</span>
      <slot name="header-extra"></slot>
    </div>
    <div class="section-body">
      <slot></slot>
    </div>
    <div v-if="divider" class="section-divider"></div>
  </div>
</template>

<style scoped>
.section-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
}

.section-panel.compact .section-header {
  padding: 4px 10px;
}

.section-panel.compact .section-body {
  padding: 6px 10px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  flex-shrink: 0;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--tech-text-secondary);
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.section-unit {
  font-size: 11px;
  color: var(--tech-text-placeholder);
}

.section-body {
  padding: 8px 12px;
  flex: 1;
  min-height: 0;
}

/* 分割线：发光的细线 */
.section-divider {
  height: 1px;
  margin: 0 12px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(var(--tech-blue-rgb), 0.25) 20%,
    rgba(var(--tech-cyan-rgb), 0.4) 50%,
    rgba(var(--tech-blue-rgb), 0.25) 80%,
    transparent 100%
  );
}
</style>
