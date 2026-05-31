<script setup lang="ts">
import PanelCard from '@/components/common/PanelCard.vue'
import type { BaseInfoGroup } from '@/mock/basicData'

interface Props {
  groups: BaseInfoGroup[]
}

defineProps<Props>()
</script>

<template>
  <div class="base-info-panel">
    <PanelCard
      v-for="group in groups"
      :key="group.title"
      :title="group.title"
      class="info-group-card"
    >
      <div class="info-grid">
        <div v-for="item in group.items" :key="item.key" class="info-row">
          <span class="info-key">{{ item.key }}</span>
          <span class="info-val">{{ item.value }}</span>
        </div>
      </div>
    </PanelCard>
  </div>
</template>

<style scoped>
.base-info-panel {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.info-group-card {
  min-width: 0;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid rgba(50, 150, 255, 0.08);
}

.info-key {
  font-size: 12px;
  color: #7a8fa3;
  white-space: nowrap;
}

.info-val {
  font-size: 12px;
  color: #c0c8d4;
  text-align: right;
  font-family: 'DIN Alternate', 'Roboto Mono', monospace;
}
</style>
