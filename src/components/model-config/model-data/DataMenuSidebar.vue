<script setup lang="ts">
/**
 * DataMenuSidebar — 模型数据左侧数据目录
 *
 * 包含：标题行 + 菜单分组列表（可滚动）+ 底部收起按钮。
 * 通过 v-model:update:activeMenuId / v-model:update:collapsed 与父组件双向绑定。
 */
import type { MenuGroup } from '@/types/model'

interface Props {
  /** 菜单分组数据 */
  menus: MenuGroup[]
  /** 当前选中的菜单项 id */
  activeMenuId: string
  /** 是否收起 */
  collapsed: boolean
  /** 图标 SVG 字符串映射 */
  iconMap: Record<string, string>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:activeMenuId', value: string): void
  (e: 'update:collapsed', value: boolean): void
}>()

const handleSelectMenu = (menuId: string) => {
  emit('update:activeMenuId', menuId)
}

const handleToggleSidebar = () => {
  emit('update:collapsed', !props.collapsed)
}
</script>

<template>
  <div class="sidebar" :class="{ collapsed }">
    <div class="sidebar-inner">
      <div class="sidebar-title-row">
        <svg v-if="!collapsed" width="16" height="16" viewBox="0 0 16 16" fill="none" class="shrink-0">
          <rect x="2" y="3" width="5" height="4" rx="1" stroke="#8aa0b8" stroke-width="1.3" />
          <rect x="9" y="3" width="5" height="4" rx="1" stroke="#8aa0b8" stroke-width="1.3" />
          <rect x="2" y="9.5" width="5" height="4" rx="1" stroke="#8aa0b8" stroke-width="1.3" />
          <rect x="9" y="9.5" width="5" height="4" rx="1" stroke="#8aa0b8" stroke-width="1.3" />
        </svg>
        <span v-if="!collapsed" class="sidebar-title">数据目录</span>
      </div>

      <div class="menu-scroll-area">
        <div v-for="(group, gIdx) in menus" :key="gIdx" class="menu-group">
          <div v-if="!collapsed" class="group-header">{{ group.groupName }}</div>
          <div
            v-for="item in group.children"
            :key="item.id"
            class="menu-item"
            :class="{ active: item.id === activeMenuId }"
            @click="handleSelectMenu(item.id)"
          >
            <span class="menu-icon" v-html="iconMap[item.icon] || iconMap.database"></span>
            <span v-if="!collapsed" class="menu-name">{{ item.name }}</span>
          </div>
        </div>
      </div>

      <!-- 收起按钮 -->
      <div class="collapse-footer" @click="handleToggleSidebar">
        <svg v-if="!collapsed" width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M10 3L5 8L10 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <svg v-else width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M6 3L11 8L6 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <span v-if="!collapsed" class="collapse-text">收起</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sidebar {
  width: 200px;
  min-width: 200px;
  transition: width 0.25s ease, min-width 0.25s ease;
  overflow: hidden;
}

.sidebar.collapsed {
  width: 48px;
  min-width: 48px;
}

.sidebar-inner {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(6, 30, 70, 0.85);
  border: 1px solid rgba(50, 150, 255, 0.35);
  border-radius: 12px;
  overflow: hidden;
}

.menu-scroll-area {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
}

.menu-scroll-area::-webkit-scrollbar {
  width: 4px;
}

.menu-scroll-area::-webkit-scrollbar-track {
  background: transparent;
}

.menu-scroll-area::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.25);
  border-radius: 2px;
}

.menu-scroll-area::-webkit-scrollbar-thumb:hover {
  background: rgba(50, 150, 255, 0.45);
}

.sidebar-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--tech-text-primary);
  white-space: nowrap;
}

.menu-group {
  padding: 6px 0;
  border-bottom: 1px solid rgba(50, 150, 255, 0.08);
}

/* 调度输入和原始表格组均固定显示6项高度，超出滚动 */
.menu-group {
  max-height: 230px;
  overflow-y: auto;
}

.menu-group::-webkit-scrollbar {
  width: 4px;
}

.menu-group::-webkit-scrollbar-track {
  background: transparent;
}

.menu-group::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.25);
  border-radius: 2px;
}

.menu-group::-webkit-scrollbar-thumb:hover {
  background: rgba(50, 150, 255, 0.45);
}

.group-header {
  font-size: 11px;
  font-weight: 500;
  color: var(--tech-text-placeholder);
  padding: 6px 14px 8px;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  margin: 0 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  color: var(--tech-text-secondary);
}

.menu-item:hover {
  background: rgba(var(--tech-blue-rgb), 0.08);
  color: var(--tech-text-regular);
}

.menu-item.active {
  background: rgba(var(--tech-blue-rgb), 0.15);
  border: 1px solid rgba(var(--tech-blue-rgb), 0.4);
  color: var(--tech-cyan);
  margin: 0 5px;
  padding: 7px 13px;
}

.menu-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: inherit;
}

.menu-name {
  font-size: 12px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collapse-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border-top: 1px solid rgba(50, 150, 255, 0.15);
  cursor: pointer;
  color: var(--tech-text-placeholder);
  font-size: 12px;
  transition: all 0.2s;
  margin-top: auto;
  flex-shrink: 0;
}

.collapse-footer:hover {
  color: var(--tech-text-regular);
  background: rgba(var(--tech-blue-rgb), 0.05);
}

.collapse-text {
  white-space: nowrap;
}

/* 收起时 */
.collapsed .menu-item {
  justify-content: center;
  padding: 10px 0;
  margin: 0 4px;
}

.collapsed .menu-item.active {
  padding: 9px 0;
  margin: 0 3px;
}

.collapsed .collapse-footer {
  justify-content: center;
  padding: 10px 0;
}
</style>
