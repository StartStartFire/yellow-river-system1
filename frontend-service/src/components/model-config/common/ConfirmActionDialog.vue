<script setup lang="ts">
/**
 * ConfirmActionDialog — 通用确认弹窗
 *
 * 用于保存 / 取消等需要二次确认的场景。
 * 通过 iconType 切换图标（success / warning），confirmType 切换确认按钮风格。
 */
import { computed } from 'vue'

interface Props {
  /** 是否显示 */
  visible: boolean
  /** 弹窗标题 */
  title: string
  /** 图标颜色（覆盖默认） */
  iconColor?: string
  /** 图标类型：success 对勾 / warning 叉号 */
  iconType?: 'success' | 'warning'
  /** 主文案 */
  mainText: string
  /** 描述文案 */
  descText?: string
  /** 确认按钮文案 */
  confirmText?: string
  /** 取消按钮文案 */
  cancelText?: string
  /** 确认按钮类型 */
  confirmType?: 'primary' | 'warning'
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: '',
  iconType: 'success',
  descText: '',
  confirmText: '确认',
  cancelText: '取消',
  confirmType: 'primary',
})

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const dialogVisible = computed({
  get: () => props.visible,
  set: (val: boolean) => emit('update:visible', val),
})

/** 实际使用的图标颜色（未传时按 iconType 取默认） */
const resolvedIconColor = computed(() => {
  if (props.iconColor) return props.iconColor
  return props.iconType === 'warning' ? '#f0a020' : '#00afff'
})

const handleCancel = () => {
  emit('cancel')
  emit('update:visible', false)
}

const handleConfirm = () => {
  emit('confirm')
}
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
      <!-- 成功图标（对勾） -->
      <svg v-if="iconType === 'success'" width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
        <circle cx="24" cy="24" r="22" :stroke="resolvedIconColor" stroke-width="2" :fill="resolvedIconColor + '1a'" />
        <path d="M16 24l6 6 10-10" :stroke="resolvedIconColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <!-- 警告图标（叉号） -->
      <svg v-else width="48" height="48" viewBox="0 0 48 48" fill="none" class="dialog-icon">
        <circle cx="24" cy="24" r="22" :stroke="resolvedIconColor" stroke-width="2" :fill="resolvedIconColor + '1a'" />
        <path d="M16 16l16 16M32 16l-16 16" :stroke="resolvedIconColor" stroke-width="2.5" stroke-linecap="round" />
      </svg>
      <div class="dialog-text">
        <span class="dialog-title-main">{{ mainText }}</span>
        <span v-if="descText" class="dialog-desc">{{ descText }}</span>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button size="small" @click="handleCancel">{{ cancelText }}</el-button>
        <el-button :type="confirmType" size="small" @click="handleConfirm">{{ confirmText }}</el-button>
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
</style>
