<script setup lang="ts">
import { computed } from 'vue'
import StatusTag from '@/components/common/StatusTag.vue'
import { reservoirList } from '@/mock/basicData'

interface Props {
  selectedId: string
  collapsed: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'select', id: string): void
  (e: 'toggle'): void
}>()

const statusMap: Record<string, 'normal' | 'warning' | 'abnormal'> = {
  normal: 'normal',
  warning: 'warning',
  abnormal: 'abnormal',
}

const displayName = computed(() => {
  // 展开时显示全名，收起时只显示第一个字
  if (props.collapsed) {
    return reservoirList.find(r => r.id === props.selectedId)?.name.charAt(0) || '-'
  }
  return ''
})
</script>

<template>
  <div class="reservoir-sidebar" :class="{ collapsed }">
    <!-- 标题栏 -->
    <div class="sidebar-header">
      <span class="header-title">水库列表</span>
      <button @click="emit('toggle')" class="collapse-btn" :title="collapsed ? '展开' : '收起'">
        <svg v-if="!collapsed" width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 3L5 8L10 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M6 3L11 8L6 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <!-- 列表区 -->
    <div class="sidebar-list">
      <div
        v-for="item in reservoirList"
        :key="item.id"
        class="sidebar-item"
        :class="{ active: item.id === selectedId }"
        @click="emit('select', item.id)"
      >
        <div class="item-dot" :class="statusMap[item.status]"></div>
        <span v-if="!collapsed" class="item-name">{{ item.name }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reservoir-sidebar {
  display: flex;
  flex-direction: column;
  width: 220px;
  min-width: 220px;
  height: 100%;
  background: rgba(6, 30, 70, 0.85);
  border: 1px solid rgba(50, 150, 255, 0.35);
  border-radius: 12px;
  box-shadow: 0 0 20px rgba(0, 160, 255, 0.12);
  overflow: hidden;
  transition: width 0.2s ease, min-width 0.2s ease;
}

.reservoir-sidebar.collapsed {
  width: 48px;
  min-width: 48px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}

.header-title {
  font-size: 13px;
  font-weight: 600;
  color: #e0e6ed;
  letter-spacing: 0.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collapse-btn {
  background: none;
  border: none;
  color: #7a8fa3;
  cursor: pointer;
  padding: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
  flex-shrink: 0;
}

.collapse-btn:hover {
  color: #00d4ff;
}

.sidebar-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 6px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.sidebar-item:hover {
  background: rgba(0, 175, 255, 0.08);
}

.sidebar-item.active {
  background: rgba(0, 175, 255, 0.15);
  border: 1px solid rgba(0, 175, 255, 0.4);
}

.item-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.item-dot.normal { background: #00FF88; box-shadow: 0 0 6px rgba(0, 255, 136, 0.5); }
.item-dot.warning { background: #FFAA00; box-shadow: 0 0 6px rgba(255, 170, 0, 0.5); }
.item-dot.abnormal { background: #FF4D4F; box-shadow: 0 0 6px rgba(255, 77, 79, 0.5); }

.item-name {
  font-size: 13px;
  color: #c0c8d4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-item.active .item-name {
  color: #e0e6ed;
  font-weight: 500;
}

/* 收起时仅显示选中项 */
.collapsed .sidebar-item:not(.active) {
  display: none;
}

.collapsed .sidebar-item {
  justify-content: center;
  padding: 14px 0;
}

.collapsed .item-dot {
  display: none;
}

.collapsed .item-name {
  font-size: 16px;
  font-weight: 600;
  color: #00d4ff;
}
</style>
