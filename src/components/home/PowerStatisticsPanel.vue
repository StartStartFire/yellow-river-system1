<script setup lang="ts">
import PanelCard from '@/components/common/PanelCard.vue'
import { powerStatistics } from '@/mock/home'
import { formatPower } from '@/utils/format'

const statsData = powerStatistics.data
</script>

<template>
  <PanelCard title="发电统计" unit="单位：万kW·h">
    <table class="power-table">
      <thead>
        <tr>
          <th>水库名称</th>
          <th class="text-right">日发电量</th>
          <th class="text-right">月发电量</th>
          <th class="text-right">年发电量</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in statsData" :key="item.reservoirName"
          :class="{ 'total-row': item.reservoirName === '合计' }">
          <td>{{ item.reservoirName }}</td>
          <td class="text-right value-cell">{{ formatPower(item.dailyPower) }}</td>
          <td class="text-right value-cell">{{ formatPower(item.monthlyPower) }}</td>
          <td class="text-right value-cell">{{ formatPower(item.yearlyPower) }}</td>
        </tr>
      </tbody>
    </table>
  </PanelCard>
</template>

<style scoped>
.power-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.power-table thead th {
  color: var(--tech-text-secondary);
  font-weight: 500;
  padding: 8px 6px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.25);
}

.power-table tbody td {
  padding: 7px 6px;
  color: var(--tech-text-regular);
  border-bottom: 1px solid rgba(50, 150, 255, 0.1);
}

.power-table tbody tr:hover {
  background: rgba(var(--tech-blue-rgb), 0.06);
}

.value-cell {
  font-family: 'DIN Alternate', 'Roboto Mono', monospace;
  color: var(--tech-cyan);
}

.total-row td {
  font-weight: 700;
  color: var(--tech-blue);
  border-top: 1px solid rgba(var(--tech-blue-rgb), 0.4);
}

.total-row .value-cell {
  color: var(--tech-cyan-light);
}
</style>
