<script setup lang="ts">
import { ref } from 'vue'
import ReservoirMonitorPanel from '@/components/home/ReservoirMonitorPanel.vue'
import PowerStatisticsPanel from '@/components/home/PowerStatisticsPanel.vue'
import BasinMapPanel from '@/components/home/BasinMapPanel.vue'
import WaterLevelChart from '@/components/home/WaterLevelChart.vue'
import LoadChart from '@/components/home/LoadChart.vue'
import WarningPanel from '@/components/home/WarningPanel.vue'
import HomeFooterBar from '@/components/home/HomeFooterBar.vue'

const selectedReservoirId = ref<string | null>(null)

const handleSelectReservoir = (id: string) => {
  selectedReservoirId.value = id
}

const handleClearSelected = () => {
  selectedReservoirId.value = null
}
</script>

<template>
  <div class="home-view">
    <!-- 三栏主体布局 -->
    <div class="home-body">
      <!-- 左侧监控区 -->
      <div class="left-panel">
        <ReservoirMonitorPanel
          class="panel-card-flex"
          @select-reservoir="handleSelectReservoir"
        />
        <PowerStatisticsPanel class="panel-card-flex" />
      </div>

      <!-- 中部 GIS 地图区 -->
      <div class="center-panel">
        <BasinMapPanel
          :selected-id="selectedReservoirId"
          @select-reservoir="handleSelectReservoir"
          @clear-selected="handleClearSelected"
        />
      </div>

      <!-- 右侧分析区 -->
      <div class="right-panel">
        <WaterLevelChart class="panel-card-flex" />
        <LoadChart class="panel-card-flex" />
        <WarningPanel class="panel-card-shrink" />
      </div>
    </div>

    <!-- 底部状态栏 -->
    <HomeFooterBar />
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.home-body {
  display: flex;
  flex: 1;
  gap: 8px;
  padding: 8px 12px 0;
  min-height: 0;
  overflow: hidden;
}

.left-panel {
  width: 24%;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
}

.center-panel {
  flex: 1;
  min-width: 0;
  display: flex;
}

.right-panel {
  width: 24%;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
}

/* 左右面板内的卡片均分高度 */
.panel-card-flex {
  flex: 1;
  min-height: 0;
  min-width: 0;
  width: 100%;
}

/* 预警卡片自适应内容高度 */
.panel-card-shrink {
  flex-shrink: 0;
  width: 100%;
}
</style>