<script setup lang="ts">
import { computed } from 'vue'
import PanelCard from '@/components/common/PanelCard.vue'
import { TECH_BLUE } from '@/utils/chart'
import { formatNumber } from '@/utils/format'
import type { MetricCardData } from '@/types/reservoir'

interface Props {
  cards: MetricCardData[]
}

const props = defineProps<Props>()

// 图标SVG
const iconMap: Record<string, string> = {
  waterLevel: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2L8 8C5 12 4 15 4 17C4 20.3 6.7 22 9 22H15C17.3 22 20 20.3 20 17C20 15 19 12 16 8L12 2Z" stroke="${TECH_BLUE}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  inflow:   `<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M4 12H20M20 12L15 7M20 12L15 17" stroke="#00E5FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  outflow:  `<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M4 12H20M4 12L9 7M4 12L9 17" stroke="#00E5FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  storage:  `<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="2" stroke="${TECH_BLUE}" stroke-width="1.5"/><path d="M4 12H20" stroke="${TECH_BLUE}" stroke-width="1.5"/></svg>`,
}

const getKey = (label: string) => {
  if (label.includes('水位')) return 'waterLevel'
  if (label.includes('入库')) return 'inflow'
  if (label.includes('出库')) return 'outflow'
  if (label.includes('蓄水')) return 'storage'
  return 'waterLevel'
}

const formatChange = computed(() => (c: number) => {
  const sign = c >= 0 ? '+' : ''
  return `${sign}${formatNumber(c, c % 1 === 0 ? 0 : 2)}`
})

const changeColor = (card: MetricCardData) => {
  // 上升为坏且上升，或下降为好且下降 → 红色；反之绿色
  const isRising = card.change > 0
  const shouldWarn = card.isUpBad ? isRising : !isRising
  return shouldWarn ? '#FF6B6B' : '#00FF88'
}
</script>

<template>
  <div class="metric-cards">
    <div v-for="card in cards" :key="card.label" class="metric-card">
      <div class="card-icon" v-html="iconMap[getKey(card.label)]"></div>
      <div class="card-content">
        <div class="card-label">{{ card.label }}</div>
        <div class="card-value">
          {{ formatNumber(card.value, 2) }}
          <span class="card-unit">{{ card.unit }}</span>
        </div>
        <div class="card-change" :style="{ color: changeColor(card) }">
          <span class="change-arrow" :class="{ up: card.change > 0, down: card.change < 0 }">
            {{ card.change > 0 ? '↑' : card.change < 0 ? '↓' : '—' }}
          </span>
          <span>{{ formatChange(card.change) }}</span>
          <span class="change-label">较昨日</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.metric-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(6, 30, 70, 0.7);
  border: 1px solid rgba(50, 150, 255, 0.25);
  border-radius: 10px;
  transition: border-color 0.2s;
}

.metric-card:hover {
  border-color: rgba(var(--tech-blue-rgb), 0.5);
}

.card-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(var(--tech-blue-rgb), 0.08);
  border-radius: 8px;
}

.card-content {
  min-width: 0;
}

.card-label {
  font-size: 12px;
  color: var(--tech-text-secondary);
  margin-bottom: 4px;
}

.card-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--tech-text-primary);
  line-height: 1.2;
}

.card-unit {
  font-size: 12px;
  font-weight: 400;
  color: var(--tech-text-secondary);
  margin-left: 4px;
}

.card-change {
  font-size: 11px;
  margin-top: 2px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.change-arrow {
  font-weight: 600;
  font-size: 13px;
}

.change-arrow.up { transform: none; }
.change-arrow.down { transform: none; }

.change-label {
  color: #5a6d80;
  margin-left: 2px;
}
</style>
