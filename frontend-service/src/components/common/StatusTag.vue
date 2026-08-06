<script setup lang="ts">
/**
 * StatusTag — 通用状态标签
 *
 * 用法 1：使用预设状态
 *   <StatusTag status="normal" />
 *   <StatusTag status="warning" />
 *
 * 用法 2：自定义标签和颜色
 *   <StatusTag label="运行中" color="#00FF88" :pulse="true" />
 *   <StatusTag label="停机" color="#8aa0b8" />
 */
import { computed } from 'vue'

interface Props {
  /** 预设状态：normal / warning / abnormal（与 label/color 二选一） */
  status?: 'normal' | 'warning' | 'abnormal'
  /** 自定义标签文本（与 status 二选一） */
  label?: string
  /** 自定义颜色（与 status 二选一） */
  color?: string
  /** 是否显示脉冲动画（运行中等动态状态使用） */
  pulse?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  pulse: false,
})

const presetConfig = {
  normal:   { label: '正常', color: '#00FF88' },
  warning:  { label: '预警', color: '#FFAA00' },
  abnormal: { label: '异常', color: '#FF4D4F' },
}

const resolved = computed(() => {
  if (props.status) {
    return presetConfig[props.status]
  }
  return { label: props.label || '', color: props.color || '#8aa0b8' }
})
</script>

<template>
  <span class="status-tag" :style="{ color: resolved.color }">
    <span
      class="status-dot"
      :class="{ 'is-pulse': pulse }"
      :style="{ background: resolved.color }"
    ></span>
    {{ resolved.label }}
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
  flex-shrink: 0;
}

.status-dot.is-pulse {
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
