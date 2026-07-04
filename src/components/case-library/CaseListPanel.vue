<script setup lang="ts">
/**
 * CaseListPanel — 案例库左侧案例列表
 *
 * 包含 panel-title-bar（标题 + 计数）与 case-list（卡片列表）。
 * 卡片样式、图标、渐变背景由本组件内部维护，
 * 案例数据、选中状态、收藏状态由父组件传入。
 */
import { getIconByType, getCoverGradient } from '@/utils/caseLibrary'

defineProps<{
  cases: any[]
  selectedCaseId: string
  total: number
  isFavorited: boolean
}>()

const emit = defineEmits<{
  (e: 'select', id: string): void
  (e: 'favorite'): void
}>()

const handleSelect = (id: string) => emit('select', id)
const handleFavorite = () => emit('favorite')
</script>

<template>
  <div class="case-list-panel">
    <div class="panel-title-bar">
      <span class="title-text">案例列表</span>
      <span class="title-count">共 {{ total }} 条</span>
    </div>
    <div class="case-list">
      <div
        v-for="caseItem in cases"
        :key="caseItem.id"
        class="case-card"
        :class="{ active: selectedCaseId === caseItem.id }"
        @click="handleSelect(caseItem.id)"
      >
        <div class="case-cover" :style="{ background: getCoverGradient(caseItem.cover) }">
          <div class="case-icon" v-html="getIconByType(caseItem.iconType)"></div>
          <span class="case-tag" :style="{ background: caseItem.tagColor + '20', color: caseItem.tagColor, borderColor: caseItem.tagColor + '40' }">
            {{ caseItem.tag }}
          </span>
        </div>
        <div class="case-info">
          <div class="case-header">
            <h4 class="case-title">{{ caseItem.title }}</h4>
            <span class="case-status" :style="{ color: caseItem.statusColor }">{{ caseItem.status }}</span>
          </div>
          <div class="case-meta">
            <span class="meta-item">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              {{ caseItem.reservoirs.join('、') }}
            </span>
          </div>
          <div class="case-meta">
            <span class="meta-item">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              {{ caseItem.caseType.join(' / ') }}
            </span>
            <span class="meta-item">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              {{ caseItem.createdAt }}
            </span>
          </div>
          <p class="case-summary">{{ caseItem.summary }}</p>
        </div>
        <div class="case-actions">
          <button
            class="action-btn"
            :class="{ favorited: isFavorited && selectedCaseId === caseItem.id }"
            @click.stop="handleFavorite"
            title="收藏"
          >
            <svg class="w-4 h-4" :fill="isFavorited && selectedCaseId === caseItem.id ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
          <button class="action-btn" @click.stop="handleSelect(caseItem.id)" title="查看详情">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.case-list-panel {
  width: 48%;
  display: flex;
  flex-direction: column;
  background: transparent;
  border: none;
  border-right: 1px solid rgba(var(--tech-blue-rgb), 0.08);
  border-radius: 0;
  overflow: hidden;
}

.panel-title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
}

.title-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--tech-text-primary);
}

.title-count {
  font-size: 12px;
  color: var(--tech-text-secondary);
}

.case-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.case-list::-webkit-scrollbar {
  width: 4px;
}

.case-list::-webkit-scrollbar-track {
  background: rgba(50, 150, 255, 0.05);
  border-radius: 2px;
}

.case-list::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.2);
  border-radius: 2px;
}

.case-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  border-radius: 0;
  cursor: pointer;
  transition: all 0.3s;
}

.case-card:hover {
  background: rgba(var(--tech-blue-rgb), 0.04);
  border-bottom-color: rgba(var(--tech-blue-rgb), 0.2);
}

.case-card.active {
  background: rgba(var(--tech-blue-rgb), 0.06);
  border-bottom-color: rgba(var(--tech-cyan-rgb), 0.4);
}

.case-cover {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  flex-shrink: 0;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.case-icon {
  width: 36px;
  height: 36px;
  color: rgba(255, 255, 255, 0.8);
}

.case-icon :deep(svg) {
  width: 100%;
  height: 100%;
}

.case-tag {
  position: absolute;
  top: 6px;
  left: 6px;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid;
  font-weight: 500;
}

.case-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.case-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.case-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--tech-text-primary);
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.case-status {
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.case-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--tech-text-secondary);
}

.case-summary {
  font-size: 11px;
  color: var(--tech-text-secondary);
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.case-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

.action-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 0;
  color: var(--tech-text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  background: rgba(var(--tech-blue-rgb), 0.08);
  color: var(--tech-text-primary);
}

.action-btn.favorited {
  color: #ff4d4f;
}
</style>
