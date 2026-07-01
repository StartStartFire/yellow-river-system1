<script setup lang="ts">
import { computed } from 'vue'
import { reservoirGroups } from '@/mock/basicData'

interface Props {
  selectedId: string
  collapsed: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'select', id: string): void
  (e: 'toggle'): void
}>()

const selectedName = computed(() => {
  for (const group of reservoirGroups.data) {
    const found = group.items.find(r => r.id === props.selectedId)
    if (found) return found.name
  }
  return ''
})

const selectedInitial = computed(() => {
  return selectedName.value ? selectedName.value.charAt(0) : ''
})
</script>

<template>
  <div class="reservoir-sidebar" :class="{ collapsed }">
    <!-- 标题栏 -->
    <div class="sidebar-header">
      <span v-if="!collapsed" class="header-title">水库列表</span>
      <button @click="emit('toggle')" class="collapse-btn" :title="collapsed ? '展开' : '收起'">
        <svg v-if="!collapsed" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 18l-6-6 6-6"/>
        </svg>
        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18l6-6-6-6"/>
        </svg>
      </button>
    </div>

    <!-- 展开时显示分组列表 -->
    <div v-if="!collapsed" class="sidebar-list">
      <div v-for="group in reservoirGroups.data" :key="group.name" class="reservoir-group">
        <div class="group-header">
          <span class="group-line"></span>
          <span class="group-name">{{ group.name }}</span>
          <span class="group-line"></span>
        </div>
        <div class="group-items">
          <div
            v-for="item in group.items"
            :key="item.id"
            class="sidebar-item"
            :class="{ active: item.id === selectedId }"
            @click="emit('select', item.id)"
          >
            <div class="item-dot" :class="item.status"></div>
            <span class="item-name">{{ item.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 收起时显示选中项首字 -->
    <div v-else class="sidebar-collapsed">
      <div class="collapsed-avatar" :title="selectedName">
        {{ selectedInitial }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.reservoir-sidebar {
  display: flex;
  flex-direction: column;
  width: 180px;
  min-width: 180px;
  height: 100%;
  background: transparent;
  border: none;
  border-right: 1px solid rgba(0, 175, 255, 0.12);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.reservoir-sidebar.collapsed {
  width: 56px;
  min-width: 56px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.08);
  flex-shrink: 0;
  min-height: 48px;
}

.header-title {
  font-size: 13px;
  font-weight: 600;
  color: #e0e6ed;
  white-space: nowrap;
}

.collapse-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(50, 150, 255, 0.08);
  border: 1px solid rgba(50, 150, 255, 0.15);
  border-radius: 6px;
  color: #7a8fa3;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.collapse-btn:hover {
  background: rgba(50, 150, 255, 0.15);
  color: #00d4ff;
  border-color: rgba(0, 175, 255, 0.3);
}

.sidebar-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.sidebar-list::-webkit-scrollbar {
  width: 3px;
}

.sidebar-list::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-list::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.15);
  border-radius: 2px;
}

.reservoir-group {
  margin-bottom: 12px;
}

.reservoir-group:last-child {
  margin-bottom: 0;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
  padding: 0 4px;
}

.group-line {
  flex: 1;
  height: 1px;
  background: rgba(50, 150, 255, 0.1);
}

.group-name {
  font-size: 10px;
  color: #4a5f73;
  white-space: nowrap;
  letter-spacing: 0.3px;
}

.group-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.sidebar-item:hover {
  background: rgba(0, 175, 255, 0.06);
}

.sidebar-item.active {
  background: rgba(0, 175, 255, 0.1);
}

.item-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.item-dot.normal { background: #00ff88; box-shadow: 0 0 4px rgba(0, 255, 136, 0.4); }
.item-dot.warning { background: #ffaa00; box-shadow: 0 0 4px rgba(255, 170, 0, 0.4); }
.item-dot.abnormal { background: #ff4d4f; box-shadow: 0 0 4px rgba(255, 77, 79, 0.4); }

.item-name {
  font-size: 12px;
  color: #7a8fa3;
  white-space: nowrap;
  transition: color 0.2s;
}

.sidebar-item.active .item-name {
  color: #e0e6ed;
  font-weight: 500;
}

/* 收起状态 */
.sidebar-collapsed {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
  gap: 8px;
}

.collapsed-avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(0, 175, 255, 0.2) 0%, rgba(0, 212, 255, 0.1) 100%);
  border: 1px solid rgba(0, 175, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #00d4ff;
  cursor: default;
}
</style>
