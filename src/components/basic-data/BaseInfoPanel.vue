<script setup lang="ts">
import type { BaseInfoGroup } from '@/mock/basicData'

interface Props {
  groups: BaseInfoGroup[]
}

defineProps<Props>()
</script>

<template>
  <div class="base-info-panel">
    <div v-for="group in groups" :key="group.title" class="info-card">
      <div class="card-header">
        <div class="header-icon" :class="group.title === '工程属性' ? 'icon-engineering' : 'icon-rule'">
          <svg v-if="group.title === '工程属性'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3 class="card-title">{{ group.title }}</h3>
      </div>
      <div class="card-body">
        <div v-for="(item, index) in group.items" :key="item.key" class="info-item" :class="{ 'item-highlight': index === 0 }">
          <div class="item-label">{{ item.key }}</div>
          <div class="item-value">{{ item.value }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.base-info-panel {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  height: 100%;
}

.info-card {
  background: rgba(6, 30, 70, 0.5);
  border: 1px solid rgba(50, 150, 255, 0.12);
  backdrop-filter: blur(16px);
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  background: rgba(10, 25, 41, 0.4);
}

.header-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon svg {
  width: 18px;
  height: 18px;
}

.icon-engineering {
  background: rgba(0, 212, 255, 0.15);
  color: #00d4ff;
}

.icon-rule {
  background: rgba(0, 255, 136, 0.15);
  color: #00ff88;
}

.card-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #e0e6ed;
}

.card-body {
  padding: 16px 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
}

.card-body::-webkit-scrollbar {
  width: 4px;
}

.card-body::-webkit-scrollbar-track {
  background: transparent;
}

.card-body::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.2);
  border-radius: 2px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: rgba(17, 37, 54, 0.4);
  border: 1px solid rgba(50, 150, 255, 0.06);
  border-radius: 8px;
}

.item-highlight {
  background: rgba(0, 212, 255, 0.08);
}

.item-label {
  font-size: 12px;
  color: #00d4ff;
  font-weight: 500;
}

.item-value {
  font-size: 12px;
  color: #c0c8d4;
  line-height: 1.6;
}
</style>
