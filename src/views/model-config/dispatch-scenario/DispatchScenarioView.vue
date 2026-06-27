<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ModelConfigStepBar from '@/components/model-config/ModelConfigStepBar.vue'
import ModelConfigFooter from '@/components/model-config/ModelConfigFooter.vue'
import { useModelConfigStore } from '@/stores/modelConfig'
import { dispatchScenarioCategories } from '@/mock/modelConfig'
import type { DispatchScenarioCategory, DispatchSubOption } from '@/mock/modelConfig'

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
  return selectedCategoryId.value !== '' && selectedSubOptionId.value !== ''
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
  // 写入 Store
  store.setDispatchScenario({
    categoryId: selectedCategoryId.value,
    subOptionId: selectedSubOptionId.value,
  })
  // 联动调度目标
  store.syncObjectivesFromScenario(selectedSubOptionId.value)
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
  // 写入 Store
  store.setDispatchScenario({
    categoryId: selectedCategoryId.value,
    subOptionId: selectedSubOptionId.value,
  })
  // 联动调度目标
  store.syncObjectivesFromScenario(selectedSubOptionId.value)
  // 标记 Step 1 已完成
  store.markStepCompleted(1)
  // 后续再改路由
  router.push('/model-config/model-data')
}

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

    <!-- 主体：3 个大卡片 -->
    <div class="main-content">
      <div class="cards-grid">
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="scenario-card"
          :class="{ 'card-selected': selectedCategoryId === cat.id }"
          @click="handleSelectCategory(cat.id)"
        >
          <!-- 选中标记 -->
          <div v-if="selectedCategoryId === cat.id" class="check-mark">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="7" fill="rgba(0,175,255,0.2)" stroke="#00afff" stroke-width="1.5"/>
              <path d="M5 8.5l2 2 4-4.5" stroke="#00afff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>

          <!-- 图标 -->
          <div class="card-icon-wrap" :class="{ 'icon-selected': selectedCategoryId === cat.id }">
            <div class="card-icon-svg" v-html="svgIcons[cat.icon]"></div>
          </div>

          <!-- 标题 -->
          <div class="card-title" :class="{ 'title-selected': selectedCategoryId === cat.id }">
            {{ cat.name }}
          </div>

          <!-- 描述 -->
          <div class="card-desc">{{ cat.description }}</div>

          <!-- 分隔线 -->
          <div class="card-divider" :class="{ 'divider-selected': selectedCategoryId === cat.id }"></div>

          <!-- 子选项列表 -->
          <div class="sub-options">
            <div
              v-for="sub in cat.subOptions"
              :key="sub.id"
              class="sub-option-item"
              :class="{
                'sub-selected': selectedCategoryId === cat.id && selectedSubOptionId === sub.id,
                'sub-inactive': selectedCategoryId !== cat.id,
              }"
              @click.stop="handleSelectSubOption(cat.id, sub.id)"
            >
              <!-- radio 圆点 -->
              <div class="radio-dot" :class="{
                'radio-checked': selectedCategoryId === cat.id && selectedSubOptionId === sub.id,
              }">
                <div v-if="selectedCategoryId === cat.id && selectedSubOptionId === sub.id" class="radio-inner"></div>
              </div>

              <!-- 子选项文字 -->
              <div class="sub-text">
                <span class="sub-name">{{ sub.name }}</span>
                <span class="sub-desc">{{ sub.description }}</span>
              </div>

              <!-- 小图标 -->
              <div v-if="subIconMap[sub.id]" class="sub-icon" v-html="svgIcons[subIconMap[sub.id] || '']"></div>
            </div>
          </div>
        </div>
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
  <el-dialog
    v-model="saveDialogVisible"
    title="保存确认"
    width="400px"
    :close-on-click-modal="false"
    class="confirm-dialog"
  >
    <div class="dialog-body">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
        <circle cx="24" cy="24" r="22" stroke="#00afff" stroke-width="2" fill="rgba(0,175,255,0.1)"/>
        <path d="M16 24l6 6 10-10" stroke="#00afff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <div class="dialog-text">
        <span class="dialog-title-main">确认保存当前调度场景配置？</span>
        <span class="dialog-desc">保存后所选场景类型和子选项将保留。</span>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button size="small" @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" size="small" @click="confirmSave">确认保存</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 取消确认弹窗 -->
  <el-dialog
    v-model="cancelDialogVisible"
    title="取消确认"
    width="400px"
    :close-on-click-modal="false"
    class="confirm-dialog"
  >
    <div class="dialog-body">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
        <circle cx="24" cy="24" r="22" stroke="#f0a020" stroke-width="2" fill="rgba(240,160,32,0.1)"/>
        <path d="M16 16l16 16M32 16l-16 16" stroke="#f0a020" stroke-width="2.5" stroke-linecap="round"/>
      </svg>
      <div class="dialog-text">
        <span class="dialog-title-main">确认取消当前操作？</span>
        <span class="dialog-desc">取消后当前页面的更改将不会保存。</span>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button size="small" @click="cancelDialogVisible = false">继续编辑</el-button>
        <el-button type="warning" size="small" @click="confirmCancel">确认取消</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.dispatch-scenario-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 8px 12px;
  gap: 8px;
  overflow: hidden;
}

/* ===== 主体区域 ===== */
.main-content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  height: 100%;
}

/* ===== 场景卡片 ===== */
.scenario-card {
  position: relative;
  display: flex;
  flex-direction: column;
  background: rgba(6, 30, 70, 0.5);
  border: 1px solid rgba(50, 150, 255, 0.25);
  border-radius: 12px;
  padding: 24px 20px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
}

.scenario-card:hover {
  border-color: rgba(0, 175, 255, 0.35);
  background: rgba(0, 175, 255, 0.03);
}

.scenario-card.card-selected {
  border-color: rgba(0, 175, 255, 0.6);
  background: rgba(0, 175, 255, 0.06);
  box-shadow: 0 0 20px rgba(0, 175, 255, 0.15), 0 4px 24px rgba(0, 0, 0, 0.25);
}

/* ===== 选中标记（右上角） ===== */
.check-mark {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 2;
  animation: checkPop 0.25s ease;
}

@keyframes checkPop {
  0% { transform: scale(0); opacity: 0; }
  60% { transform: scale(1.2); }
  100% { transform: scale(1); opacity: 1; }
}

/* ===== 图标 ===== */
.card-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  margin: 0 auto 12px;
  border-radius: 16px;
  background: rgba(0, 175, 255, 0.06);
  border: 1px solid rgba(50, 150, 255, 0.2);
  transition: all 0.3s ease;
}

.card-icon-wrap.icon-selected {
  background: rgba(0, 175, 255, 0.15);
  border-color: rgba(0, 175, 255, 0.4);
  box-shadow: 0 0 16px rgba(0, 175, 255, 0.12);
}

.card-icon-svg {
  width: 48px;
  height: 48px;
  color: #5a8abf;
  transition: color 0.3s ease;
}

.icon-selected .card-icon-svg {
  color: #00d4ff;
}

/* ===== 标题 ===== */
.card-title {
  text-align: center;
  font-size: 16px;
  font-weight: 700;
  color: #7a8fa3;
  margin-bottom: 8px;
  transition: color 0.3s ease;
  letter-spacing: 0.5px;
}

.title-selected {
  color: #e0e6ed;
}

/* ===== 描述 ===== */
.card-desc {
  text-align: center;
  font-size: 11px;
  line-height: 1.6;
  color: #5a6f83;
  margin-bottom: 14px;
  min-height: 36px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ===== 分隔线 ===== */
.card-divider {
  width: 40px;
  height: 2px;
  margin: 0 auto 14px;
  background: rgba(50, 150, 255, 0.2);
  border-radius: 1px;
  transition: all 0.3s ease;
}

.divider-selected {
  width: 60px;
  background: linear-gradient(90deg, rgba(0, 175, 255, 0.3), rgba(0, 229, 255, 0.6));
}

/* ===== 子选项列表 ===== */
.sub-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.sub-option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.sub-option-item:hover {
  background: rgba(0, 175, 255, 0.05);
}

.sub-option-item.sub-selected {
  background: rgba(0, 175, 255, 0.08);
  border-color: rgba(0, 175, 255, 0.25);
}

.sub-option-item.sub-inactive {
  opacity: 0.55;
}

.sub-option-item.sub-inactive:hover {
  opacity: 0.75;
  background: rgba(0, 175, 255, 0.03);
}

/* ===== radio 圆点 ===== */
.radio-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid rgba(80, 100, 120, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.25s ease;
}

.radio-dot.radio-checked {
  border-color: #00afff;
  box-shadow: 0 0 6px rgba(0, 175, 255, 0.3);
}

.radio-inner {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00afff;
  animation: radioPop 0.2s ease;
}

@keyframes radioPop {
  0% { transform: scale(0); }
  100% { transform: scale(1); }
}

/* ===== 子选项文字 ===== */
.sub-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.sub-name {
  font-size: 13px;
  font-weight: 600;
  color: #c0c8d4;
  transition: color 0.2s ease;
}

.sub-selected .sub-name {
  color: #e0e6ed;
}

.sub-desc {
  font-size: 10px;
  color: #5a6f83;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.sub-icon {
  width: 16px;
  height: 16px;
  color: #5a6f83;
  flex-shrink: 0;
  opacity: 0.6;
}

.sub-selected .sub-icon {
  color: #00d4ff;
  opacity: 0.8;
}

/* ===== 弹窗样式 ===== */
.confirm-dialog :deep(.el-dialog) {
  background: rgba(6, 30, 70, 0.98) !important;
  border: 1px solid rgba(50, 150, 255, 0.4);
  border-radius: 12px;
}

.confirm-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(50, 150, 255, 0.2);
  padding: 16px 20px;
  margin: 0;
}

.confirm-dialog :deep(.el-dialog__title) {
  color: #e0e6ed;
  font-size: 15px;
  font-weight: 600;
}

.confirm-dialog :deep(.el-dialog__body) {
  padding: 24px 20px;
}

.confirm-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid rgba(50, 150, 255, 0.1);
  padding: 12px 20px;
}

.dialog-body {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.dialog-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.dialog-text {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.dialog-title-main {
  color: #e0e6ed;
  font-size: 14px;
  font-weight: 500;
}

.dialog-desc {
  color: #7a8fa3;
  font-size: 12px;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

:deep(.el-button) {
  --el-button-bg-color: transparent;
  --el-button-border-color: rgba(50, 150, 255, 0.3);
  --el-button-text-color: #c0c8d4;
  --el-button-hover-bg-color: rgba(0, 175, 255, 0.1);
  --el-button-hover-border-color: rgba(50, 150, 255, 0.5);
  --el-button-hover-text-color: #e0e6ed;
}

:deep(.el-button--primary) {
  --el-button-bg-color: rgba(0, 175, 255, 0.2);
  --el-button-border-color: rgba(0, 175, 255, 0.5);
  --el-button-text-color: #00d4ff;
  --el-button-hover-bg-color: rgba(0, 175, 255, 0.3);
  --el-button-hover-border-color: rgba(0, 175, 255, 0.7);
  --el-button-hover-text-color: #00e5ff;
}
</style>
