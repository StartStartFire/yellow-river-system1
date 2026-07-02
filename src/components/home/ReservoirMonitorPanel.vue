<script setup lang="ts">
import PanelCard from '@/components/common/PanelCard.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import { homeReservoirMonitor } from '@/mock/home'

const monitorData = homeReservoirMonitor.data

const emit = defineEmits<{
  (e: 'select-reservoir', id: string): void
}>()
</script>

<template>
  <PanelCard title="水情监控">
    <div class="space-y-3">
      <div
        v-for="reservoir in monitorData"
        :key="reservoir.id"
        class="reservoir-block"
        style="padding: 12px;"
      >
        <!-- 水库名称 + 状态 - 名称可点击 -->
        <div class="flex items-center justify-between mb-3">
          <span
            class="text-sm font-semibold text-tech-primary cursor-pointer hover:brightness-125 transition-all"
            @click="emit('select-reservoir', reservoir.id)"
          >
            {{ reservoir.name }}
          </span>
          <StatusTag :status="reservoir.status" />
        </div>
        <!-- 指标网格 -->
        <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-xs">
          <div class="metric-item">
            <span class="metric-label">入库流量</span>
            <span class="metric-value">{{ reservoir.inflow }}</span>
            <span class="metric-unit">m³/s</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">出库流量</span>
            <span class="metric-value">{{ reservoir.outflow }}</span>
            <span class="metric-unit">m³/s</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">坝前水位</span>
            <span class="metric-value">{{ reservoir.forebayLevel }}</span>
            <span class="metric-unit">m</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">尾水位</span>
            <span class="metric-value">{{ reservoir.tailwaterLevel }}</span>
            <span class="metric-unit">m</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">库容</span>
            <span class="metric-value">{{ reservoir.storage }}</span>
            <span class="metric-unit">亿m³</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">机组过流</span>
            <span class="metric-value">{{ reservoir.turbineFlow }}</span>
            <span class="metric-unit">m³/s</span>
          </div>
        </div>
      </div>
    </div>
  </PanelCard>
</template>

<style scoped>
.reservoir-block {
  border-bottom: 1px solid rgba(50, 150, 255, 0.1);
}

.reservoir-block:last-child {
  border-bottom: none;
}

.metric-item {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.metric-label {
  color: #8aa0b8;
  min-width: 52px;
}

.metric-value {
  color: #00d4ff;
  font-weight: 600;
  font-family: 'DIN Alternate', 'Roboto Mono', monospace;
  font-size: 13px;
}

.metric-unit {
  color: #6e8a9e;
  font-size: 11px;
}
</style>