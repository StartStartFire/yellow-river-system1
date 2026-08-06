<script setup lang="ts">
/**
 * DataContentToolbar — 模型数据右侧顶部操作栏
 *
 * 包含：当前路径展示（分组名 / 菜单项名）+ 上传 / 下载按钮。
 */
interface Props {
  /** 当前分组名 */
  groupName: string
  /** 当前菜单项名 */
  menuItemName: string
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'upload'): void
  (e: 'download'): void
}>()

const handleUpload = () => emit('upload')
const handleDownload = () => emit('download')
</script>

<template>
  <div class="toolbar">
    <div class="toolbar-left">
      <div class="current-info">
        <span class="info-label">{{ groupName }}</span>
        <span class="info-divider">/</span>
        <span class="info-value">{{ menuItemName }}</span>
      </div>
    </div>
    <div class="toolbar-right">
      <el-button type="primary" size="small" @click="handleUpload" class="toolbar-btn-custom">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
          <path d="M8 2v9M4 6l4-4 4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M2 12v2h12v-2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
        </svg>
        上传数据
      </el-button>
      <el-button size="small" @click="handleDownload" class="toolbar-btn-custom">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
          <path d="M8 11V2M4 7l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M2 12v2h12v-2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
        </svg>
        下载模板
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(var(--tech-blue-rgb), 0.1);
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.current-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.info-label {
  color: var(--tech-text-placeholder);
}

.info-divider {
  color: rgba(50, 150, 255, 0.3);
}

.info-value {
  color: var(--tech-cyan);
  font-weight: 500;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-btn-custom {
  font-size: 12px !important;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.btn-icon {
  flex-shrink: 0;
}
</style>
