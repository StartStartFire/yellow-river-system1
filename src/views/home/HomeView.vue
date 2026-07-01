<script setup lang="ts">
import { ref } from 'vue'
import BasinMapPanel from '@/components/home/BasinMapPanel.vue'
import ReservoirMonitorPanel from '@/components/home/ReservoirMonitorPanel.vue'
import PowerStatisticsPanel from '@/components/home/PowerStatisticsPanel.vue'
import WaterLevelChart from '@/components/home/WaterLevelChart.vue'
import LoadChart from '@/components/home/LoadChart.vue'
import WarningPanel from '@/components/home/WarningPanel.vue'

const selectedReservoirId = ref<string | null>(null)
const panelsVisible = ref(false)

const handleSelectReservoir = (id: string) => {
  selectedReservoirId.value = id
}

const handleClearSelected = () => {
  selectedReservoirId.value = null
}
</script>

<template>
  <div class="home-view">
    <div class="home-body">
      <!-- 全屏地图背景 -->
      <div class="map-background">
        <BasinMapPanel
          :selected-id="selectedReservoirId"
          @select-reservoir="handleSelectReservoir"
          @clear-selected="handleClearSelected"
        />
      </div>

      <!-- 左侧面板（滑入/滑出） -->
      <div class="side-panel left-panel" :class="{ visible: panelsVisible }">
        <ReservoirMonitorPanel class="panel-card-flex" @select-reservoir="handleSelectReservoir" />
        <PowerStatisticsPanel class="panel-card-flex" />
      </div>

      <!-- 右侧面板（滑入/滑出） -->
      <div class="side-panel right-panel" :class="{ visible: panelsVisible }">
        <WaterLevelChart class="panel-card-flex" />
        <LoadChart class="panel-card-flex" />
        <WarningPanel class="panel-card-shrink" />
      </div>

      <!-- 右侧边缘展开/收起按钮 -->
      <button
        class="toggle-btn"
        :class="{ active: panelsVisible }"
        @click="panelsVisible = !panelsVisible"
        :title="panelsVisible ? '收起面板' : '展开面板'"
      >
        <span class="toggle-text">{{ panelsVisible ? '收起面板' : '展开面板' }}</span>
        <span class="toggle-arrow">{{ panelsVisible ? '◀' : '▶' }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: rgba(6, 20, 42, 0.88);
  backdrop-filter: blur(16px);
}

.home-body {
  position: relative;
  flex: 1;
  overflow: hidden;
}

/* ===== 全屏地图背景 ===== */
.map-background {
  position: absolute;
  inset: 0;
  z-index: 0;
}

/* ===== 侧边面板（滑入/滑出） ===== */
.side-panel {
  position: absolute;
  top: 8px;
  bottom: 8px;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
  width: 24%;
  transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1),
              right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.left-panel {
  left: calc(-24% - 12px);
}

.left-panel.visible {
  left: 12px;
}

.right-panel {
  right: calc(-24% - 12px);
}

.right-panel.visible {
  right: 12px;
}

/* ===== 面板内卡片 ===== */
.panel-card-flex {
  flex: 1;
  min-height: 0;
  min-width: 0;
  width: 100%;
}

.panel-card-shrink {
  flex-shrink: 0;
  width: 100%;
}

/* ===== 右侧边缘展开/收起按钮 ===== */
.toggle-btn {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  width: 24px;
  height: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: rgba(6, 30, 70, 0.55);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(50, 150, 255, 0.15);
  border-right: none;
  border-radius: 4px 0 0 4px;
  cursor: pointer;
  padding: 8px 0;
  color: #7a8fa3;
  transition: all 0.3s ease;
  user-select: none;
}

.toggle-btn:hover {
  background: rgba(6, 30, 70, 0.75);
  border-color: rgba(50, 150, 255, 0.3);
  color: #c0c8d4;
}

.toggle-btn.active {
  color: #00d4ff;
  border-color: rgba(0, 175, 255, 0.25);
}

.toggle-text {
  writing-mode: vertical-rl;
  font-size: 12px;
  letter-spacing: 3px;
  color: inherit;
  transition: color 0.3s;
}

.toggle-arrow {
  font-size: 10px;
  color: #00afff;
  line-height: 1;
  transition: transform 0.3s;
}
</style>
