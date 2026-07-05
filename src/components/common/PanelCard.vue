<script setup lang="ts">
interface Props {
  title?: string
  unit?: string
  /** 是否显示底部分割线 */
  divider?: boolean
  /** 紧凑模式 - 更小的padding */
  compact?: boolean
  /** 是否显示强调色条（标题左侧渐变线） */
  accent?: boolean
}
withDefaults(defineProps<Props>(), {
  divider: false,
  compact: false,
  accent: false,
})
</script>

<template>
  <div class="section-panel" :class="{ compact, 'has-accent': accent }">
    <div v-if="title || $slots['header-extra'] || $slots['header-icon'] || $slots['header-actions']" class="section-header">
      <div class="header-left">
        <div v-if="accent" class="header-accent-line"></div>
        <slot name="header-icon"></slot>
        <span v-if="title" class="section-title">{{ title }}</span>
        <span v-if="unit" class="section-unit">{{ unit }}</span>
      </div>
      <div class="header-right">
        <slot name="header-extra"></slot>
        <slot name="header-actions"></slot>
      </div>
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
  gap: 8px;
  padding: 8px 12px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
}

/* 强调色条 */
.header-accent-line {
  width: 3px;
  height: 18px;
  background: linear-gradient(180deg, var(--tech-cyan), rgba(var(--tech-cyan-rgb), 0.3));
  border-radius: 2px;
  flex-shrink: 0;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--tech-text-secondary);
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

/* 强调模式：标题更大更亮 */
.section-panel.has-accent .section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--tech-text-primary);
  letter-spacing: normal;
  text-transform: none;
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
