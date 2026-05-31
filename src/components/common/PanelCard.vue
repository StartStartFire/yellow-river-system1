<script setup lang="ts">
interface Props {
  title?: string
  unit?: string
}
defineProps<Props>()
</script>

<template>
  <div class="panel-card"
    style="background: rgba(6, 30, 70, 0.85); border: 1px solid rgba(50, 150, 255, 0.35); backdrop-filter: blur(6px); border-radius: 12px; box-shadow: 0 0 20px rgba(0, 160, 255, 0.12);">
    <div v-if="title" class="panel-header">
      <span class="panel-title">{{ title }}</span>
      <span v-if="unit" class="panel-unit">{{ unit }}</span>
      <slot name="header-extra"></slot>
    </div>
    <div class="panel-body">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.panel-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: #e0e6ed;
  letter-spacing: 0.5px;
}

.panel-unit {
  font-size: 12px;
  color: #7a8fa3;
}

.panel-body {
  padding: 12px 16px;
  flex: 1;
  min-height: 0;
}
</style>