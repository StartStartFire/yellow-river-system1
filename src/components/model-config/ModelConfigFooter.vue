<script setup lang="ts">
/**
 * 模型配置底部操作栏
 * 将取消、保存、上一步、下一步居中放置
 * 根据 step 自动控制显示：
 *   step=1 → 取消、保存、下一步（无上一步）
 *   step=2~4 → 取消、上一步、保存、下一步
 *   step=5 → 不渲染（ConfigSummary 使用独立底部）
 */
defineProps<{
  step: number
}>()

defineEmits<{
  cancel: []
  save: []
  prev: []
  next: []
}>()
</script>

<template>
  <div class="model-config-footer">
    <div class="footer-content">
      <el-button size="default" @click="$emit('cancel')" class="footer-btn footer-btn-cancel">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
          <path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        取消
      </el-button>

      <el-button
        v-if="step > 1"
        size="default"
        @click="$emit('prev')"
        class="footer-btn footer-btn-prev"
      >
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
          <path d="M10 13L5 8l5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        上一步
      </el-button>

      <div class="footer-divider" />

      <el-button size="default" @click="$emit('save')" class="footer-btn footer-btn-save">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
          <path d="M13 5v9H3V2h7l3 3z" stroke="currentColor" stroke-width="1.3" fill="none"/>
          <path d="M5 12h6" stroke="currentColor" stroke-width="1.3"/>
          <path d="M5 9h6" stroke="currentColor" stroke-width="1.3"/>
        </svg>
        保存
      </el-button>

      <div class="footer-divider" />

      <el-button
        v-if="step < 5"
        type="primary"
        size="default"
        @click="$emit('next')"
        class="footer-btn footer-btn-next"
      >
        下一步
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" class="btn-icon">
          <path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.model-config-footer {
  flex-shrink: 0;
  background: rgba(6, 30, 70, 0.85);
  border: 1px solid rgba(50, 150, 255, 0.35);
  border-radius: 12px;
  padding: 10px 16px;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.footer-btn {
  font-size: 12px !important;
  display: inline-flex !important;
  align-items: center;
  gap: 4px;
}

.footer-divider {
  width: 1px;
  height: 20px;
  background: rgba(50, 150, 255, 0.15);
  flex-shrink: 0;
}

/* 取消按钮 - 默认为灰色 */
.footer-btn-cancel {
  color: #7a8fa3 !important;
  border-color: rgba(80, 100, 120, 0.3) !important;
}

.footer-btn-cancel:hover {
  color: #c0c8d4 !important;
  border-color: rgba(50, 150, 255, 0.4) !important;
  background: rgba(0, 175, 255, 0.05) !important;
}

/* 保存按钮 - 青色描边 */
.footer-btn-save {
  background: rgba(0, 175, 255, 0.1) !important;
  border-color: rgba(0, 175, 255, 0.4) !important;
  color: #00d4ff !important;
}

.footer-btn-save:hover {
  background: rgba(0, 175, 255, 0.2) !important;
  border-color: rgba(0, 175, 255, 0.6) !important;
  color: #00e5ff !important;
}

/* 上一步按钮 - 默认 */
.footer-btn-prev {
  /* inherits .el-button defaults from the page */
}

/* 下一步按钮 - primary */
.footer-btn-next {
  /* inherits .el-button--primary from the page */
}

.btn-icon {
  flex-shrink: 0;
}

/* 深色主题按钮覆盖（只影响本组件内的 el-button） */
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
