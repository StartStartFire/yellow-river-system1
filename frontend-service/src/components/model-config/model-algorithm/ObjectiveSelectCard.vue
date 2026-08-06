<script setup lang="ts">
import type { DispatchObjective } from '@/types/model'

interface Props {
  objectives: DispatchObjective[]
  selected: string[]
  icons: Record<string, string>
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'toggle', id: string): void
}>()
</script>

<template>
  <div class="card-base objectives-card">
    <div class="card-header">
      <div class="card-icon-box obj-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="9"/>
          <circle cx="12" cy="12" r="4"/>
          <circle cx="12" cy="12" r="1.5" fill="currentColor"/>
        </svg>
      </div>
      <div class="card-title-group">
        <span class="card-title">调度目标</span>
        <span class="card-sub">选择需要优化的目标（可多选）</span>
      </div>
      <span class="obj-badge">{{ selected.length }} / {{ objectives.length }}</span>
    </div>
    <div class="card-body">
      <div class="obj-grid">
        <div
          v-for="obj in objectives"
          :key="obj.id"
          class="obj-item"
          :class="{ 'obj-active': selected.includes(obj.id) }"
          @click="emit('toggle', obj.id)"
        >
          <div class="obj-item-icon" v-html="icons[obj.icon] || ''"></div>
          <div class="obj-item-info">
            <div class="obj-item-name">{{ obj.name }}</div>
            <div class="obj-item-desc">{{ obj.description }}</div>
          </div>
          <div class="obj-check" :class="{ checked: selected.includes(obj.id) }">
            <svg v-if="selected.includes(obj.id)" width="12" height="12" viewBox="0 0 16 16" fill="none">
              <path d="M4 8l3 3 5-6" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.obj-icon { background: rgba(179, 127, 235, 0.12); color: #b37feb; }

.card-title-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--tech-text-primary);
}

.card-sub {
  font-size: 10px;
  color: var(--tech-text-placeholder);
}

.card-body {
  flex: 1;
  padding: 8px 10px;
  overflow: hidden;
}

.obj-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.obj-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.obj-item:hover { background: rgba(179, 127, 235, 0.04); }
.obj-item.obj-active { background: rgba(179, 127, 235, 0.06); border-color: rgba(179, 127, 235, 0.2); }

.obj-item-icon { width: 16px; height: 16px; color: var(--tech-text-placeholder); flex-shrink: 0; }
.obj-item.obj-active .obj-item-icon { color: #b37feb; }
.obj-item-info { min-width: 0; flex: 1; }
.obj-item-name { font-size: 11px; font-weight: 600; color: var(--tech-text-regular); }
.obj-item.obj-active .obj-item-name { color: var(--tech-text-primary); }
.obj-item-desc { font-size: 9px; color: var(--tech-text-placeholder); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.obj-check {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid rgba(80, 100, 120, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.obj-check.checked { border-color: #b37feb; background: #b37feb; }

.obj-badge {
  font-size: 10px;
  color: #8a7ab8;
  background: rgba(179, 127, 235, 0.08);
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}
</style>
