import { defineStore } from 'pinia'
import { ref } from 'vue'

export type TaskStatus = 'idle' | 'running' | 'completed' | 'failed'

export interface TaskState {
  id: string
  name: string
  status: TaskStatus
  progress: number
  message: string
}

export const useTaskStore = defineStore('task', () => {
  // 当前模型配置步骤（1-5）
  const currentStep = ref<number>(1)

  // 当前模拟任务状态
  const taskState = ref<TaskState>({
    id: '',
    name: '',
    status: 'idle',
    progress: 0,
    message: ''
  })

  // 设置当前模型配置步骤
  const setCurrentStep = (step: number) => {
    if (step >= 1 && step <= 5) {
      currentStep.value = step
    }
  }

  // 设置任务状态
  const setTaskState = (state: Partial<TaskState>) => {
    taskState.value = { ...taskState.value, ...state }
  }

  // 更新任务进度
  const updateProgress = (progress: number) => {
    taskState.value.progress = Math.min(Math.max(progress, 0), 100)
  }

  // 重置任务状态
  const resetTask = () => {
    taskState.value = {
      id: '',
      name: '',
      status: 'idle',
      progress: 0,
      message: ''
    }
  }

  return {
    currentStep,
    taskState,
    setCurrentStep,
    setTaskState,
    updateProgress,
    resetTask
  }
})
