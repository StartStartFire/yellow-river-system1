<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import ReservoirSidebar from '@/components/basic-data/ReservoirSidebar.vue'
import SectionChart from '@/components/chart/ReservoirSectionGraph.vue'
import BaseInfoPanel from '@/components/basic-data/BaseInfoPanel.vue'
import ProcessChart from '@/components/basic-data/ProcessChart.vue'
import EngineeringInfo from '@/components/basic-data/EngineeringInfo.vue'

import {
  getSection,
  getBaseInfo,
  getProcessData,
  getEngineeringInfo,
} from '@/mock/basicData'

// 当前选中的水库（默认龙羊峡）
const selectedId = ref('longyangxia')

// 左侧列表折叠状态
const sidebarCollapsed = ref(false)

// 断面图数据
const section = computed(() => getSection(selectedId.value).data)

// 基础信息数据
const baseInfoGroups = computed(() => getBaseInfo(selectedId.value).data)

// 水情过程数据
const processData = computed(() => {
  const data = getProcessData(selectedId.value).data
  return {
    xAxis: data.dates,
    series: [
      { name: '水位', data: data.levels },
      { name: '入库流量', data: data.inflows },
      { name: '出库流量', data: data.outflows },
    ],
  }
})

// 工情信息数据
const engineeringInfo = computed(() => getEngineeringInfo(selectedId.value).data)

// 二级标签页
const activeTab = ref('section') // section | baseinfo | process | engineering

// 切换水库时重置到断面标签
watch(selectedId, () => {
  activeTab.value = 'section'
})

const tabList = [
  { key: 'section', label: '水库断面' },
  { key: 'baseinfo', label: '基础信息' },
  { key: 'process', label: '水情过程' },
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
    <!-- 左侧水库列表 -->
    <ReservoirSidebar
      :selected-id="selectedId"
      :collapsed="sidebarCollapsed"
      @select="handleSelectReservoir"
      @toggle="handleToggleSidebar"
    />

    <!-- 右侧详情区 -->
    <div class="detail-panel">
      <!-- 二级标签页 -->
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

      <!-- 标签页内容 -->
      <div class="tab-content">
        <!-- 基础信息 -->
        <div v-if="activeTab === 'baseinfo'" class="tab-page">
          <BaseInfoPanel :groups="baseInfoGroups" />
        </div>

        <!-- 水库断面 -->
        <div v-if="activeTab === 'section'" class="tab-page">
          <SectionChart :section="section" />
        </div>

        <!-- 水情过程 -->
        <div v-if="activeTab === 'process'" class="tab-page">
          <ProcessChart
            :x-axis="processData.xAxis"
            :series="processData.series"
          />
        </div>

        <!-- 工情信息 -->
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
  gap: 8px;
  padding: 8px 12px 0;
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
  gap: 2px;
  flex-shrink: 0;
}

.tab-btn {
  background: none;
  border: 1px solid rgba(50, 150, 255, 0.2);
  color: #7a8fa3;
  font-size: 13px;
  padding: 6px 20px;
  cursor: pointer;
  border-radius: 6px 6px 0 0;
  transition: all 0.2s;
  position: relative;
}

.tab-btn:hover {
  color: #c0c8d4;
  border-color: rgba(50, 150, 255, 0.35);
}

.tab-btn.active {
  color: #00d4ff;
  border-color: rgba(0, 175, 255, 0.5);
  background: rgba(0, 175, 255, 0.08);
  font-weight: 500;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 1px;
  background: rgba(0, 175, 255, 0.08);
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
