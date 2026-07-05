<script setup lang="ts">
import PanelCard from '@/components/common/PanelCard.vue'
import StatusTag from '@/components/common/StatusTag.vue'
import type { TurbineItem, GateItem, EngineeringSummary } from '@/types/reservoir'

interface Props {
  summary: EngineeringSummary
  turbines: TurbineItem[]
  gates: GateItem[]
}

defineProps<Props>()

// 机组/闸门状态映射（用于 StatusTag 自定义模式）
const statusMap: Record<string, { label: string; color: string }> = {
  running:     { label: '运行', color: '#00FF88' },
  stop:        { label: '停机', color: '#8aa0b8' },
  maintenance: { label: '检修', color: '#f0a020' },
}
</script>

<template>
  <div class="engineering-info">
    <!-- 工情摘要卡片 -->
    <div class="summary-bar">
      <div class="summary-item">
        <span class="summary-label">机组总数</span>
        <span class="summary-value">{{ summary.turbineTotal }} 台</span>
      </div>
      <div class="summary-divider"></div>
      <div class="summary-item">
        <span class="summary-label">运行中</span>
        <span class="summary-value" style="color: #00FF88;">{{ summary.turbineRunning }} 台</span>
      </div>
      <div class="summary-divider"></div>
      <div class="summary-item">
        <span class="summary-label">闸门总数</span>
        <span class="summary-value">{{ summary.gateTotal }} 扇</span>
      </div>
      <div class="summary-divider"></div>
      <div class="summary-item">
        <span class="summary-label">开启数</span>
        <span class="summary-value" style="color: var(--tech-blue);">{{ summary.gateOpen }} 扇</span>
      </div>
      <div class="summary-divider"></div>
      <div class="summary-item">
        <span class="summary-label">当前总出力</span>
        <span class="summary-value">{{ (summary.totalOutput / 1000).toFixed(0) }} MW</span>
      </div>
    </div>

    <!-- 机组运行表格 -->
    <PanelCard title="机组运行状态" class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>机组编号</th>
            <th>名称</th>
            <th>状态</th>
            <th>出力 (kW)</th>
            <th>发电流量 (m³/s)</th>
            <th>闸门开度</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in turbines" :key="t.id">
            <td class="cell-id">{{ t.id }}</td>
            <td>{{ t.name }}</td>
            <td>
              <StatusTag
                :label="statusMap[t.status].label"
                :color="statusMap[t.status].color"
              />
            </td>
            <td class="cell-num">{{ t.output }}</td>
            <td class="cell-num">{{ t.flow }}</td>
            <td class="cell-gate">
              <div class="gate-bar-bg">
                <div class="gate-bar-fill" :style="{ width: t.gateOpen + '%', background: t.gateOpen > 0 ? 'var(--tech-blue)' : '#2a3a4a' }"></div>
              </div>
              <span class="gate-pct">{{ t.gateOpen }}%</span>
            </td>
          </tr>
        </tbody>
      </table>
    </PanelCard>

    <!-- 闸门开度信息 -->
    <PanelCard title="泄洪闸门状态" class="table-card">
      <table class="data-table">
        <thead>
          <tr>
            <th>闸门编号</th>
            <th>名称</th>
            <th>开度 (%)</th>
            <th>泄洪流量 (m³/s)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in gates" :key="g.id">
            <td class="cell-id">{{ g.id }}</td>
            <td>{{ g.name }}</td>
            <td class="cell-num">
              <span v-if="g.openPercentage > 0" style="color: var(--tech-blue); font-weight: 600;">{{ g.openPercentage }}</span>
              <span v-else style="color: #5a6d80;">关闭</span>
            </td>
            <td class="cell-num">{{ g.dischargeFlow }}</td>
          </tr>
        </tbody>
      </table>
    </PanelCard>
  </div>
</template>

<style scoped>
.engineering-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
}

.summary-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  background: rgba(var(--tech-blue-rgb), 0.05);
  border: 1px solid rgba(50, 150, 255, 0.2);
  border-radius: 8px;
}

.summary-item {
  display: flex;
  align-items: baseline;
  gap: 6px;
  white-space: nowrap;
}

.summary-label {
  font-size: 11px;
  color: var(--tech-text-secondary);
}

.summary-value {
  font-size: 15px;
  font-weight: 700;
  font-family: 'DIN Alternate', 'Roboto Mono', monospace;
}

.summary-divider {
  width: 1px;
  height: 18px;
  background: rgba(50, 150, 255, 0.2);
}

.table-card {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.table-card .panel-body {
  overflow: auto;
  flex: 1;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.data-table th {
  text-align: left;
  padding: 8px 12px;
  color: var(--tech-text-secondary);
  font-weight: 500;
  font-size: 11px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  position: sticky;
  top: 0;
  background: rgba(6, 30, 70, 0.35);
}

.data-table td {
  padding: 6px 12px;
  color: var(--tech-text-regular);
  border-bottom: 1px solid rgba(50, 150, 255, 0.06);
}

.data-table tbody tr:hover {
  background: rgba(var(--tech-blue-rgb), 0.05);
}

.cell-id {
  font-family: 'Roboto Mono', monospace;
  color: var(--tech-blue);
  font-size: 11px;
}

.cell-num {
  font-family: 'DIN Alternate', 'Roboto Mono', monospace;
  text-align: right;
}

.cell-gate {
  display: flex;
  align-items: center;
  gap: 8px;
}

.gate-bar-bg {
  flex: 1;
  height: 6px;
  background: rgba(50, 150, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  min-width: 40px;
}

.gate-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.gate-pct {
  font-size: 11px;
  font-family: 'Roboto Mono', monospace;
  color: var(--tech-text-secondary);
  min-width: 32px;
  text-align: right;
}
</style>
