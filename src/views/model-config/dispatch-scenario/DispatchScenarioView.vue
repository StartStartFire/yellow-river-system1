<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import ModelConfigFooter from '@/components/model-config/ModelConfigFooter.vue'
import ScenarioNameRow from '@/components/model-config/dispatch-scenario/ScenarioNameRow.vue'
import ScenarioCard from '@/components/model-config/dispatch-scenario/ScenarioCard.vue'
import ConfirmActionDialog from '@/components/model-config/common/ConfirmActionDialog.vue'
import { useModelConfigStore } from '@/stores/modelConfig'
import { dispatchScenarioCategories } from '@/mock/modelConfig'
import type { DispatchScenarioCategory, DispatchSubOption } from '@/types/model'

// ==================== 弹窗状态 ====================
const saveDialogVisible = ref(false)
const cancelDialogVisible = ref(false)

// ==================== Store ====================
const store = useModelConfigStore()

// ==================== Mock 数据 ====================
const categories = dispatchScenarioCategories as DispatchScenarioCategory[]

// ==================== 状态 ====================
const router = useRouter()

/** 选中的大类ID */
const selectedCategoryId = ref<string>('')

/** 选中的子选项ID */
const selectedSubOptionId = ref<string>('')

/** 方案名称 */
const scenarioName = ref(store.dispatchScenario.scenarioName)

// 查找选中的子选项对象
const selectedSubOption = computed<DispatchSubOption | null>(() => {
  if (!selectedCategoryId.value || !selectedSubOptionId.value) return null
  const cat = categories.find(c => c.id === selectedCategoryId.value)
  if (!cat) return null
  return cat.subOptions.find(s => s.id === selectedSubOptionId.value) || null
})

// 查找选中的大类对象
const selectedCategory = computed<DispatchScenarioCategory | null>(() => {
  if (!selectedCategoryId.value) return null
  return categories.find(c => c.id === selectedCategoryId.value) || null
})

/** 是否可以进入下一步 */
const canNext = computed(() => {
  return selectedCategoryId.value !== '' && selectedSubOptionId.value !== '' && scenarioName.value.trim() !== ''
})

// ==================== 交互 ====================

/** 点击卡片区域选中该大类 */
const handleSelectCategory = (categoryId: string) => {
  selectedCategoryId.value = categoryId
  // 切换大类时清空子选项
  selectedSubOptionId.value = ''
}

/** 选中子选项 */
const handleSelectSubOption = (categoryId: string, subOptionId: string) => {
  selectedCategoryId.value = categoryId
  selectedSubOptionId.value = subOptionId
}

const handleSave = () => {
  saveDialogVisible.value = true
}

const handleCancel = () => {
  cancelDialogVisible.value = true
}

const confirmSave = () => {
  saveDialogVisible.value = false
  if (!canNext.value) {
    ElMessage.warning('请先选择调度场景')
    return
  }
  if (!scenarioName.value.trim()) {
    ElMessage.warning('请输入方案名称')
    return
  }
  // 写入 Store
  store.setDispatchScenario({
    categoryId: selectedCategoryId.value,
    subOptionId: selectedSubOptionId.value,
    scenarioName: scenarioName.value.trim(),
  })
  // 联动调度目标
  store.syncObjectivesFromScenario(selectedSubOptionId.value)
  // 联动模型选择
  store.syncModelFromScenario(selectedCategoryId.value, selectedSubOptionId.value)
  ElMessage.success('调度场景已保存')
}

const confirmCancel = () => {
  cancelDialogVisible.value = false
  selectedCategoryId.value = ''
  selectedSubOptionId.value = ''
  ElMessage.info('已取消，未保存任何更改')
}

const handleNext = () => {
  if (!canNext.value) {
    ElMessage.warning('请先选择调度场景')
    return
  }
  if (!scenarioName.value.trim()) {
    ElMessage.warning('请输入方案名称')
    return
  }
  // 写入 Store
  store.setDispatchScenario({
    categoryId: selectedCategoryId.value,
    subOptionId: selectedSubOptionId.value,
    scenarioName: scenarioName.value.trim(),
  })
  // 联动调度目标
  store.syncObjectivesFromScenario(selectedSubOptionId.value)
  // 联动模型选择
  store.syncModelFromScenario(selectedCategoryId.value, selectedSubOptionId.value)
  // 标记 Step 1 已完成
  store.markStepCompleted(1)
  // 跳转 Step 2
  router.push('/model-config/dispatch-subject')
}

// ==================== 生命周期 ====================
onMounted(() => {
  if (store.dispatchScenario.scenarioName) {
    scenarioName.value = store.dispatchScenario.scenarioName
  }
  if (store.dispatchScenario.categoryId) {
    selectedCategoryId.value = store.dispatchScenario.categoryId
  }
  if (store.dispatchScenario.subOptionId) {
    selectedSubOptionId.value = store.dispatchScenario.subOptionId
  }
})

// ==================== SVG 图标 ====================
const svgIcons: Record<string, string> = {
  calendar: `<svg viewBox="0 0 48 48" fill="none">
    <rect x="6" y="10" width="36" height="30" rx="4" stroke="currentColor" stroke-width="2" fill="none"/>
    <path d="M16 6v8M32 6v8M6 18h36" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <rect x="12" y="24" width="4" height="4" rx="1" fill="currentColor" opacity="0.6"/>
    <rect x="20" y="24" width="4" height="4" rx="1" fill="currentColor" opacity="0.6"/>
    <rect x="28" y="24" width="4" height="4" rx="1" fill="currentColor" opacity="0.6"/>
    <rect x="12" y="32" width="4" height="4" rx="1" fill="currentColor" opacity="0.6"/>
    <rect x="20" y="32" width="4" height="4" rx="1" fill="currentColor" opacity="0.6"/>
    <rect x="28" y="32" width="4" height="4" rx="1" fill="currentColor" opacity="0.6"/>
  </svg>`,
  wave: `<svg viewBox="0 0 48 48" fill="none">
    <path d="M4 28c4-8 8-8 12 0s8 8 12 0 8-8 12 0 8 8 12 0" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" fill="none"/>
    <path d="M4 36c4-8 8-8 12 0s8 8 12 0 8-8 12 0 8 8 12 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.5"/>
    <path d="M4 20c4-8 8-8 12 0s8 8 12 0 8-8 12 0 8 8 12 0" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" fill="none" opacity="0.3"/>
  </svg>`,
  lightning: `<svg viewBox="0 0 48 48" fill="none">
    <path d="M26 4L12 26h10l-2 18 16-24H26l2-16z" stroke="currentColor" stroke-width="2" stroke-linejoin="round" fill="rgba(0,175,255,0.1)"/>
    <path d="M26 4L12 26h10l-2 18 16-24H26l2-16z" stroke="currentColor" stroke-width="2" stroke-linejoin="round" fill="none"/>
  </svg>`,
  shield: `<svg viewBox="0 0 16 16" fill="none"><path d="M8 2L3 4v3c0 3.3 5 6 5 6s5-2.7 5-6V4L8 2z" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M6.5 8.5L8 10l2.5-3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  snow: `<svg viewBox="0 0 16 16" fill="none"><path d="M8 2v12M4 4l8 8M4 12l8-8M2 8h12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><circle cx="8" cy="8" r="3" stroke="currentColor" stroke-width="1.3" fill="none"/></svg>`,
  droplet: `<svg viewBox="0 0 16 16" fill="none"><path d="M8 2C8 2 4 6.5 4 9.5C4 11.7 5.8 13.5 8 13.5S12 11.7 12 9.5C12 6.5 8 2 8 2Z" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M6.5 9.5C6.5 10.3 7.2 11 8 11" stroke="currentColor" stroke-width="1.2"/></svg>`,
  sand: `<svg viewBox="0 0 16 16" fill="none"><path d="M4 2h8l-2 4H6L4 2z" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M5 6l-2 8h10l-2-8" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M6 10h4" stroke="currentColor" stroke-width="1.2"/></svg>`,
  sync: `<svg viewBox="0 0 16 16" fill="none"><path d="M13 4C11 2 9 2 7 4S3 8 3 10" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><path d="M3 12c2 2 4 2 6 0s4-4 4-6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><path d="M10 4l3-2v3l-3-1z" fill="currentColor"/><path d="M6 12l-3 2v-3l3 1z" fill="currentColor"/></svg>`,
  arrow: `<svg viewBox="0 0 16 16" fill="none"><path d="M2 12l6-8 6 8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  target: `<svg viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.3"/><circle cx="8" cy="8" r="2.5" stroke="currentColor" stroke-width="1.3" fill="rgba(0,175,255,0.15)"/><circle cx="8" cy="8" r="1" fill="currentColor"/></svg>`,
}

/** 子选项小图标 */
const subIconMap: Record<string, string> = {
  flood: 'shield',
  ice: 'snow',
  supply: 'droplet',
  'sediment-period': 'sand',
  'multi-objective': 'target',
  'ice-sediment': 'snow',
  'cross-section': 'arrow',
  reach: 'target',
  'multi-energy': 'sync',
}
</script>

<template>
  <div class="dispatch-scenario-view">
    <!-- 步骤条（新版 6 步） -->
    <ModelConfigStepBar :current-step="1" version="new" />

    <!-- 方案名称输入行 -->
    <ScenarioNameRow v-model="scenarioName" />

    <!-- 主体：3 个大卡片 -->
    <div class="main-content">
      <div class="cards-grid">
        <ScenarioCard
          v-for="cat in categories"
          :key="cat.id"
          :category="cat"
          :selected-category-id="selectedCategoryId"
          :selected-sub-option-id="selectedSubOptionId"
          :svg-icons="svgIcons"
          :sub-icon-map="subIconMap"
          @select-category="handleSelectCategory"
          @select-sub-option="handleSelectSubOption"
        />
      </div>
    </div>

    <!-- 底部操作栏 -->
    <ModelConfigFooter
      :step="1"
      @cancel="handleCancel"
      @save="handleSave"
      @next="handleNext"
    />
  </div>

  <!-- 保存确认弹窗 -->
  <ConfirmActionDialog
    v-model:visible="saveDialogVisible"
    title="保存确认"
    icon-color="#00afff"
    main-text="确认保存当前调度场景配置？"
    desc-text="保存后所选场景类型和子选项将保留。"
    confirm-text="确认保存"
    cancel-text="取消"
    @confirm="confirmSave"
    @cancel="saveDialogVisible = false"
  />

  <!-- 取消确认弹窗 -->
  <ConfirmActionDialog
    v-model:visible="cancelDialogVisible"
    title="取消确认"
    icon-color="#f0a020"
    main-text="确认取消当前操作？"
    desc-text="取消后当前页面的更改将不会保存。"
    confirm-text="确认取消"
    cancel-text="继续编辑"
    @confirm="confirmCancel"
    @cancel="cancelDialogVisible = false"
  />
</template>

<style scoped>
.dispatch-scenario-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
  gap: 0;
  overflow: hidden;
  background: rgba(var(--tech-bg-rgb), 0.92);
}

/* ===== 主体区域 ===== */
.main-content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: 0 12px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  height: 100%;
}
</style>
