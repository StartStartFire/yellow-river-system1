<script setup lang="ts">
import { computed } from 'vue'

interface StepItem {
  step: number
  title: string
  desc: string
}

interface Props {
  currentStep: number
  /** 步骤配置，默认使用旧 5 步流程；传入 'new' 使用新 6 步流程 */
  version?: 'old' | 'new'
}

const emit = defineEmits<{
  (e: 'step-click', step: number): void
}>()

const props = withDefaults(defineProps<Props>(), {
  version: 'old',
})

const handleStepClick = (step: number) => {
  // Only allow clicking on completed steps (steps before current)
  if (step < props.currentStep) {
    emit('step-click', step)
  }
}

/** 旧版 5 步流程 */
const oldSteps: StepItem[] = [
  { step: 1, title: '调度数据', desc: '选择与管理模型输入数据' },
  { step: 2, title: '基础配置', desc: '设置调度规则与工程目标' },
  { step: 3, title: '模型算法', desc: '选择模型与优化算法' },
  { step: 4, title: '场景配置', desc: '布置调度场景与约束条件' },
  { step: 5, title: '配置汇总', desc: '确认配置并开始计算' },
]

/** 新版 6 步流程 */
const newSteps: StepItem[] = [
  { step: 1, title: '调度场景', desc: '选择调度目的与业务场景' },
  { step: 2, title: '调度主体', desc: '选择水库、时段与周期' },
  { step: 3, title: '调度数据', desc: '上传与选择水文数据' },
  { step: 4, title: '模型算法', desc: '选择模型与优化算法' },
  { step: 5, title: '场景配置', desc: '配置约束条件与参数' },
  { step: 6, title: '配置汇总', desc: '确认配置并开始计算' },
]

const steps = computed(() => props.version === 'new' ? newSteps : oldSteps)
</script>

<template>
  <div
    class="step-bar flex items-center px-6 py-3"
    style="background: rgba(6, 30, 70, 0.85); border: 1px solid rgba(50, 150, 255, 0.35); border-radius: 12px;"
  >
    <div
      v-for="(s, idx) in steps"
      :key="s.step"
      class="flex items-center flex-1"
    >
      <!-- 步骤项 -->
      <div
        class="flex items-center gap-3 cursor-pointer"
        :class="{
          'cursor-pointer': s.step < currentStep,
          'cursor-default': s.step >= currentStep,
        }"
        @click="handleStepClick(s.step)"
      >
        <!-- 步骤编号 -->
        <div
          class="step-number flex items-center justify-center rounded-full text-sm font-bold shrink-0 transition-all duration-300"
          :class="{
            'active-step': s.step === currentStep,
            'completed-step': s.step < currentStep,
            'pending-step': s.step > currentStep,
          }"
        >
          <span v-if="s.step < currentStep" class="text-black">✓</span>
          <span v-else>{{ s.step }}</span>
        </div>
        <!-- 步骤文字 -->
        <div class="flex flex-col leading-tight">
          <span
            class="text-sm font-semibold transition-all duration-300"
            :class="s.step === currentStep ? 'text-tech-primary' : 'text-tech-muted'"
          >
            {{ s.title }}
          </span>
          <span class="text-xs text-tech-muted/60 whitespace-nowrap">{{ s.desc }}</span>
        </div>
      </div>

      <!-- 连接线（最后一项不显示） -->
      <div v-if="idx < steps.length - 1" class="flex-1 mx-4">
        <div
          class="h-px transition-all duration-300"
          :class="s.step <= currentStep ? 'bg-tech-primary/50' : 'bg-tech-border'"
        ></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.step-number {
  width: 32px;
  height: 32px;
}

.active-step {
  background: linear-gradient(135deg, rgba(0, 175, 255, 0.3) 0%, rgba(0, 229, 255, 0.15) 100%);
  border: 1px solid rgba(0, 175, 255, 0.6);
  color: #00d4ff;
  box-shadow: 0 0 12px rgba(0, 175, 255, 0.25);
}

.completed-step {
  background: rgba(0, 255, 136, 0.2);
  border: 1px solid rgba(0, 255, 136, 0.5);
  color: #00ff88;
}

.pending-step {
  background: rgba(50, 150, 255, 0.08);
  border: 1px solid rgba(50, 150, 255, 0.2);
  color: #5a6f83;
}
</style>
