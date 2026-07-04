<script setup lang="ts">
import type { DispatchScenarioCategory } from '@/types/model'

interface Props {
  category: DispatchScenarioCategory
  selectedCategoryId: string
  selectedSubOptionId: string
  svgIcons: Record<string, string>
  subIconMap: Record<string, string>
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'select-category', categoryId: string): void
  (e: 'select-sub-option', categoryId: string, subOptionId: string): void
}>()

const isCategorySelected = () => props.selectedCategoryId === props.category.id

const handleCardClick = () => {
  emit('select-category', props.category.id)
}

const handleSubOptionClick = (subId: string) => {
  emit('select-sub-option', props.category.id, subId)
}
</script>

<template>
  <div
    class="scenario-card"
    :class="{ 'card-selected': isCategorySelected() }"
    @click="handleCardClick"
  >
    <!-- 选中标记 -->
    <div v-if="isCategorySelected()" class="check-mark">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <circle cx="8" cy="8" r="7" fill="rgba(0,175,255,0.2)" stroke="#00afff" stroke-width="1.5"/>
        <path d="M5 8.5l2 2 4-4.5" stroke="#00afff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>

    <!-- 图标 -->
    <div class="card-icon-wrap" :class="{ 'icon-selected': isCategorySelected() }">
      <div class="card-icon-svg" v-html="svgIcons[category.icon]"></div>
    </div>

    <!-- 标题 -->
    <div class="card-title" :class="{ 'title-selected': isCategorySelected() }">
      {{ category.name }}
    </div>

    <!-- 描述 -->
    <div class="card-desc">{{ category.description }}</div>

    <!-- 分隔线 -->
    <div class="card-divider" :class="{ 'divider-selected': isCategorySelected() }"></div>

    <!-- 子选项列表 -->
    <div class="sub-options">
      <div
        v-for="sub in category.subOptions"
        :key="sub.id"
        class="sub-option-item"
        :class="{
          'sub-selected': isCategorySelected() && selectedSubOptionId === sub.id,
          'sub-inactive': !isCategorySelected(),
        }"
        @click.stop="handleSubOptionClick(sub.id)"
      >
        <!-- radio 圆点 -->
        <div class="radio-dot" :class="{
          'radio-checked': isCategorySelected() && selectedSubOptionId === sub.id,
        }">
          <div v-if="isCategorySelected() && selectedSubOptionId === sub.id" class="radio-inner"></div>
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
</template>

<style scoped>
.scenario-card {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 28px 22px 22px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  height: 100%;
  border-right: 1px solid rgba(var(--tech-blue-rgb), 0.08);
}

.scenario-card:hover {
  background: rgba(var(--tech-blue-rgb), 0.03);
}

.scenario-card.card-selected {
  background: rgba(var(--tech-blue-rgb), 0.06);
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
  width: 76px;
  height: 76px;
  margin: 0 auto 14px;
  border-radius: 18px;
  background: rgba(var(--tech-blue-rgb), 0.06);
  border: 1px solid rgba(50, 150, 255, 0.2);
  transition: all 0.3s ease;
}

.card-icon-wrap.icon-selected {
  background: rgba(var(--tech-blue-rgb), 0.15);
  border-color: rgba(var(--tech-blue-rgb), 0.4);
  box-shadow: 0 0 20px rgba(var(--tech-blue-rgb), 0.15);
}

.card-icon-svg {
  width: 56px;
  height: 56px;
  color: #5a8abf;
  transition: color 0.3s ease;
}

.icon-selected .card-icon-svg {
  color: var(--tech-cyan);
}

/* ===== 标题 ===== */
.card-title {
  text-align: center;
  font-size: 17px;
  font-weight: 700;
  color: var(--tech-text-secondary);
  margin-bottom: 10px;
  transition: color 0.3s ease;
  letter-spacing: 0.5px;
}

.title-selected {
  color: var(--tech-text-primary);
}

/* ===== 描述 ===== */
.card-desc {
  text-align: center;
  font-size: 12px;
  line-height: 1.7;
  color: var(--tech-text-placeholder);
  margin-bottom: 16px;
  min-height: 42px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ===== 分隔线 ===== */
.card-divider {
  width: 40px;
  height: 2px;
  margin: 0 auto 16px;
  background: rgba(50, 150, 255, 0.2);
  border-radius: 1px;
  transition: all 0.3s ease;
}

.divider-selected {
  width: 60px;
  background: linear-gradient(90deg, rgba(var(--tech-blue-rgb), 0.3), rgba(0, 229, 255, 0.6));
}

/* ===== 子选项列表 ===== */
.sub-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.sub-option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.sub-option-item:hover {
  background: rgba(var(--tech-blue-rgb), 0.05);
}

.sub-option-item.sub-selected {
  background: rgba(var(--tech-blue-rgb), 0.08);
  border-color: rgba(var(--tech-blue-rgb), 0.25);
}

.sub-option-item.sub-inactive {
  opacity: 0.55;
}

.sub-option-item.sub-inactive:hover {
  opacity: 0.75;
  background: rgba(var(--tech-blue-rgb), 0.03);
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
  border-color: var(--tech-blue);
  box-shadow: 0 0 6px rgba(var(--tech-blue-rgb), 0.3);
}

.radio-inner {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--tech-blue);
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
  color: var(--tech-text-regular);
  transition: color 0.2s ease;
}

.sub-selected .sub-name {
  color: var(--tech-text-primary);
}

.sub-desc {
  font-size: 10px;
  color: var(--tech-text-placeholder);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.sub-icon {
  width: 16px;
  height: 16px;
  color: var(--tech-text-placeholder);
  flex-shrink: 0;
  opacity: 0.6;
}

.sub-selected .sub-icon {
  color: var(--tech-cyan);
  opacity: 0.8;
}
</style>
