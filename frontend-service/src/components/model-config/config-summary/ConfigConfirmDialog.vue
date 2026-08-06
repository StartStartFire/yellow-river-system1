<script setup lang="ts">
import { computed } from 'vue'

type ConfirmColor = 'primary' | 'success' | 'warning' | 'danger' | 'info'

interface Props {
  visible: boolean
  title: string
  icon: string
  message: string
  confirmText: string
  cancelText: string
  confirmColor?: ConfirmColor
}

const props = withDefaults(defineProps<Props>(), {
  confirmColor: 'primary',
})

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (v: boolean) => emit('update:visible', v),
})

const descMap: Record<string, string> = {
  save: '保存后当前配置汇总状态将保留。',
  cancel: '取消后当前页面的更改将不会保存。',
  delete: '删除后不可恢复，请谨慎操作。',
}

const desc = computed(() => descMap[props.icon] || '')
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    width="400px"
    :close-on-click-modal="false"
    class="confirm-dialog"
  >
    <div class="dialog-body">
      <!-- 保存图标 -->
      <svg v-if="icon === 'save'" width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
        <circle cx="24" cy="24" r="22" stroke="#00afff" stroke-width="2" fill="rgba(0,175,255,0.1)"/>
        <path d="M16 24l6 6 10-10" stroke="#00afff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <!-- 取消图标 -->
      <svg v-else-if="icon === 'cancel'" width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
        <circle cx="24" cy="24" r="22" stroke="#f0a020" stroke-width="2" fill="rgba(240,160,32,0.1)"/>
        <path d="M16 16l16 16M32 16l-16 16" stroke="#f0a020" stroke-width="2.5" stroke-linecap="round"/>
      </svg>
      <!-- 删除图标 -->
      <svg v-else-if="icon === 'delete'" width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
        <circle cx="24" cy="24" r="22" stroke="#ff4d4f" stroke-width="2" fill="rgba(255,77,79,0.1)"/>
        <path d="M16 16l16 16M32 16l-16 16" stroke="#ff4d4f" stroke-width="2.5" stroke-linecap="round"/>
      </svg>
      <div class="dialog-text">
        <span class="dialog-title-main">{{ message }}</span>
        <span v-if="desc" class="dialog-desc">{{ desc }}</span>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button size="small" @click="emit('cancel')">{{ cancelText }}</el-button>
        <el-button :type="confirmColor" size="small" @click="emit('confirm')">{{ confirmText }}</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
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
  color: var(--tech-text-primary);
  font-size: 14px;
  font-weight: 500;
}

.dialog-desc {
  color: var(--tech-text-secondary);
  font-size: 12px;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* Element Plus 深色覆盖（弹窗按钮 teleport 到 body，需本组件内自带） */
:deep(.el-button--danger) {
  --el-button-bg-color: rgba(255, 77, 79, 0.15);
  --el-button-border-color: rgba(255, 77, 79, 0.5);
  --el-button-text-color: #ff6b6b;
  --el-button-hover-bg-color: rgba(255, 77, 79, 0.25);
  --el-button-hover-border-color: rgba(255, 77, 79, 0.7);
  --el-button-hover-text-color: #ff8585;
}
</style>
