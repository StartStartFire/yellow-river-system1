<script setup lang="ts">
interface Props {
  status: 'normal' | 'warning' | 'abnormal'
}
defineProps<Props>()

const statusConfig = {
  normal: { label: '正常', color: '#00FF88' },
  warning: { label: '预警', color: '#FFAA00' },
  abnormal: { label: '异常', color: '#FF4D4F' },
}
</script>

<template>
  <span class="status-tag" :style="{ color: statusConfig[status].color }">
    <span class="status-dot" :style="{ background: statusConfig[status].color }"></span>
    {{ statusConfig[status].label }}
  </span>
</template>

<style scoped>
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
</style>
