<script setup lang="ts">
/**
 * ConstraintPanel — 约束条件配置面板
 *
 * 包含两组约束：
 *   1. 起调水位（龙羊峡 / 刘家峡）
 *   2. 防凌期最小流量（11月 ~ 3月）
 * 使用 v-model 双向绑定约束值，值变化时实时同步到父组件。
 */
export interface ConstraintGroup {
  /** 起调水位 */
  initialWaterLevelLongyangxia: number | null
  initialWaterLevelLiujiaxia: number | null
  /** 防凌流量 [11月,12月,1月,2月,3月] */
  icePreventionFlows: number[] | null
}

interface Props {
  modelValue: ConstraintGroup
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: ConstraintGroup): void
}>()

const defaults = {
  longyangxia: 2580,
  liujiaxia: 1720,
  icePrevention: [610, 420, 420, 420, 420],
} as const

const iceLabels = ['11月', '12月', '1月', '2月', '3月']

const setLongyangxia = (val: number | null) => {
  emit('update:modelValue', { ...props.modelValue, initialWaterLevelLongyangxia: val })
}
const setLiujiaxia = (val: number | null) => {
  emit('update:modelValue', { ...props.modelValue, initialWaterLevelLiujiaxia: val })
}
const setIceFlow = (idx: number, val: number | null) => {
  const flows = props.modelValue.icePreventionFlows ? [...props.modelValue.icePreventionFlows] : [...defaults.icePrevention]
  if (val !== null) flows[idx] = val
  emit('update:modelValue', { ...props.modelValue, icePreventionFlows: flows })
}
const resetDefaults = () => {
  emit('update:modelValue', {
    initialWaterLevelLongyangxia: defaults.longyangxia,
    initialWaterLevelLiujiaxia: defaults.liujiaxia,
    icePreventionFlows: [...defaults.icePrevention],
  })
}
</script>

<template>
  <div class="constraint-section">
    <div class="constraint-header">
      <div class="constraint-title-group">
        <div class="constraint-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="1"/>
            <path d="M9 14h6M9 10h6"/>
          </svg>
        </div>
        <div class="constraint-title-text">
          <span class="constraint-title">约束条件</span>
          <span class="constraint-sub">起调水位 · 防凌流量</span>
        </div>
        <button class="constraint-edit-btn" @click="resetDefaults" title="恢复默认值">
          <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
            <path d="M2 8c0-3.3 2.7-6 6-6s6 2.7 6 6-2.7 6-6 6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            <path d="M2 8h4M2 8l2-2M2 8l2 2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          默认
        </button>
      </div>
    </div>

    <div class="constraint-body">
      <!-- 起调水位 -->
      <div class="constraint-group">
        <div class="constraint-group-title">起调水位</div>
        <div class="constraint-input-row">
          <div class="constraint-input-item">
            <label class="constraint-label">龙羊峡</label>
            <el-input-number
              :model-value="props.modelValue.initialWaterLevelLongyangxia ?? defaults.longyangxia"
              @update:model-value="setLongyangxia"
              :min="2530" :max="2600" :step="1"
              size="small" controls-position="right"
              class="dark-input-number"
            />
            <span class="constraint-unit">m</span>
          </div>
          <div class="constraint-input-item">
            <label class="constraint-label">刘家峡</label>
            <el-input-number
              :model-value="props.modelValue.initialWaterLevelLiujiaxia ?? defaults.liujiaxia"
              @update:model-value="setLiujiaxia"
              :min="1690" :max="1735" :step="1"
              size="small" controls-position="right"
              class="dark-input-number"
            />
            <span class="constraint-unit">m</span>
          </div>
        </div>
      </div>

      <!-- 防凌流量 -->
      <div class="constraint-group">
        <div class="constraint-group-title">防凌期最小下泄流量</div>
        <div class="constraint-input-row constraint-input-row-multi">
          <div v-for="(label, idx) in iceLabels" :key="idx" class="constraint-input-item">
            <label class="constraint-label">{{ label }}</label>
            <el-input-number
              :model-value="(props.modelValue.icePreventionFlows ?? defaults.icePrevention)[idx]"
              @update:model-value="(val: number | undefined) => setIceFlow(idx, val ?? null)"
              :min="300" :max="1200" :step="10"
              size="small" controls-position="right"
              class="dark-input-number"
            />
          </div>
          <span class="constraint-unit">m³/s</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.constraint-section {
  border: 1px solid rgba(50, 150, 255, 0.12);
  border-radius: 10px;
  background: rgba(10, 25, 41, 0.4);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.constraint-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(50, 150, 255, 0.08);
  flex-shrink: 0;
}

.constraint-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.constraint-edit-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  font-size: 10px;
  color: #5a8abf;
  background: rgba(var(--tech-blue-rgb), 0.06);
  border: 1px solid rgba(50, 150, 255, 0.2);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s;
}

.constraint-edit-btn:hover { background: rgba(var(--tech-blue-rgb), 0.12); border-color: rgba(var(--tech-blue-rgb), 0.4); color: var(--tech-cyan); }

.constraint-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 229, 255, 0.1);
  color: var(--tech-cyan-light);
}

.constraint-title-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.constraint-title { font-size: 13px; font-weight: 600; color: var(--tech-text-primary); }
.constraint-sub { font-size: 10px; color: var(--tech-text-placeholder); }

/* ===== 约束主体区域 ===== */
.constraint-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 12px;
  flex: 1;
}

.constraint-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 6px;
  background: rgba(17, 37, 54, 0.4);
  border: 1px solid rgba(50, 150, 255, 0.06);
}

.constraint-group-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--tech-text-secondary);
}

.constraint-input-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.constraint-input-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.constraint-label {
  font-size: 10px;
  color: var(--tech-text-placeholder);
  white-space: nowrap;
  min-width: 28px;
}

.constraint-unit {
  font-size: 10px;
  color: var(--tech-text-placeholder);
  margin-left: 2px;
}

.dialog-footer { display: flex; justify-content: flex-end; gap: 8px; }
</style>
