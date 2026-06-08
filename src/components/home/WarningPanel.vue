<script setup lang="ts">
import PanelCard from '@/components/common/PanelCard.vue'
import { warningList } from '@/mock/home'

const warningData = warningList.data

const levelConfig = {
  1: { label: '一级', color: '#FF4D4F' },
  2: { label: '二级', color: '#FFAA00' },
  3: { label: '三级', color: '#FFD700' },
  4: { label: '四级', color: '#00AFFF' },
}
</script>

<template>
  <PanelCard title="预警信息">
    <!-- 预警表格 -->
    <div class="warning-list">
      <div v-for="warning in warningData" :key="warning.id" class="warning-item">
        <div class="warning-time">{{ warning.time }}</div>
        <div class="warning-type">{{ warning.type }}</div>
        <div class="warning-content" :title="warning.content">{{ warning.content }}</div>
        <div class="warning-target">{{ warning.target }}</div>
        <span class="warning-level" :style="{ color: levelConfig[warning.level].color }">
          {{ levelConfig[warning.level].label }}
        </span>
      </div>
    </div>
  </PanelCard>
</template>

<style scoped>
.warning-list {
  max-height: 108px;
  overflow-y: auto;
}

.warning-list::-webkit-scrollbar {
  width: 4px;
}

.warning-list::-webkit-scrollbar-track {
  background: rgba(50, 150, 255, 0.1);
}

.warning-list::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.3);
  border-radius: 2px;
}

.warning-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 12px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.1);
}

.warning-time {
  color: #7a8fa3;
  white-space: nowrap;
  min-width: 65px;
}

.warning-type {
  color: #c0c8d4;
  white-space: nowrap;
  min-width: 60px;
}

.warning-content {
  color: #7a8fa3;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.warning-target {
  color: #c0c8d4;
  white-space: nowrap;
  min-width: 70px;
}

.warning-level {
  font-weight: 600;
  font-size: 11px;
  white-space: nowrap;
  min-width: 30px;
  text-align: right;
}
</style>
