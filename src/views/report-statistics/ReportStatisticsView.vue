<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  yearOptions,
  monthOptions,
  reservoirOptions,
  monthlyOperationData,
  monthlyEconomicData,
  monthlyPowerData,
  yearlySummaryData,
} from '@/mock/reportStatistics'
import { formatNumber, formatThousands } from '@/utils/format'

// 2 位小数格式化（含空值回退）
const fmt = (v: number | null | undefined) => formatNumber(v, 2)
// 千分位整数格式化
const fmtInt = (v: number | null | undefined) => formatThousands(v, 0)

const reportType = ref<'monthly' | 'yearly'>('monthly')
const selectedYear = ref('2025')
const selectedMonth = ref('5')
const selectedReservoir = ref('all')

const showMonthFilter = computed(() => reportType.value === 'monthly')

const handleQuery = () => {
  ElMessage.success('查询条件已更新')
}

const handleReset = () => {
  reportType.value = 'monthly'
  selectedYear.value = '2025'
  selectedMonth.value = '5'
  selectedReservoir.value = 'all'
  ElMessage.success('已重置为默认条件')
}

const handleExport = () => {
  ElMessage.info('当前为前端原型，暂不支持真实导出')
}

const filteredOperationData = computed(() => {
  let data = monthlyOperationData.data
  if (selectedReservoir.value !== 'all') {
    const nameMap: Record<string, string> = {
      longyangxia: '龙羊峡水库',
      liujiaxia: '刘家峡水库',
      qingtongxia: '青铜峡水库',
      maerdang: '玛尔挡水库',
      laxiwa: '拉西瓦水库',
    }
    data = data.filter(r => r.reservoirName === nameMap[selectedReservoir.value])
  }
  return data
})

const filteredEconomicData = computed(() => {
  let data = monthlyEconomicData.data
  if (selectedReservoir.value !== 'all') {
    const nameMap: Record<string, string> = {
      longyangxia: '龙羊峡水库',
      liujiaxia: '刘家峡水库',
      qingtongxia: '青铜峡水库',
      maerdang: '玛尔挡水库',
      laxiwa: '拉西瓦水库',
    }
    data = data.filter(r => r.reservoirName === nameMap[selectedReservoir.value])
  }
  return data
})

const filteredPowerData = computed(() => {
  let data = monthlyPowerData.data
  if (selectedReservoir.value !== 'all') {
    const nameMap: Record<string, string> = {
      longyangxia: '龙羊峡水库',
      liujiaxia: '刘家峡水库',
      qingtongxia: '青铜峡水库',
      maerdang: '玛尔挡水库',
      laxiwa: '拉西瓦水库',
    }
    data = data.filter(r => r.reservoirName === nameMap[selectedReservoir.value])
  }
  return data
})

const filteredYearlyData = computed(() => {
  let data = yearlySummaryData.data
  if (selectedReservoir.value !== 'all') {
    const nameMap: Record<string, string> = {
      longyangxia: '龙羊峡水库',
      liujiaxia: '刘家峡水库',
      qingtongxia: '青铜峡水库',
      maerdang: '玛尔挡水库',
      laxiwa: '拉西瓦水库',
    }
    data = data.filter(r => r.reservoirName === nameMap[selectedReservoir.value])
  }
  return data
})

const getAssessmentColor = (result: string) => {
  return result === '达标' ? '#00ff88' : '#ff4d4f'
}
</script>

<template>
  <div class="report-statistics-view">
    <!-- 筛选操作区 -->
    <div class="filter-bar">
      <div class="filter-items">
        <!-- 报表类型切换 -->
        <div class="filter-item">
          <label class="filter-label">报表类型</label>
          <div class="type-switcher">
            <button
              class="type-btn"
              :class="{ active: reportType === 'monthly' }"
              @click="reportType = 'monthly'"
            >
              逐月报表
            </button>
            <button
              class="type-btn"
              :class="{ active: reportType === 'yearly' }"
              @click="reportType = 'yearly'"
            >
              逐年报表
            </button>
          </div>
        </div>

        <!-- 年份 -->
        <div class="filter-item">
          <label class="filter-label">年份</label>
          <el-select v-model="selectedYear" style="width: 100px;">
            <el-option v-for="item in yearOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </div>

        <!-- 月份（仅逐月报表显示） -->
        <div class="filter-item" v-if="showMonthFilter">
          <label class="filter-label">月份</label>
          <el-select v-model="selectedMonth" style="width: 80px;">
            <el-option v-for="item in monthOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </div>

        <!-- 水库筛选 -->
        <div class="filter-item">
          <label class="filter-label">水库筛选</label>
          <el-select v-model="selectedReservoir" style="width: 140px;">
            <el-option v-for="item in reservoirOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </div>
      </div>

      <div class="filter-actions">
        <button class="btn-primary" @click="handleQuery">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          查询
        </button>
        <button class="btn-secondary" @click="handleReset">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          重置
        </button>
        <button class="btn-export" @click="handleExport">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          导出报表
        </button>
      </div>
    </div>

    <!-- 报表内容区 -->
    <div class="report-content">
      <!-- 逐月报表 -->
      <template v-if="reportType === 'monthly'">
        <!-- 表块一：水库调度运行情况 -->
        <div class="report-section">
          <h3 class="section-title">一、水库调度运行情况</h3>
          <div class="table-wrapper">
            <table class="report-table">
              <thead>
                <tr>
                  <th rowspan="2" class="fixed-col">水库名称</th>
                  <th colspan="4">水位（m）</th>
                  <th colspan="4">库容（亿m³）</th>
                  <th colspan="2">入库水量（亿m³）</th>
                  <th colspan="6">出库水量（亿m³）</th>
                  <th colspan="2">弃水量（亿m³）</th>
                </tr>
                <tr>
                  <th>期初水位</th>
                  <th>期末水位</th>
                  <th>最高水位</th>
                  <th>最低水位</th>
                  <th>期初库容</th>
                  <th>期末库容</th>
                  <th>最大库容</th>
                  <th>最小库容</th>
                  <th>本月</th>
                  <th>年累计</th>
                  <th colspan="2">总出库</th>
                  <th colspan="2">发电放水</th>
                  <th colspan="2">下泄生态水量</th>
                  <th>本月</th>
                  <th>年累计</th>
                </tr>
                <tr>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th></th>
                  <th>本月</th>
                  <th>年累计</th>
                  <th>本月</th>
                  <th>年累计</th>
                  <th>本月</th>
                  <th>年累计</th>
                  <th></th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in filteredOperationData" :key="row.reservoirName" :class="{ 'total-row': row.reservoirName === '合计' }">
                  <td class="fixed-col name-cell">{{ row.reservoirName }}</td>
                  <td>{{ fmt(row.initialLevel) }}</td>
                  <td>{{ fmt(row.finalLevel) }}</td>
                  <td>{{ fmt(row.maxLevel) }}</td>
                  <td>{{ fmt(row.minLevel) }}</td>
                  <td>{{ fmt(row.initialStorage) }}</td>
                  <td>{{ fmt(row.finalStorage) }}</td>
                  <td>{{ fmt(row.maxStorage) }}</td>
                  <td>{{ fmt(row.minStorage) }}</td>
                  <td>{{ fmt(row.inflowMonth) }}</td>
                  <td>{{ fmt(row.inflowYear) }}</td>
                  <td>{{ fmt(row.totalOutflowMonth) }}</td>
                  <td>{{ fmt(row.totalOutflowYear) }}</td>
                  <td>{{ fmt(row.powerReleaseMonth) }}</td>
                  <td>{{ fmt(row.powerReleaseYear) }}</td>
                  <td>{{ fmt(row.ecologicalReleaseMonth) }}</td>
                  <td>{{ fmt(row.ecologicalReleaseYear) }}</td>
                  <td>{{ fmt(row.abandonedWaterMonth) }}</td>
                  <td>{{ fmt(row.abandonedWaterYear) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 表块二：水库运行主要经济指标 -->
        <div class="report-section">
          <h3 class="section-title">二、水库运行主要经济指标</h3>
          <div class="table-wrapper">
            <table class="report-table">
              <thead>
                <tr>
                  <th rowspan="2" class="fixed-col">水库名称</th>
                  <th colspan="3">装机容量（万kW）</th>
                  <th>年设计发电量（亿kW·h）</th>
                  <th colspan="2">水库年径流量（亿m³）</th>
                  <th colspan="2">水库年利用水量（亿m³）</th>
                  <th colspan="2">水库利用率（%）</th>
                  <th colspan="2">供水量（亿m³）</th>
                  <th colspan="2">防洪库容（亿m³）</th>
                  <th>防洪标准（年一遇）</th>
                </tr>
                <tr>
                  <th>总装机</th>
                  <th>已投产</th>
                  <th>本月新增</th>
                  <th></th>
                  <th>多年平均</th>
                  <th>本年累计</th>
                  <th>本月</th>
                  <th>年累计</th>
                  <th>本月</th>
                  <th>年累计</th>
                  <th>本月</th>
                  <th>年累计</th>
                  <th>设计</th>
                  <th>当前</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in filteredEconomicData" :key="row.reservoirName">
                  <td class="fixed-col name-cell">{{ row.reservoirName }}</td>
                  <td>{{ row.installedCapacityTotal }}</td>
                  <td>{{ row.installedCapacityInService }}</td>
                  <td>{{ row.installedCapacityNew }}</td>
                  <td>{{ fmt(row.annualDesignPower) }}</td>
                  <td>{{ row.averageRunoff }}</td>
                  <td>{{ fmt(row.currentYearRunoff) }}</td>
                  <td>{{ fmt(row.waterUseMonth) }}</td>
                  <td>{{ fmt(row.waterUseYear) }}</td>
                  <td>{{ fmt(row.utilizationRateMonth) }}</td>
                  <td>{{ fmt(row.utilizationRateYear) }}</td>
                  <td>{{ fmt(row.waterSupplyMonth) }}</td>
                  <td>{{ fmt(row.waterSupplyYear) }}</td>
                  <td>{{ fmt(row.floodStorageDesign) }}</td>
                  <td>{{ fmt(row.floodStorageCurrent) }}</td>
                  <td>{{ fmtInt(row.floodStandard) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- 表块三：发电量及发电考核情况 -->
        <div class="report-section">
          <h3 class="section-title">三、发电量及发电考核情况</h3>
          <div class="table-wrapper">
            <table class="report-table">
              <thead>
                <tr>
                  <th rowspan="2" class="fixed-col">水库名称</th>
                  <th colspan="3">发电量（亿kW·h）</th>
                  <th colspan="2">平均耗水率（m³/kW·h）</th>
                  <th colspan="2">考核指标</th>
                  <th colspan="2">上网电量（亿kW·h）</th>
                  <th colspan="2">容量利用小时（h）</th>
                  <th>备注</th>
                </tr>
                <tr>
                  <th>本月</th>
                  <th>年累计</th>
                  <th>完成年计划（%）</th>
                  <th>本月</th>
                  <th>年累计</th>
                  <th>耗水率考核值</th>
                  <th>考核结果</th>
                  <th>本月</th>
                  <th>年累计</th>
                  <th>本月</th>
                  <th>年累计</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in filteredPowerData" :key="row.reservoirName">
                  <td class="fixed-col name-cell">{{ row.reservoirName }}</td>
                  <td>{{ fmt(row.powerMonth) }}</td>
                  <td>{{ fmt(row.powerYear) }}</td>
                  <td>{{ fmt(row.planCompletionRate) }}%</td>
                  <td>{{ fmt(row.waterConsumptionMonth) }}</td>
                  <td>{{ fmt(row.waterConsumptionYear) }}</td>
                  <td>≤ {{ fmt(row.waterConsumptionAssessment) }}</td>
                  <td>
                    <span class="assessment-badge" :style="{ color: getAssessmentColor(row.assessmentResult), borderColor: getAssessmentColor(row.assessmentResult) + '40' }">
                      {{ row.assessmentResult }}
                    </span>
                  </td>
                  <td>{{ fmt(row.gridPowerMonth) }}</td>
                  <td>{{ fmt(row.gridPowerYear) }}</td>
                  <td>{{ row.utilizationHoursMonth }}</td>
                  <td>{{ row.utilizationHoursYear }}</td>
                  <td>{{ row.remark }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

      <!-- 逐年报表 -->
      <template v-else>
        <div class="report-section">
          <h3 class="section-title">年度汇总统计表（{{ selectedYear }}年）</h3>
          <div class="table-wrapper">
            <table class="report-table">
              <thead>
                <tr>
                  <th rowspan="2" class="fixed-col">水库名称</th>
                  <th colspan="5">水位（m）</th>
                  <th colspan="5">水量（亿m³）</th>
                  <th rowspan="2">年发电量<br>（亿kW·h）</th>
                  <th rowspan="2">年平均耗水率<br>（m³/kW·h）</th>
                  <th rowspan="2">年平均出力<br>（万kW）</th>
                  <th rowspan="2">年利用小时<br>（h）</th>
                  <th rowspan="2">考核结果</th>
                </tr>
                <tr>
                  <th>年初上游水位</th>
                  <th>年末上游水位</th>
                  <th>年平均上游水位</th>
                  <th>年最高水位</th>
                  <th>年最低水位</th>
                  <th>年总入库水量</th>
                  <th>年总出库水量</th>
                  <th>年发电水量</th>
                  <th>年弃水量</th>
                  <th>年供水量</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in filteredYearlyData" :key="row.reservoirName">
                  <td class="fixed-col name-cell">{{ row.reservoirName }}</td>
                  <td>{{ fmt(row.initialYearLevel) }}</td>
                  <td>{{ fmt(row.finalYearLevel) }}</td>
                  <td>{{ fmt(row.averageYearLevel) }}</td>
                  <td>{{ fmt(row.maxYearLevel) }}</td>
                  <td>{{ fmt(row.minYearLevel) }}</td>
                  <td>{{ fmt(row.totalYearInflow) }}</td>
                  <td>{{ fmt(row.totalYearOutflow) }}</td>
                  <td>{{ fmt(row.yearPowerWater) }}</td>
                  <td>{{ fmt(row.yearAbandonedWater) }}</td>
                  <td>{{ fmt(row.yearWaterSupply) }}</td>
                  <td>{{ fmt(row.yearPower) }}</td>
                  <td>{{ fmt(row.yearAverageConsumption) }}</td>
                  <td>{{ fmt(row.yearAverageOutput) }}</td>
                  <td>{{ fmtInt(row.yearUtilizationHours) }}</td>
                  <td>
                    <span class="assessment-badge" :style="{ color: getAssessmentColor(row.assessmentResult), borderColor: getAssessmentColor(row.assessmentResult) + '40' }">
                      {{ row.assessmentResult }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<style scoped>
.report-statistics-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0;
  gap: 0;
  background: rgba(var(--tech-bg-rgb), 0.92);
  overflow: hidden;
}

/* 筛选区 */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  border-radius: 0;
  flex-shrink: 0;
}

.filter-items {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 12px;
  color: var(--tech-text-secondary);
  white-space: nowrap;
}

.type-switcher {
  display: flex;
  background: transparent;
  border: none;
  border-radius: 0;
  overflow: hidden;
}

.type-btn {
  padding: 6px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--tech-text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.type-btn:hover {
  color: var(--tech-text-primary);
}

.type-btn.active {
  background: transparent;
  color: var(--tech-cyan);
  border-bottom-color: rgba(var(--tech-cyan-rgb), 0.6);
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: linear-gradient(135deg, var(--tech-blue) 0%, var(--tech-cyan) 100%);
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--tech-cyan) 0%, var(--tech-cyan-light) 100%);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: rgba(50, 150, 255, 0.1);
  border: 1px solid rgba(50, 150, 255, 0.3);
  border-radius: 6px;
  color: var(--tech-cyan);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  background: rgba(50, 150, 255, 0.2);
  border-color: rgba(50, 150, 255, 0.5);
}

.btn-export {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: linear-gradient(135deg, #00b96b 0%, #00d48a 100%);
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-export:hover {
  background: linear-gradient(135deg, #00d48a 0%, #00f0a0 100%);
}

/* 报表内容区 */
.report-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0;
}

.report-content::-webkit-scrollbar {
  width: 6px;
}

.report-content::-webkit-scrollbar-track {
  background: rgba(50, 150, 255, 0.05);
  border-radius: 3px;
}

.report-content::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.2);
  border-radius: 3px;
}

/* 报表区块 */
.report-section {
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  border-radius: 0;
  overflow: hidden;
}

.section-title {
  padding: 12px 16px;
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--tech-cyan);
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  background: transparent;
}

.table-wrapper {
  overflow-x: auto;
}

.table-wrapper::-webkit-scrollbar {
  height: 4px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: rgba(50, 150, 255, 0.05);
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.2);
  border-radius: 2px;
}

/* 表格样式 */
.report-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.report-table th,
.report-table td {
  padding: 8px 12px;
  border: 1px solid rgba(50, 150, 255, 0.12);
  text-align: center;
  white-space: nowrap;
}

.report-table thead th {
  background: rgba(10, 25, 41, 0.6);
  color: var(--tech-text-regular);
  font-weight: 500;
  font-size: 11px;
}

.report-table tbody tr {
  transition: background 0.2s;
}

.report-table tbody tr:hover {
  background: rgba(var(--tech-blue-rgb), 0.05);
}

.report-table tbody td {
  color: var(--tech-text-primary);
}

.fixed-col {
  position: sticky;
  left: 0;
  background: rgba(10, 25, 41, 0.9);
  z-index: 1;
}

.name-cell {
  text-align: left;
  font-weight: 500;
  color: var(--tech-text-primary);
}

.total-row {
  background: rgba(var(--tech-blue-rgb), 0.05);
}

.total-row td {
  font-weight: 600;
  color: var(--tech-cyan);
}

.assessment-badge {
  display: inline-block;
  padding: 2px 8px;
  border: 1px solid;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

</style>
