<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import router from '@/router'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const appStore = useAppStore()

const navItems = [
  { name: '首页', path: '/home', key: 'home' },
  { name: '基础数据', path: '/basic-data', key: 'basic-data' },
  { name: '水调水情', path: '/water-condition', key: 'water-condition' },
  { name: '模型配置', path: '/model-config', key: 'model-config' },
  { name: '过程透明', path: '/process-transparent', key: 'process-transparent' },
  { name: '评价决策', path: '/evaluation-decision', key: 'evaluation-decision' },
  { name: '案例库', path: '/case-library', key: 'case-library' },
  { name: '报表统计', path: '/report-statistics', key: 'report-statistics' }
]

const activeIndex = computed(() => {
  const index = navItems.findIndex(item => route.path.startsWith(item.path))
  return index >= 0 ? index : 0
})

const currentTime = ref('')

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

const handleNavClick = (item: (typeof navItems)[0]) => {
  appStore.setActiveModule(item.key as any)
  router.push(item.path)
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-tech-bg">
    <!-- 合并的顶部栏：系统名称 + 导航 + 时间/状态 -->
    <div
      class="h-12 flex items-center px-6 border-b border-tech-border/30"
      style="background: rgba(6, 30, 70, 0.92); backdrop-filter: blur(6px);"
    >
      <!-- 左侧：系统名称 -->
      <div class="flex items-center gap-2 shrink-0">
        <div class="w-2 h-2 rounded-full bg-tech-primary animate-pulse"></div>
        <span class="text-sm font-semibold text-tech-text whitespace-nowrap">黄河上游水库群调度系统</span>
      </div>

      <!-- 中间：导航按钮 - 居中 -->
      <nav class="flex-1 flex items-center justify-center gap-1">
        <button
          v-for="(item, index) in navItems"
          :key="item.key"
          @click="handleNavClick(item)"
          class="relative px-4 py-1.5 text-xs font-medium transition-all duration-300 rounded-md whitespace-nowrap"
          :class="[
            index === activeIndex
              ? 'text-white'
              : 'text-tech-muted hover:text-tech-text hover:bg-white/5',
          ]"
        >
          <span class="relative z-10">{{ item.name }}</span>
          <div
            v-if="index === activeIndex"
            class="absolute inset-0 rounded-md"
            style="background: linear-gradient(135deg, rgba(0, 175, 255, 0.2) 0%, rgba(0, 229, 255, 0.1) 100%); border: 1px solid rgba(0, 175, 255, 0.4);"
          ></div>
        </button>
      </nav>

      <!-- 右侧：时间 + 调度状态 -->
      <div class="flex items-center gap-3 text-xs text-tech-muted shrink-0">
        <span>{{ currentTime }}</span>
        <span class="text-tech-muted/50">|</span>
        <span class="flex items-center gap-1">
          <span class="w-1.5 h-1.5 rounded-full" style="background: #00ff88;"></span>
          <span style="color: #00ff88;">正常执行</span>
        </span>
      </div>
    </div>

    <!-- 页面主体内容区 -->
    <main class="flex-1 overflow-hidden h-0 flex flex-col">
      <router-view class="flex-1 min-h-0" />
    </main>
  </div>
</template>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>