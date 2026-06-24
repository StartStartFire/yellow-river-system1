<script setup lang="ts">
import { computed } from 'vue'
import type { BaseInfoGroup } from '@/mock/basicData'

interface Props {
  groups: BaseInfoGroup[]
}

const props = defineProps<Props>()

const engineeringItems = computed(() => {
  const group = props.groups.find(g => g.title === '工程属性')
  return group?.items ?? []
})

const ruleItems = computed(() => {
  const group = props.groups.find(g => g.title === '调度规则')
  return group?.items ?? []
})
</script>

<template>
  <div class="base-info-panel">
    <!-- ====== 工程属性区 ====== -->
    <section class="section">
      <div class="section-header">
        <h3 class="section-title">工程属性</h3>
      </div>
      <div class="engineering-grid">
        <div
          v-for="item in engineeringItems"
          :key="item.key"
          class="eng-card"
        >
          <div class="eng-label">{{ item.key }}</div>
          <div class="eng-value">{{ item.value }}</div>
        </div>
      </div>
    </section>

    <!-- ====== 调度规则区 ====== -->
    <section class="section">
      <div class="section-header">
        <h3 class="section-title">调度规则</h3>
      </div>
      <div class="rules-list">
        <div
          v-for="item in ruleItems"
          :key="item.key"
          class="rule-card"
        >
          <div class="rule-name">
            <span class="rule-dot"></span>
            {{ item.key }}
          </div>
          <div class="rule-desc">{{ item.value }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.base-info-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  padding-right: 4px;
}

.base-info-panel::-webkit-scrollbar {
  width: 4px;
}
.base-info-panel::-webkit-scrollbar-track {
  background: transparent;
}
.base-info-panel::-webkit-scrollbar-thumb {
  background: rgba(50, 150, 255, 0.2);
  border-radius: 2px;
}

/* ====== 公共分区 ====== */
.section {
  background: rgba(6, 30, 70, 0.5);
  border: 1px solid rgba(50, 150, 255, 0.12);
  backdrop-filter: blur(16px);
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
}

.section-header {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: rgba(10, 25, 41, 0.4);
  border-bottom: 1px solid rgba(50, 150, 255, 0.08);
}

.section-title {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #e0e6ed;
  letter-spacing: 1px;
}

/* ====== 工程属性 4 列简约布局 ====== */
.engineering-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  padding: 10px 16px;
}

.eng-card {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 6px 4px;
}

.eng-label {
  font-size: 11px;
  color: #5a7a9a;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.eng-value {
  font-size: 13px;
  color: #e0e6ed;
  font-weight: 500;
  line-height: 1.4;
}

/* ====== 调度规则条目 ====== */
.rules-list {
  padding: 8px 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rule-card {
  background: rgba(17, 37, 54, 0.4);
  border: 1px solid rgba(50, 150, 255, 0.06);
  border-radius: 8px;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: border-color 0.2s;
}

.rule-card:hover {
  border-color: rgba(0, 255, 136, 0.2);
}

.rule-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #00ff88;
}

.rule-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #00ff88;
  flex-shrink: 0;
  opacity: 0.7;
}

.rule-desc {
  font-size: 12px;
  color: #c0c8d4;
  line-height: 1.6;
  padding-left: 11px;
}
</style>
