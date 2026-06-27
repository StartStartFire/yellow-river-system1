<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import ReservoirSidebar from '@/components/basic-data/ReservoirSidebar.vue'
import SectionChart from '@/components/chart/ReservoirSectionGraph.vue'
import BaseInfoPanel from '@/components/basic-data/BaseInfoPanel.vue'
import EngineeringInfo from '@/components/basic-data/EngineeringInfo.vue'
import KeyCurvesPanel from '@/components/basic-data/KeyCurvesPanel.vue'

import {
  getSection,
  getBaseInfo,
  getEngineeringInfo,
  getKeyCurves,
} from '@/mock/basicData'

const selectedId = ref('longyangxia')
const sidebarCollapsed = ref(false)

const section = computed(() => getSection(selectedId.value).data)
const baseInfoGroups = computed(() => getBaseInfo(selectedId.value).data)

const engineeringInfo = computed(() => getEngineeringInfo(selectedId.value).data)
const keyCurves = computed(() => getKeyCurves(selectedId.value).data)

const activeTab = ref('section')

watch(selectedId, () => {
  activeTab.value = 'section'
})

const tabList = [
  { key: 'section', label: '水库断面' },
  { key: 'baseinfo', label: '基础信息' },
  { key: 'keycurves', label: '关键曲线' },
  { key: 'engineering', label: '工情信息' },
]

const handleSelectReservoir = (id: string) => {
  selectedId.value = id
}

const handleToggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<template>
  <div class="basic-data-view">
    <ReservoirSidebar
      :selected-id="selectedId"
      :collapsed="sidebarCollapsed"
      @select="handleSelectReservoir"
      @toggle="handleToggleSidebar"
    />

    <div class="detail-panel">
      <div class="tabs-bar">
        <button
          v-for="tab in tabList"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'baseinfo'" class="tab-page">
          <BaseInfoPanel :groups="baseInfoGroups" />
        </div>

        <div v-if="activeTab === 'section'" class="tab-page">
          <SectionChart :section="section" />
        </div>

        <div v-if="activeTab === 'keycurves'" class="tab-page">
          <KeyCurvesPanel :curves="keyCurves" />
        </div>

        <div v-if="activeTab === 'engineering'" class="tab-page">
          <EngineeringInfo
            :summary="engineeringInfo.summary"
            :turbines="engineeringInfo.turbines"
            :gates="engineeringInfo.gates"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.basic-data-view {
  display: flex;
  height: 100%;
  gap: 12px;
  padding: 12px;
  overflow: hidden;
}

.detail-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: 12px;
}

.tabs-bar {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  padding: 4px;
  background: rgba(6, 30, 70, 0.45);
  border: 1px solid rgba(50, 150, 255, 0.10);
  backdrop-filter: blur(14px);
  border-radius: 10px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: none;
  color: #7a8fa3;
  font-size: 13px;
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #c0c8d4;
  background: rgba(50, 150, 255, 0.05);
}

.tab-btn.active {
  color: #00d4ff;
  background: rgba(0, 175, 255, 0.1);
  font-weight: 500;
}

.tab-content {
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.tab-page {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
</style>
