<script setup lang="ts">
/**
 * CaseLibraryView — 案例库页面
 *
 * 拆分后的页面级容器，仅持有页面级状态与各子组件的事件协调：
 * - selectedCaseId / activeTab / isFavorited / filters
 * - filteredCases / currentCase / selectedCase computed
 * - 路由跳转（handleCompare / handleReproduce）
 *
 * 视图拆分到子组件：
 * - CaseFilterBar       顶部筛选区
 * - CaseListPanel       左侧案例列表
 * - CaseDetailPanel     右侧详情容器（内部使用 CaseMetricsSection）
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import CaseFilterBar, { type CaseFilters } from '@/components/case-library/CaseFilterBar.vue'
import CaseListPanel from '@/components/case-library/CaseListPanel.vue'
import CaseDetailPanel from '@/components/case-library/CaseDetailPanel.vue'
import { caseList, caseDetail } from '@/mock/caseLibrary'

const router = useRouter()

const selectedCaseId = ref('case-2024-flood-001')
const activeTab = ref('config-summary')
const isFavorited = ref(false)

const filters = ref<CaseFilters>({
  dateRange: [],
  caseType: 'all',
  reservoir: 'all',
  keyword: '',
})

const filteredCases = computed(() => {
  return caseList.data.filter(c => {
    if (filters.value.caseType !== 'all' && !c.caseType.includes(filters.value.caseType)) return false
    if (filters.value.reservoir !== 'all' && !c.reservoirs.includes(filters.value.reservoir)) return false
    if (filters.value.keyword && !c.title.includes(filters.value.keyword) && !c.summary.includes(filters.value.keyword)) return false
    return true
  })
})

const currentCase = computed(() => {
  return caseDetail.data[selectedCaseId.value as keyof typeof caseDetail.data]
})

const handleSelectCase = (id: string) => {
  selectedCaseId.value = id
  activeTab.value = 'config-summary'
  isFavorited.value = false
}

const handleReset = () => {
  filters.value = {
    dateRange: [],
    caseType: 'all',
    reservoir: 'all',
    keyword: '',
  }
}

const handleFavorite = () => {
  isFavorited.value = !isFavorited.value
  ElMessage.success(isFavorited.value ? '已收藏' : '已取消收藏')
}

const handleExport = () => {
  ElMessage.info('当前为前端原型，暂不支持真实报告导出')
}

const handleViewReport = () => {
  ElMessage.info('当前为前端原型，暂不支持查看详细报告')
}

const handleCompare = () => {
  router.push('/evaluation-decision')
}

const handleReproduce = () => {
  router.push('/model-config/model-data')
}

const handleTabChange = (tab: string) => {
  activeTab.value = tab
}
</script>

<template>
  <div class="case-library-view">
    <!-- 顶部筛选区 -->
    <CaseFilterBar
      v-model:filters="filters"
      @reset="handleReset"
    />

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧案例列表 -->
      <CaseListPanel
        :cases="filteredCases"
        :selected-case-id="selectedCaseId"
        :total="filteredCases.length"
        :is-favorited="isFavorited"
        @select="handleSelectCase"
        @favorite="handleFavorite"
      />

      <!-- 右侧案例详情 -->
      <CaseDetailPanel
        :case-data="currentCase"
        :active-tab="activeTab"
        :is-favorited="isFavorited"
        @favorite="handleFavorite"
        @export="handleExport"
        @view-report="handleViewReport"
        @compare="handleCompare"
        @reproduce="handleReproduce"
        @tab-change="handleTabChange"
      />
    </div>
  </div>
</template>

<style scoped>
.case-library-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0;
  gap: 0;
  background: rgba(var(--tech-bg-rgb), 0.92);
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  gap: 0;
  min-height: 0;
}
</style>
